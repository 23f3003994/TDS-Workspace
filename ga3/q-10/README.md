# Gemini Multi-Page PDF Analysis

### Project Architecture
```
[Local PDF File]
      │
      ▼
[GenAI Client: client.files.upload()]
      │  (poll until ACTIVE)
      ▼
[Gemini Files API]
      │  (analyzes PDF pages, text, tables)
      ▼
[Gemini LLM: generate_content]
      │  (prompted to extract Jan 10 -amount, convert doolars,dollar,USD→Rs)
      ▼
[Structured JSON Output] ---> Summed in Python → Total Expense

```
```bash
pip install google-genai
export GEMINI_API_KEY="your_key_here"
```
> Used gemini api key from google ai studio( free tier) and not ai pipe token

#### What You’ll Finally Do

**Run:**

`python3 main.py expenses_23f3003994.pdf "10Jan"`

**Output:**

Total spent on 10Jan: Rs 797777  (this is the correct amount in my case)

That number is your answer (±15% accepted).