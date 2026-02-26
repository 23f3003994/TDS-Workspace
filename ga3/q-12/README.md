#  Function Calling

## project architecture
```
Employee types query (Web UI)
        ↓
HTTP GET → /execute?q=...
        ↓
FastAPI receives query
        ↓
Regex-based template matching
        ↓
Identify correct function + extract parameters
        ↓
Return JSON:
{name, arguments}
```

> This mimicks OpenAI’s function selection behavior, but using rule-based logic instead of AI.
> We are building the routing logic that OpenAI would normally do.

**Compare Both Approaches Side-by-Side**

🔹 **Approach A (Real GPT Function Calling)**

```
User Query
   ↓
Send to OpenAI with function schemas
   ↓
GPT decides function + arguments
   ↓
Return JSON
```


🔹**Approach B (This Assignment)**

```
User Query
   ↓
FastAPI regex matching
   ↓
YOU decide function + arguments
   ↓
Return same JSON format

We are simulating what GPT would have done.
```
---
## local testing

1. `pip install requirements.txt`
2. In wsl - `uvicorn main:app --reload` (default 8000)  or `uvicorn main:app --reload --port 8001`
   Your Final API Endpoint: `http://127.0.0.1:8000/execute`
3. send a curl request from another terminal

**Example Test URLs**

Ticket Status
` http://127.0.0.1:8000/execute?q=What is the status of ticket 83742? `

Response:

```json
{
  "name": "get_ticket_status",
  "arguments": "{\"ticket_id\": 83742}"
}
```
Schedule Meeting
`http://127.0.0.1:8000/execute?q=Schedule a meeting on 2025-02-15 at 14:00 in Room A.`

Expense Balance
`http://127.0.0.1:8000/execute?q=Show my expense balance for employee 10056.`

Performance Bonus
`http://127.0.0.1:8000/execute?q=Calculate performance bonus for employee 10056 for 2025.`

Report Office Issue
`http://127.0.0.1:8000/execute?q=Report office issue 45321 for the Facilities department.`

---