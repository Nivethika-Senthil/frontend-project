from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from passlib.hash import bcrypt
import psycopg2
from psycopg2 import sql
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection function
def get_db_connection():
    conn = psycopg2.connect(
        dbname="superstore_db",
        user="postgres",
        password="nive2003",
        host="localhost",
        port="5432"
    )
    return conn

app = FastAPI()

# Serve static frontend files
app.mount("/frontend", StaticFiles(directory="../frontend", html=True), name="frontend")

# User model for sign-up and login
class User(BaseModel):
    name: str = None  # Optional for login
    gender: str = None  # Optional for login
    email: str
    password: str

# Helper function to check if user already exists
def user_exists(email: str, conn):
    try:
        with conn.cursor() as cursor:
            query = sql.SQL("SELECT * FROM users WHERE email = %s")
            cursor.execute(query, (email,))
            return cursor.fetchone()
    except Exception as e:
        logger.error(f"Error checking user existence: {e}")
        return None

# API route for user sign-up
@app.post("/signup")
async def signup(user: User):
    conn = get_db_connection()
    if user_exists(user.email, conn):
        conn.close()
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = bcrypt.hash(user.password)

    try:
        with conn.cursor() as cursor:
            query = sql.SQL(
                "INSERT INTO users (name, gender, email, password) VALUES (%s, %s, %s, %s)"
            )
            cursor.execute(query, (user.name, user.gender, user.email, hashed_password))
            conn.commit()
            logger.info(f"User {user.email} signed up successfully.")
    except Exception as e:
        logger.error(f"Error during signup: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        conn.close()

    return RedirectResponse(url="/frontend/menu.html", status_code=303)

# API route for user login
@app.post("/login")
async def login(user: User):
    logger.info(f"Login attempt for email: {user.email}")
    
    conn = get_db_connection()
    
    # Check if user exists
    existing_user = user_exists(user.email, conn)
    if not existing_user:
        conn.close()
        logger.warning(f"Login attempt failed for {user.email}: User not found")
        raise HTTPException(status_code=404, detail="User not found")

    logger.info(f"Entered Password: {user.password}")
    logger.info(f"Stored Hashed Password: {existing_user[4]}")

    # Verify the password
    if not bcrypt.verify(user.password, existing_user[4]):
        conn.close()
        logger.warning(f"Login attempt failed for {user.email}: Invalid password")
        raise HTTPException(status_code=401, detail="Invalid password")

    logger.info(f"User {user.email} logged in successfully.")
    conn.close()
    return RedirectResponse(url="/frontend/menu.html", status_code=303)

# Root route to redirect to the signup/login page
@app.get("/")
async def root():
    return RedirectResponse(url="/frontend/index.html", status_code=303)

# GET routes for signup and login to redirect to the index page
@app.get("/signup")
async def get_signup():
    return RedirectResponse(url="/frontend/index.html", status_code=303)

@app.get("/login")
async def get_login():
    return RedirectResponse(url="/frontend/index.html", status_code=303)
