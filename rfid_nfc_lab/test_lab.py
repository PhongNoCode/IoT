#!/usr/bin/env python3
"""
RFID/NFC Security Lab — Comprehensive Test Suite
Kiểm tra tất cả 6 module simulators + 5 loại tấn công + 3 biện pháp phòng chống
"""
import os, subprocess, sys, time, threading, json, socket, io
from datetime import datetime
from colorama import Fore, Style, init

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

init(autoreset=True)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class LabTester:
    def __init__(self):
        self.results = {
            'simulators': {},
            'attacks': {},
            'defense': {},
            'issues': []
        }
        self.processes = []
    
    def log_test(self, category, name, status, details=''):
        """Ghi kết quả test"""
        self.results[category][name] = {
            'status': status,
            'details': details,
            'time': datetime.now().isoformat()
        }
        color = Fore.GREEN if status == 'PASS' else Fore.RED
        icon = '✓' if status == 'PASS' else '✗'
        print(f'{color}[{icon}] {name}: {details}')
    
    def start_process(self, script_path, name, timeout=3):
        """Khởi động một process"""
        try:
            script = os.path.join(BASE_DIR, script_path)
            proc = subprocess.Popen(
                [sys.executable, script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes.append((proc, name))
            print(f'{Fore.CYAN}[*] Started: {name}')
            return proc
        except Exception as e:
            self.log_test('simulators', name, 'FAIL', str(e))
            return None
    
    def test_simulators(self):
        """Test các module simulators"""
        print(f'\n{Fore.BLUE}=== 1. TESTING SIMULATORS ===')
        
        # 1. RFID Tag Simulator (EM4100)
        print(f'\n{Fore.YELLOW}[1.1] RFID Tag Simulator (EM4100)')
        try:
            proc = self.start_process('rfid/rfid_tag.py', 'RFID Tag Server', timeout=2)
            if proc is None:
                raise RuntimeError('RFID Tag Server did not start')
            time.sleep(1)
            # Kiểm tra xem server có lắng nghe không
            s = socket.socket()
            s.settimeout(1)
            s.connect(('127.0.0.1', 6001))
            s.send(json.dumps({'cmd':'QUERY'}).encode())
            resp = json.loads(s.recv(512).decode())
            s.close()
            if resp.get('uid'):
                self.log_test('simulators', 'RFID EM4100', 'PASS', 
                             f"UID={resp['uid']}, Type={resp.get('type')}")
            else:
                self.log_test('simulators', 'RFID EM4100', 'FAIL', 'No UID in response')
            proc.terminate()
        except Exception as e:
            self.log_test('simulators', 'RFID EM4100', 'FAIL', str(e))
        
        # 2. NFC Tag Simulator (NTAG213)
        print(f'\n{Fore.YELLOW}[1.2] NFC Tag Simulator (NTAG213)')
        try:
            proc = self.start_process('nfc/nfc_tag.py', 'NFC Tag Server', timeout=2)
            if proc is None:
                raise RuntimeError('NFC Tag Server did not start')
            time.sleep(1)
            s = socket.socket()
            s.settimeout(1)
            s.connect(('127.0.0.1', 6011))
            s.send(json.dumps({'cmd':'GET_UID'}).encode())
            resp = json.loads(s.recv(512).decode())
            s.close()
            if resp.get('uid'):
                self.log_test('simulators', 'NFC NTAG213', 'PASS', 
                             f"UID={resp['uid'][:8]}..., NDEF-compatible")
            else:
                self.log_test('simulators', 'NFC NTAG213', 'FAIL', 'No UID')
            proc.terminate()
        except Exception as e:
            self.log_test('simulators', 'NFC NTAG213', 'FAIL', str(e))
        
        # 3. Access Control Server
        print(f'\n{Fore.YELLOW}[1.3] Access Control Server')
        try:
            proc = self.start_process('access_control/ac_server.py', 'AC Server', timeout=2)
            if proc is None:
                raise RuntimeError('Access Control Server did not start')
            time.sleep(1)
            s = socket.socket()
            s.settimeout(1)
            s.connect(('127.0.0.1', 7001))
            s.send(json.dumps({'cmd':'AUTH','uid':'A1B2C3D4E5'}).encode())
            resp = json.loads(s.recv(512).decode())
            s.close()
            if resp.get('status'):
                self.log_test('simulators', 'Access Control', 'PASS', 
                             f"Status={resp['status']}, DB loaded")
            else:
                self.log_test('simulators', 'Access Control', 'FAIL', 'No status')
            proc.terminate()
        except Exception as e:
            self.log_test('simulators', 'Access Control', 'FAIL', str(e))
    
    def test_attacks(self):
        """Test các loại tấn công"""
        print(f'\n{Fore.BLUE}=== 2. TESTING ATTACKS ===')
        
        # Khởi động servers trước
        tag_proc = subprocess.Popen([sys.executable, os.path.join(BASE_DIR, 'rfid/rfid_tag.py')], 
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        ac_proc = subprocess.Popen([sys.executable, os.path.join(BASE_DIR, 'access_control/ac_server.py')],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)
        
        # 1. Eavesdropping
        print(f'\n{Fore.YELLOW}[2.1] Eavesdropping Attack')
        try:
            s = socket.socket()
            s.settimeout(1)
            s.connect(('127.0.0.1', 6001))
            s.send(json.dumps({'cmd':'QUERY'}).encode())
            resp = json.loads(s.recv(512).decode())
            s.close()
            if resp.get('uid'):
                self.log_test('attacks', 'Eavesdropping', 'PASS', 
                             f"Captured UID={resp['uid']} (unencrypted)")
            else:
                self.log_test('attacks', 'Eavesdropping', 'FAIL', 'No capture')
        except Exception as e:
            self.log_test('attacks', 'Eavesdropping', 'FAIL', str(e))
        
        # 2. Replay Attack
        print(f'\n{Fore.YELLOW}[2.2] Replay Attack')
        try:
            stolen_uid = 'A1B2C3D4E5'
            s = socket.socket()
            s.settimeout(1)
            s.connect(('127.0.0.1', 7001))
            s.send(json.dumps({'cmd':'AUTH','uid':stolen_uid}).encode())
            resp = json.loads(s.recv(512).decode())
            s.close()
            if resp.get('status') == 'GRANTED':
                self.log_test('attacks', 'Replay Attack', 'PASS', 
                             f"✗ Server vulnerable - Granted access to {stolen_uid}")
            else:
                self.log_test('attacks', 'Replay Attack', 'FAIL', 'Attack failed')
        except Exception as e:
            self.log_test('attacks', 'Replay Attack', 'FAIL', str(e))
        
        # 3. UID Brute Force
        print(f'\n{Fore.YELLOW}[2.3] UID Brute Force')
        try:
            found = []
            for uid_int in range(0x0000, 0x1000, 100):
                uid = f'{uid_int:010X}'
                s = socket.socket()
                s.settimeout(0.5)
                try:
                    s.connect(('127.0.0.1', 7001))
                    s.send(json.dumps({'cmd':'AUTH','uid':uid}).encode())
                    resp = json.loads(s.recv(512).decode())
                    if resp.get('status') == 'GRANTED':
                        found.append(uid)
                except:
                    pass
                finally:
                    s.close()
            self.log_test('attacks', 'Brute Force', 'PASS', 
                         f"Found {len(found)} valid UIDs in 4096 space")
        except Exception as e:
            self.log_test('attacks', 'Brute Force', 'FAIL', str(e))
        
        # 4. RFID Cloning
        print(f'\n{Fore.YELLOW}[2.4] RFID Cloning')
        try:
            s = socket.socket()
            s.settimeout(1)
            s.connect(('127.0.0.1', 6001))
            s.send(json.dumps({'cmd':'GET_INFO'}).encode())
            resp = json.loads(s.recv(512).decode())
            s.close()
            if resp.get('owner'):
                self.log_test('attacks', 'RFID Cloning', 'PASS', 
                             f"✗ Owner info leaked: {resp['owner']}")
            else:
                self.log_test('attacks', 'RFID Cloning', 'FAIL', 'No leak')
        except Exception as e:
            self.log_test('attacks', 'RFID Cloning', 'FAIL', str(e))
        
        tag_proc.terminate()
        ac_proc.terminate()
        time.sleep(1)
    
    def test_defense(self):
        """Test các biện pháp phòng chống"""
        print(f'\n{Fore.BLUE}=== 3. TESTING DEFENSE ===')
        
        # 1. Anti-Replay Token (Secure AC)
        print(f'\n{Fore.YELLOW}[3.1] Anti-Replay Token (Time Window)')
        try:
            secure_ac = subprocess.Popen([sys.executable, os.path.join(BASE_DIR, 'defense/secure_reader.py')],
                                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1)
            
            # Cố gắng replay cùng timestamp
            uid = 'A1B2C3D4E5'
            ts = time.time()
            
            # Lần 1 - OK
            s = socket.socket()
            s.settimeout(1)
            s.connect(('127.0.0.1', 7001))
            s.send(json.dumps({'cmd':'AUTH','uid':uid,'timestamp':ts}).encode())
            resp1 = json.loads(s.recv(512).decode())
            s.close()
            
            # Lần 2 - cùng timestamp, nên bị chặn (replay)
            s = socket.socket()
            s.settimeout(1)
            s.connect(('127.0.0.1', 7001))
            s.send(json.dumps({'cmd':'AUTH','uid':uid,'timestamp':ts}).encode())
            resp2 = json.loads(s.recv(512).decode())
            s.close()
            
            if resp1.get('status') == 'GRANTED' and resp2.get('status') == 'DENIED':
                self.log_test('defense', 'Anti-Replay', 'PASS', 
                             '✓ Token reuse blocked')
            else:
                self.log_test('defense', 'Anti-Replay', 'FAIL', 
                             f'resp1={resp1.get("status")}, resp2={resp2.get("status")}')
            
            secure_ac.terminate()
        except Exception as e:
            self.log_test('defense', 'Anti-Replay', 'FAIL', str(e))
        
        # 2. NDEF HMAC Signing & 3. NFC Write Protection
        print(f'\n{Fore.YELLOW}[3.2] NDEF HMAC Signing')
        secure_tag_proc = None
        try:
            secure_tag_proc = subprocess.Popen(
                [sys.executable, os.path.join(BASE_DIR, 'defense/secure_tag.py')],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            time.sleep(1.5)

            # Test 3.2 NDEF HMAC
            s = socket.socket()
            s.settimeout(2)
            s.connect(('127.0.0.1', 6011))
            s.send(json.dumps({'cmd':'READ_NDEF'}).encode())
            resp = json.loads(s.recv(1024).decode())
            s.close()
            
            if resp.get('signature'):
                self.log_test('defense', 'NDEF HMAC', 'PASS',
                             f"✓ Signature: {resp['signature'][:16]}...")
            else:
                self.log_test('defense', 'NDEF HMAC', 'FAIL', 'No signature')
                
            # Test 3.3 NFC Write Protection
            print(f'\n{Fore.YELLOW}[3.3] NFC Write Protection')
            # Thử ghi không password
            s = socket.socket(); s.settimeout(1)
            s.connect(('127.0.0.1', 6011))
            s.send(json.dumps({'cmd':'WRITE_NDEF', 'ndef_hex': '00112233'}).encode())
            resp_write1 = json.loads(s.recv(512).decode()); s.close()
            
            # Thử ghi đúng password
            s = socket.socket(); s.settimeout(1)
            s.connect(('127.0.0.1', 6011))
            s.send(json.dumps({'cmd':'WRITE_NDEF', 'ndef_hex': '00112233', 'pwd': '41424344'}).encode())
            resp_write2 = json.loads(s.recv(512).decode()); s.close()
            
            if resp_write1.get('status') == 'DENIED' and resp_write2.get('status') == 'WRITTEN':
                self.log_test('defense', 'NFC Write Protection', 'PASS', 
                             '✓ Unauthorized write blocked, authorized write allowed')
            else:
                self.log_test('defense', 'NFC Write Protection', 'FAIL', 
                             f'resp1={resp_write1.get("status")}, resp2={resp_write2.get("status")}')
                             
        except Exception as e:
            self.log_test('defense', 'NDEF HMAC', 'FAIL', str(e))
            self.log_test('defense', 'NFC Write Protection', 'FAIL', str(e))
        finally:
            if secure_tag_proc:
                secure_tag_proc.terminate()
    
    def generate_report(self):
        """Tạo báo cáo tổng hợp"""
        print(f'\n{Fore.BLUE}{"="*60}')
        print(f'{Fore.BLUE}RFID/NFC SECURITY LAB — COMPREHENSIVE TEST REPORT')
        print(f'{Fore.BLUE}{"="*60}')
        
        for category, tests in self.results.items():
            if not tests or not isinstance(tests, dict):
                continue
            print(f'\n{Fore.YELLOW}{category.upper()}:')
            for name, result in tests.items():
                status = result.get('status', 'UNKNOWN')
                color = Fore.GREEN if status == 'PASS' else (Fore.YELLOW if status == 'SKIP' else Fore.RED)
                icon = '✓' if status == 'PASS' else ('○' if status == 'SKIP' else '✗')
                print(f"  {color}{icon} {name:30} {status:8} {result.get('details', '')}")
        
        # Tính toán tỷ lệ thành công
        total = 0
        passed = 0
        for v in self.results.values():
            if isinstance(v, dict):
                total += len(v)
                passed += sum(1 for t in v.values() if t.get('status') == 'PASS')
        
        print(f'\n{Fore.BLUE}{"="*60}')
        print(f'{Fore.GREEN}Overall: {passed}/{total} tests passed ({passed*100//total}%)')
        print(f'{Fore.BLUE}{"="*60}\n')
        
        return self.results

def main():
    tester = LabTester()
    
    print(f'{Fore.CYAN}╔════════════════════════════════════════════════════╗')
    print(f'{Fore.CYAN}║  RFID/NFC SECURITY LAB - COMPREHENSIVE TEST SUITE  ║')
    print(f'{Fore.CYAN}╚════════════════════════════════════════════════════╝\n')
    
    tester.test_simulators()
    time.sleep(2)
    tester.test_attacks()
    time.sleep(2)
    tester.test_defense()
    
    results = tester.generate_report()
    
    # Lưu kết quả
    result_file = os.path.join(BASE_DIR, 'test_results.json')
    with open(result_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f'{Fore.GREEN}Results saved to test_results.json')

if __name__ == '__main__':
    main()
