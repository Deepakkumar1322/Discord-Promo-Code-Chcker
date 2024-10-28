import os
import aiohttp
import asyncio
from colorama import Fore, Style
import tasksio
import logging
import random
from dateutil import parser
import datetime
import requests
import sys
import pyfiglet
import json
import time
import colorsys

def load_configuration():
    with open('config.json') as config:
        return json.load(config)

config = load_configuration()
delay_time = config['delay']
log_filename = config['log_file']
max_concurrent_tasks = config['max_workers']

class Utility:
    @staticmethod
    def current_timestamp():
        return int(time.time() * 1000)

class ColorUtility:
    @staticmethod
    def from_hex(hex_code):
        return f"\033[38;2;{int(hex_code[1:3], 16)};{int(hex_code[3:5], 16)};{int(hex_code[5:], 16)}m"

    @staticmethod
    def from_rgb(r: int, g: int, b: int):
        return f"\033[38;2;{r};{g};{b}m"

    @staticmethod
    def from_hsl(h: int, s: int, l: int):
        r, g, b = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
        r, g, b = int(r * 255), int(g * 255), int(b * 255)
        return f"\033[38;2;{r};{g};{b}m"

    @staticmethod
    def apply_ansi(color: str, text: str):
        return f"\033[38;2;{color}m{text}\033[38;2;255;255;255m"

class Log:
    @staticmethod
    def success(message: str) -> None:
        print(f'{ColorUtility.from_hex("#FFFFFF")} [{ColorUtility.from_hex("#6c757d")} {Utility.current_timestamp()} {ColorUtility.from_hex("#FFFFFF")}] {ColorUtility.from_hex("#6c757d")}| {ColorUtility.from_hex("#29bf12")}SUC {ColorUtility.from_hex("#6c757d")}| {message}')

    @staticmethod
    def error(message: str) -> None:
        print(f'{ColorUtility.from_hex("#FFFFFF")} [{ColorUtility.from_hex("#6c757d")} {Utility.current_timestamp()} {ColorUtility.from_hex("#FFFFFF")}] {ColorUtility.from_hex("#6c757d")}| {ColorUtility.from_hex("#d00000")}ERR {ColorUtility.from_hex("#6c757d")}| {message}')

    @staticmethod
    def info(message: str) -> None:
        print(f'{ColorUtility.from_hex("#FFFFFF")} [{ColorUtility.from_hex("#6c757d")} {Utility.current_timestamp()} {ColorUtility.from_hex("#FFFFFF")}] {ColorUtility.from_hex("#6c757d")}| {ColorUtility.from_hex("#2a9d8f")}INF {ColorUtility.from_hex("#6c757d")}| {message}')

    @staticmethod
    def warning(message: str) -> None:
        print(f'{ColorUtility.from_hex("#FFFFFF")} [{ColorUtility.from_hex("#6c757d")} {Utility.current_timestamp()} {ColorUtility.from_hex("#FFFFFF")}] {ColorUtility.from_hex("#6c757d")}| {ColorUtility.from_hex("#ffea00")}WAR {ColorUtility.from_hex("#6c757d")}| {message}')

    @staticmethod
    def debug(message: str) -> None:
        print(f'{ColorUtility.from_hex("#FFFFFF")} [{ColorUtility.from_hex("#6c757d")} {Utility.current_timestamp()} {ColorUtility.from_hex("#FFFFFF")}] {ColorUtility.from_hex("#6c757d")}| {ColorUtility.from_hex("#ff7b00")}DBG {ColorUtility.from_hex("#6c757d")}| {message}')

class TokenHandler:
    def __init__(self, token_list):
        self.tokens = token_list
        self.index = 0

    def get_next_token(self):
        token = self.tokens[self.index]
        self.index = (self.index + 1) % len(self.tokens)
        return {"Authorization": token}

token_handler = TokenHandler(config['tokens'])
auth_header = token_handler.get_next_token()

# Track counts
total_checked = 0
valid_codes_count = 0
currently_checking = 0

def clear_console():
    os.system("clear||cls")

def set_title(title):
    os.system(f'title "{title}"')  # Updated to wrap title in quotes


banner = pyfiglet.figlet_format("LGN")

response = requests.get("https://ptb.discord.com/api/v10/users/@me", headers=auth_header)
if response.status_code not in [201, 204, 200]:
    Log.error("Invalid Token.")
    sys.exit()

def is_duplicate(file, item):
    with open(file, "r") as f:
        items = f.read().split("\n")
        try:
            items.remove("")
        except:
            pass
    return item in items

def save_to_file(file, data):
    with open(file, "a+") as f:
        if not is_duplicate(file, data):
            f.write(data + "\n")
        else:
            Log.error(f"Duplicate Found -> {data}")

def update_title():
    title = f"Checked: {total_checked} | Valid Codes: {valid_codes_count} | Currently Checking: {currently_checking}"
    set_title(title)

async def validate_promo_code(promo_code):
    global auth_header, total_checked, valid_codes_count, currently_checking
    currently_checking += 1
    update_title()  # Update title before checking

    async with aiohttp.ClientSession(headers=auth_header) as session:
        async with session.get(f"https://ptb.discord.com/api/v10/entitlements/gift-codes/{promo_code}") as response:
            total_checked += 1
            currently_checking -= 1
            update_title()  # Update title after checking
            
            if response.status in [200, 204, 201]:
                data = await response.json()
                if data["uses"] == data["max_uses"]:
                    Log.debug(f"Already Claimed -> {promo_code}")
                    save_to_file("claimed.txt", f"https://discord.com/billing/promotions/{promo_code}")
                else:
                    try:
                        now = datetime.datetime.utcnow()
                        expiration = data["expires_at"].split(".")[0]
                        parsed_date = parser.parse(expiration)
                        days_left = abs((now - parsed_date).days)
                        promo_title = data["promotion"]["inbound_header_text"]
                    except Exception as e:
                        Log.error(f"Error parsing promo code: {promo_code}, Error: {e}")
                        expiration = "Failed To Fetch!"
                        days_left = "Failed To Parse!"
                        promo_title = "Failed To Fetch!"
                        
                    valid_codes_count += 1  # Increment valid codes count
                    Log.success(f"Valid promo code: {promo_code[:8]}, Days Left: {days_left}, Title: {promo_title}")
                    save_to_file("valid.txt", f"https://discord.com/billing/promotions/{promo_code}")
            elif response.status == 429:
                try:
                    data = await response.json()
                    retry_after = data["retry_after"]
                    Log.warning(f"Rate Limited For {retry_after} Seconds!")
                    await asyncio.sleep(retry_after)
                    auth_header = token_handler.get_next_token()  
                    await validate_promo_code(promo_code)  
                except Exception as e:
                    Log.error(f"IP Banned or unexpected error: {e}")
            else:
                Log.error(f"Invalid Code -> {promo_code}")
                Log.error(f"Invalid promo code: {promo_code}")

async def main():
    with open("promotions.txt", "r") as file:
        promo_codes = file.read().split("\n")
    try:
        promo_codes.remove("")
    except:
        pass
    async with tasksio.TaskPool(workers=max_concurrent_tasks) as pool:
        for promo in promo_codes:
            code = promo.replace('https://discord.com/billing/promotions/', '').replace('https://promos.discord.gg/', '').replace('/', '')
            await pool.put(validate_promo_code(code))
            await asyncio.sleep(delay_time)

if __name__ == "__main__":
    event_loop = asyncio.new_event_loop()
    event_loop.run_until_complete(main())
