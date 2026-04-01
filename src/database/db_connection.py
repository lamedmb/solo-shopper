"""Database connection utilities for Solo Shopper"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from pathlib import Path

# Load .env for local development
load_dotenv()

# Try to import streamlit for cloud deployment
try:
    import streamlit as st
    # Use Streamlit secrets if available (cloud deployment)
    if hasattr(st, 'secrets'):
        DB_HOST = st.secrets.get("DB_HOST", os.getenv('DB_HOST'))
        DB_NAME = st.secrets.get("DB_NAME", os.getenv('DB_NAME'))
        DB_USER = st.secrets.get("DB_USER", os.getenv('DB_USER'))
        DB_PASSWORD = st.secrets.get("DB_PASSWORD", os.getenv('DB_PASSWORD'))
        DB_PORT = st.secrets.get("DB_PORT", os.getenv('DB_PORT'))
    else:
        # Fallback to environment variables
        DB_HOST = os.getenv('DB_HOST')
        DB_NAME = os.getenv('DB_NAME')
        DB_USER = os.getenv('DB_USER')
        DB_PASSWORD = os.getenv('DB_PASSWORD')
        DB_PORT = os.getenv('DB_PORT')
except ImportError:
    # Streamlit not available, use environment variables
    DB_HOST = os.getenv('DB_HOST')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_PORT = os.getenv('DB_PORT')

def get_connection():
    """Create and return a database connection"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            connect_timeout=10,
            options='-c statement_timeout=30000'
        )
        return conn
    except Exception as e:
        print(f"Connection error: {e}")
        print(f"Attempting connection with:")
        print(f"  Host: {DB_HOST}")
        print(f"  User: {DB_USER}")
        print(f"  Port: {DB_PORT}")
        print(f"  Database: {DB_NAME}")
        raise

def execute_query(query, params=None, fetch=True):
    """Execute a SQL query and return results"""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            if fetch:
                return cur.fetchall()
            conn.commit()
            return None
    finally:
        conn.close()

def execute_script(script_path):
    """Execute a SQL script file"""
    with open(script_path, 'r') as f:
        script = f.read()
    
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(script)
        conn.commit()
        print(f"✅ Executed: {script_path}")
    finally:
        conn.close()

if __name__ == "__main__":
    # Test connection
    try:
        conn = get_connection()
        print("✅ Database connection successful!")
        conn.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")