from fastapi import FastAPI, Request
from starlette.responses import RedirectResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth

app = FastAPI()

# session secret key
app.add_middleware(SessionMiddleware, secret_key="supersecret")

oauth = OAuth()

oauth.register(
    name="google",
    client_id="put-client-id",  #in .env file
    client_secret="put-client-secret", #in .env file
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

# Step 1: redirect user to Google login
@app.get("/login")
async def login(request: Request):
    redirect_uri = "http://localhost:8000/auth"
    return await oauth.google.authorize_redirect(request, redirect_uri)

# Step 2: callback from Google
@app.get("/auth")
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request)
    id_token = token.get("id_token")

    # store in session
    request.session["id_token"] = id_token

    return RedirectResponse(url="/id_token")

# Step 3: endpoint to return id_token
@app.get("/id_token")
async def get_id_token(request: Request):
    id_token = request.session.get("id_token")

    if not id_token:
        return JSONResponse({"error": "Not logged in"}, status_code=401)

    return {"id_token": id_token}