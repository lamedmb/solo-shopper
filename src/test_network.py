import socket
import os
from dotenv import load_dotenv

load_dotenv()

host = os.getenv('DB_HOST')

print(f"Testing connection to: {host}")
print("-" * 50)

# Test DNS resolution
try:
    ip = socket.gethostbyname(host)
    print(f"✅ DNS resolution successful: {ip}")
except socket.gaierror as e:
    print(f"❌ DNS resolution failed: {e}")
    print("\nPossible fixes:")
    print("1. Check internet connection")
    print("2. Flush DNS cache: sudo dscacheutil -flushcache")
    print("3. Try pooler URL instead")
    print("4. Check if behind firewall/VPN")
    exit(1)

# Test port connectivity
import socket
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((host, int(os.getenv('DB_PORT'))))
    sock.close()
    
    if result == 0:
        print(f"✅ Port {os.getenv('DB_PORT')} is reachable")
    else:
        print(f"❌ Port {os.getenv('DB_PORT')} is not reachable")
except Exception as e:
    print(f"❌ Port test failed: {e}")