import ipaddress

def ip_range_to_list(start_ip, end_ip):
    start = int(ipaddress.IPv4Address(start_ip))
    end = int(ipaddress.IPv4Address(end_ip))
    return [str(ipaddress.IPv4Address(ip)) for ip in range(start, end + 1)]

input_file = 'ranges.txt'
output_file = 'ip.txt'

with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
    for line in infile:
        parts = line.strip().split(',')
        if len(parts) >= 2:
            start_ip, end_ip = parts[0], parts[1]
            for ip in ip_range_to_list(start_ip, end_ip):
                outfile.write(ip + '\n')