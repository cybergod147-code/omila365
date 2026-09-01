import requests

class EmailHarvester:
    def __init__(self, access_token):
        self.headers = {"Authorization": f"Bearer {access_token}"}
    
    def harvest_contacts(self):
        url = "https://graph.microsoft.com/v1.0/me/contacts"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json().get('value', [])
    
    def harvest_inbox(self, limit=100):
        url = "https://graph.microsoft.com/v1.0/me/messages"
        params = {"$top": limit, "$orderby": "receivedDateTime DESC"}
        resp = requests.get(url, headers=self.headers, params=params)
        resp.raise_for_status()
        return resp.json().get('value', []) 
