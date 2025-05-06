import socket
import time
import threading
import requests
import subprocess
from concurrent.futures import ThreadPoolExecutor

INPUT_FILE = 'ip.txt'
OUTPUT_FILE = 'live_rdp_verified.txt'
PORT = 3389
TIMEOUT = 3

BOT_TOKEN = '7489463491:AAEM8-TBUkxRIINHWjjQj0Fkp9A7B5th5hg'
CHAT_ID = '5326706151'

RDP_HANDSHAKE = bytes.fromhex('030000130ee000000000000100080003000000')

def is_real_rdp(ip):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(TIMEOUT)
            s.connect((ip, PORT))
            s.sendall(RDP_HANDSHAKE)
            data = s.recv(16)
            return data and data.startswith(b'\x03\x00')
    except:
        return False

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
    if is_real_rdp(ip):
        print(f"[RDP] {ip} - checking if Windows...")
        if is_windows_rdp(ip):
            print(f"[WIN-RDP] {ip}")
            with open(OUTPUT_FILE, 'a+') as f:
                f.seek(0)
                if ip not in f.read():
                    f.write(ip + '\n')
        else:
            print(f"[XRDP/LINUX] {ip}")
    else:
        print(f"[NO RDP] {ip}")

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

    with ThreadPoolExecutor(max_workers=1500) as executor:
        executor.map(check_and_save, ips)

if __name__ == '__main__':
    main()
