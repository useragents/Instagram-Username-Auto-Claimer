try:
    import requests, os, threading, ctypes, time, platform
    from colorama import Fore
except ImportError:
    input("Error while importing modules. Please install the modules in requirements.txt")

ascii_text = """
        _           _        
       (_)         | |       
        _ _ __  ___| |_ __ _ 
       | | '_ \/ __| __/ _` |
       | | | | \__ \ || (_| |
       |_|_| |_|___/\__\__,_|"""

if platform.system() == "Windows":
    clear = "cls"
else:
    clear = "clear"


class Instagram:

    def __init__(self):
        self.url = "https://instagram.com"
        self.session = requests.Session()
        self.lock = threading.Lock()
        self.claiming = True
        self.proxy_errors = 0
        self.proxies = []
        self.attempts = 0
        self.retries = 0
        self.counter = 0

    def change_title(self):
        if clear == "cls":
            ctypes.windll.kernel32.SetConsoleTitleW(
                f"Instagram Auto Claimer | Attempts: {self.attempts} | Retries: {self.retries} | Proxy Errors: {self.proxy_errors} | Developed by @useragents on Github"
            )
    
    def safe_print(self, arg):
        self.lock.acquire()
        print(arg)
        self.lock.release()

    def print_console(self, arg):
        self.safe_print(f"\n       {Fore.WHITE}[{Fore.LIGHTMAGENTA_EX}Console{Fore.WHITE}] {arg}")
    
    def get_csrf_token(self):
        headers = {
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36",
            "Referer": "https://www.instagram.com/"
        }
        r = self.session.get(
            self.url + "/data/shared_data/",
            headers = headers
        )
        return r.json()["config"]["csrf_token"]

    def login(self, username: str, password: str):
        csrf_token = self.get_csrf_token()
        data = {
            "enc_password": "#PWD_INSTAGRAM_BROWSER:0:&:" + password,
            "username": username,
            "queryParams": {},
            "optIntoOneTap": False,
            "stopDeletionNonce": "",
            "trustedDeviceRecords": {}
        }
        headers = {
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "https://www.instagram.com/",
            "X-CSRFToken": csrf_token,
        }
        r = self.session.post(
            self.url + "/accounts/login/ajax/",
            headers = headers,
            data = data
        )
        if "userId" in r.text:
            user_id = r.json()["userId"]
            self.print_console(f"Successfully logged into @{username} ({user_id})")
            for cookie in r.cookies:
                if cookie.name == "csrftoken":
                    csrf_token = cookie.value
                    return csrf_token
        elif "spam" in r.text:
            if r.json()["spam"] == True:
                self.print_console(f"Login request considered as spam, try again later")
        elif "authenticated" in r.text:
            if r.json()["authenticated"] == False:
                self.print_console(f"Invalid credentials")
        else:
            print(r.text)
            input()
            os._exit(0)
    
    def get_email(self, csrf_token: str):
        headers = {
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36",
            "Referer": "https://www.instagram.com/",
            "X-CSRFToken": csrf_token,
        }
        r = self.session.get(
            self.url + "/accounts/edit/",
            headers = headers
        )
        email = r.text.split('"email":"')[1].split('"')[0]
        name = r.text.split('"first_name":"')[1].split('"')[0]
        return email, name
    
    def load_proxies(self):
        if not os.path.exists("proxies.txt"):
            self.print_console("File proxies.txt not found")
            time.sleep(10)
            os._exit(0)
        with open("proxies.txt", "r", encoding = "UTF-8") as f:
            for line in f.readlines():
                line = line.replace("\n", "")
                self.proxies.append(line)
            if not len(self.proxies):
                self.print_console("No proxies loaded in proxies.txt")
                time.sleep(10)
                os._exit(0)
    
    def claim_username(self, target, csrf_token, email_address, name, proxy):
        headers = {
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": csrf_token,
        }
        data = {
            "username": target,
            "email": email_address,
            "first_name": name,
        }
        try:
            r = self.session.post(
                self.url + "/accounts/edit/",
                headers = headers,
                data = data,
                proxies = {"https": "https://{}".format(proxy)}
            )
        except:
            self.proxy_errors += 1
            self.change_title()
            return
        if "status" in r.text:
            if r.json()["status"] == "fail":
                if "This username isn't available" in r.text:
                    self.attempts += 1
                elif "wait a few minutes" in r.text:
                    self.retries += 1
                else:
                    print(r.text)
            elif r.json()["status"] == "ok":
                self.print_console(f"Successfully claimed @{target}")
                self.claiming = False
            else:
                print(r.text)
        else:
            print(r.text)
        self.change_title()
    
    def main(self):
        os.system(clear)
        if clear == "cls":
            ctypes.windll.kernel32.SetConsoleTitleW("Instagram Auto Claimer | Developed by @useragents on Github")
        print(Fore.LIGHTMAGENTA_EX + ascii_text)
        self.load_proxies()
        username = str(input(f"\n       {Fore.WHITE}[{Fore.LIGHTMAGENTA_EX}Console{Fore.WHITE}] Username: @"))
        password = str(input(f"       {Fore.WHITE}[{Fore.LIGHTMAGENTA_EX}Console{Fore.WHITE}] Password: "))
        target = str(input(f"       {Fore.WHITE}[{Fore.LIGHTMAGENTA_EX}Console{Fore.WHITE}] Target: @"))
        threads = int(input(f"       {Fore.WHITE}[{Fore.LIGHTMAGENTA_EX}Console{Fore.WHITE}] Threads: "))
        csrf_token = self.login(username, password)
        email_address, name = self.get_email(csrf_token)
        
        def thread_starter():
            self.claim_username(target, csrf_token, email_address, name, self.proxies[self.counter])
        while self.claiming:
            if threading.active_count() <= threads:
                try:
                    threading.Thread(target = thread_starter).start()
                    self.counter += 1
                except:
                    pass
                if len(self.proxies) <= self.counter: #Loop through proxy list
                    self.counter = 0
            
        
obj = Instagram()
obj.main()
input()
