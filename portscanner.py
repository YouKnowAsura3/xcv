import time
import threading
import requests
import subprocess
import os
from concurrent.futures import ThreadPoolExecutor

INPUT_FILE = 'ip.txt'
OUTPUT_FILE = 'live_rdp_verified.txt'
BOT_TOKEN = '7691507387:AAEl81yaGi3Te1KOqOtBqPahu_fjzXljQs4'
CHAT_ID = '5326706151'

lock = threading.Lock()
total_ips = 0
scanned = 0
good = 0
bad = 0

def is_windows_rdp(ip):
    try:
        result = subprocess.run(
            ['nmap', '-p', '3389', '--script', 'rdp-ntlm-info', '-Pn', ip],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=15
        )
        output = result.stdout.decode()
        return "Product: Windows" in output
    except:
        return False

def check_and_save(ip):
    global scanned, good, bad
    os.system(f'echo "[SCAN] {ip} - checking if Windows RDP..."')
    if is_windows_rdp(ip):
        os.system(f'echo "[WIN-RDP] {ip}"')
        with lock:
            with open(OUTPUT_FILE, 'a+') as f:
                f.seek(0)
                if ip not in f.read():
                    f.write(ip + '\n')
            good += 1
    else:
        os.system(f'echo "[NOT Windows] {ip}"')
        with lock:
            bad += 1
    with lock:
        scanned += 1

def send_status_update():
    while True:
        time.sleep(120)
        with lock:
            message = f"SCANNED: {scanned}\nGOOD: {good}\nBAD: {bad}\nTOTAL: {total_ips}"
        requests.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
            data={'chat_id': CHAT_ID, 'text': message}
        )

def send_file_to_telegram():
    time.sleep(3 * 3600 + 15 * 60)
    os.system('echo "[!] 3h15m reached. Sending file to Telegram..."')
    try:
        with open(OUTPUT_FILE, 'rb') as file:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
                data={'chat_id': CHAT_ID},
                files={'document': file}
            )
        os.system('echo "[+] File sent to Telegram."')
    except Exception as e:
        os.system(f'echo "[!] Failed to send file: {e}"')

def main():
    global total_ips
    threading.Thread(target=send_file_to_telegram, daemon=True).start()
    threading.Thread(target=send_status_update, daemon=True).start()

    with open(INPUT_FILE, 'r') as f:
        ips = [line.strip() for line in f if line.strip()]
    total_ips = len(ips)

    with ThreadPoolExecutor(max_workers=100) as executor:
        executor.map(check_and_save, ips)

if __name__ == '__main__':
    main()
