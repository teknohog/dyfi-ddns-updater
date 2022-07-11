#!/usr/bin/python3
import random
import time
from subprocess import run
import argparse
import requests

parser = argparse.ArgumentParser(
    description="A program that updates the IP for a Dynamic DNS service.\
     The IP address of the machine running this script will be retrieved and used.\
     The IP is checked every 10 minutes. Example: \
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
# Dy.fi documentation deletes the IP if not updated in 7 days.
# 6 days in seconds
UPDATE_INTERVAL = 518400
CHECKIP_URL = "https://icanhazip.com"
dyndns_url = f"{args.ddns}{hostname}"
stored_ip = ""

def log(msg):
    run(f"echo '[{time.asctime()}]{str(msg)}' >> /var/log/dyfi.log", shell=True)

def fetch_content():
    resp = None
    try:
        resp = requests.get(CHECKIP_URL)
        print("current ip is=", resp.text)
    except requests.ConnectionError as e:
        log(f"[get_ip]: NewConnectionError. error: {e}")
        return False
    except Exception as e:
        log(f"[get_ip]: Unhandled exception. error: {e}")
        return False
    return resp.text

def get_ip():
    fail_count = 0
    result = fetch_content()
    while True:
        if result:
            if fail_count > 0:
                log(f"[get_ip]: Got IP after {fail_count} tries")
            return result
        fail_count += 1
        time.sleep(600)
        result = fetch_content()


def dns_update():
    # GET request to the ddns by running curl in a shell.
    run(f"curl -D - --user '{username}:{password}' '{dyndns_url}'", shell=True)
    # Logs each IP update to a file
    log(f"Updated IP: {stored_ip}")
    # run(f"echo '{username}:{password}' '{dyndns_url}'", shell=True)


def main():
    global stored_ip
    # +- 60 minutes
    refresh_limit = UPDATE_INTERVAL + random.randint(-3600, 3600)
    start_time = time.time()
    while True:
        ip = get_ip()
        if ip != stored_ip or (time.time() - start_time) > refresh_limit:
            stored_ip = ip
            dns_update()
            # Make a new random update limit
            refresh_limit = UPDATE_INTERVAL + random.randint(-3600, 3600)
            start_time = time.time()
        # Wait 10 minutes until next check
        time.sleep(600)


if __name__ == "__main__":
    main()
