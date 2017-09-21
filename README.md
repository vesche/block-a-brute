# block-a-brute

This is a command-line tool for blocking IP addresses conducting SSH bruteforce attempts. It uses `auth.log` to find SSH login attempts and gets IP geolocation information by scraping [ipinfo.io](https://ipinfo.io) and blocks IP addresses using good ol' iptables. Geoip information is typically all I need to look at to make a determination if an IP address should be blocked. If you'd like something more automated and mature, check out [Fail2ban](https://en.wikipedia.org/wiki/Fail2ban). This tool is useful if you'd like to make hard determinations on hosts to block, such as on a honeypot or a sensitive public server.

## Whitelist
A whilelist file can be included to have block-a-brute ignore certain hosts.

IP's should be listed on separate lines like so:
```
# home
1.2.3.4

# work
5.6.7.8
```

## Usage
```
$ ./block-a-brute.py --help
usage: block-a-brute.py [-h] [-w WHITELIST] [-l LOG] [-y]

block-a-brute - block SSH bruteforcers

optional arguments:
-h, --help            show this help message and exit
-w WHITELIST, --whitelist WHITELIST
                      ip whitelist file
-l LOG, --log LOG     log file
-y, --yes             ban IP's without prompting

```

Here's how to throw down the banhammer:
```
$ sudo ./block-a-brute.py -w whitelist.txt -l log.txt
 _     _            _                     _                _
| |__ | | ___   ___| | __      __ _      | |__  _ __ _   _| |_ ___
| '_ \| |/ _ \ / __| |/ /____ / _` |_____| '_ \| '__| | | | __/ _ \
| |_) | | (_) | (__|   <_____| (_| |_____| |_) | |  | |_| | ||  __/
|_.__/|_|\___/ \___|_|\_\     \__,_|     |_.__/|_|   \__,_|\__\___|
               https://github.com/vesche/block-a-brute

Loading IP's from auth.log...

IP: <removed>
City: St Petersburg
Region: St.-Petersburg
Country: RU
Org: AS57043 HOSTKEY B.V.

Would you like to ban <removed> (y/N)? y
Got em' coach! <removed> was blocked.

IP: <removed>
City: Hebei
Region: Hebei
Country: CN
Org: AS4837 CHINA UNICOM China169 Backbone

Would you like to ban <removed> (y/N)? y
Got em' coach! <removed> was blocked
```

If you're confident in your whitelist file, use the `-y` option to ban without prompting.
