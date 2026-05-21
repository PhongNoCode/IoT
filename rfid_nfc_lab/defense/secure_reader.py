#!/usr/bin/env python3
"""Secure Access Control Server — anti-replay + time window"""
import socket, json, time, threading, hmac, hashlib
from colorama import Fore, init
init(autoreset=True)

HOST, PORT = '127.0.0.1', 7002
HMAC_KEY   = b'SecretACServerKey_2024'
TIME_WINDOW = 5.0    # giây — yêu cầu phải đến trong 5 giây
COOLDOWN    = 60.0   # giây — chặn replay trong 60 giây

CARD_DB = {
    'A1B2C3D4E5': {'owner':'Nguyen Van A','level':'EMPLOYEE','active':True},
    'DEADBEEF01': {'owner':'Tran Thi B',  'level':'ADMIN',   'active':True},
}

# Lưu (uid, timestamp_token) đã dùng — chống replay
USED_TOKENS: dict[str, float] = {}
lock = threading.Lock()

def cleanup_tokens():
    """Xóa token cũ hơn COOLDOWN"""
    now = time.time()
    with lock:
        expired = [k for k,v in USED_TOKENS.items() if now-v > COOLDOWN]
        for k in expired: del USED_TOKENS[k]

def handle(conn, addr):
    try:
        data = json.loads(conn.recv(512).decode())
        uid  = data.get('uid','')
        ts   = float(data.get('timestamp', 0))
        token_key = f'{uid}:{ts:.1f}'
        now = time.time()

        # Kiểm tra 1: Time window
        if abs(now - ts) > TIME_WINDOW:
            resp = {'status':'DENIED','msg':f'Timestamp out of window ({abs(now-ts):.1f}s)'}
            print(f'{Fore.RED}[SECURE AC] REPLAY BLOCKED: {uid} ts_diff={abs(now-ts):.1f}s')
        # Kiểm tra 2: Anti-replay token
        elif token_key in USED_TOKENS:
            resp = {'status':'DENIED','msg':'Token already used (replay detected)'}
            print(f'{Fore.RED}[SECURE AC] REPLAY DETECTED: {uid}')
        # Kiểm tra 3: Card database
        elif uid not in CARD_DB or not CARD_DB[uid]['active']:
            resp = {'status':'DENIED','msg':'Unknown card'}
        else:
            # Đánh dấu token đã dùng
            with lock: USED_TOKENS[token_key] = now
            card = CARD_DB[uid]
            resp = {'status':'GRANTED','owner':card['owner'],'level':card['level']}
            print(f"{Fore.GREEN}[SECURE AC] GRANTED: {card['owner']}")

        conn.send(json.dumps(resp).encode())
        cleanup_tokens()
    except Exception as e:
        print(f'{Fore.RED}[SECURE AC] Error: {e}')
    finally:
        conn.close()

server = socket.socket(); server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
server.bind((HOST,PORT)); server.listen(10)
print(f'{Fore.GREEN}[SECURE AC] Running @ {HOST}:{PORT} — Anti-replay ENABLED')
while True:
    c,a = server.accept()
    threading.Thread(target=handle,args=(c,a),daemon=True).start()
