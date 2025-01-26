import requests
import json
import tls_client 
from bs4 import BeautifulSoup
import requests
import re
from urllib.parse import unquote
import threading
from threading import Lock
import string, random
from colorama import *
from Source.Linker.Linker import *
from Source.Solver.Custom import *
from Source.Emails.TempMail import *
from Source.Utils.Utils import *


with open('config.json', 'r') as config_file:
    config = json.load(config_file)

prxy = config['Proxy']['Proxy']
screpy_key = config['Setting']['scrappey_key']


                
captcha_solved_count = 0
promo_gen_count = 0
counter_lock = threading.Lock()
lock = Lock()
client = tls_client.Session(client_identifier='chrome_120', random_tls_extension_order=True)


class Streamlabs:
    def __init__(self):
        self.client = tls_client.Session(client_identifier='chrome_120', random_tls_extension_order=True)
        self.email, self.token = tempmail.create_temp_email()
        print(f"{timestamp()} | {Fore.LIGHTBLUE_EX}EMAIL{Fore.RESET}   | Attempting To Buy Email [{Fore.LIGHTBLUE_EX}Email{Fore.RESET}: {self.email}]")
        eight_digit_password_with_uppercase_lowercase_and_digits_and_special = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=8))
        self.password = eight_digit_password_with_uppercase_lowercase_and_digits_and_special    
        self.client.proxies = {
            'http': prxy,
            'https': prxy
        }
    
    def get_xsrf_token_from_cookies(self):
        url = "https://streamlabs.com/slid/signup"
        self.client.get(url)
        
        xsrf_token = self.client.cookies.get('XSRF-TOKEN')
        cookies = self.client.cookies.get_dict()

        if xsrf_token:
            xsrf_token = xsrf_token.replace('%3D', '=')

            cookie_header = "; ".join([f"{key}={value}" for key, value in cookies.items()])
            
            request_cookies = {key: value for key, value in cookies.items()}
            
            return xsrf_token, cookie_header, request_cookies
        else:
            raise ValueError("XSRF token not found in cookies")


    def solve_turnstile(self):
        api_key = "Turnstile-Solverrrrrrr"
        sitekey = "0x4AAAAAAACELUBpqiwktdQ9"
        url = "https://streamlabs.com/slid/signup"
        captcha_token = solve_turnstile(api_key, sitekey, url)
        return captcha_token

    def register(self):
        tokenn, cookie_header, self.request_cokkkies = self.get_xsrf_token_from_cookies()
        headers = {
            'accept'            : 'application/json, text/plain, */*',
            'accept-language'   : 'en-US,en;q=0.9',
            'cache-control'     : 'no-cache',
            'client-id'         : '419049641753968640',
            'content-type'      : 'application/json',
            'origin'            : 'https://streamlabs.com',
            'pragma'            : 'no-cache',
            'priority'          : 'u=1, i',
            'referer'           : 'https://streamlabs.com/',
            'sec-ch-ua'         : '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile'  : '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest'    : 'empty',
            'sec-fetch-mode'    : 'cors',
            'sec-fetch-site'    : 'same-site',
            'user-agent'        : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'x-xsrf-token'      :  tokenn,
        }
        
        try:
            tturnstile = self.solve_turnstile()
        except Exception as e:
            return False

        json_data = {
            'email': self.email,
            'username': '',
            'password': 'DboostsGen@6969',
            'agree': True,
            'agreePromotional': True,
            'dob': '',
            'captcha_token': tturnstile,
            'locale': 'en-US',
    }
        for i in range(5):
            try:
                res = self.client.post('https://api-id.streamlabs.com/v1/auth/register', headers=headers, json=json_data)
                if res.status_code == 200:
                    print(f"{timestamp()} | {Fore.GREEN}SUCCESS{Fore.RESET} | Successfully Created Streamlabs Account [{Fore.GREEN}Email{Fore.RESET}: {self.email}]")
                break
            except:
                continue

        

        otp_verified = False
        while not otp_verified:
            otp = tempmail.check_inbox(self.token)

            if otp:
                print(f"{timestamp()} | {Fore.YELLOW}WARNING{Fore.RESET} | Verifying OTP... [{Fore.YELLOW}Code{Fore.RESET}: {otp}]")
                otp_verified = True
                break
            
        eVerify = f'https://api-id.streamlabs.com/v1/users/@me/email/verification/confirm'
        data = {"code":otp,"email":self.email,"tfa_code":""}
        print(f"{timestamp()} | {Fore.LIGHTBLUE_EX}EMAIL{Fore.RESET}   | Verifying OTP To Account [{Fore.LIGHTBLUE_EX}Code{Fore.RESET}: {otp}]")
        for i in range(5):
            try:
                res = self.client.post(eVerify, headers=headers, json=data)
                break
            except:
                continue
        
        if res.status_code != 204:
            print(f"{timestamp()} | {Fore.RED}ERROR{Fore.RESET}   | Failed To Verify OTP.")
            return False
        
        print(f"{timestamp()} | {Fore.GREEN}SUCCESS{Fore.RESET} | Successfully Verified Streamlabs Account [{Fore.GREEN}Email{Fore.RESET}: {self.email}]")
        with open(f'accounts.txt','a') as f:
            f.write(f'{self.email}:DboostsGen@6969\n')
            
        self.client.headers = {
            'accept'            : 'application/json, text/plain, */*',
            'accept-language'   : 'en-US,en;q=0.9',
            'cache-control'     : 'no-cache',
            'client-id'         : '419049641753968640',
            'content-type'      : 'application/json',
            'origin'            : 'https://streamlabs.com',
            'pragma'            : 'no-cache',
            'priority'          : 'u=1, i',
            'referer'           : 'https://streamlabs.com/',
            'sec-ch-ua'         : '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile'  : '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest'    : 'empty',
            'sec-fetch-mode'    : 'cors',
            'sec-fetch-site'    : 'same-site',
            'user-agent'        : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'x-xsrf-token'      :  tokenn,
        }
        try:
            csrf = self.csrf(tokenn)
        except Exception as e:
            return False
        
        if csrf:
            twitter_token = self.get_twitter_token()
            if twitter_token:
                merge = self.merge(csrf=csrf, twitter_token=twitter_token)
                if merge:
                    print(f"{timestamp()} | {Fore.GREEN}SUCCESS{Fore.RESET} | Twitter account successfully linked [{Fore.GREEN}Token{Fore.RESET}: {twitter_token}]")
                    cookies = self.client.cookies
                    formatted_cookies = "; ".join([f"{cookie.name}={cookie.value}" for cookie in cookies])
                    promo = self.puller(formatted_cookies)

                else:
                    print(f"{timestamp()} | {Fore.RED}ERROR{Fore.RESET}   | Failed to merge accounts")
                    return False
                        
            else:
                print(f"{timestamp()} | {Fore.RED}ERROR{Fore.RESET}   | Failed to get Twitter token")
                return False
        else:
            print(f"{timestamp()} | {Fore.RED}ERROR{Fore.RESET}   | Failed to get CSRF token")
            return False
                

    def csrf(self, xsrf):
        url = "https://api-id.streamlabs.com/v1/identity/clients/419049641753968640/oauth2"
        payload = {
            "origin": "https://streamlabs.com",
            "intent": "connect",
            "state": ""
        }
        headers = {
            "X-XSRF-Token": xsrf,
            "Content-Type": "application/json"
        }
        

        response = self.client.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            data = response.json()
            redirect_url = data.get("redirect_url")
            
            if redirect_url:
                while redirect_url:
                    redirect_response = self.client.get(redirect_url, allow_redirects=False)
                    
                    self.client.cookies.update(redirect_response.cookies)
                
                    if redirect_response.status_code in (301, 302) and 'Location' in redirect_response.headers:
                        redirect_url = redirect_response.headers['Location']
                    else:
                        match = re.search(r"var\s+redirectUrl\s*=\s*'(.*?)';", redirect_response.text)
                        if match:
                            redirect_url = match.group(1)
                            red4 = self.client.get(redirect_url)
                            self.client.cookies.update(red4.cookies)
                            red5 = self.client.get("https://streamlabs.com/dashboard")
                            self.client.cookies.update(red5.cookies)
                            soup = BeautifulSoup(red5.text, "html.parser")
                            csrf = soup.find("meta", {"name": "csrf-token"})["content"]
                            return csrf

            else:
                print(f"{timestamp()} | {Fore.RED}ERROR{Fore.RESET}   | Redirect URL Not Found")
                return None
        else:
            print(f"{timestamp()} | {Fore.RED}ERROR{Fore.RESET}   | Request Failed [{Fore.RED}Error{Fore.RESET}: {response.text}]")
            return None
        
    def get_twitter_token(self):
        try:
            with open('data/tokens.txt', 'r') as f:
                tokens = f.readlines()
            if not tokens:
                print(f"{timestamp()} | {Fore.RED}ERROR{Fore.RESET}   | No Twitter Tokens Found In data/Tokens.txt")
                return None
            token = tokens[0].strip()
            if ':' in token:
                token = token.split(':')[-1]
            with open('data/tokens.txt', 'w') as f:
                f.writelines(tokens[1:])
            return token
        except FileNotFoundError:
            print(f"{timestamp()} | {Fore.RED}ERROR{Fore.RESET}   | data/Tokens.txt Not Found")
            return None


    def merge(self,csrf,twitter_token: str) -> bool:
        try:
            response = self.client.get(
                    "https://streamlabs.com/api/v5/user/accounts/merge/twitter_account",
                    params={"r": "/dashboard#/settings/account-settings/platforms"}
                )
                
            if response.status_code != 200:
                print(f"{timestamp()} | {Fore.RED}ERROR{Fore.RESET}   | Failed To Get OAuth URL")
                return False
                    
            oauth_url = response.json().get('redirect_url')
            oauth_token = oauth_url.split("oauth_token=")[1]

            session = tls_client.Session('chrome_131', random_tls_extension_order=True)

            auth_response = session.get(
                    oauth_url, 
                    headers={'cookie': f"auth_token={twitter_token};"}
                )
                
            try:
                authenticity_token = auth_response.text.split(' <input name="authenticity_token" type="hidden" value="')[1].split('">')[0]
            except IndexError:
                twitter_tokenn = self.get_twitter_token()
                print(f"{timestamp()} | {Fore.RED}ERROR{Fore.RESET}   | Invaild Twitter Account Retrying")
                remove_content(filename='data/tokens.txt', delete_line=twitter_token)
                return self.merge(csrf, twitter_tokenn)
                
            auth_data = {
                    'authenticity_token': authenticity_token,
                    'oauth_token': oauth_token
                }
                
            final_response = session.post('https://x.com/oauth/authorize', data=auth_data, headers={'cookie': f"auth_token={twitter_token};"})
            try:
                redirect_url = final_response.text.split('<p>If your browser doesn\'t redirect you please <a class="maintain-context" href="')[1].split('">')[0]
                    
                if redirect_url:
                    if 'You are being' in redirect_url:
                        print("Twitter account already used.")
                        
                        return False
                    session.headers.update({'referer': "https://twitter.com"})
                    response = self.client.get(unquote(redirect_url).replace("amp;", '').replace("amp;", ''))
                    if response.status_code == 302:
                        return True
                    else:
                        remove_content(filename='data/tokens.txt', delete_line=twitter_token)
                        print(f"Failed to link Twitter account: {response.status_code}")
                else:
                    remove_content(filename='data/tokens.txt', delete_line=twitter_token)
                    print("Failed to find redirect URL")
                    
                return False
            except IndexError:
                remove_content(filename='data/tokens.txt', delete_line=twitter_token)
                twitter_tokenn = self.get_twitter_token()
                print(f"{timestamp()} | {Fore.RED}ERROR{Fore.RESET}   | Failed To Extract Redirect URL Retrying")
                return self.merge(csrf, twitter_tokenn)
                    
        except Exception as e:
            print(f"{timestamp()} | {Fore.RED}ERROR{Fore.RESET}   | Failed to Link Twitter Account [{Fore.RED}Error{Fore.RESET}: {e}]")
            return False
    
    
    def puller(self, cookiesx):

        headers = {
        'Content-Type': 'application/json',
        }

        params = {
        'key': screpy_key,
        }

        json_data = {
            'cmd': 'request.get',
            'url': 'https://streamlabs.com/discord/nitro',
            'mobileProxy': True,
            'browser': [{'name': 'chrome'}],
            'noDriver': True,
            'cookies': cookiesx,
            'proxy': prxy,
        }
        response = requests.post('https://publisher.scrappey.com/api/v1', params=params, headers=headers, json=json_data)
        response.raise_for_status()  
        data = response.json()

        promo = data['solution']['currentUrl']
        if 'https://discord.com/billing/partner-promotions/' not in promo:
            print(f"{timestamp()} | {Fore.RED}ERROR{Fore.RESET}   | Failed to Link Twitter Account [{Fore.RED}Error{Fore.RESET}: {promo}]")
            return None
        with open("data/Output/Promos.txt","a")as f:
            f.write(f"{promo}\n")
        print(f"{timestamp()} | {Fore.GREEN}SUCCESS{Fore.RESET} | Successfully Gathed Promotion [{Fore.GREEN}Promotion{Fore.RESET}: {promo[:130]}...]")
        processTokens()
        global promo_gen_count
        with counter_lock:
            promo_gen_count += 1
        return promo