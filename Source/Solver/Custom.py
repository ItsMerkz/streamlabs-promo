import requests
import json
import time
import datetime

def timestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def solve_turnstile(api_key, sitekey, url, api_base="http://localhost:8080"):
    try:
        # Step 1: Create a task
        body = {
            "api_key": api_key,
            "sitekey": sitekey,
            "url": url
        }
        response = requests.post(f"{api_base}/create_task", json=body)
        
        if response.status_code != 200:
            print("Failed to create task:", response.text)
            return None
        
        task_id = response.json().get('task_id')
        if not task_id:
            print("No task ID received.")
            return None
        
        
        # Step 2: Wait and get the result
        time.sleep(4)  # Wait for the task to be solved
        result_response = requests.get(f"{api_base}/get_result/{task_id}")
        
        if result_response.status_code != 200:
            print("Failed to get result:", result_response.text)
            return None
        
        token = result_response.json()['captcha_key']
        return token
    
    except Exception as e:
        print("An error occurred:", str(e))
        return None


def solve_CF_Clearance(api_key, url, api_base="http://localhost:8080"):
    try:
        solve_cf_response = requests.post(f"{api_base}/solve_cloudflare", json={
            "api_key": api_key,
            "url": url
        })
        
        if solve_cf_response.status_code != 200:
            print("Failed to solve Cloudflare:", solve_cf_response.text)
            return None
        
        print("Cloudflare solution:", solve_cf_response.text)
        return solve_cf_response.json()
    
    except Exception as e:
        print("An error occurred:", str(e))
        return None


