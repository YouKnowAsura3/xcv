import ipaddress

input_file = 'ranges.txt'
output_file = 'ip.txt'

with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
    for line in infile:
        cidr = line.strip()
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            for ip in network.hosts():  # skips network and broadcast addresses
                outfile.write(str(ip) + '\n')
        except ValueError:
            print(f"Invalid CIDR: {cidr}")