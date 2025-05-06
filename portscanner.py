import socket
import time
import threading
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

INPUT_FILE = 'ip.txt'
OUTPUT_FILE = 'live_rdp_verified.txt'
PORT = 3389
TIMEOUT = 3

BOT_TOKEN = '7390307264:AAH9pZEC2i6xrOe67eOQi2i-4r3cIZVaA-k'
CHAT_ID = '5326706151'

RDP_HANDSHAKE = bytes.fromhex('030000130ee000000000000100080003000000')

sent_flag = False  # To prevent sending twice

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

def check_and_save(ip):
    if is_real_rdp(ip):
        print(f"[RDP] {ip}")
        with open(OUTPUT_FILE, 'a') as f:
            f.write(ip + '\n')
    else:
        print(f"[NO RDP] {ip}")

def send_file_to_telegram():
    global sent_flag
    if sent_flag:
        return
    sent_flag = True
    print("[!] Sending file to Telegram...")
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
    # Schedule a backup send
    threading.Thread(target=schedule_file_send, daemon=True).start()

    with open(INPUT_FILE, 'r') as f:
        ips = [line.strip() for line in f if line.strip()]

    with ThreadPoolExecutor(max_workers=1000) as executor:
        list(executor.map(check_and_save, ips))

    # Once scanning is done, send file if not already sent
    send_file_to_telegram()

if __name__ == '__main__':
    main()
