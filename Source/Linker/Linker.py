import os
import datetime
from itertools import cycle
import requests
from colorama import Fore
import json
import ctypes
from Source.Utils.Utils import *
import time



retrieved = 0
failed = 0
error = 0
threeMonths = 0
oneMonth = 0

output_folder = f"Output/{time.strftime('%Y-%m-%d %H-%M-%S')}"
outputTokens = os.path.join(output_folder, "Tokens.txt")
outputPromos = os.path.join(output_folder, "Promos.txt")

def folderExithm(folder_path):
    os.makedirs(folder_path, exist_ok=True)

def fileExithm(file_path):
    if not os.path.exists(file_path):
        open(file_path, 'w').close()

def clearOutput(folder_path):
    if os.path.exists(folder_path):
        for file in os.listdir(folder_path):
            os.remove(os.path.join(folder_path, file))

def loadLines(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return [line.strip() for line in file.readlines() if line.strip()]
    return []

def writeFile(file_path, content):
    fileExithm(file_path)
    with open(file_path, 'a') as file:
        file.write(content + '\n')

def update_file(file_path, lines):
    with open(file_path, 'w') as file:
        file.writelines(line + '\n' for line in lines)

def time_right_now():
    return datetime.now().strftime("%I:%M %p")

def timestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def processTokens():
    global retrieved, failed, error, oneMonth, threeMonths

    folderExithm(output_folder)

    fileExithm(outputTokens)
    fileExithm(outputPromos)


    tokens = loadLines("data/Discord/Tokens.txt")
    proxies = loadLines("data/Discord/Proxies.txt")
    promos = loadLines("data/Output/Promos.txt")
    proxy_pool = cycle(proxies)

    for token_line in tokens[:]:
        token = token_line.split(":")[-1]
        proxy = {"http": f"http://{next(proxy_pool)}"} if proxies else None

        for full_promo in promos[:]:
            try:
                promo_id, promo_jwt = full_promo.split('/')[5:7]
                promo_url = f"https://discord.com/api/v9/entitlements/partner-promotions/{promo_id}"
                headers = {
                    "authorization": token,
                    'accept': '*/*',
                    'accept-language': 'en-US,en;q=0.9',
                    'content-type': 'application/json',
                    'origin': 'https://discord.com',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                }

                response = requests.post(promo_url, headers=headers, json={"jwt": promo_jwt}, proxies=proxy)

                if response.status_code == 200:
                    promo_data = response.json()
                    promo_redemption_id = promo_data.get("code")

                    if promo_redemption_id:
                        if promo_id == "1310745123109339258":
                            checkPromoType = f"3 Months"
                            threeMonths += 1
                        elif promo_id == "1310745070936391821":
                            checkPromoType = f"1 Month"
                            oneMonth += 1
                        else:
                            checkPromoType = f"{Fore.LIGHTRED_EX}Unknown{Fore.RESET}"
                        print(f"{timestamp()} | {Fore.GREEN}SUCCESS{Fore.RESET} | Successfully Linked To Token [{Fore.GREEN}Type{Fore.RESET}: {checkPromoType}]")
                        writeFile(outputPromos, f"https://promos.discord.gg/{promo_redemption_id}")
                        writeFile(outputTokens, token_line)
        

                        retrieved += 1
                        promos.remove(full_promo)
                        tokens.remove(token_line)

                        update_file("data/Output/Promos.txt", promos)
                        update_file("data/Discord/Tokens.txt", tokens)

                        break
                else:
                    print(f"{timestamp()} | {Fore.RESET}{Fore.LIGHTRED_EX}ERROR{Fore.RESET} | Failed to retrieve promo {Fore.LIGHTWHITE_EX}[Error: {Fore.RESET}{Fore.LIGHTRED_EX}{response.text}{Fore.RESET}{Fore.LIGHTWHITE_EX}]{Fore.RESET}")
                    promos.remove(full_promo)
                    tokens.remove(token_line)
                    failed += 1

                    update_file("data/Output/Promos.txt", promos)
                    update_file("data/Discord/Tokens.txt", tokens)

            except Exception as e:
                error += 1


