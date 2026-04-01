import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

print("Testing database connection...")
print("=" * 50)
print(f"Host: {os.getenv('DB_HOST')}")
print(f"Port: {os.getenv('DB_PORT')}")
print(f"User: {os.getenv('DB_USER')}")
print(f"Database: {os.getenv('DB_NAME')}")
print("=" * 50)

try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        port=os.getenv('DB_PORT'),
        connect_timeout=10
    )
    print("\n✅ Database connection successful!")
    
    # Test a simple query
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print(f"✅ PostgreSQL version: {version[0][:50]}...")
    
    cur.close()
    conn.close()
    
except psycopg2.OperationalError as e:
    print(f"\n❌ Connection failed!")
    print(f"Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check DB_USER format for pooler: should be 'postgres.PROJECT_REF'")
    print("2. Verify DB_PASSWORD is correct")
    print("3. Try direct connection instead of pooler")
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")