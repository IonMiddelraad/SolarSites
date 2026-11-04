from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from models import RegisterRequest, LoginRequest
from pvgis_data_caller import send_PVcalc_request
from database import init_db
from auth import register_user, login_user, logout_user, get_current_user

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)
bearer = HTTPBearer()

# Register, Login, Logout

@app.post("/api/register")
def register(data: RegisterRequest):
    return register_user(data)

@app.post("/api/login")
def login(data: LoginRequest):
    return login_user(data)

@app.post("/api/logout")
def logout(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    return logout_user(credentials.credentials)

@app.get("/api/me")
def get_current_user_email(user: dict = Depends(get_current_user)):
    return user["email"]

@app.get("/api/sites")
def get_caller_sites():
    test = send_PVcalc_request(52.09, 5.12, 4)
    # code here
    return test

@app.post("/api/sites")
def create_site():
    # code here
    return

@app.get("/api/sites/{id}")
def get_site():
    # code here
    return

@app.put("/api/sites/{id}")
def update_site():
    # code here
    return

@app.delete("/api/sites/{id}")
def delete_site():
    # code here
    return

@app.get("/api/sites/{id}/production")
def get_site_production():
    # code here
    return

@app.get("/api/sites/{id}/battery")
def get_site_battery():
    # code here
    return
