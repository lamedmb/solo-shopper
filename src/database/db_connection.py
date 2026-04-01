"""Database connection utilities for Solo Shopper"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

def get_connection():
    """Create and return a database connection"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT'),
            connect_timeout=10,
            options='-c statement_timeout=30000'
        )
        return conn
    except Exception as e:
        print(f"Connection error: {e}")
        print(f"Attempting connection with:")
        print(f"  Host: {os.getenv('DB_HOST')}")
        print(f"  User: {os.getenv('DB_USER')}")
        print(f"  Port: {os.getenv('DB_PORT')}")
        print(f"  Database: {os.getenv('DB_NAME')}")
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