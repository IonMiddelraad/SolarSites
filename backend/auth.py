import uuid
import time
import hashlib
import sqlite3
import secrets
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, Depends
from pwdlib import PasswordHash

from models import RegisterRequest, LoginRequest
from database import connect_to_db

password_hash = PasswordHash.recommended()
bearer = HTTPBearer()

def hash_token(token):
    return hashlib.sha256(token.encode()).hexdigest()

def register_user(data: RegisterRequest):
    data.password = password_hash.hash(data.password)

    connection = connect_to_db("app.db")

    try:
        connection.execute(
             "INSERT INTO users VALUES (?, ?, ?)",
             (str(uuid.uuid4()), str(data.email).lower(), data.password)
        )
        connection.commit()

    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email is already registered")
    
    finally:
        connection.close()

    return {"detail": "User registered"}

def login_user(data: LoginRequest):
    connection = connect_to_db("app.db")
    connection.row_factory = sqlite3.Row

    user = connection.execute(
        "SELECT * FROM users WHERE email = ?",
        (str(data.email).lower(),)
    ).fetchone()

    # user doesnt exist or wrong password
    if user is None or not password_hash.verify(
        data.password, user["password_hash"]
    ):
        connection.close()
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    # correct password
    token = secrets.token_urlsafe(32)
    token_digest = hash_token(token)
    # token lasts for 60 minutes
    expires_at = int(time.time()) + (60 * 60)

    connection.execute(
        """
        INSERT INTO sessions (token_hash, user_id, expires_at)
        VALUES (?, ?, ?)
        """,
        (token_digest, user["id"], expires_at)
    )
    connection.commit()
    connection.close()
    
    return {
        "access_token": token,
        "token_type": "bearer"
    }

def logout_user(token: str):
    token_digest = hash_token(token)

    connection = connect_to_db("app.db")

    connection.execute(
        "DELETE FROM sessions WHERE token_hash = ?",
        (token_digest,)
    )

    connection.commit()
    connection.close()

    return {"message": "Logged out"}

def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(bearer)
        ):
    token = credentials.credentials
    token_digest = hash_token(token)

    connection = connect_to_db("app.db")
    connection.row_factory = sqlite3.Row

    # find not expired session
    session = connection.execute("""
        SELECT users.id, users.email
        FROM sessions
        JOIN users ON users.id = sessions.user_id
        WHERE sessions.token_hash = ?
        AND sessions.expires_at > ?
        """,
        (token_digest, int(time.time()))
    ).fetchone()

    connection.close()

    if session is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session"
        )

    return dict(session)