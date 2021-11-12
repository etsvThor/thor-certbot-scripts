#!/usr/bin/env python

# script to list server names in format for certbot from nginx server.
# Jeroen van Oorschot 2016-2017
# CoCo - e.t.s.v. Thor

# To add a extra domain to an existing cert, add the domain to the server names
# in /etc/nginx/sites_enabled/<name> and reload nginx
# Then just rerun certbot with the old AND new domains with the '-d' flag.
# Get these names directly by running this script.

import sys

# container name
name = str(raw_input("Name of the web container: ")).strip()
if name[:3] != "web":
    print("Name should start with 'web'")
    q = raw_input("Use this name anyway? (y/n)")
    if q != "y":
        sys.exit()

path = "/etc/nginx/sites-available/" + name

file = open(path, "r")
txt = file.read()
a = txt.find("server_name") + 11
b = txt.find(";", a)
snames = txt[a:b]
snames = snames.split()
domains = []
for sname in snames:
    domains.append("-d")
    domains.append(sname)

print(" ".join(domains))
