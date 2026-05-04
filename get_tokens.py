import os
import base64
import requests
import time
from urllib.parse import urlencode
from dotenv import load_dotenv
from app import database

load_dotenv()

CLIENT_ID = os.getenv("FITBIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("FITBIT_CLIENT_SECRET")
REDIRECT_URI = "http://127.0.0.1:8080" 
def get_auth_url():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "scope": "activity sleep nutrition weight",
        "redirect_uri": REDIRECT_URI,
        "expires_in": 2592000 
    }
    return f"https://www.fitbit.com/oauth2/authorize?{urlencode(params)}"

def exchange_code(code):
    url = "https://api.fitbit.com/oauth2/token"
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "client_id": CLIENT_ID,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
        "code": code
    }
    
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        tokens = response.json()
        expires_at = time.time() + tokens.get("expires_in", 28800)
        
        database.update_tokens(tokens["access_token"], tokens["refresh_token"], expires_at)
        print("\n✅ SUCCESS: Tokens saved to Cloud PostgreSQL Database!")
    else:
        print(f"\n❌ Error exchanging code: {response.text}")

if __name__ == "__main__":
    print("\n=== Fitbit OAuth2 Cloud Setup ===")
    print("1. Click this link to authorize:")
    print(get_auth_url())
    print("\n2. You will be redirected to a page that might say 'Site cannot be reached'. This is normal.")
    print("3. Look at the URL. It will look like: http://127.0.0.1:8080/?code=XXXXX")
    print("4. Copy ONLY the code (the part after '?code=' and before any '#').")
    
    code = input("\nPaste the code here: ").strip()
    
    if code.endswith("#_=_"):
        code = code[:-4]
        
    exchange_code(code)