import ipaddress
import multiprocessing

INPUT_FILE = 'ranges.txt'
OUTPUT_FILE = 'ip.txt'

def expand_cidr(cidr):
    try:
        return [str(ip) for ip in ipaddress.ip_network(cidr.strip(), strict=False)]
    except Exception:
        return []

def main():
    with open(INPUT_FILE, 'r') as f:
        cidrs = [line.strip() for line in f if line.strip()]

    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        results = pool.map(expand_cidr, cidrs)

    with open(OUTPUT_FILE, 'w') as out:
        for ip_list in results:
            out.write('\n'.join(ip_list) + '\n')

if __name__ == '__main__':
    main()
