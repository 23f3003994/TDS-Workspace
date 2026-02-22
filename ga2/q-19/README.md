
#running the app on port 8000 is necessary
coz i submitted http://localhost:8000/auth while creating oauth client id in google.ie once the user authenticates , google will be redirecting and sending that user indo that http://localhost:8000/auth endpoint only.

STEP 4️⃣ Run the App
uvicorn main:app --reload  

Open browser:

http://localhost:8000/login

Login using:

23f3003994@ds.study.iitm.ac.in
STEP 5️⃣ Get the Token

After login, open:

http://localhost:8000/id_token

You’ll see:

{
  "id_token": "djsjdsf..."
}

Copy it.

STEP 6️⃣ Submit JSON

Final submission:

{
  "id_token": "PASTE_TOKEN_HERE",
  "client_id": "YOUR_CLIENT_ID"
}