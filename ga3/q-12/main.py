
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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import re
import json


# Initialize FastAPI application
app = FastAPI()


# Configure CORS middleware to allow cross-origin requests from all origins
# This is necessary for browser-based API calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"]  # Expose all headers to clients
)

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