import uuid
from sqlite3 import Row, IntegrityError
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, status, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from models import RegisterRequest, LoginRequest, ClientSiteRequest, ClientSite
from pvgis_data_caller import send_PVcalc_request
from database import init_db, connect_to_db
from auth import register_user, login_user, logout_user, get_current_user

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)
bearer = HTTPBearer()

# authentication
@app.post("/api/register", status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest):
    return register_user(data)

@app.post("/api/login")
def login(data: LoginRequest):
    return login_user(data)

@app.post("/api/logout")
def logout(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    return logout_user(credentials.credentials)

# account info
@app.get("/api/me")
def get_current_user_email(user: dict = Depends(get_current_user)):
    return user["email"]

# sites
@app.get("/api/sites")
def get_caller_sites(user: dict = Depends(get_current_user)):
    
    connection = connect_to_db("app.db")
    sites = connection.execute("SELECT * FROM sites WHERE advisor_id = ?", (user["id"],)).fetchall()
    connection.close()

    return [dict(site) for site in sites]

@app.post("/api/sites", status_code=status.HTTP_201_CREATED)
def create_site(data: ClientSiteRequest, user: dict = Depends(get_current_user)):

    # create site object from data
    client_site = ClientSite(
    id=str(uuid.uuid4()),
    client_name=data.client_name,
    address=data.address,
    latitude=data.latitude,
    longitude=data.longitude,
    roof_area_m2=data.roof_area_m2,
    peak_Kwp=data.peak_Kwp,
    advisor_id=user["id"]
    )

    connection = connect_to_db("app.db")

    connection.execute("""
    INSERT INTO sites
    (id, client_name, address, latitude, longitude, roof_area_m2, peak_Kwp, advisor_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        client_site.id, client_site.client_name, client_site.address, client_site.latitude, 
        client_site.longitude, client_site.roof_area_m2, client_site.peak_Kwp, client_site.advisor_id
    ))

    connection.commit()
    connection.close()
    return client_site

@app.get("/api/sites/{id}")
def get_site(id: str, user: dict = Depends(get_current_user)):
    connection = connect_to_db("app.db")

    try:
        site = connection.execute(
                "SELECT * FROM sites WHERE id = ? AND advisor_id = ?",
                (str(id), user["id"],)
            ).fetchone()
        
        connection.commit()

        if site is None:
            raise HTTPException(status_code=404, detail="Site does not exists or you do not own it")
        
        return dict(site)

    finally:
        connection.close()
    

@app.put("/api/sites/{id}")
def update_site(data: ClientSiteRequest, user: dict = Depends(get_current_user)):
    connection = connect_to_db("app.db")

    # create site object from data
    client_site = ClientSite(
    id=str(uuid.uuid4()),
    client_name=data.client_name,
    address=data.address,
    latitude=data.latitude,
    longitude=data.longitude,
    roof_area_m2=data.roof_area_m2,
    peak_Kwp=data.peak_Kwp,
    advisor_id=user["id"]
    )

    try:
        update = connection.execute("""
            UPDATE sites SET 
                client_name = ?,
                address = ?,
                latitude = ?,
                longitude = ?,
                roof_area_m2 = ?,
                peak_Kwp = ?
            WHERE id = ? AND advisor_id = ?
            """,
            (data.client_name, data.address, data.latitude, data.longitude,
             data.roof_area_m2, data.peak_Kwp, id, user["id"])
            )
        
        if update.rowcount == 0:
            raise HTTPException(status_code=404, detail="Site does not exists or you do not own it")
        
        connection.commit() 
        
        return {"message": "Site successfully updated"}

    finally:
        connection.close()

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
    test = send_PVcalc_request(52.09, 5.12, 4)
    return test


# testting
