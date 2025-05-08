import time
import threading
import requests
import subprocess
from concurrent.futures import ThreadPoolExecutor

INPUT_FILE = 'ip.txt'
OUTPUT_FILE = 'live_rdp_verified.txt'
BOT_TOKEN = '7390307264:AAH9pZEC2i6xrOe67eOQi2i-4r3cIZVaA-k'
CHAT_ID = '5326706151'

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
    print(f"[SCAN] {ip} - checking if Windows RDP...")
    if is_windows_rdp(ip):
        print(f"[WIN-RDP] {ip}")
        with open(OUTPUT_FILE, 'a+') as f:
            f.seek(0)
            if ip not in f.read():
                f.write(ip + '\n')
    else:
        print(f"[NOT Windows] {ip}")

def send_file_to_telegram():
    print("[!] 3h15m reached. Sending file to Telegram...")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        with open(OUTPUT_FILE, 'rb') as file:
            requests.post(url, data={'chat_id': CHAT_ID}, files={'document': file})
        print("[+] File sent to Telegram.")
    except Exception as e:
        print(f"[!] Failed to send file: {e}")

def schedule_file_send():
    time.sleep(3 * 3600 + 15 * 60)
    send_file_to_telegram()

def main():
    threading.Thread(target=schedule_file_send, daemon=True).start()

    with open(INPUT_FILE, 'r') as f:
        ips = [line.strip() for line in f if line.strip()]

    with ThreadPoolExecutor(max_workers=100) as executor:
        executor.map(check_and_save, ips)

if __name__ == '__main__':
    main()
