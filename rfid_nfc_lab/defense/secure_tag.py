#!/usr/bin/env python3
"""Secure NFC Tag — NDEF signing + write protection"""
import socket, json, time, hmac, hashlib, struct
import ndef
from colorama import Fore, init
init(autoreset=True)

HOST, PORT = '127.0.0.1', 6011
WRITE_PWD  = bytes([0x41,0x42,0x43,0x44])    # 4-byte write password
AUTHLIM    = 3                                # Khóa sau 3 lần sai

class SecureNTAG213:
    def __init__(self):
        self.uid       = bytes([0x04,0xA1,0xB2,0xC3,0xD4,0xE5,0xF6])
        self.pages     = bytearray(45 * 4)
        self.pw_auth   = False
        self.auth_fail = 0
        # Khởi tạo NDEF
        ndef_data = b''.join(ndef.message_encoder([
            ndef.UriRecord('https://secure.iotlab.edu.vn')
        ]))
        self.pages[16:16+len(ndef_data)] = ndef_data
        self.ndef_hmac = self.sign_ndef(ndef_data)
        self.locked    = False
        
    def sign_ndef(self, data: bytes) -> bytes:
        """Tính HMAC-SHA256 cho NDEF"""
        key = b'SecureNDEFKey_IoTLab'
        return hmac.new(key, data, hashlib.sha256).digest()
    
    def read_page(self, page_no: int) -> bytes:
        offset = page_no * 4
        return bytes(self.pages[offset:offset+4])
    
    def write_page(self, page_no: int, data: bytes, pwd: bytes = None) -> bool:
        """Ghi page với xác thực password"""
        if page_no >= 2:  # Page 2+ yêu cầu password
            if pwd != WRITE_PWD:
                self.auth_fail += 1
                if self.auth_fail >= AUTHLIM:
                    raise PermissionError('Tag permanently locked!')
                raise PermissionError(f'Wrong PWD ({self.auth_fail}/{AUTHLIM})')
        
        if self.locked:
            raise PermissionError('Tag write-protected')
        
        offset = page_no * 4
        self.pages[offset:offset+4] = data[:4]
        self.auth_fail = 0  # Reset counter
        return True
    
    def get_ndef_with_signature(self) -> dict:
        """Lấy NDEF cùng chữ ký"""
        ndef_bytes = bytes(self.pages[16:80])
        return {
            'ndef': ndef_bytes.hex(),
            'signature': self.ndef_hmac.hex(),
            'locked': self.locked
        }

class SecureNFCTagServer:
    def __init__(self):
        self.tag = SecureNTAG213()
        self.server = socket.socket()
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((HOST, PORT))
        self.server.listen(5)
        print(f'{Fore.GREEN}[SECURE NFC] NTAG213 @ {HOST}:{PORT}')
        print(f'{Fore.GREEN}[SECURE NFC] ✓ Write password protected')
        print(f'{Fore.GREEN}[SECURE NFC] ✓ NDEF HMAC signed')
    
    def handle(self, conn, addr):
        try:
            data = conn.recv(512)
            if not data: return
            req = json.loads(data.decode())
            cmd = req.get('cmd','')
            resp = {}
            
            if cmd == 'GET_UID':
                resp = {'uid': self.tag.uid.hex().upper()}
            
            elif cmd in ('READ_NDEF', 'READ_NDEF_SECURE'):
                resp = self.tag.get_ndef_with_signature()
            
            elif cmd in ('WRITE_NDEF', 'WRITE_NDEF_SECURE'):
                pwd = bytes.fromhex(req.get('pwd','')) if 'pwd' in req else None
                ndef_hex = req.get('ndef_hex','')
                try:
                    self.tag.write_page(4, bytes.fromhex(ndef_hex[:8]), pwd)
                    resp = {'status':'WRITTEN','msg':'NDEF updated (requires valid password)'}
                    print(f'{Fore.GREEN}[SECURE NFC] ✓ Authorized NDEF write from {addr}')
                except PermissionError as e:
                    resp = {'status':'DENIED','msg':str(e)}
                    print(f'{Fore.RED}[SECURE NFC] ✗ Write rejected: {e}')
            
            elif cmd == 'LOCK_TAG':
                pwd = bytes.fromhex(req.get('pwd','')) if 'pwd' in req else None
                if pwd == WRITE_PWD:
                    self.tag.locked = True
                    resp = {'status':'LOCKED'}
                    print(f'{Fore.GREEN}[SECURE NFC] ✓ Tag locked')
                else:
                    resp = {'status':'DENIED','msg':'Invalid password'}
            
            else:
                resp = {'status':'ERROR'}
            
            conn.send(json.dumps(resp).encode() + b'\n')
        finally:
            conn.close()
    
    def run(self):
        import threading
        while True:
            c,a = self.server.accept()
            threading.Thread(target=self.handle, args=(c,a), daemon=True).start()

if __name__ == '__main__':
    SecureNFCTagServer().run()

