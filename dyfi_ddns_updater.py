#!/usr/bin/python3
import random
import time
from subprocess import run
import argparse
import requests

parser = argparse.ArgumentParser(
    description="A program that updates the IP for a Dynamic DNS service.\
     The IP address of the machine running this script will be retrieved and used.\
     The IP is checked every 2 minutes. Example: \
         'dyfi_ddns_updater.py -u=\"user@example.com\" -p=\"password\" -n=\"example.dy.fi\"'"
)
parser.add_argument(
    "-u", "--username", type=str, help="Your account's username to the DDNS service"
)
parser.add_argument(
    "-p", "--password", type=str, help="Your account's password to the DDNS service"
)
parser.add_argument(
    "-n",
    "--hostname",
    type=str,
    help="Domain name you wish to update the IP address of. Example 'example.dy.fi'",
)
parser.add_argument(
    "-d",
    "--ddns",
    type=str,
    default="https://www.dy.fi/nic/update?hostname=",
    help="URL to the DDNS, including path to the update \
    resource and possible hostname query params",
)
args = parser.parse_args()

username = args.username
password = args.password
hostname = args.hostname
UPDATE_INTERVAL = 4380
CHECKIP_URL = "https://icanhazip.com"
dyndns_url = f"{args.ddns}{hostname}"
# Dy.fi documentation says it deletes the IP if not updated in 6-7 days.


def get_ip():
    resp = requests.get(CHECKIP_URL)
    return resp.text


def dns_update():
    run(f"curl -D - --user '{username}:{password}' '{dyndns_url}'", shell=True)
    run("date >> /var/log/dyfi.log", shell=True)
    # run(f"echo '{username}:{password}' '{dyndns_url}'", shell=True)


def main():
    randomized_interval = UPDATE_INTERVAL - random.randint(-60, 60)
    count = 1
    stored_ip = ""  # get_ip()
    while True:
        ip = get_ip()
        if ip != stored_ip or count > randomized_interval:
            stored_ip = ip
            dns_update()
            randomized_interval = UPDATE_INTERVAL - random.randint(-60, 60)
            count = 0

        time.sleep(120)
        count += 1


if __name__ == "__main__":
    main()
