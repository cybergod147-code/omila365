import requests
import time

CLIENT_ID = "04b07795-8ddb-461a-bbee-02f9e1bf7b46"

def get_device_code():
    url = "https://login.microsoftonline.com/common/oauth2/v2.0/devicecode"
    data = {"client_id": CLIENT_ID, "scope": "https://graph.microsoft.com/.default"}
    resp = requests.post(url, data=data)
    resp.raise_for_status()
    return resp.json()

def poll_for_token(device_code, max_attempts=60):
    url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
    data = {
        "client_id": CLIENT_ID,
        "device_code": device_code,
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
    }
    for _ in range(max_attempts):
        resp = requests.post(url, data=data)
        if resp.status_code == 200:
            return resp.json()
        time.sleep(5)
    return None 
