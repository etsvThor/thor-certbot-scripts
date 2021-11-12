#!/usr/bin/env python3

# script to make web container proxy config for nginx with certbot.
# Jeroen van Oorschot 2016-2017
# CoCo - e.t.s.v. Thor

import sys
import subprocess
import argparse
from time import sleep
from shutil import which
from string import Template
from typing import List

print(
    """This file generates a config file for a proxy server for a container.
Next it enables a http server to let letsencrypt authenticate the domain.
Then a certificate is obtained and installed.
Finally the temporary server is deleted and the final config is placed.
The config uses a lot of includes from /etc/nginx/snippets"""
)

DEFAULT_BODY_SIZE = "1M"
WEBROOT = "/var/www/"
CERT_PATH = "/etc/letsencrypt/live/"
WEB_USER = "www-data"
SERVER_PATH = "/etc/nginx/"
TEMP_SERVER_NAME = SERVER_PATH + "sites-enabled/temp-letsencrypt"
NGINX_RELOAD_COMMAND = ["nginx", "-s", "reload"]


def run_command(command: List):
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    output, err = process.communicate()
    return process.returncode, output, err


def write_string_to_file(string: str, filename: str):
    file = open(filename, "w")
    file.write(string)
    file.flush()
    file.close()


def read_string_from_file(filename) -> str:
    text_file = open(filename, "r")
    data = text_file.read()
    text_file.close()
    return data


def prepare():
    """Checks if environment is correct"""
    if not which("nginx"):
        raise Exception("Nginx not installed")
    if not which("certbot"):
        raise Exception("certbot not installed")


def create_certbot_command(domains: List) -> List:
    command = ["certbot", "certonly", "-n", "--nginx"]
    for domain in domains:
        command += ["-d", str(domain)]
    return command


def create_vhost_proxy_config(
    domains: List, container_name: str, container_ip: str, body_size: str
) -> str:
    template = Template(read_string_from_file("vhost_proxy.conf.template"))
    vhost_conf = template.substitute(
        domains=", ".join(domains),
        main_domain=domains[0],
        body_size=body_size,
        container_name=container_name,
        container_ip=container_ip,
        WEBROOT=WEBROOT,
        CERT_PATH=CERT_PATH,
    )
    return vhost_conf


def good():
    q = str(input("Please check the output. Looking good? (y/n): ")).strip()
    if q != "y":
        sys.exit()


parser = argparse.ArgumentParser()
parser.add_argument("-domains", type=str, help="Domains to be used")
parser.add_argument("-container_name", type=str, help="Name of the proxy host")
parser.add_argument("-container_ip", type=str, help="ip of the proxy host")
parser.add_argument("-body_size", type=str, help="Max body size (default 3M)")

args = parser.parse_args()

# prepare()

###############
# Input reading#
###############

# container name
if args.container_name:
    container_name = args.container_name
else:
    container_name = str(input("Name of the web container: ")).strip()
if container_name[:3] != "web":
    print("Name should start with 'web'")
    q = input("Use this name anyway? (y/n)")
    if q != "y":
        sys.exit()

# container ip, allow only "10.x.x.x" addresses.
if args.container_ip:
    container_ip = args.container_ip
else:
    container_ip = str(input("IP address of container: ")).strip()
if container_ip.count(".") != 3 or len(container_ip) < 8 or container_ip[:3] != "10.":
    print("Invalid IP address supplied")
    sys.exit()

# max body size
if args.body_size:
    body_size = args.body_size
else:
    body_size = str(input("Max body size (e.g. 3M): ")).strip()
if len(body_size) > 4 or len(body_size) == 1:
    print("Invalid size supplied")
    sys.exit()

if len(body_size) == 0:
    print("Defaulting to " + DEFAULT_BODY_SIZE)
    body_size = DEFAULT_BODY_SIZE

# server_name
if args.domains:
    server_name = args.domains
else:
    server_name = str(input("Comma separated list of server names: ")).strip()
if len(server_name) == 0:
    print("Invalid server_name supplied")
    sys.exit()

server_name_list = list(map(str.strip, server_name.split(",")))
print("Domains parsed as:")
for server_name_single in server_name_list:
    print(server_name_single)
first_domain = server_name_list[0]

command = create_certbot_command(server_name_list)

exitcode, stdout, stderr = run_command(command)
print(stdout)
print(stderr)
if exitcode != 0:
    raise Exception(f"Certbot command failed: {command}")

print(
    """If certbot did not produce output, continue.\n
If certbot failed, exit the script and run nginx -s reload and
the above certbot command manually. Then rerun this script."""
)
good()

######################################
# Remove temp server and install final#
######################################
vhost_config = create_vhost_proxy_config(
    server_name_list, container_name, container_ip, body_size
)
filename = SERVER_PATH + "sites-available/" + container_name

write_string_to_file(vhost_config, filename)

subprocess.call(
    [
        "ln",
        "-s",
        "../sites-available/" + container_name,
        "/etc/nginx/sites-enabled/" + container_name,
    ]
)
subprocess.check_output(["nginx", "-t"])
good()
print("reloading nginx...")
subprocess.check_output(NGINX_RELOAD_COMMAND)
print("Everyting done!")
