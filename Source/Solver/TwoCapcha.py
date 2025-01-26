from twocaptcha import TwoCaptcha
from Source.Utils.Config import *
import json
import datetime
from colorama import *


solver = TwoCaptcha(api_key)

def timestamp():
        return datetime.datetime.now().strftime("%H:%M:%S") 

def twocaptchasolver():
    print(f"{timestamp()} | {Fore.YELLOW}CAPCHA{Fore.RESET}  | Captcha Detected Solving [{Fore.YELLOW}Capcha{Fore.RESET}: Turnstile] [{Fore.YELLOW}Solver{Fore.RESET}: TwoCaptcha]\n")
    captcha_token = solver.turnstile(
        sitekey='0x4AAAAAAACELUBpqiwktdQ9',
        url='https://streamlabs.com/slid/signup',
        userAgent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',

    )
    token = captcha_token['code']
    print(f"{timestamp()} | {Fore.GREEN}SUCCESS{Fore.RESET} | Successfully Solved Captcha [{Fore.GREEN}Solution{Fore.RESET}: {token[:45]}...]")
    return token



