import time
import threading
import requests
import subprocess
from concurrent.futures import ThreadPoolExecutor

INPUT_FILE = 'ip.txt'
OUTPUT_FILE = 'live_rdp_verified.txt'
BOT_TOKEN = '7691507387:AAEl81yaGi3Te1KOqOtBqPahu_fjzXljQs4'
CHAT_ID = '5326706151'

lock = threading.Lock()
total_ips = 0
scanned = 0
good = 0

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
    global scanned, good
    subprocess.run(['echo', f'[SCAN] {ip} - checking if Windows RDP...'])
    if is_windows_rdp(ip):
        subprocess.run(['echo', f'[WIN-RDP] {ip}'])
        with lock:
            with open(OUTPUT_FILE, 'a+') as f:
                f.seek(0)
                if ip not in f.read():
                    f.write(ip + '\n')
                    good += 1
    else:
        subprocess.run(['echo', f'[NOT Windows] {ip}'])
    with lock:
        scanned += 1

def status_updater():
    while True:
        time.sleep(120)
        with lock:
            bad = scanned - good
            subprocess.run(['echo', f'SCANNED : {scanned}'])
            subprocess.run(['echo', f'GOOD    : {good}'])
            subprocess.run(['echo', f'BAD     : {bad}'])
            subprocess.run(['echo', f'TOTAL   : {total_ips}'])

def send_file_to_telegram():
    subprocess.run(['echo', '[!] 3h15m reached. Sending file to Telegram...'])
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        with open(OUTPUT_FILE, 'rb') as file:
            requests.post(url, data={'chat_id': CHAT_ID}, files={'document': file})
        subprocess.run(['echo', '[+] File sent to Telegram.'])
    except Exception as e:
        subprocess.run(['echo', f'[!] Failed to send file: {e}'])

def schedule_file_send():
    time.sleep(3 * 3600 + 15 * 60)
    send_file_to_telegram()

def main():
    global total_ips
    threading.Thread(target=schedule_file_send, daemon=True).start()
    threading.Thread(target=status_updater, daemon=True).start()

    with open(INPUT_FILE, 'r') as f:
        ips = [line.strip() for line in f if line.strip()]
        total_ips = len(ips)

    with ThreadPoolExecutor(max_workers=100) as executor:
        executor.map(check_and_save, ips)

if __name__ == '__main__':
    main()
