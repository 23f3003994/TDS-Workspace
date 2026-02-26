

import os
import sys
import traceback
from io import StringIO
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Literal,List
from pydantic import BaseModel, Field
from openai import OpenAI


# Create OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", ""),
    base_url=os.environ.get("OPENAI_BASE_URL", "https://aipipe.org/openai/v1")
)

# Create FastAPI app
app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)



##################################################################Q-2#####################################################################

"""
Sentiment Analysis API using FastAPI and OpenAI GPT.

This module provides a FastAPI application that analyzes the sentiment of user comments
using OpenAI's GPT model. It includes CORS support for cross-origin requests and
validates input/output using Pydantic models.
"""

class CommentRequest(BaseModel):
    """
    Request model for comment analysis.

    Attributes:
        comment (str): The user comment to analyze for sentiment.
    """
    comment: str

class SentimentResponse(BaseModel):
    """
    Response model for sentiment analysis.

    Attributes:
        sentiment (Literal["positive", "negative", "neutral"]): The sentiment classification.
        rating (int): A rating from 1 to 5 (1=highly negative, 3=neutral, 5=highly positive).
    """
    sentiment: Literal["positive", "negative", "neutral"]
    rating: int = Field(..., ge=1, le=5)

@app.post("/comment", response_model=SentimentResponse)
async def analyze_comment(request: CommentRequest):
    """
    Analyze the sentiment of a user comment using OpenAI GPT.

    This endpoint takes a comment, sends it to the OpenAI GPT model for sentiment analysis,
    and returns the sentiment classification and rating.

    Args:
        request (CommentRequest): The request containing the comment to analyze.

    Returns:
        SentimentResponse: The sentiment analysis result with sentiment and rating.

    Raises:
        HTTPException: If the comment is empty (422) or if there's an API error (500).

    LLM Response Format:
        The LLM is instructed to return a JSON object in the following format:
        {
            "sentiment": "positive" | "negative" | "neutral",
            "rating": 1-5 (integer, where 1=highly negative, 3=neutral, 5=highly positive)
        }
        Example: {"sentiment": "positive", "rating": 4}
    """
    # Validate input: check if comment is empty or whitespace-only
    if not request.comment or not request.comment.strip():
        raise HTTPException(status_code=422, detail="Comment cannot be empty")

    try:
        # Call OpenAI API for sentiment analysis
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a sentiment analysis assistant. "
                        "Analyze the sentiment of the given comment and return a JSON object with:\n"
                        "- sentiment: one of 'positive', 'negative', or 'neutral'\n"
                        "- rating: integer from 1 to 5 (5=highly positive, 3=neutral, 1=highly negative)\n"
                        "Return only valid JSON, nothing else."
                    )
                },
                {
                    "role": "user",
                    "content": request.comment
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "sentiment_analysis",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "sentiment": {
                                "type": "string",
                                "enum": ["positive", "negative", "neutral"]
                            },
                            "rating": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 5
                            }
                        },
                        "required": ["sentiment", "rating"],
                        "additionalProperties": False
                    }
                }
            }
        )

        # The 'response' variable is a ChatCompletion object from OpenAI API.
        # Structure:
        # response.choices: list of completion choices (usually 1 item)
        # response.choices[0].message.content: the JSON string returned by the LLM
        # Example content: '{"sentiment": "positive", "rating": 4}'
        #
        # Full example of the 'response' object:
        # {
        #   "id": "chatcmpl-123",
        #   "object": "chat.completion",
        #   "created": 1677652288,
        #   "model": "gpt-4.1-mini",
        #   "choices": [
        #     {
        #       "index": 0,
        #       "message": {
        #         "role": "assistant",
        #         "content": "{\"sentiment\": \"positive\", \"rating\": 4}"
        #       },
        #       "finish_reason": "stop"
        #     }
        #   ],
        #   "usage": {
        #     "prompt_tokens": 50,
        #     "completion_tokens": 10,
        #     "total_tokens": 60
        #   }
        # }

        # Parse the JSON response from the LLM
        import json
        result = json.loads(response.choices[0].message.content)
        return SentimentResponse(sentiment=result["sentiment"], rating=result["rating"])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API error: {str(e)}")
    
##################################################################Q-3#####################################################################

# =====================================================================
# REQUEST AND RESPONSE MODELS FOR CODE INTERPRETER
# =====================================================================

class CodeRequest(BaseModel):
    """
    Request model for code interpreter endpoint.
    
    Attributes:
        code (str): Python code string to execute. Can be single or multi-line.
                   Should be valid Python syntax.
    
    Example:
        {"code": "x = 5\\nprint(x * 2)"}
    """
    code: str


class ErrorAnalysis(BaseModel):
    """
    Response model for AI error analysis.
    
    Attributes:
        error_lines (List[int]): List of line numbers where errors were detected.
                                Empty list if no errors found.
    
    Example:
        {"error_lines": [3, 5]} or {"error_lines": []}
    """
    error_lines: List[int]


# =====================================================================
# TOOL FUNCTION: PYTHON CODE EXECUTION
# =====================================================================

def execute_python_code(code: str) -> dict:
    """
    Execute Python code safely and capture output or errors.
    
    This function:
    - Captures stdout to extract print statements
    - Handles exceptions gracefully
    - Returns execution status and output/traceback
    
    Args:
        code (str): Python code to execute. Can contain multiple statements.
    
    Returns:
        dict: Result dictionary with two keys:
            - "success" (bool): True if code executed without errors, False otherwise
            - "output" (str): Standard output if successful, or full traceback if error
    
    Example:
        >>> result = execute_python_code("print('Hello')")
        >>> result
        {'success': True, 'output': 'Hello\\n'}
        
        >>> result = execute_python_code("x = 1/0")
        >>> result['success']  # False
        >>> print(result['output'])  # Traceback...
    
    Note:
        - Uses exec() for code execution (not eval)
        - Captures both stdout and stderr via traceback
        - Always restores original stdout in finally block
    """
    # Save original stdout before redirecting
    old_stdout = sys.stdout
    # Redirect stdout to capture print statements
    sys.stdout = StringIO()

    try:
        # Execute the user's code
        exec(code)
        # Get all captured output
        output = sys.stdout.getvalue()
        # Return success status with output
        return {"success": True, "output": output}

    except Exception:
        # If error occurs, capture full traceback
        output = traceback.format_exc()
        # Return failure status with traceback
        return {"success": False, "output": output}

    finally:
        # Always restore original stdout
        sys.stdout = old_stdout


# =====================================================================
# AI ERROR ANALYSIS FUNCTION
# =====================================================================

def analyze_error_with_ai(code: str, tb: str) -> List[int]:
    """
    Use OpenAI GPT to analyze Python code and identify error line numbers.
    
    When code execution fails, this function sends the code and traceback to
    the LLM to intelligently identify which lines caused the error. Useful for
    syntax errors, runtime errors, and logical issues.
    
    Args:
        code (str): The original Python code that failed to execute.
        tb (str): Full traceback string from the exception (from traceback.format_exc()).
    
    Returns:
        List[int]: List of line numbers where errors were detected.
                   Returns empty list if AI cannot identify specific lines.
    
    Example:
        >>> code = "x = 10\\ny = 0\\nresult = x / y"
        >>> tb = "Traceback (most recent call last):\\n  File '', line 3, in <module>\\nZeroDivisionError: division by zero"
        >>> error_lines = analyze_error_with_ai(code, tb)
        >>> error_lines  # [3]
    
    LLM Response Format:
        Expected response from OpenAI API:
        {
            "error_lines": [line1, line2, ...]
        }
        Example: {"error_lines": [3]}
    
    Note:
        - Uses structured JSON schema to ensure consistent output format
        - Model: gpt-4o-mini (compatible with aipipe.org)
        - Validates response using Pydantic ErrorAnalysis model
    """
    # Create prompt for AI to analyze the code and traceback
    prompt = f"""
Analyze the Python code and traceback.
Return the exact line numbers where error occurred.

CODE:
{code}

TRACEBACK:
{tb}
"""

    # Call OpenAI API with structured JSON output
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # aipipe compatible model
        messages=[{"role": "user", "content": prompt}],
        # Enforce strict JSON schema for consistent response
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "error_schema",
                "schema": {
                    "type": "object",
                    "properties": {
                        "error_lines": {
                            "type": "array",
                            "items": {"type": "integer"}
                        }
                    },
                    "required": ["error_lines"]
                }
            }
        }
    )

     # Full example of the 'response' object:
        # {
        #   "id": "chatcmpl-123",
        #   "object": "chat.completion",
        #   "created": 1677652288,
        #   "model": "gpt-4.1-mini",
        #   "choices": [
        #     {
        #       "index": 0,
        #       "message": {
        #         "role": "assistant",
        #         "content": "{\"error_lines\": [3]}"
        #       },
        #       "finish_reason": "stop"
        #     }
        #   ],
        #   "usage": {
        #     "prompt_tokens": 50,
        #     "completion_tokens": 10,
        #     "total_tokens": 60
        #   }
        # }

    # Parse and validate the JSON response using Pydantic model
    result = ErrorAnalysis.model_validate_json(
        response.choices[0].message.content
    )
    # Return the error line numbers
    return result.error_lines


# =====================================================================
# MAIN ENDPOINT: CODE INTERPRETER
# =====================================================================

@app.post("/code-interpreter")
def run_code(req: CodeRequest):
    """
    Execute Python code and analyze errors using AI if execution fails.
    
    This is the main endpoint that orchestrates the code execution flow:
    1. Receives Python code from user
    2. Attempts to execute the code
    3. If successful: returns output
    4. If error: uses AI to analyze and identify error line numbers
    
    Args:
        req (CodeRequest): Request object containing Python code to execute.
                          Example: {"code": "print(10/0)"}
    
    Returns:
        dict: Response with two keys:
            - "error" (List[int]): Empty list if no errors, otherwise line numbers with errors
            - "result" (str): Output of code execution or full traceback if error
    
    Response Examples:
        Success case:
        {
            "error": [],
            "result": "15\\n"
        }
        
        Error case:
        {
            "error": [3],
            "result": "Traceback (most recent call last):\\n  File '', line 3, in <module>\\nZeroDivisionError: division by zero"
        }
    
    Flow Diagram:
        Input Code
            ↓
        execute_python_code()
            ↓
        Success? → Yes → Return {error: [], result: output}
            ↓
            No
            ↓
        analyze_error_with_ai()
            ↓
        Return {error: [lines], result: traceback}
    """
    # Step 1: Execute the provided Python code
    execution = execute_python_code(req.code)

    # Step 2: Check if execution was successful
    if execution["success"]:
        # Success case: return empty error list and the output
        return {
            "error": [],
            "result": execution["output"]
        }

    # Step 3: If error occurred, use AI to analyze error locations
    error_lines = analyze_error_with_ai(req.code, execution["output"])

    # Step 4: Return error case with identified line numbers and traceback
    return {
        "error": error_lines,
        "result": execution["output"]
    }


#####################################################################Q-12######################################################################
import re
import json


"""
Simple FastAPI query parser

This module provides a single endpoint (/execute) that receives a natural
language query string and attempts to parse it into a structured command
name with JSON arguments. Regular expressions are used to identify well-
formed templates in the incoming text. If no pattern matches, an error
message is returned.

The endpoint is intentionally lightweight and demonstrates how regex
patterns can be used as a quick way to dispatch commands from free-form
text.

Regex patterns in this file use the following conventions:
  - `\s` matches whitespace (space, tab, newline)
  - `\d` matches a digit (0-9)
  - `+` quantifier means "one or more" of the preceding token
  - `*` quantifier means "zero or more"
  - `()` capturing groups return matched substrings via `group()`
  - `[\w\s]` character class allows letters, digits, underscore, and spaces

Example pattern: r"ticket\s+(\d+)"
   looks for the word "ticket" followed by one or more spaces and then
   captures one or more digits as the ticket ID.
"""


@app.get("/execute")
def execute(q: str):
    """
    Process the incoming text query and return a command payload.

    Parameters:
        q (str): raw user query, e.g. "Schedule a meeting on 2023-10-01 at 09:00 in conference room A"

    Returns:
        dict: either a command with name/arguments or an error description.
    """
    # Normalize to lowercase so patterns are case-insensitive
    query = q.lower()
    # 1️⃣ Ticket Status
    #What is the status of ticket 83742?
    # regex explanation:
    #   r"ticket\s+(\d+)" -> match the word "ticket" followed by at least
    #   one whitespace (\s+) and capture a sequence of digits (\d+).
    #   captured digits correspond to the ticket ID.
    ticket_match = re.search(r"ticket\s+(\d+)", query)
    if ticket_match:
        ticket_id = int(ticket_match.group(1)) # first matched group ie the digits after "ticket"
        return {
            "name": "get_ticket_status",
            "arguments": json.dumps({
                "ticket_id": ticket_id
            })
        }
    
    # 2️⃣ Schedule Meeting
    #Schedule a meeting on 2025-02-15 at 14:00 in Room A.
    # Pattern breakdown:
    #   ([\d-]+)  -> capture a date string consisting of digits and hyphens
    #   ([\d:]+)  -> capture a time string with digits and colons
    #   ([\w\s]+) -> capture the meeting room; allow word chars and spaces
    meeting_match = re.search(
        r"schedule a meeting on ([\d-]+) at ([\d:]+) in ([\w\s]+)",
        query
    )
    if meeting_match:
        date, time, room = meeting_match.groups()
        return {
            "name": "schedule_meeting",
            "arguments": json.dumps({
                "date": date,
                "time": time,
                "meeting_room": room.strip().title() 
                # remove extra spaces and capitalize each word in room name,ie first letter capital
            })
        }

    # 3️⃣ Expense Balance
    #Show my expense balance for employee 10056.
    # Look for "employee <number>"; this will match any instance of the word
    # followed by digits. Only treat as expense query if "expense balance"
    # phrase is also present.
    expense_match = re.search(r"employee\s+(\d+)", query)
    if "expense balance" in query and expense_match:
        employee_id = int(expense_match.group(1))
        return {
            "name": "get_expense_balance",
            "arguments": json.dumps({
                "employee_id": employee_id
            })
        }


    # 4️⃣ Performance Bonus
    #Calculate performance bonus for employee 10056 for 2025
    # Pattern explanation:
    #   "employee\s+(\d+)\s+for\s+(\d{4})"
    #   - capture employee number (digits)
    #   - then the literal word "for" and a four-digit year (\d{4})
    # We only process if "performance bonus" phrase appears in query.
    bonus_match = re.search(r"employee\s+(\d+)\s+for\s+(\d{4})", query)
    if "performance bonus" in query and bonus_match:
        emp_id, year = bonus_match.groups()
        return {
            "name": "calculate_performance_bonus",
            "arguments": json.dumps({
                "employee_id": int(emp_id),
                "current_year": int(year)
            })
        }


    # 5️⃣ Report Office Issue
    #Report office issue 45321 for the Facilities department
    # Pattern:
    #   "issue <number> for the <department> department"
    #   - captures issue code digits and department name (letters/spaces).
    issue_match = re.search(
        r"issue\s+(\d+)\s+for the ([\w\s]+) department",
        query
    )
    if issue_match:
        issue_code, dept = issue_match.groups()
        return {
            "name": "report_office_issue",
            "arguments": json.dumps({
                "issue_code": int(issue_code),
                "department": dept.strip().title() # remove whitespace and capitalize
            })
        }

    # ❌ If query doesn't match any template
    return {
        "error": "Query not recognized"
    }