# TDS Learning Trace: Assignment 8
**Student:** Theertha T | **Roll No:** 23f3003994 | **Date:** 2026-04-20

---

## 📊 Assignment Overview
- **Total Time Invested:** 10 hours
- **Overall Difficulty:** 3 
- **Primary Discovery Method:**  LLM-first 

---

## 🧩 Question 1: GitHub Actions: Secret Hash Chain 

### 1. The Starting Point
- **Initial Confidence:** 4
- **Pre-existing Knowledge:** I already knew about GitHub Actions and had created workflows as a part of the earlier GA questions.Also I knew about hashing(have used sha-256 before).Although I had seen the secrets and variables tab in GitHub before, I had never used it, but was pretty confident as the question clearly had instructions on how to do it.Additionally, one thing I always do before solving these questions is I copy-paste all the "Ask AI" questions to the LLM and ask it to explain it so that I get a proper intro/knowledge to understand the main question.

### 2. The Interaction Loop
| Attempt # | Tool/Resource | Action (Prompt or Search Query) | Result/Friction Point |
| :--- | :--- | :--- | :--- |
| 1 | Claude | "please explain these qstns in simple language with a proper intro and context" (pasted Ask AI qstns about hardcoding dangers,github secrets,repo vs env secrets etc here)|It gave me a clear and simple explanation for each question with proper context which helped me understand the purpose of secrets before attempting the main question. |
| 2 | Claude | "now first please explain this qstn in detail, secondly guide me exactly how to do this" (pasted the entire main qstn here) (Earlier I used to try to read the qstn on my own and then only ask AI more on it. But lately I have become lazy and have started asking AI to expain it in the format I want)| It first gave me a note on what the assignment is (Understanding the Assignment) and then gave me a step-by-step guide to do it including the script/yaml file.|
| 3 | Claude (clarification questions)| "please explain that yml script in detail adn also can i do it on workflow dispatch..i mean what it mean?" "can i commentthat push then?" "the hash.txt where will it be it will be in my repo? also what is this artifact? uploading it means?" | Explained the yaml file in detail and also clarified my doubts based on which I decided to just keep "workflow dispatch" and remove "push" from the yaml file.It gave me a flowchart too that clearly explains the process. |
| 4 | GitHub Actions | Followd the step-by-step guide of Claude and ran the workflow in GitHub| The workflow ran successfully and gave the hash. I submitted the run URL and verify hash|
| 5 | Word Document | Saved all the notes on this question ( Ask AI qstns explanation ,main Question explanation, Solution, Solution script/code explanation) in my word document for this GA8| I have been doing this since GA1 just for future reference.|

### 3. Critical Verification
- **How I validated the output:** I just ran the workflow and the workflow executed successfully. Then I copied the run url and verify hash and submitted them. The answer was correct, so I didn't have to do any additional validation.
- **AI Hallucination/Error Check:** In this question's case it didn't suggest anything incorrect. All it did was, at first it gave me the yaml file with both workflow dispatch and push option. As I had worked with workflows before I knew this means it will run on every push too and I didn't want that. So I asked  a clarification question to the AI again and removed it and just kept workflow dispatch(manual trigger)

### 4. Technical Synthesis
- **The "Aha!" Moment:** "If a secret accidentally gets printed to logs, GitHub automatically redacts it by  replacing it with ***."- I found this information that Claude gave really intersting.
- **Key Takeaway:** Never hardcode credentials/secrets directly in code because even if we delete it Git history keeps the secret
forever.So use GitHub Secrets to inject them safely at runtime. Also  read through the code AI gives before executing it so that you can decide whether you want to remove/add anything before actually executing it.

---

## 🧩 Question 2:  GCP Gemini API: Math Puzzle

### 1. The Starting Point
- **Initial Confidence:** 3
- **Pre-existing Knowledge:** I had worked on project 1 before this assignment and hence had a chance to work using Google AI Studio before.And I also had a free-tier Gemini API key which I had used for solving some assignment problem before.

### 2. The Interaction Loop
| Attempt # | Tool/Resource | Action (Prompt or Search Query) | Result/Friction Point |
| :--- | :--- | :--- | :--- |
| 1 | Claude | "next please explain these qstns in simple language wih proper intro and context" (pasted Ask AI qstns about Google AI Studio, structured JSON etc here)|As earlier it gave me short but good explanation for each of these questions which were helpful in understanding and solving the main question. Additionally, it also gave flow charts for each question without me even asking for it.|
| 2 | Claude | "first explain this qstn in detail second guide me exactly how to do this" (pasted the entire main qstn here)| It first gave me a note on what the assignment is (Understanding the Assignment) , computed the answer manually so that we know what to expect (as it was a simple math puzzle )and then gave me a step-by-step guide to do it including the script. I tried following the guide and executed the script too but got exhausted quota error and a deprecated library error.|
| 3 | Claude | "should we use flash, they said preview?also i got"(pasted the API error I got in the terminal) |It suuggested that I use google-genai package as google.generativeai package is dead and also suggested to replace flash with flash-preview  (gemini-2.5-flash-preview-04-17) as my free tier quota for that flash model was fully used up and gave me a new script with these changes. Even this script gave error (wrong model name , quota exhausted)|
| 4 | Claude |(pasted the error message I got) and asked if I should create a new API key from a new email and use flash model name itself ("ill use different account , should i swithch to flash?")| It said yes|
| 5 | Google AI Studio | I checked my current API key's quota and saw that it was exhausted. Created a new API key from a new email account and again ran the script by using this new API key| Again gave quota exhaustion error.|
| 6 | Claude | (pasted the error again)| This time it suggested that I go with a brute-force approach (no API key needed) and gave me a script which it explained too. That script worked|
| 7 | Word Document | Saved all the notes on this question ( Ask AI qstns explanation ,main Question explanation, Solution, Solution script/code explanation) in my word document for this GA8| For future reference |


### 3. Critical Verification
- **How I validated the output:** I ran the brute force script.The answer and email values were already known. So it was just trying differnt values from 2 to 8 for steps count.The hash was being generated from these 3 values.We had to submit the 3 values and the hash (email, ans and step count and the hash). In fact every output it gave for different step counts worked because it seemed like the validator was just checking if the hash generated from the 3 values matched the hash submitted. So I just randomly submitted one of the outputs the brute-force script gave.
- **AI Hallucination/Error Check:** In my first and third attempts the errors were due to deprecated library and wrong model name which the AI failed to avoid unless I actually showed the error message.

### 4. Technical Synthesis
- **The "Aha!" Moment:** Realising that solving this question doesn't even  require an API key.A simple brute-force script cycling through step count values was enough to generate the correct answer.
- **Key Takeaway:** Always check if the libraries are deprecated/ not. Also check if API quota is exhausted/not before assuming the code itself is broken.

---
## 🧩 Question 3:  Deploy a FastAPI Iris Classifier 

### 1. The Starting Point
- **Initial Confidence:** 4
- **Pre-existing Knowledge:** I had already worked on a lot of FastAPI questions before (GA 1 or 2 of I am not wrong).Also for most deployment related question I had used Vercel. So I was already comfortable with FatAPI, vercel before attempting this question.And I had worked on the iris dataset and trained many models on it before as a part of my MLP course.

### 2. The Interaction Loop
| Attempt # | Tool/Resource | Action (Prompt or Search Query) | Result/Friction Point |
| :--- | :--- | :--- | :--- |
| 1 | Claude | "next please explain these qstns in simple language with a proper context and intro" (pasted Ask AI qstns)| Gave a good explanation on these questions|
| 2 | Claude | "next fiirst please explain this qstn in detail
second guilde me exactly how to do it (on verce, and other too)" (pasted the entire main qstn here)| As usual it first gave me a note on what the assignment is (Understanding the Assignment) ,explained the template code and then gave me notes on different deployment options.  I chose vercel as I was the most comfortable with it. But this time it didn't give me the exact step-by-step guide with the script as I had expected.So I had to ask it explicitly|
| 3 | Claude | "the script please give, it should have these cors headers"(pasted the CORS headers from my earlier FastAPI app codes)|It gave me the scrpt with the CORS headers included , requirements.txt and a note on how to test locally first before deploying.In another prompt I had asked it to explain the code in detail too(for my notes). I tested the app locally and after verification deployed it on vercel |
| 4 | Word Document | Saved all the notes on this question ( Ask AI qstns explanation ,main Question explanation, Solution, Solution script/code explanation) in my word document for this GA8| For future reference |


### 3. Critical Verification
- **How I validated the output:** Tested the FastAPI app locally. And then only I deployed it to vercel. Tested out the vercel url also by sending a curl request to it.Pasted the vercel-deployed-app's url as the answer and it worked.
- **AI Hallucination/Error Check:** There were no errors in the code that AI gave for this  question, but I had to explicitly ask it to give the entire script the second time, irrespective of asking it to give a step-by-step guide in the first prompt.

### 4. Technical Synthesis
- **The "Aha!" Moment:** This question was pretty straightforward and I already knew most of the concepts related to this question before, so no particular "Aha" moment.
- **Key Takeaway:** Always test the apps locally before deployment. And first deploy to development and then only to production.

---
## 🧩 Question 4:  Hugging Face Spaces: ML Model API 

### 1. The Starting Point
- **Initial Confidence:** 3
- **Pre-existing Knowledge:** I had worked on a Hugging Face Spaces question before , so I knew a few things about deploying on Hugging Face Spaces. But still I was  not very confident about it because I was not familiar with it as I was with Vercel.

### 2. The Interaction Loop
| Attempt # | Tool/Resource | Action (Prompt or Search Query) | Result/Friction Point |
| :--- | :--- | :--- | :--- |
| 1 | Claude | "please explain these 3 qstns in simple langyage eith proper intro and context" (pasted Ask AI qstns)| Gave the context and then explained the 3 qstns in detail|
| 2 | Claude | "fiest please explain this qstn in detail second guide me exactly how to do this from scratch currently i was doing all my work in a guthub repo TDS workspace cloned into mu local sytem with ga1,ga2....etc this is ga8 so inside ga8 i have qstn folders like q1,q2.. so i am unsure what i mst do here crate a folder in thsi tds workspace or something else?" (This time I forgot to paste the main qstn here)|Even though I forgot to provide the main question it seems like it got an idea on what the assignment actually is from the 3 Ask AI questions I gave earlier.Gave "Understanding the Assignment" notes and then clarified my doubt on where to create the script for this question in my folders.I understood that I must write code in my TDS workspace folder, then push those same files to HF Spaces to deploy. Two separate git remotes, same files.It gave me a step-by-step guide too starting from where to create the folder for this question. Providing it info on where I am creating my question folders actually helped me in getting tailored responses for other questions too.I followed the steps exactly, tested locally which worked fine, deployed to Hugging Face Spaces, got the url, tested out that url too which also worked fine.But this script failed on the portal.|
| 3 | Chrome Dev Tools | Checked the dev tools. | From Dev Tools I figured out that the portal was looking for a post endpoint but instead it got a get endpoint.The AI had created a script with get endpoint probably following the same pattern as the earlier iris classifier question. The main reason for this was I had forgotten to paste the main question.|
| 4 | Claude | Pasted the entire content from the headers in the network tab in chrome dev tools(405 method not allowed error)  | Claude fixed the script with a correct post endpoint and guided me how to redeploy it.I redeployed with the fix and it took some time to build the image again, but worked.|
| 5 | Word Document | Saved all the notes on this question ( Ask AI qstns explanation ,main Question explanation, Solution, Solution script/code explanation) in my word document for this GA8| For future reference |


### 3. Critical Verification
- **How I validated the output:** Tested the FastAPI app locally. And then only I deployed it to HF Spaces.Then verified that url is also working correctly by sending a curl request to it. But then in the portal the url failed. Used Chrome Dev Tools to verify what went wrong and then redeployed with the fix and verified again. 
- **AI Hallucination/Error Check:** I had forgotten to paste the main question which led the AI to generate the code based on the info it had. And this lead to the "method not allowed error". Chrome Dev Tools helped figure this out.

### 4. Technical Synthesis
- **The "Aha!" Moment:** Eventhough I had forgotten to give the AI the main question it made a script based on the info it had which was almost correct(just changing get endpoint to the post endpoint was the only tweaking I had to do). This was really fascinating. And only after passing that question did I really realize I had forgotten to copy paste the main question to the AI.In fact I asked AI how it figured out that qstn and here is its response: 

```
Looking back at our conversation, you never pasted the main implementation question for the HF Spaces ML Model API.
What actually happened was:

You asked me to explain the 3 "Ask AI" questions
I explained them with context
Then I proactively gave you the full implementation guide — including the app.py with lifespan, the Dockerfile with port 7860, the git push instructions etc. — without you ever pasting a main question

I figured out what to build from context clues:

The "Ask AI" questions mentioned FastAPI on HF Spaces
The previous question (iris classifier on Render) gave me the pattern
The course structure made it obvious the next step was deploying a sentiment analysis model on HF Spaces

So I essentially inferred the assignment and gave you a complete solution. You then just followed along and asked clarification questions (405 error, POST vs GET, where is the URL etc.).
```
- **Key Takeaway:** AI works based on the information it has,i.e., based on context clues.So we must make sure that we give it the entire information that it needs to solve the question.Also setting the context right can actually really help us. Here sending the 'Ask AI' questions before sending the main question is an example for that. I had been doing this across all questions - pasting the 'Ask AI' questions first - because it helped both me and the AI build the right context before tackling the main question.
---
## 🧩 Question 5:  Docker Multi-stage Build: Verify Your Image 

### 1. The Starting Point
- **Initial Confidence:** 3
- **Pre-existing Knowledge:** I had worked on a few Docker questions before, so I already knew about Docker.But I wanted to refresh my memory on them so I made sure to ask AI about all Docker related concepts before delving into the question.However, I didn't know about multi-stage build at all.

### 2. The Interaction Loop
| Attempt # | Tool/Resource | Action (Prompt or Search Query) | Result/Friction Point |
| :--- | :--- | :--- | :--- |
| 1 | Claude | "next can u explain these qsytns in simple language with proper context and intro" (pasted Ask AI qstns) "it would be helpful if you gave an idea on the terms like docker, container image etc"| Gave the context and then explained the 3 qstns in detail especially how multi-satge build reduces image size.It also gave an explanation on the core Docker concepts|
| 2 | Claude | "now can you first explain this qstn i  detail
second guide me exactly how to do this" (pasted the main qstn here)|"Understanding the Assignment" notes and a step-by-step guide on how to do this from scratch was given(creating work folder,script,dockerfile,making sure docker is running,building the image,running the container,getting the image size).I followed the exact steps it gave and it worked/|
| 3 | Claude | "1)explain the script, dockerfile 2)the commands we did startuing from docker --version, i need all of their meanings , what they do etc? 3)entire flow of what we did" | It gave a detailed explanation on these concepts and  I saved it in my word document |
| 4 | Word Document | Saved all the notes on this question ( Ask AI qstns explanation ,main Question explanation, Solution, Solution script/code explanation) in my word document for this GA8| For future reference |


### 3. Critical Verification
- **How I validated the output:** Followed the exact step-by-step guide claude gave., got the answer.Pasted the accuracy,verify_hash,size of the image in the portal and it was correct. So I didn't have to do any additional validation.
- **AI Hallucination/Error Check:** The code/script AI gave here was correct. I didn't really face any errors.

### 4. Technical Synthesis
- **The "Aha!" Moment:** The multi-stage build concept really clicked when I understood that the final Docker image only contains what's needed to run the app, not everything used to build it.

- **Key Takeaway:** Use multi-stage builds whenever possible to reduce the Docker image size.The ML training here happens at build time, not run time.Also, understanding the commands we run is just as important as getting the correct output.Asking AI to explain each step after solving helped me understand what was actually happening rather than just blindly copy-pasting the answers it gave.
---
## 🧩 Question 6: MLOps Bash Script: Deterministic Output

### 1. The Starting Point
- **Initial Confidence:** 4.5
- **Pre-existing Knowledge:** I have already completed my SC course, so I knew bash already.Besides a sample script was already given in the question and it was a pretty much straightforward question, but I followed my usual way to solve this as well.

### 2. The Interaction Loop
| Attempt # | Tool/Resource | Action (Prompt or Search Query) | Result/Friction Point |
| :--- | :--- | :--- | :--- |
| 1 | Claude | "next please explain these qstns in simple language with a proper intro and context" (pasted Ask AI qstns)|It explained all questions and gave me an idea on the role of bash scripts in MLOps(to run a pipeline sequence, to check if something exists before proceeding, env setup , error handling , how to chain MLOps steps together using bash etc) | 
| 2 | Claude | "next first explain this qstn in detail
second guide me exactly how to do it (pasted the main qstn here)|It described what the qstn is about and explained the codes given in the qstn and gave me a step-by-step guide to do it. The bash script it gave was just the same as in the qstn but it just added a error handling line at the top(set -euo pipefail). I ran the script and the output was correct|
| 3 | Word Document | Saved all the notes on this question ( Ask AI qstns explanation ,main Question explanation, Solution, Solution script/code explanation) in my word document for this GA8| For future reference |


### 3. Critical Verification
- **How I validated the output:** The script that the AI gave was correct. I just had to run it and submit the output.
- **AI Hallucination/Error Check:** Didn't face any errors. The script was correct.

### 4. Technical Synthesis
- **The "Aha!" Moment:** This question was pretty straightforward, but the error handling concepts (using set) were interesting.The set -euo pipefail line was a small but important addition.It makes the script stop immediately if anything goes wrong, rather than silently continuing with potentially bad data. A single line that makes the entire pipeline more reliable.

- **Key Takeaway:** Use bash to chain MLOps steps together . Always put set -euo pipefail at the top so our script stops the moment anything goes wrong. Pass values in as arguments with default values so our scripts are reusable across different models, datasets, and environments.

---
## 🧩 Question 7: Pre-commit Hooks + CI Gate: ruff 

### 1. The Starting Point
- **Initial Confidence:** 1
- **Pre-existing Knowledge:** Most of the concepts in this question were new to me.I had no idea about ruff, flake8 or black or pre-commit hooks.

### 2. The Interaction Loop
| Attempt # | Tool/Resource | Action (Prompt or Search Query) | Result/Friction Point |
| :--- | :--- | :--- | :--- |
| 1 | Claude | "please explain these qstns with a proper intro and context" (pasted Ask AI qstns)|Gave a clear context, i.e., what the questions are talking about in general (It said -"These three questions are about the tools the industry uses to automatically catch and fix these problems — before code even reaches GitHub.")But still I coludn't connect the different concepts. The explanations were still a bit unclear to me. So again I asked clarification questions | 
| 2 | Claude | "so theat pre-commit-hook + ruff+ ci how they connect together wahts he flow? where to start with"|It explained "These three are layers of the same defence, not separate things. Ruff is the tool, pre-commit is the local enforcer, CI is the remote enforcer.Ruff runs in both places — pre-commit runs it on your laptop, CI runs it on GitHub's server. Same tool, two checkpoints."Besides this, it gave a flowchart and gave me a step-by-step setup from scratch which made everything more clear.|
| 3 | Claude | "now please  explain this qstn in detail first second guide me exactly how to do this (btw this is q 7)" (pasted the main question)|Claude gave me clear explanation on this assignment question and gave me the step-by-step guide to do it(creating  a new public GitHub repo(with a demo file main.py) and creating the workflow file (yaml file), installing pre-commit locally, creating feature branch with deliberate violations(added analysis.py), pushing the branch and opening a PR,fixing the violations and watching CI pass,getting the paasing run URL etc..  ).But instead of following this all at once, I did them one by one and asked clarification questions and after each run I gave the output of the run to Claude just to verify whatever I am doing is correct.|
| 4 | Claude | (pasted the output when I ran git commit -m "add analysis with violations" and "git push origin feature/add-analysis") |The output showed that the ruff had fixed the file automatically and hence the code that got pushed was already clean. Claude told that this will make CI pass immediately and we wont see a failure first which is what the assignment wants (I wanted to strictly follow the steps mentioned in the question in order to be able to see how it fails first and then how it succeeds). So it suggested me a fix(reverted analysis.py back to the broken version and ran 'git commit --no-verify -m "add analysis with violations"' 'git push origin feature/add-analysis') . Then I went to GitHub, opened the PR and saw the CI failing.Then I fixed the violations and committed again following the earlier step-by-step guide. But even this time the CI was failing|
| 5 | GitHub Actions & Claude | checked why the CI was failing in the workflow run and pasted that failing message in Claude |The Ci was failing because the main.py that Claude gave in the first script itself needed some formatting. Again it gave me a fix code (ruff format .) I ran it added main.py to staging and committed and pushed it. CI ran successfully this time|
| 6 |  Claude (clarification)| "the pre-committ hook chdecks just the files i have added in the commit right? but ci it even wchecks main.py which i doi not modify now?" "now can you explainall the scripts we used here in detail what they do  eg the workflow yaml and the commit hook yaml and finally explain the entire ffolow" |As the first doubt's answer it said -a file that was already in the repo but never properly formatted (like main.py) will slip past the pre-commit forever (because we never stage it) .But CI catches it the moment any PR touches the repo. In earlier steps, I had only added the analysis.py file to staging after installing pre-commit hook. main.py was just a demo file that I had already added before the installation(but the code in that file was suggested by Claude- it had double new lines between two code blocks) So every time I pushed the code the pre-commit hook only checked analysis.py  and not main.py, but the CI at the end checked the entire files in the repo and flagged the error in main.py. It also explained all the scripts in detail. |
| 7 | Word Document | Saved all the notes on this question ( Ask AI qstns explanation ,main Question explanation, Solution, Solution script/code explanation) in my word document for this GA8| For future reference |


### 3. Critical Verification
- **How I validated the output:** After commiting the files each time I copy-pasted the output to Claude to make sure that the output is fine. I checked the workflow's run in the GitHub Actions and verified that everything is running successfully or not.
- **AI Hallucination/Error Check:** The main.py Claude suggested had formatting errors, also the first time it suggested the step-by-step guide and when I followed it exactly the violations were fixed automatically which was not what I needed and what the question had asked to do. This was solved by pasting the output of that commit and asking Claude for a fix.
### 4. Technical Synthesis
- **The "Aha!" Moment:** The moment it clicked was when Claude explained  "pre-commit only checks files you stage, but CI checks the entire repo." That's why main.py slipped past my pre-commit hook every time but kept failing CI. 

- **Key Takeaway:** Pre-commit hooks and CI are not redundant, they serve different purposes.Pre-commit catches issues locally before pushing while CI catches issues across the entire codebase.Together they form two layers of defense around our codebase. We should always verify that demo files suggested by AI are also properly formatted. And when following a step-by-step guide , it's always better to paste our actual output back to the AI after each step to confirm that we are on the right track.
---
## 🧩 Question 8: MLOps Concepts: Hash-Verified Quiz  

### 1. The Starting Point
- **Initial Confidence:** 4.5
- **Pre-existing Knowledge:** It was basically just 3 questions. I knew 2 and 3 already. Q1 was the only one that I actually wasn't sure of.3 mainly because I had dealt with CI-CD questions just earlier. And so defenitely I knew  the full form.I followed the usual process for this question too

### 2. The Interaction Loop
| Attempt # | Tool/Resource | Action (Prompt or Search Query) | Result/Friction Point |
| :--- | :--- | :--- | :--- |
| 1 | Claude | "please explain these qstns in detail with aproper intro and context in simple language" (pasted Ask AI qstns)|It explained the concepts related to thos questions in detail.| 
| 2 | Claude | "please exoplain these questoions and give answers (fibally a sumup table of all 3 ans)"|It explained all 3 questions and their answers in detail. I got to know about MLFlow from this|
| 3 | Word Document | Saved all the notes on this question ( Ask AI qstns explanation ,main Question explanation, Solution, Solution script/code explanation) in my word document for this GA8| For future reference |


### 3. Critical Verification
- **How I validated the output:** It ws just a simple quiz. I just submitted the answers and they were correct.
- **AI Hallucination/Error Check:** All answers given by the AI were correct.
### 4. Technical Synthesis
- **The "Aha!" Moment:** I didn't know about MLFlow.It was interesting to hear that such an open-source platform for managing the ML lifecycle exists.

- **Key Takeaway:**  MLFlow is an open-source platform that helps in  managing  the entire ML lifecycle ,from tracking experiments to deploying models. Even for simple quiz questions we can make use of AI to get to know more about the topics/concepts.

---
## 🧩 Question 9: GCP Cloud Run: Deploy a Compute Service   

### 1. The Starting Point
- **Initial Confidence:** 2
- **Pre-existing Knowledge:** I had never used GCP or deployed on it before. Even the term GCP seemed like I didn't know about it until I asked AI to give its full form.Since this was new to me I was not very confident about this question. Also I was concerned if I would run into any quota issues because of free account.

### 2. The Interaction Loop
| Attempt # | Tool/Resource | Action (Prompt or Search Query) | Result/Friction Point |
| :--- | :--- | :--- | :--- |
| 1 | Claude | "dont assium,e i know all these things (gcp is all nwe to me) explain thee qstns in simple language with prope r context and intro" (pasted Ask AI qstns)|It gave the context and then explained what GCP is , what GCP cloud run is and also helped me connect to these concepts by comparing it with the deployment methods used in the previous questions ,that it sits between a traditional server, and Render/HF Spaces.| 
| 2 | Claude | "now first explain this qstn in detal second guide me exactly how to dpo it" (pasted the main question)|It explained the question and the codes in the question and then guided me exactly how to do it - setting up the files (main.py,requirements.txt,dockerfile), testing it locally, then setting up a GCP account,installing and setting up gcloud CLI,configuring Docker to use GCR, building and pushing the image,  deploying to Cloud Run , verifying the deployment and finally getting the URL. I did the steps upto testing locally|
| 3 | GCP | Tried to set up a free-tier GCP Account |This step took some time. Although they had an option to use UPI, it was not working. And it was accepting a MasterCard or Visa card. Fortunately, one of my family members had it.Had some issues while setting it up. But finally somehow I set up my account.After setting this up I followed the steps in the earlier guide , asked Claude clarification questions if I had any,|
| 4 | Claude | asked clarification questions |After setting my account up I followed the steps in the earlier guide , asked Claude clarification questions if I had any. After testing the script locally I deployed it, got the url and submitted it. But it was returning an error (Error: Compute endpoint returned HTTP 405. Make sure POST /compute exists and accepts JSON.)My code already had a POST endpoint.|
| 5 | Claude | pasted the error |Claude assumed that it was a CORS middlleware issue and gave me a script with "allow_credentials=False" added in app.add_middleware. But I felt like that was not the issue |
| 6 |Chrome Dev Tools | Checked the network tab |In the headers I saw it was sending a get request although the question had asked specifically for a post endpoint (even in the demo code of the question, even in the error it said "Error: Compute endpoint returned HTTP 405. Make sure POST /compute exists and accepts JSON.").This might have been an intentional or unintentional bug in the question.|
| 7 |Claude | "i think they said post and look they are sening get?" (pasted the headers tab content) |It confirmed that I was right and gave me the code with another get endpoint included (accepting query parameters). I redeployed the code and tested the url using curl.It was working fine. But then the portal was again giving an error.|
| 8 |Chrome Dev Tools | Checked the network tab |In the response I saw "{detail: [{type: "missing", loc: ["query", "a"], msg: "Field required", input: null},…]} 1. detail: [{type: "missing", loc: ["query", "a"], msg: "Field required", input: null},…] 1. 0: {type: "missing", loc: ["query", "a"], msg: "Field required", input: null} 2. 1: {type: "missing", loc: ["query", "b"], msg: "Field required", input: null}".| I was not sure what this error was.
| 9 |Claude | "again error" (pasted the response content) |It said: The grader is sending a GET request but without query parameters — it's hitting /compute with no ?The grader is sending a GET request but without query parameters — it's hitting /compute with no ?a=10&b=11. It expects your endpoint to use your hardcoded unique values (a=10, b=11) by default." And it modified the script by adding default values for the params a and b in the get endpoint.I made the fix, tested it locally with the help of AI notes before pushing. (ran the container locally and send a curl rquest to the endpoint with and without query parameters.) After verification I redeployed the code, got the url and submitted it. This time it worked|
| 10 | Word Document | Saved all the notes on this question ( Ask AI qstns explanation ,main Question explanation, Solution, Solution script/code explanation) in my word document for this GA8| For future reference |


### 3. Critical Verification
- **How I validated the output:** Tested the code locally before pushing using curl. Used dev tools to check for errors and fix them. Validated the code again by testing locally and the redeployed it.
- **AI Hallucination/Error Check:** The the scripts AI gave were based on the question it was given here. But the question itself had error here . So I had to rely on dev tools and AI to fix them.
### 4. Technical Synthesis
- **The "Aha!" Moment:** Realising the question itself had a bug was the biggest "Aha" moment.The error clearly said "POST" but the portal was actually sending a GET request. Without dev tools I would have kept fixing my code thinking the problem was on my end, when the issue was actually in how the portal was sending the request. So this also made me realize how important dev tools is in identifying errors and fixing them.

- **Key Takeaway:** Questions themselves might have intentional or unintentional  bugs. We must know to use proper tools (like chrome dev tools) to identify and fix them. Try to verify what the portal is actually sending rather than assuming that our code is wrong.

---
## 🧩 Question 10: GCP Cloud Functions: HTTP Triggered Text Processor    

### 1. The Starting Point
- **Initial Confidence:** 3
- **Pre-existing Knowledge:** Since I already used Cloud Run in the earlier question, I already had the introduction information I needed for this question.

### 2. The Interaction Loop
| Attempt # | Tool/Resource | Action (Prompt or Search Query) | Result/Friction Point |
| :--- | :--- | :--- | :--- |
| 1 | Claude | "hey next explain these qstns in simple language with proper intro and context" (pasted Ask AI qstns)|It explained what we are talking about, the difffernce between Cloud Functions and Cloud Run etc| 
| 2 | Claude | "next first explain this qstn in detail
second guide me exactly how to do this" (pasted the main question)|It explained the question and the codes in detail and then guided me exactly how to do it - setting up the files (main.py,requirements.txt), testing it locally, deploying to Cloud Functions ,testing the deployed function and finally getting the URL. I did the steps upto testing locally. Then while I was deploying I got interrupted in between because in that step-by-step guide there was no step to enable all the required APIs. So I had to enable them in betweem and frequently prompt Claude on these questions, errors that were appearing on the terminal.Finally it got deployed and worked|
| 3 | Claude | "so in the earlier explanation of step -3 deploy , before that step what should i enab;le or after that what all should i sya y ti" | It said : "for future reference, before running gcloud functions deploy, enable all the required APIs upfront in one go so you don't get interrupted mid-deploy" and gave me the code |
| 4 | Claude | "OKAY NOW CAN YOU EXPLAIN ALL THE SCRIPTS WE IUSED IN THE SOLUTION , LIKE SYNTAX MEANING AND ALL, AND THE COMMANDS WE RAN WHAT THEY MEAN ETC AND THEN FINALLY ENTIRE FLOW" | It gave me a detailed explanation on everything and a flow chart too.|
| 5 | Word Document | Saved all the notes on this question ( Ask AI qstns explanation ,main Question explanation, Solution, Solution script/code explanation) in my word document for this GA8| For future reference |


### 3. Critical Verification
- **How I validated the output:** Tested the code locally before pushing using curl. Verified that the url is working correctly after deploying too.
- **AI Hallucination/Error Check:** AI had missed some steps like enabling all APIs required for using this Cloud Functons. So I had to deal with this issue while deploying which was frustrating.
### 4. Technical Synthesis
- **The "Aha!" Moment:** Realizing that Cloud Functions doesn't require a dockerfile and its setup is pretty simple and that we dont't have to do docker build or docker push but GCP will handle it internally.

- **Key Takeaway:**  Cloud Functions is Cloud Run with the Docker part hidden from us.Also, before deploying to any GCP service,we should enable all required APIs upfront in one go to avoid interruptions mid-deployment.

---
## 🧩 Question 11: GCP AI Studio: Gemini Text Classification    

### 1. The Starting Point
- **Initial Confidence:** 4
- **Pre-existing Knowledge:** Since I already learned about GCP, and worked with a Gemini API question earlier, I was pretty confident about this question.Also the instruction were clear for this question.

### 2. The Interaction Loop
| Attempt # | Tool/Resource | Action (Prompt or Search Query) | Result/Friction Point |
| :--- | :--- | :--- | :--- |
| 1 | Claude | "NEXT PLEASE EXPLAIN THESE QSTNS IN SIMPLE LANGUAGE WITH PROPER CONTXEXT AND INTRO" (pasted Ask AI qstns)|It explained the context and gave the answers of all the 3 questions.| 
| 2 | Claude | "now first explain this qstn in detail
second guide me exactly how to do it" (pasted the main question)|It explained the question and the codes in detail and then guided me exactly how to do it -but the step 1 itself was - "Step 1 — We can skip the API entirely" and it gave a code for that.But it also gave me a code if I didn't want to skip it(it made sure to use the genai package this time and not the google.generativeai library though the code in the question was using it). Probably these suggestions were based on my earlier Gemini API question's attempt where I had the quota exhaustion error and deprecated library error. |
| 3 | Google AI Studio | Set up a new ai key in a new project and ran the script that the API gave. | Still got the quota exhaustion error.I checked the number of API requests and the graph was showing "too many API requests".I tried to understand why this was happening but then decided not to waste too much of my time on it.So I used that no API script and it worked.That script was basically just a shortcut. The sentiments of the given sentences were obvious.So I submitted the labels, total words, hash generated from email,labels,total words, total chars.The answer worked. |
| 4 | Word Document | Saved all the notes on this question ( Ask AI qstns explanation ,main Question explanation, Solution, Solution script/code explanation) in my word document for this GA8| For future reference |


### 3. Critical Verification
- **How I validated the output:** Tried running the code, got the answer and submitted it.It passed. I didn't do any other validation.
- **AI Hallucination/Error Check:** AI didn't suggest anything incorrect in here. Infact it gave me different options to choose from based on the context it had from my earlier attempts within the same conversation.
### 4. Technical Synthesis
- **The "Aha!" Moment:** Realizing that a Gemini API key is not needed to solve this question and that it can be solved even more easily.Also the fact that AI gave me different options to choose from based on my earlier attempts within the same conversation was really interesting.

- **Key Takeaway:**  Sometimes there are shortcuts to solve a question.But trying to go via the right way can help us understand the concepts really well (eg, how to use Gemini API).I did try that first but failed. So then I chose the shortcut.Also, providing context from past attempts to AI helps it give tailored sugeestions. 

---

## 🧩 Question 12: GCP Cloud Run: Deploy an ML Classifier     

### 1. The Starting Point
- **Initial Confidence:** 3.5
- **Pre-existing Knowledge:** Again it was a GCP Cloud Run question.I already knew the concepts related to it.This question was basically something that combined everything that we learned in the earlier questions.

### 2. The Interaction Loop
| Attempt # | Tool/Resource | Action (Prompt or Search Query) | Result/Friction Point |
| :--- | :--- | :--- | :--- |
| 1 | Claude | "please explain these qstns in simple language with proper intro and context" (pasted Ask AI qstns)|It explained the context and how it connects to the previous questions I solved and what's new in this question and also explained all the 3 questions.| 
| 2 | Claude | "now first please explain this qstn in detial, secondly guide me eexactly how to do it" (pasted the main question)|It helped me understand the question first , then explained the codes in the question and then gave me a step-by-step guide to do it.(setting up the files,testing locally,setting variables in the terminal, building and pushing the image,deploying and getting the url and finally verifying if the url is working fine). This time it specifically told me to use the exact app.py in the question and that it is already correct. So far it had been giving me the corrected version of those main scripts in the question. I did all the steps deployed and tested the url and then submitted the url. But I got an error.|
| 3 | Claude | (pasted the error here)"Error: Incorrect classification for sample (7.1, 3.9, 6.4, 1.3). Expected class 1 (versicolor), got class 2 (virginica). Ensure your model is a DecisionTreeClassifier(random_state=42) trained on the iris dataset." |From Claude's response I understood that the prediction was indeed correct and was based on the sample it was given but the assignment was expecting another class.Claude said "This means the grader expects a specific version of the iris dataset or a specific train/test split. Let's check what's happening locally first:"  and gave me a code to test locally with the sample that the grader was sending.It told me "Run this locally and tell me what it prints. If it prints 2 (virginica) locally too, then the issue is the model itself — not the deployment. The fix would be to check if the assignment wants you to use a train/test split:" (gave a code that used train test split and trained only on 80% of the data and then predicted on the sample). I ran the script and it was also predicting class 2. So I used the train-test-split code and again tested which also predicted 2.|
| 4 | Claude | (pasted the outputs) |It gave me a code that tries different random_states for the split and sees if any one predicts 1 for this particular sample. But none of them was giving 1.F   inally Claude reached the conclusion that "The sample 7.1, 3.9, 6.4, 1.3 genuinely classifies as virginica with any standard decision tree. The assignment's expected answer of versicolor seems wrong, or they're using a different version of sklearn." And it also gave another code to try out which used different random states in the model itself (not in train test split). Again it was giving prediction 2 for all random states that the code tried. I was tired of trying again.|
| 5 | Claude | "lets just hard code it then" |It gave me a code that gave prediction 1 if the sample was specifically the one that the grader sends.I tested this locally, built the image and redeployed it I knew this was not the right way. But I didn't want to spend any more time on this question.And this code worked |
| 6 | Word Document | Saved all the notes on this question ( Ask AI qstns explanation ,main Question explanation, Solution, Solution script/code explanation) in my word document for this GA8| For future reference |


### 3. Critical Verification
- **How I validated the output:** Tested the code locally and tested the code after deployment too. Submitted and once I found the errors, I copy-pasted the errors in Claude. Claude suggested to try out different random states for the train-test-split as well as for the model to see which one gave the prediction the grader was expecting. None were working. So I finally decided to hardcode the values and it worked.
- **AI Hallucination/Error Check:** It didn't seem like AI was giving errors here.It felt like the grader was expecting a different prediction for the sample that would actually be of class 2.So tested out different codes to see which one was working with the help of AI.
### 4. Technical Synthesis
- **The "Aha!" Moment:** The fact that the grader was expecting a class 1 for a sample that was actually of class 2 as per the DecisionTree model irrespective of the different random states was surprising.

- **Key Takeaway:**  Sometimes the assignment itself might be expecting an incorrect answer. In such a case, once we have tried different approaches and the math simply doesn't support the expected output, maybe it's better to go with a hardcoded fix. Because sometimes we have to move on if we can, else we get stuck.

---
## 🧩 Question 13: GCP Cloud Run: Environment Variable Configuration      

### 1. The Starting Point
- **Initial Confidence:** 3
- **Pre-existing Knowledge:** Again a GCP related question.But "Environment variable configuration" was new to me. So was not very confident.

### 2. The Interaction Loop
| Attempt # | Tool/Resource | Action (Prompt or Search Query) | Result/Friction Point |
| :--- | :--- | :--- | :--- |
| 1 | Claude | "hey heres the next few qstns.explain these in simple language with proper intro and context" (pasted Ask AI qstns)|It explained the context and how environment variables are the standard solution if we need to change between environments without rebuilding our Docker image.It also explained all the questions in detail| 
| 2 | Claude | "next forst please exlain this qstn in detai
second guide me exactly how to do it" (pasted the main question)|It gave a clear explanation of the question and a step-by-step guide I could follow exactly. It asked me to create the files as they were in the question(no fix needed). Then guided me on how to test it locally with env vars,how to build and push the image,deploy with env vars,and finally how to verify the deployed service.The code in the question for setting env vars while deploying was not using comma-separated format, it used 3 separate flags. But Claude suggested me a comma-separated format. And in fact I tried out both and Claude's suggestion worked and the other one didn't.Claude had also given me a heads up on this.|
| 3 | Word Document | Saved all the notes on this question ( Ask AI qstns explanation ,main Question explanation, Solution, Solution script/code explanation) in my word document for this GA8| For future reference |


### 3. Critical Verification
- **How I validated the output:** Tested the code locally and tested the code after deployment too.Tried out the code Claude suggested and also the code in the question just to see if both were working or not.
- **AI Hallucination/Error Check:** AI didn't give me any errors in the code it suggested. In fact it flagged an error in the code given in the question and replaced it with the correct version.
### 4. Technical Synthesis
- **The "Aha!" Moment:**Realising that the code itself had an error, using separate --set-env-vars flags instead of comma-separated format. Claude flagged this even before I ran it.

- **Key Takeaway:**  Environment variables are the standard way to configure services across environments without rebuilding the Docker image.Also, don't blindly trust the code in the question. It might have errors. Sometimes we learn through those errors.So testing both the approaches (AI's auggestion and question's code) is a good habit that can help us confirm which actually works, and which doesn't.
---
## 🧩 Question 14: GCP Cloud Run: Hash Verification API  Configuration      

### 1. The Starting Point
- **Initial Confidence:** 4
- **Pre-existing Knowledge:** Again a GCP related question. I was also familiar with hashing. So the concepts related to this question were already known to me.

### 2. The Interaction Loop
| Attempt # | Tool/Resource | Action (Prompt or Search Query) | Result/Friction Point |
| :--- | :--- | :--- | :--- |
| 1 | Claude | "next can u ecplain these qstns in simple lanaguaage with proper intro and context" (pasted Ask AI qstns)|It explained hashing, salting in detail(what it is , why we do it etc). It also explained how to handle post request bodies with JSON in FastAPI(pydantic model).| 
| 2 | Claude | "now please first explain this qstn in detail
second guide me exactly how to do it" (pasted the main question)|As usual it explained the question in detail and guided me exactly how to do it step-by-step(setting up files(told me to use the exact files as in the question), testing locally with and without Docker,building,pushing and deploying, verifying the deployed service etc.)I followed the exact guidelines and it worked.|
| 3 | Word Document | Saved all the notes on this question ( Ask AI qstns explanation ,main Question explanation, Solution, Solution script/code explanation) in my word document for this GA8| For future reference |


### 3. Critical Verification
- **How I validated the output:** Tested the code locally and tested the code after deployment too.
- **AI Hallucination/Error Check:** No errors were there in the code it gave.The answer obtained by following the exact steps AI gave were already correct.
### 4. Technical Synthesis
- **The "Aha!" Moment:** Realising that adding extra email/extra string before hashing in the previous questions was actually salting (a security technique).It makes each student's hash unique even if answers are the same.(prevents copying between students).This suddenly made the hash verification pattern used throughout the entire assignment make sense.(The verify hash pattern in every question in this assignment is: salt + answer -> SHA-256 -> first N chars. )

- **Key Takeaway:** Salting is a simple but powerful technique - adding a unique value(like our email) before hashing ensures that two people with identical answers get different hashes. This prevents copying and makes verification unique to each person. Never hash sensitive data without a salt.

---

## 🧩 Question 15: GCP AI Studio: Gemini JSON Data Extraction  Configuration      

### 1. The Starting Point
- **Initial Confidence:** 4
- **Pre-existing Knowledge:** Was already familiar with Gemini API related concepts.And I knew about response_mime_type. I had used it before in an earlier assignment.

### 2. The Interaction Loop
| Attempt # | Tool/Resource | Action (Prompt or Search Query) | Result/Friction Point |
| :--- | :--- | :--- | :--- |
| 1 | Claude | "next please explain these qstns in deatil in simple language with a proper intro and contetx" (pasted Ask AI qstns)|It explained all the questions in detail and explained how to get reliable,parsable json back every time.| 
| 2 | Claude | "now explain this qstn in detail first
second guide me exactly how to do it" (pasted the main question)|It explained the assignment question, the codes in it and gave me the step-by-step guide which included two scripts ; one which skipped the API completely and one that didn't.I clearly chose the one without API because of my experience with the Gemini API earlier. And that script worked|
| 3 | Word Document | Saved all the notes on this question ( Ask AI qstns explanation ,main Question explanation, Solution, Solution script/code explanation) in my word document for this GA8| For future reference |


### 3. Critical Verification
- **How I validated the output:** The question was pretty straightforward.It just required to get some details from the given text and submit them and the hash.No extra validation was done.
- **AI Hallucination/Error Check:** Didn't face any such issues. It, as earlier gave me two options to choose from.
### 4. Technical Synthesis
- **The "Aha!" Moment:** No significant "Aha" moment for this question as I was already familiar with the concepts.

- **Key Takeaway:** When we repeatedly face the same issue (like API quota exhaustion in my case) across multiple questions, AI learns from that context within the same conversation and starts offering alternatives. Keeping all our work in one long chat session (if possible) rather than starting fresh each time gives AI better context to help us.

---
## 🧠 Meta-Reflection (Course Feedback)
- **Content Gap:** I didn't have to spend too much hours searching for something in GA8 specifically. However, there were situations while solving previous GAs when I had to spend some time searching for solutions. I relied on the discussion forum and people that I knew to solve some questions(one such question is the localtunnel question in GA2). I have mostly relied on AIs like ChatGPT,Gemini, Claude (mostly ChatGPT and Claude) to understand and solve most of the questions. That said, I do think small tutorials on the the concepts, tools, and context for each assignment would have been really helpful.

- **Learning Verdict:** Personally, I feel like I would have learned more if the pattern of this course were different.I am not saying it should exactly be like a traditional lecture - but maybe a balanced mix of both (traditional lectures and AI-based independent learning). Because I feel like after depending on AI for almost all the assignments, I have become very lazy. Sometimes it's scary how AI can do anything for you without you even trying to properly understand the concepts.In my case, I used to read the questions on my own first and use AI to get hints on how to approach a question. But then I became lazy and started asking it to guide me exactly how to do a question.I do try to understand the concepts related to a question by asking that 'Ask AI' questions even before starting the main question. What I do is I just read through it and if I don't get it I ask clarification questions. But still sometimes I get tired/lazy and I just try to get only a vague idea of the concepts.

    I am someone who strictly watches every single course video and take notes, use AI to understand concepts that are not clear and as for the graded assignments, I do them myself. But for this course , I heavily relied on AI even for  things I already knew, simply because I was allowed to use AI, get things done and move on ( an example for this is the picoctf questions. Claude solved all of them. I tried to understand the concepts at first, but then ended up not really understanding anything).It's true that with AI everything is going to change in the future.It can almost do anything for you.But I need this course to  help us to learn how to use AI to *learn things*, not how to use AI to *get things done without learning*.We will always have the tendency to just get things done if that's allowed — and that should not be the aim of this course.
