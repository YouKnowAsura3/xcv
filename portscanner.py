import socket
import time
import threading
import requests
from concurrent.futures import ThreadPoolExecutor

INPUT_FILE = 'ip.txt'
OUTPUT_FILE = 'live_rdp_verified.txt'
PORT = 3389
TIMEOUT = 3

BOT_TOKEN = '7489463491:AAEM8-TBUkxRIINHWjjQj0Fkp9A7B5th5hg'
CHAT_ID = '5326706151'

RDP_HANDSHAKE = bytes.fromhex('030000130ee000000000000100080003000000')

# Stats
total = 0
scanned = 0
good = 0
fail = 0

lock = threading.Lock()

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
    global scanned, good, fail
    if is_real_rdp(ip):
        with lock:
            good += 1
            with open(OUTPUT_FILE, 'a+') as f:
                f.seek(0)
                if ip not in f.read():
                    f.write(ip + '\n')
    else:
        with lock:
            fail += 1
    with lock:
        scanned += 1

def send_status_to_telegram():
    while True:
        time.sleep(120)  # Every 2 minutes
        with lock:
            msg = f"TOTAL : {total}\nSCANNED : {scanned}\nGOOD : {good}\nFAIL : {fail}"
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={
            'chat_id': CHAT_ID,
            'text': msg
        })

def main():
    global total
    with open(INPUT_FILE, 'r') as f:
        ips = [line.strip() for line in f if line.strip()]
    total = len(ips)

    threading.Thread(target=send_status_to_telegram, daemon=True).start()

    with ThreadPoolExecutor(max_workers=1000) as executor:
        executor.map(check_and_save, ips)

if __name__ == '__main__':
    main()
