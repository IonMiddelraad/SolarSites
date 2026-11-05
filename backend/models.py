from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ClientSite(BaseModel):
    id: str
    client_name: str
    address: str
    latitude: float
    longitude: float
    roof_area_m2: int | None = None
    peak_Kwp: float
    advisor_id: str

class ClientSiteRequest(BaseModel):
    client_name: str
    address: str
    latitude: float
    longitude: float
    roof_area_m2: int | None = None
    peak_Kwp: float