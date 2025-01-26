import requests
import re
import os
API_BASE_URL = "https://api.tempmail.lol/v2"
headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36","x-requested-with": "XMLHttpRequest"}
payload = {"domain": "y1mv.underseagolf.com", "prefix": "Dboosts"}

class tempmail():

    def create_temp_email():
        url = f"{API_BASE_URL}/inbox/create"
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 201:  # HTTP Created
                data = response.json()
                email = data.get("address")
                token = data.get("token")
                return email, token
            else:
                return None, None
        except requests.RequestException as e:
            return None, None
    
    def check_inbox(token):
        url = f"{API_BASE_URL}/inbox"
        params = {"token": token}
    
        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
             return None 
        
            data = response.json()
            emails = data.get("emails", [])
        
            if not emails:
                return None  
            
            for email in emails:
                html_content = email.get("html", "")
                if html_content:
                    otp_match = re.search(r'(\d{8})', html_content)
                    if otp_match:
                        return otp_match.group(1) 
        
                    return None 
    
        except requests.RequestException:
            return None  
    
    


