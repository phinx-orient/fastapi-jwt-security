from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from auth import Auth
from user_model import AuthModel
from crud_user import get_db
import uvicorn
import logging

logging.getLogger("passlib").setLevel(logging.ERROR)
app = FastAPI()

security = HTTPBearer()
auth_handler = Auth()

# Dependency to secure routes
def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    username = auth_handler.decode_token(token)
    if username is None:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )
    return username


@app.post("/signup")
def signup(user_details: AuthModel):
    db_client = get_db()  # Create a new database client for each request
    if db_client.user_exists(user_details.username):
        return "Account already exists"
    try:
        hashed_password = auth_handler.encode_password(user_details.password)
        user_details.password = hashed_password  # Update password to hashed
        db_client.create_user(user_details)
        db_client.close()
        return {"message": "User created successfully"}
    except Exception as e:
        error_msg = "Failed to signup user: " + str(e)
        db_client.close()
        return error_msg


@app.post("/login")
def login(user_details: AuthModel):
    db_client = get_db()
    user = db_client.get_user(user_details.username)
    if user is None:
        return HTTPException(status_code=401, detail="Invalid username")
    if not auth_handler.verify_password(user_details.password, user[1]):
        return HTTPException(status_code=401, detail="Invalid password")

    access_token = auth_handler.encode_token(user[0])
    refresh_token = auth_handler.encode_refresh_token(user[0])
    db_client.close()
    return {"access_token": access_token, "refresh_token": refresh_token}


@app.get("/refresh_token")
def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    refresh_token = credentials.credentials
    try:
        new_token = auth_handler.refresh_token(refresh_token)
        return {"access_token": new_token}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Refresh token expired or invalid")


@app.get("/secret", dependencies=[Depends(get_current_user)])
def secret_data():
    return "Top Secret data only authorized users can access this info"

@app.get("/notsecret")
def not_secret_data():
    return "Not secret data"


if __name__ == "__main__":
    app_module = "main:app"
    uvicorn.run(app_module, host="0.0.0.0", port=8000, reload=True)
