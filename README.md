# dyfi-ddns-updater

Client for updating the IP to your free hostname at https://dy.fi. Your network's IP is checked for changes every 2 minutes, or if it hasn't changed,
still do a request to dyfi after 6 days +-60 random minutes, so that your hostname doesn't get released.

Requires the `requests` pip package, and is only made to work on linux.

- `chmod +x dyfi_ddns_updater.py`
- Run `./dyfi_ddns_updater.py --help` for more information
- Example `dyfi_ddns_updater.py -u="user@example.com" -p="password" -n="example.dy.fi"`

## Run on system startup and in the background
It is easiest and reliable to create a systemctl service for the script.
Create `/lib/systemd/system/dyfi.service`

```bash
$ sudo nano /lib/systemd/system/dyfi.service
```
Paste these contents into the file, and change the ExecStart line to point to the script and supply it your dyfi information.
```
[Unit]
Description=Dyfi ddns update client
After=multi-user.target

[Service]
Type=idle
ExecStart=/absolute/path/to/dyfi_ddns_updater.py -u="user@example.com" -p="password" -n="example.dy.fi"

[Install]
WantedBy=multi-user.target
```
Reload systemctl and enable the service then reboot.
```
$ sudo systemctl daemon-reload
$ sudo systemctl enable dyfi.service

$ sudo reboot
```
Check the status and output with
```
$ sudo systemctl status dyfi
```

Each IP update/refresh is logged to `/var/log/dyfi.log`
