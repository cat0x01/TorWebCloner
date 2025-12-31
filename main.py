import os
import re
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from colorama import Fore, init

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

init(autoreset=True)

os.system("sudo service tor start")

# =========================
# TOR PROXY
# =========================
proxies = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050"
}

visited = set()

# =========================
def banner():
    print(Fore.RED + "=" * 50)
    print(Fore.YELLOW + " TorSiteTool ")
    print(Fore.CYAN + " 1) Copy site")
    print(Fore.CYAN + " 2) Screenshot site")
    print(Fore.RED + "=" * 50)

# =========================
def clean_name(text):
    return re.sub(r"[^a-zA-Z0-9_.-]", "_", text)

# =========================
def save_file(url, content, folder):
    path = urlparse(url).path

    if path == "" or path.endswith("/"):
        path += "index.html"

    filename = clean_name(path.strip("/"))
    full_path = os.path.join(folder, filename)

    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    with open(full_path, "wb") as f:
        f.write(content)

    print(Fore.GREEN + f"[+] Saved: {full_path}")

# =========================
def copy_site(url, folder, depth=0, max_depth=2):
    if url in visited or depth > max_depth:
        return

    visited.add(url)

    try:
        r = requests.get(url, proxies=proxies, timeout=25)
    except Exception as e:
        print(Fore.RED + f"[!] Error: {e}")
        return

    save_file(url, r.content, folder)

    if "text/html" not in r.headers.get("Content-Type", ""):
        return

    soup = BeautifulSoup(r.text, "html.parser")

    for tag in soup.find_all(["a", "link", "script", "img"]):
        attr = "href" if tag.name in ["a", "link"] else "src"
        link = tag.get(attr)

        if not link:
            continue

        full_url = urljoin(url, link)

        if urlparse(full_url).netloc == urlparse(url).netloc:
            copy_site(full_url, folder, depth + 1)

# =========================
def screenshot_site(url):
    options = Options()
    options.headless = True

    # TOR SETTINGS
    options.set_preference("network.proxy.type", 1)
    options.set_preference("network.proxy.socks", "127.0.0.1")
    options.set_preference("network.proxy.socks_port", 9050)
    options.set_preference("network.proxy.socks_remote_dns", True)

    service = Service("/usr/bin/geckodriver")

    driver = webdriver.Firefox(service=service, options=options)
    driver.set_window_size(1366, 768)

    print(Fore.BLUE + "[i] Opening site via Tor...")
    driver.get(url)

    filename = clean_name(urlparse(url).netloc) + ".png"
    driver.save_screenshot(filename)

    print(Fore.GREEN + f"[✓] Screenshot saved: {filename}")
    driver.quit()

# =========================
def main():
    banner()

    choice = input(Fore.YELLOW + "Choose option (1/2): ").strip()
    target = input(Fore.YELLOW + "Enter .onion URL: ").strip()

    if not target.startswith("http"):
        target = "http://" + target

    if choice == "1":
        folder = clean_name(urlparse(target).netloc)
        print(Fore.BLUE + f"[i] Copying site to folder: {folder}")
        copy_site(target, folder)
        print(Fore.GREEN + "[✓] Copy finished")

    elif choice == "2":
        screenshot_site(target)

    else:
        print(Fore.RED + "[!] Invalid option")

# =========================
if __name__ == "__main__":
    main()
