#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Secure Access Control Server - anti-replay + time window + rate limiting"""
import socket, json, time, threading, hmac, hashlib, io, sys
from colorama import Fore, init
init(autoreset=True)

# Fix Windows CP1252 encoding issue
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

HOST, PORT  = '127.0.0.1', 7001
HMAC_KEY    = b'SecretACServerKey_2024'
TIME_WINDOW = 5.0    # seconds - request must arrive within 5s of its timestamp
COOLDOWN    = 60.0   # seconds - keep used tokens for 60s to block replays

# Rate limiting: max requests per IP per window
RATE_LIMIT       = 5          # max 5 attempts
RATE_WINDOW      = 10.0       # per 10 seconds
LOCKOUT_DURATION = 30.0       # lockout IP for 30s after too many attempts

CARD_DB = {
    'A1B2C3D4E5': {'owner': 'Nguyen Van A', 'level': 'EMPLOYEE', 'active': True},
    'DEADBEEF01': {'owner': 'Tran Thi B',   'level': 'ADMIN',    'active': True},
}

# Track used tokens (uid:ts) to block replays
USED_TOKENS: dict[str, float] = {}

# Track request counts per IP for rate limiting
IP_ATTEMPTS: dict[str, list] = {}   # ip -> [timestamps of recent attempts]
IP_LOCKOUT:  dict[str, float] = {}  # ip -> lockout_until timestamp

lock = threading.Lock()


def cleanup_tokens():
    """Remove tokens older than COOLDOWN"""
    now = time.time()
    with lock:
        expired = [k for k, v in USED_TOKENS.items() if now - v > COOLDOWN]
        for k in expired:
            del USED_TOKENS[k]


def is_rate_limited(ip: str) -> tuple[bool, str]:
    """Check if IP is rate-limited or locked out. Returns (blocked, reason)."""
    now = time.time()
    with lock:
        # Check lockout
        if ip in IP_LOCKOUT:
            if now < IP_LOCKOUT[ip]:
                remaining = IP_LOCKOUT[ip] - now
                return True, f'IP locked out for {remaining:.0f}s (brute force detected)'
            else:
                del IP_LOCKOUT[ip]
                IP_ATTEMPTS.pop(ip, None)

        # Count recent attempts in window
        recent = [t for t in IP_ATTEMPTS.get(ip, []) if now - t < RATE_WINDOW]
        IP_ATTEMPTS[ip] = recent

        if len(recent) >= RATE_LIMIT:
            # Too many attempts - lockout this IP
            IP_LOCKOUT[ip] = now + LOCKOUT_DURATION
            print(f'{Fore.RED}[SECURE AC] RATE LIMIT: {ip} locked out for {LOCKOUT_DURATION}s')
            return True, f'Too many attempts - locked out for {LOCKOUT_DURATION}s'

        # Record this attempt
        IP_ATTEMPTS[ip].append(now)
        return False, ''


def handle(conn, addr):
    ip = addr[0]
    try:
        data = json.loads(conn.recv(512).decode())
        uid  = data.get('uid', '')
        ts   = float(data.get('timestamp', 0))
        token_key = f'{uid}:{ts:.1f}'
        now  = time.time()

        # Check 1: Rate limiting (anti brute-force)
        blocked, reason = is_rate_limited(ip)
        if blocked:
            resp = {'status': 'DENIED', 'msg': reason}
            print(f'{Fore.RED}[SECURE AC] BLOCKED {ip}: {reason}')

        # Check 2: Time window (anti replay with old timestamp)
        elif abs(now - ts) > TIME_WINDOW:
            resp = {'status': 'DENIED', 'msg': f'Timestamp out of window ({abs(now - ts):.1f}s)'}
            print(f'{Fore.RED}[SECURE AC] REPLAY BLOCKED: {uid} ts_diff={abs(now - ts):.1f}s')

        # Check 3: Anti-replay token (same timestamp used twice)
        elif token_key in USED_TOKENS:
            resp = {'status': 'DENIED', 'msg': 'Token already used (replay detected)'}
            print(f'{Fore.RED}[SECURE AC] REPLAY DETECTED: {uid}')

        # Check 4: Card database
        elif uid not in CARD_DB or not CARD_DB[uid]['active']:
            resp = {'status': 'DENIED', 'msg': 'Unknown card'}

        else:
            with lock:
                USED_TOKENS[token_key] = now
            card = CARD_DB[uid]
            resp = {'status': 'GRANTED', 'owner': card['owner'], 'level': card['level']}
            print(f"{Fore.GREEN}[SECURE AC] GRANTED: {card['owner']} from {ip}")

        conn.send(json.dumps(resp).encode())
        cleanup_tokens()
    except Exception as e:
        print(f'{Fore.RED}[SECURE AC] Error: {e}')
    finally:
        conn.close()


if __name__ == '__main__':
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(10)
    print(f'{Fore.GREEN}[SECURE AC] Running @ {HOST}:{PORT}')
    print(f'{Fore.GREEN}[SECURE AC] Anti-replay ENABLED  (time window: {TIME_WINDOW}s)')
    print(f'{Fore.GREEN}[SECURE AC] Rate limiting ENABLED (max {RATE_LIMIT} req / {RATE_WINDOW}s, lockout {LOCKOUT_DURATION}s)')
    while True:
        c, a = server.accept()
        threading.Thread(target=handle, args=(c, a), daemon=True).start()
