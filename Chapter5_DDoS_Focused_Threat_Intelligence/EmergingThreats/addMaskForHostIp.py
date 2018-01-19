#!/usr/bin/env python

# List from https://rules.emergingthreats.net/fwrules/emerging-Block-IPs.txt

with open('emerging-Block-IPs.txt', 'r') as inFile:
    with open('emerging-Block-IPs_new.txt', 'w') as outFile:
        for line in inFile.readlines():
            #prefix with subnet mask
            if "/" in line.strip():
                outFile.write(line.strip()+"\n")
            #host prefix adding /32
            elif line and line[0].isdigit():
                outFile.write(line.strip()+"/32\n")
            else: 
                outFile.write(line)


