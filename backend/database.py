import sqlite3
import time

def connect_to_db(database_name: str):
    return sqlite3.connect(database_name)


def init_db():
    connection = sqlite3.connect("app.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
        token_hash TEXT  PRIMARY KEY,
        user_id TEXT NOT NULL,
        expires_at INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sites (
        id TEXT PRIMARY KEY,
        client_name TEXT NOT NULL,
        address TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        roof_area_m2 INTEGER,
        peak_Kwp REAL NOT NULL,
        advisor_id TEXT NOT NULL,
        FOREIGN KEY (advisor_id) REFERENCES users(id)
        );
    """)

    # Delete old and expired sessions
    cursor.execute(
            "DELETE FROM sessions WHERE expires_at <= ?",
            (int(time.time()),)
        )

    connection.commit()
    connection.close()