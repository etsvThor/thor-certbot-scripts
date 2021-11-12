#!/usr/bin/env python3

# Simple wrapper to create wildcard dns certificates using certbot and acme-dns
# CoCo - e.t.s.v. Thor

import subprocess
import argparse
from string import Template
from typing import List
import re

AUTHHOOK_PATH = "/etc/letsencrypt/acme-dns-auth.py"
CERTBOT_COMMAND_BASE = [
    "certbot",
    "certonly",
    "--manual",
    "--manual-auth-hook",
    AUTHHOOK_PATH,
    "--preferred-challenges",
    "dns",
    "--debug-challenges",
]

domain_pattern = re.compile(
    r"^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|"
    r"([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|"
    r"([a-zA-Z0-9][-_.a-zA-Z0-9]{0,61}[a-zA-Z0-9]))\."
    r"([a-zA-Z]{2,13}|[a-zA-Z0-9-]{2,30}.[a-zA-Z]{2,3})$"
)


def create_certbot_command(domain: str) -> List:
    if domain.startswith("*."):
        domain = domain[2:]
    command = CERTBOT_COMMAND_BASE + ["-d", domain, "-d", "*." + domain]
    return command


parser = argparse.ArgumentParser()
parser.add_argument("domain", type=str, help="Domain to be used")
args = parser.parse_args()

domain = args.domain

if not domain_pattern.match(domain):
    raise Exception("Invalid domain provided")


command = create_certbot_command(domain)

subprocess.call(command)
