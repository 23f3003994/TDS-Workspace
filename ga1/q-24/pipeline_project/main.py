#read README.md for running info
#i ran this just on local host and didnt use ngrok
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
from datetime import datetime, timezone
from openai import OpenAI
import os


app = FastAPI()



# Initialize OpenAI client (set your API key in environment)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""),base_url=os.environ.get("OPENAI_BASE_URL", "https://aipipe.org/openai/v1"))


# Middleware handles most requests automatically
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all websites
    allow_methods=["*"],  # allow all HTTP methods
    allow_headers=["*"],  # allow all headers
    expose_headers=["*"] # expose all headers ie allow client side JS to access them
)


# Input schema
class PipelineRequest(BaseModel):
    email: str
    source: str



# ===== WHY REQUESTS LIBRARY? =====
        # The 'requests' library is used because:
        # 1. Built for HTTP/HTTPS communication - makes API calls simple and readable
        # 2. Handles headers, parameters, authentication automatically
        # 3. Provides timeout support to prevent hanging on slow networks
        # 4. Automatic redirect handling (follows HTTP redirects)
        # 5. Built-in error checking with raise_for_status()
        # 6. Much simpler than using urllib (Python's built-in library)
        #
        # Alternative: Python's built-in 'urllib' library (more complex, less user-friendly)
        # We use: import requests (pip install requests)

        # ===== WHY RESPONSE.JSON()? =====
        # response.json() is used because:
        # 1. The API returns data as JSON text (raw string in HTTP body)
        # 2. response.json() automatically DESERIALIZES the JSON string into Python objects
        # 3. Converts JSON to native Python dict/list (easier to work with)
        # 4. Handles encoding/decoding automatically (UTF-8, etc.)
        # 5. Raises error if JSON is invalid (data validation)
        #
        # Example:
        #   Raw response text: '[{"userId": 1, "id": 1, "body": "..."}]'  (JSON string)
        #   response.json(): [{"userId": 1, "id": 1, "body": "..."}]  (Python list of dicts)
        #
        # Alternative approaches (NOT recommended):
        #   json.loads(response.text)  - requires manual string parsing
        #   eval(response.text)        - unsafe, security risk
        #
# -------- Stage 1: Fetch Posts --------
def fetch_posts():
    """
    Fetch the first 3 posts from JSONPlaceholder API
    
    Makes an HTTP GET request to the JSONPlaceholder API endpoint and retrieves
    the initial 3 posts to be processed by the pipeline.
    
    Returns:
        tuple: (posts_list, error_list)
            - posts_list: List of post dictionaries with userId, id, title, and body
            - error_list: Empty list if successful, or list with error message if failed
    
    Raises:
        Returns empty posts list and error message on network/API errors
    """
    url = "https://jsonplaceholder.typicode.com/posts"
    try:
        
        
        # Make HTTP GET request with 5 second timeout
        # The timeout=5 parameter specifies the maximum number of seconds to wait for the server to respond.
        # If the server doesn't respond within 5 seconds, the request will be canceled and raise an exception, 
        # preventing the code from hanging indefinitely on a slow or unresponsive API.
        response = requests.get(url, timeout=5)
        print(response)
        # Raise exception if HTTP status indicates an error
        response.raise_for_status()
        

        # Extract JSON data and get first 3 posts
        #  The API returns data as JSON text (raw string in HTTP body)
        #  response.json() automatically DESERIALIZES the JSON string into Python objects
        posts = response.json()[:3]
        # Return posts and empty errors list
        """ posts from that url looks like this
        [
            {
                "userId": 1,
                "id": 1,
                "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit",
                "body": "quia et suscipit\nsuscipit recusandae consequuntur expedita et cum\nreprehenderit molestiae ut ut quas totam\nnostrum rerum est autem sunt rem eveniet architecto"
            },
            {
                "userId": 1,
                "id": 2,
                "title": "qui est esse",
                "body": "est rerum tempore vitae\nsequi sint nihil reprehenderit dolor beatae ea dolores neque\nfugiat blanditiis voluptate porro vel nihil molestiae ut reiciendis\nqui aperiam non debitis possimus qui neque nisi nulla"
            },]

        """
        return posts, []
    except Exception as e:
        return [], [f"API Fetch Error: {str(e)}"]


# -------- Stage 2: AI Analysis --------
def analyze_text(text):
    """
    Analyze text using OpenAI GPT-4o-mini model and classify sentiment
    
    Sends the text to OpenAI's chat completion API for analysis and extracts
    sentiment classification (positive, negative, or neutral) by parsing the response.
    
    Args:
        text (str): The text content to analyze (typically the body of a post)
    
    Returns:
        tuple: (analysis, sentiment, error_list)
            - analysis (str): AI-generated analysis of the text (2 sentences)
            - sentiment (str): Classified sentiment - one of ["optimistic", "pessimistic", "balanced"]
            - error_list: Empty list if successful, or list with error message if failed
    
    Returns (None, None, [error_msg]) on API failures
    """
    try:
        prompt = f"""
        Analyze this text in 2 short sentences and classify sentiment strictly as one of:
        optimistic, pessimistic, balanced.
        {text}
        """

        # ===== CHAT COMPLETION REQUEST =====
        # Chat Completion: OpenAI API endpoint that takes conversation messages and returns AI-generated responses
        # messages parameter: Array of message objects representing the conversation history
        #   - "role": "user" = message from the user/human (not from the AI)
        #   - "content": the actual text/question sent to the AI
        # model="gpt-4o-mini": Specifies which AI model to use for analysis
        #
        # Example request:
        #   messages=[
        #     {"role": "user", "content": "Analyze this text..."},
        #     {"role": "assistant", "content": "Previous AI response..."},  # optional for context
        #   ]
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        # ===== RESPONSE STRUCTURE =====
        # The response is a ChatCompletion object that looks like:
        # {
        #   "id": "chatcmpl-123abc",
        #   "object": "chat.completion",
        #   "created": 1677649420,
        #   "model": "gpt-4o-mini",
        #   "choices": [
        #     {
        #       "index": 0,
        #       "message": {
        #         "role": "assistant",
        #         "content": "This text expresses optimistic emotions. The writing shows optimism and enthusiasm."
        #       },
        #       "finish_reason": "stop"
        #     }
        #   ],
        #   "usage": {
        #     "prompt_tokens": 50,
        #     "completion_tokens": 20,
        #     "total_tokens": 70
        #   }
        # }
        #
        # Extract the AI's response text:
        # response.choices[0] = Get the first (and main) completion choice
        # .message = The message object containing the AI's response
        # .content = The actual text generated by the AI
        # .strip() = Remove leading/trailing whitespace (newlines, spaces)
        analysis = response.choices[0].message.content.strip()

        # ===== SENTIMENT DETECTION =====
        # Parse the AI's analysis text to determine overall sentiment
        # Simple approach: Search for keyword indicators in the response (case-insensitive)
        # Examples of what analysis might contain:
        #   "This is a optimistic response showing enthusiasm..." → sentiment = "optimistic"
        #   "The text appears pessimistic with complaints..." → sentiment ="pessimistic"
        #   "This is balanced and factual information..." → sentiment = "balanced"

        # Strict sentiment extraction
        if "optimistic" in analysis.lower():
            sentiment = "optimistic"
        elif "pessimistic" in analysis.lower():
            sentiment = "pessimistic"
        else:
            sentiment = "balanced"

        return analysis, sentiment, []

    except Exception as e:
        return None, None, [f"AI Analysis Error: {str(e)}"]


# -------- Stage 3: Storage --------
def store_result(item):
    """
    Store a processed item (analysis result) to a JSON file database
    
    Args:
        item (dict): Dictionary containing original text, analysis, sentiment, timestamp, and source
    
    Returns:
        tuple: (success_boolean, error_list)
            - True, [] if save successful
            - False, [error_message] if save failed
    """
    # Outer try-except: Catch any file operations or JSON processing errors
    try:
        # Inner try-except: Attempt to read existing data from file
        try:
            # Open db.json file in read mode
            # json.load() deserializes JSON file content into a Python list/dict
            with open("db.json", "r") as f:
                data = json.load(f) #DATA IS A DICT NOW
        except:
            # If file doesn't exist or has invalid JSON, start with empty list
            # This handles first-time storage when db.json doesn't exist yet
            data = []

        # Append the new item (analysis result) to the list
        # item structure: {"original": text, "analysis": analysis, "sentiment": sentiment, "timestamp": "...", "source": source}
        data.append(item)

        # Write updated data back to db.json file in write mode
        # json.dump() serializes the Python list into JSON format
        # indent=2 makes JSON human-readable with 2-space indentation
        # Example output in db.json:
        # [
        #   {
        #     "original": "text content",
        #     "analysis": "AI analysis result",
        #     "sentiment": "positive",
        #     "timestamp": "2026-02-13T14:30:45.123456Z",
        #     "source": "source_name"
        #   }
        # ]
        with open("db.json", "w") as f:
            json.dump(data, f, indent=2)

        # Storage successful - return True and empty error list
        return True, []
    # Catch any exceptions from file operations (permissions, disk space, etc.)
    except Exception as e:
        # Return failure status and error message for logging
        return False, [f"Storage Error: {str(e)}"]


# -------- Stage 4: Notification --------
def send_notification(email):
    """
    Send a notification to the user via email (currently mocked)
    
    Currently prints a notification message to console as a mock implementation.
    In a production system, this would send an actual email notification.
    
    Args:
        email (str): The email address to send the notification to
    
    Returns:
        tuple: (success_boolean, error_list)
            - True, [] if notification sent successfully
            - False, [error_message] if notification failed
    """
    try:
        # mock notification (console log)
        print(f"Notification sent to: {email}")
        return True, []
    except Exception as e:
        return False, [f"Notification Error: {str(e)}"]


# -------- Main Pipeline Endpoint --------
@app.post("/pipeline")
def run_pipeline(request: PipelineRequest):
    """
    Main pipeline endpoint - orchestrates all 4 stages: fetch, analyze, store, notify
    
    This is the main FastAPI POST endpoint that executes the complete data processing
    pipeline for each request. It:
    1. Fetches posts from JSONPlaceholder API
    2. Analyzes each post using OpenAI API
    3. Stores results in db.json file
    4. Sends notification email to user
    
    Args:
        request (PipelineRequest): Request object containing:
            - email (str): User's email for notification
            - source (str): Source identifier for the request
    
    Returns:
        dict: JSON response containing:
            - items (list): List of processed results with analysis and sentiment
            - notificationSent (bool): Whether notification was successfully sent
            - processedAt (str): ISO 8601 timestamp when pipeline completed
            - errors (list): List of all errors encountered during processing
    """
    # email and source provided
    results = []
    errors = []

    # STEP 1 - Fetch data
    posts, fetch_errors = fetch_posts()
    errors.extend(fetch_errors) # extend will adds all items from one list into another list.
    #errors = ["error1"]
    # fetch_errors = ["error2", "error3"]
    # errors.extend(fetch_errors)
    # # Result: errors = ["error1", "error2", "error3"]

    # STEP 2 - Process each post (EXTRACT THEME -> SEND TO AI TO ANALYZE -> STORE RESULT IN JSON FILE)
    for post in posts:
        try:
            text = post.get("body", "")#extract theme of the post 

            analysis, sentiment, ai_errors = analyze_text(text)#send it to ai to analyze
            errors.extend(ai_errors)

            if analysis is None:
                continue  # skip failed item

            item = {
                "original": text,
                "analysis": analysis,
                "sentiment": sentiment,
                # Generate current UTC timestamp in ISO 8601 format with Z suffix
                # datetime.now(timezone.utc) = Get current date/time in UTC (Coordinated Universal Time)
                # .isoformat() = Convert to string format: "2026-02-13T14:30:45.123456+00:00"
                # + "Z" = Replace timezone offset with Z to indicate UTC (ISO 8601 standard)
                # Final result example: "2026-02-13T14:30:45.123456Z"
                "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                "source": request.source
            }

            stored, store_errors = store_result(item) # store this result in json file, srored is a boolean
            errors.extend(store_errors)

            results.append({
                "original": text,
                "analysis": analysis,
                "sentiment": sentiment,
                "stored": stored,
                "timestamp": item["timestamp"]
            })

        except Exception as e:
            errors.append(f"Processing Error: {str(e)}")
            continue

    # STEP3- Send notification
    notified, notify_errors = send_notification(request.email)
    errors.extend(notify_errors)
    
    # you don't need to use json.dumps().
    # FastAPI automatically converts dictionaries to JSON before sending them to the client.
    # FastAPI automatically:

    #     Serializes the dict to JSON using json.dumps() internally
    #     Sets the Content-Type: application/json header
    #     Sends the JSON response to the client
    return {
        "items": results,
        "notificationSent": notified,
        # Generate current UTC timestamp in ISO 8601 format with Z suffix
        # datetime.now(timezone.utc) = Get current date/time in UTC (Coordinated Universal Time)
        # .isoformat() = Convert to string format: "2026-02-13T14:30:45.123456+00:00"
        # + "Z" = Replace timezone offset with Z to indicate UTC (ISO 8601 standard)
        # Final result example: "2026-02-13T14:30:45.123456Z"
        "processedAt": datetime.now(timezone.utc).isoformat() + "Z",
        "errors": errors
    }

import uvicorn
if __name__ == "__main__":
    print("Initializing with FastAPI...")
    print("API Docs: http://localhost:8002/docs")
    uvicorn.run(app,port=8002)

