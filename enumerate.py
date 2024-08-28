#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# Copyright (C) 2023 Niels Bijleveld

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import subprocess
import datetime
import sys
import termcolor
from colorama import init, Fore, Style

# Reset color to default after using.
init(autoreset=True)

if len(sys.argv) < 2:
    print("Usage: python example.py 192.168.1.1 192.168.1.10 ...")
    sys.exit(1)
try:
    ip_addresses = sys.argv[1:]
    if not isinstance(ip_addresses, list):
        print("Error: argument must be a list")
        sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
print("Received list of ip addresses:" + Fore.GREEN + f"{ip_addresses}")

# Define the individual IP addresses to scan
# ip_addresses = ["192.168.240.120", "192.168.240.121", "192.168.240.122"]
scanned_web_ports_for_ips = dict()

start_time = datetime.datetime.now()
print("\nScript elapsed time: " + Fore.GREEN +  f"{str(start_time)}\n")

# Create a directory for each IP address
for ip in ip_addresses:
    ip_dir = f"{ip}"
    os.makedirs(ip_dir, exist_ok=True)

    # Create files and folders inside the IP address directory
    open(f"{ip_dir}/hashes.txt", "w").close()
    open(f"{ip_dir}/passwords.txt", "w").close()
    open(f"{ip_dir}/users.txt", "w").close()
    open(f"{ip_dir}/creds.txt", "w").close()
    os.makedirs(f"{ip_dir}/vulns", exist_ok=True)
    os.makedirs(f"{ip_dir}/files", exist_ok=True)
    os.makedirs(f"{ip_dir}/scan_output", exist_ok=True) 

# Perform Nmap scan with verbose output
for ip in ip_addresses:
    nmap_scan = subprocess.run(["nmap", "-sV", "-sC", "-p-", "-r", "-Pn", "-T5", "-v", "--open", ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    nmap_output = nmap_scan.stdout.decode("utf-8")
    print(f"Nmap scan output for {ip}:")
    print(nmap_output)

    # Save Nmap output to a file
    nmap_output_file = f"{ip}/scan_output/nmap_{ip}.txt"
    with open(nmap_output_file, "w") as f:
        f.write(nmap_output)

# Proceed with the rest of the script
for ip in ip_addresses:
    # Get open web ports from Nmap output
    web_ports = []
    with open(f"{ip}/scan_output/nmap_{ip}.txt", "r") as f:
        nmap_output = f.read()
        for line in nmap_output.splitlines():
            if "open" in line:
                 if "http" in line or "https" in line:
                    port = line.split()[0].split("/")[0]
                    web_ports.append(port)

    removed_web_ports = list()
    # Perform web scans on open web ports
    for port in web_ports:
        # Perform WhatWeb scan with verbose output
        whatweb_scan = subprocess.run(["whatweb", f"http://{ip}:{port}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        whatweb_output = whatweb_scan.stdout.decode("utf-8")

        # Replace commas with newline characters
        whatweb_output = whatweb_output.replace(",", "\n")

        print(f"WhatWeb scan output for {ip}:{port}:")
        print(whatweb_output)

        # Save WhatWeb output to a file
        whatweb_output_file = f"{ip}/scan_output/whatweb_{ip}_{port}.txt"
        with open(whatweb_output_file, "w") as f:
            f.write(whatweb_output)

        # Check if the output contains "[200 OK]"
        if not "[200 OK]" in whatweb_output:
            removed_web_ports.append(port) 
    
    # Remove ports that not going to be used anymore
    web_ports = [x for x in web_ports if x not in removed_web_ports ]
    if web_ports:           # Skip empty ports
        scanned_web_ports_for_ips[ip] = web_ports

scanned_web_ports_for_ips = dict(sorted(scanned_web_ports_for_ips.items()))
print(Fore.WHITE + "Further scans will be done on: " + Fore.GREEN + f"{scanned_web_ports_for_ips}")


# Proceed with the directories scan
for ip, port_list in scanned_web_ports_for_ips.items():
    print(Fore.WHITE + "Dirb scan is started for: " + Fore.BLUE + f"{ip, port_list}" + Fore.WHITE)
    for port in port_list:
            
        # Perform Dirb scan with verbose output
        dirb_scan = subprocess.run(["dirb", f"http://{ip}:{port}", "-o", f"{ip}/scan_output/dirb_{ip}_{port}.txt"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        dirb_output = dirb_scan.stdout.decode("utf-8")
        print(f"Dirb scan output for {ip}:{port}:")
        print(dirb_output)

        # Save Dirb output to a file
        dirb_output_file = f"{ip}/scan_output/dirb_{ip}_{port}.txt"
        
        for line in dirb_output:
            # Check if Dirb output contains WordPress directories
            if "wp-admin" in line or "wp-content" in line or "wp-includes" in line:
                print(Fore.WHITE + "Wordpress founded. Starting a plug-in scan for: " + Fore.BLUE + f"{ip, port_list}" + Fore.WHITE)
                # Run WPScan with plugins detection and verbose output
                wpscan_scan = subprocess.run(["wpscan", "--url", f"http://{ip}:{port}", "--enumerate", "vp", "--plugins-detection", "aggressive"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                wpscan_output = wpscan_scan.stdout.decode("utf-8")
                print(f"WPScan output for {ip}:{port}:")
                print(wpscan_output)

                # Save WPScan output to a file
                wpscan_output_file = f"{ip}/scan_output/wpscan_{ip}_{port}.txt"
                with open(wpscan_output_file, "w") as f:
                    f.write(wpscan_output)
                break

for ip, port_list in scanned_web_ports_for_ips.items(): 
    print(Fore.WHITE + "Nikto scan is started for: " + Fore.BLUE + f"{ip, port_list}" + Fore.WHITE)
    for port in port_list:               
        # Perform Nikto scan
        nikto_scan = subprocess.run(["nikto", "--url", f"http://{ip}:{port}", "-C", "all"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        nikto_output = nikto_scan.stdout.decode("utf-8")
        output_file = f"{ip}/scan_output/nikto_{ip}_{port}.txt"
        
        with open(output_file, "w") as f:
            f.write(nikto_output)
        print(nikto_output)

end_time = datetime.datetime.now()

# Calculate the elapsed time
elapsed_time = end_time - start_time

print("\nScript elapsed time: " + Fore.BLUE +  f"{str(elapsed_time)}")
