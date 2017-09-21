#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# block-a-brute
# https://github.com/vesche/block-a-brute
#

import argparse
import json
import os
import re
import requests
import subprocess
import sys
import time

from urllib.parse import urlparse

BANNER = '''
 _     _            _                     _                _
| |__ | | ___   ___| | __      __ _      | |__  _ __ _   _| |_ ___
| '_ \| |/ _ \ / __| |/ /____ / _` |_____| '_ \| '__| | | | __/ _ \\
| |_) | | (_) | (__|   <_____| (_| |_____| |_) | |  | |_| | ||  __/
|_.__/|_|\___/ \___|_|\_\     \__,_|     |_.__/|_|   \__,_|\__\___|
              https://github.com/vesche/block-a-brute
'''


def _autoban_preflight():
    if not os.geteuid() == 0:
        print('Error: This program needs to run as root.')
        sys.exit(1)

    if not os.path.isfile('/var/log/auth.log'):
        print('Error: /var/log/auth.log could not be found.')
        sys.exit(1)


def ban_ip(ip):
    command = 'iptables -A INPUT -s {} -j DROP'.format(ip)
    subprocess.call(command.split())


def check_ip(ip, whitelist):
    for good_ip in whitelist:
        if ip == good_ip:
            return True

    command = 'iptables -L INPUT -v -n | grep -w "{}"'.format(ip)

    ps = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    output = ps.communicate()[0]

    if output:
        return True
    else:
        return False


def load_whitelist(whitelist_file):
    whitelist = []
    with open(whitelist_file) as f:
        for line in f.read().splitlines():
            if not line.startswith('#'):
                whitelist.append(line)
    return whitelist


def get_parser():
    parser = argparse.ArgumentParser(description='block-a-brute')
    parser.add_argument('-w', '--whitelist',
                        help='ip whitelist file', type=str)
    parser.add_argument('-l', '--log',
                        help='log file)', type=str)
    parser.add_argument('-y', '--yes',
                        help='ban IP\'s without prompting',
                        default=False, action='store_true')
    return parser


def main():
    parser = get_parser()
    args = vars(parser.parse_args())

    # get command-line arguments
    whitelist_file = args['whitelist']
    log_file = args['log']
    autoban = args['yes']

    # ladies and gentlemen this is your captain speaking
    _autoban_preflight()

    # get IP's from whitelist file
    whitelist = ['127.0.0.1']
    if whitelist_file:
        whitelist = load_whitelist(whitelist_file)

    print(BANNER)
    print('Loading IP\'s from auth.log...')

    # get IP's from auth.log
    ips = []
    with open('/var/log/auth.log') as f:
        for line in f.read().splitlines()[::-1]:
            ips += re.findall(r'[0-9]+(?:\.[0-9]+){3}', line)

    for ip in set(ips):
        # stop if IP is already blocked or in whitelist
        if check_ip(ip, whitelist):
            continue

        # get IP information and prompt if autoban not enabled
        if not autoban:
            response = requests.get('https://ipinfo.io/{}'.format(ip)).text
            ip_data = json.loads(response)

            city    = ip_data['city']
            region  = ip_data['region']
            country = ip_data['country']
            org     = ip_data['org']

            print('\nIP: {}\nCity: {}\nRegion: {}\nCountry: {}\nOrg: {}\n'.format(
                ip, city, region, country, org))

            ban_choice = input('Would you like to ban {} (y/N)? '.format(ip))
        else:
            ban_choice = 'y'

        # ban IP and log action
        if ban_choice.lower().startswith('y'):
            ban_ip(ip)
            print('Got em\' coach! {} was blocked.'.format(ip))

            if log_file:
                with open(log_file, 'a') as f:
                    dt = time.strftime('%a, %d %b %Y %H:%M:%S {}'.format(
                        time.tzname[0]), time.localtime())
                    f.write('{} - {} blocked.\n'.format(dt, ip))


if __name__ == '__main__':
    main()
