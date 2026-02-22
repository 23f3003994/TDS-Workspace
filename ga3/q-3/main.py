import os
import sys
import traceback
from io import StringIO
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

# Create OpenAI client (aipipe compatible)
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