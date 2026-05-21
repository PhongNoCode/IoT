#!/usr/bin/env python3
"""
OWASP IoT Top 10 Security Analysis
Phân tích các lỗ hổng bảo mật tìm được trong lab
"""
from colorama import Fore, init
init(autoreset=True)

ANALYSIS = {
    'I1: Weak Guessing of Credentials': {
        'cvss': 7.5,
        'severity': 'HIGH',
        'description': 'RFID UID phát trực tiếp không yêu cầu xác thực',
        'found_in': ['rfid_tag.py', 'eavesdropper.py'],
        'evidence': 'UID="A1B2C3D4E5" phát trực tiếp qua mạng',
        'mitigation': 'Dùng mutual authentication + encryption'
    },
    
    'I2: Weak Transport Layer Protection': {
        'cvss': 8.1,
        'severity': 'HIGH',
        'description': 'Dữ liệu truyền qua TCP plain text (không TLS/SSL)',
        'found_in': ['rfid_tag.py', 'nfc_tag.py', 'ac_server.py'],
        'evidence': 'socket.send(json.dumps(data)) - không mã hóa',
        'mitigation': 'Thêm TLS/SSL, use secure_reader.py'
    },
    
    'I3: Insecure Web Interface': {
        'cvss': 6.5,
        'severity': 'MEDIUM',
        'description': 'Dashboard không có authentication, chạy port mở',
        'found_in': ['dashboard/dashboard.py'],
        'evidence': 'app.run(host="0.0.0.0", port=8080) - tất cả có thể truy cập',
        'mitigation': 'Thêm login + rate limiting + HTTPS'
    },
    
    'I4: Lack of Security Configurability': {
        'cvss': 5.3,
        'severity': 'MEDIUM',
        'description': 'Không thể cấu hình bảo mật (password cứng, không có config file)',
        'found_in': ['ac_server.py', 'defense/secure_reader.py'],
        'evidence': 'CARD_DB = {...} - hardcoded, không có config',
        'mitigation': 'Dùng config file, env variables cho secrets'
    },
    
    'I5: Insecure Software/Firmware': {
        'cvss': 7.1,
        'severity': 'HIGH',
        'description': 'Không có versioning, update mechanism, hoặc integrity check',
        'found_in': ['Tất cả modules'],
        'evidence': 'Mô phỏng không có OTA updates, digital signatures',
        'mitigation': 'Thêm firmware versioning + signed OTA updates'
    },
    
    'I6: Insecure Network Services': {
        'cvss': 8.6,
        'severity': 'HIGH',
        'description': 'Replay attack không được chặn trong phiên bản bình thường',
        'found_in': ['access_control/ac_server.py', 'attacks/replay_attack.py'],
        'evidence': 'Lần 1: GRANTED, Lần 2: GRANTED cùng UID - replay success',
        'mitigation': 'Use defense/secure_reader.py (anti-replay tokens)'
    },
    
    'I7: Poor Physical Security': {
        'cvss': 6.7,
        'severity': 'MEDIUM',
        'description': 'RFID tags không có tamper protection, có thể sao chép',
        'found_in': ['rfid_cloner.py'],
        'evidence': 'Đọc được toàn bộ UID + data, ghi được lại',
        'mitigation': 'Thêm write protection, encryption (secure_tag.py)'
    },
    
    'I8: Privacy Concerns': {
        'cvss': 5.9,
        'severity': 'MEDIUM',
        'description': 'Thông tin cá nhân (owner, facility, level) bị lộ',
        'found_in': ['rfid_tag.py GET_INFO', 'nfc_tag.py NDEF'],
        'evidence': 'resp["owner"] = "Nguyen Van A" - public info leak',
        'mitigation': 'Chỉ trả UID, không trả thông tin user'
    },
    
    'I9: Insecure Default Settings': {
        'cvss': 7.2,
        'severity': 'HIGH',
        'description': 'Tags mở để ghi (write accessible), không password',
        'found_in': ['nfc_tag.py', 'rfid_tag.py'],
        'evidence': 'WRITE_NDEF không kiểm tra password (lỗ hổng)',
        'mitigation': 'Bật password protection by default'
    },
    
    'I10: Lack of Physical Hardening': {
        'cvss': 4.3,
        'severity': 'MEDIUM',
        'description': 'Không có detection khi tag bị remove, power supply không protected',
        'found_in': ['rfid_tag.py', 'nfc_tag.py'],
        'evidence': 'Mô phỏng không kiểm tra attack thời gian',
        'mitigation': 'Thêm watchdog + intrusion detection'
    }
}

CVSS_VECTORS = {
    'I1: Weak Guessing of Credentials': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N',
    'I2: Weak Transport Layer Protection': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N',
    'I3: Insecure Web Interface': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N',
    'I4: Lack of Security Configurability': 'CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L',
    'I5: Insecure Software/Firmware': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H',
    'I6: Insecure Network Services': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N',
    'I7: Poor Physical Security': 'CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L',
    'I8: Privacy Concerns': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N',
    'I9: Insecure Default Settings': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N',
    'I10: Lack of Physical Hardening': 'CVSS:3.1/AV:P/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L'
}

def print_report():
    """In báo cáo OWASP"""
    print(f'\n{Fore.CYAN}╔════════════════════════════════════════════════════╗')
    print(f'{Fore.CYAN}║        OWASP IoT Top 10 - Security Analysis        ║')
    print(f'{Fore.CYAN}║           (Based on RFID/NFC Lab Testing)           ║')
    print(f'{Fore.CYAN}╚════════════════════════════════════════════════════╝\n')
    
    sorted_issues = sorted(ANALYSIS.items(), key=lambda x: x[1]['cvss'], reverse=True)
    
    for i, (title, data) in enumerate(sorted_issues, 1):
        severity_color = {
            'CRITICAL': Fore.RED,
            'HIGH': Fore.LIGHTRED_EX,
            'MEDIUM': Fore.YELLOW,
            'LOW': Fore.CYAN
        }.get(data['severity'], Fore.WHITE)
        
        print(f'{Fore.BLUE}{"─"*70}')
        print(f'{Fore.WHITE}[{i}] {Fore.CYAN}{title}')
        print(f'{severity_color}    Severity: {data["severity"]:8} | CVSS Score: {data["cvss"]}')
        print(f'{Fore.WHITE}    Description: {data["description"]}')
        print(f'{Fore.YELLOW}    Found In: {", ".join(data["found_in"])}')
        print(f'{Fore.RED}    Evidence: {data["evidence"]}')
        print(f'{Fore.GREEN}    Mitigation: {data["mitigation"]}')
        print(f'{Fore.MAGENTA}    CVSS Vector: {CVSS_VECTORS[title]}')
    
    # Tính toán thống kê
    print(f'\n{Fore.BLUE}{"─"*70}')
    print(f'{Fore.CYAN}STATISTICS:')
    critical = sum(1 for d in ANALYSIS.values() if d['severity'] == 'CRITICAL')
    high = sum(1 for d in ANALYSIS.values() if d['severity'] == 'HIGH')
    medium = sum(1 for d in ANALYSIS.values() if d['severity'] == 'MEDIUM')
    low = sum(1 for d in ANALYSIS.values() if d['severity'] == 'LOW')
    
    avg_cvss = sum(d['cvss'] for d in ANALYSIS.values()) / len(ANALYSIS)
    
    print(f'  {Fore.RED}Critical: {critical}')
    print(f'  {Fore.LIGHTRED_EX}High:     {high}')
    print(f'  {Fore.YELLOW}Medium:   {medium}')
    print(f'  {Fore.CYAN}Low:      {low}')
    print(f'  {Fore.MAGENTA}Average CVSS Score: {avg_cvss:.2f}')
    print(f'{Fore.BLUE}{"─"*70}\n')
    
    # Mitigations
    print(f'{Fore.GREEN}RECOMMENDED MITIGATIONS:')
    print(f'{Fore.GREEN}1. Enable encryption for all transport (TLS/SSL)')
    print(f'{Fore.GREEN}2. Implement mutual authentication (Challenge-Response)')
    print(f'{Fore.GREEN}3. Add anti-replay tokens with time windows')
    print(f'{Fore.GREEN}4. Enable write protection & HMAC signing for tags')
    print(f'{Fore.GREEN}5. Use secure_reader.py for access control')
    print(f'{Fore.GREEN}6. Implement firmware versioning & OTA updates')
    print(f'{Fore.GREEN}7. Add monitoring & anomaly detection')
    print()

if __name__ == '__main__':
    print_report()
    
    # Lưu báo cáo
    import json
    with open('owasp_analysis.json', 'w', encoding='utf-8') as f:
        report = {
            'title': 'OWASP IoT Top 10 Security Analysis',
            'lab': 'RFID/NFC Security Lab',
            'issues': ANALYSIS,
            'cvss_vectors': CVSS_VECTORS,
            'statistics': {
                'total_issues': len(ANALYSIS),
                'average_cvss': sum(d['cvss'] for d in ANALYSIS.values()) / len(ANALYSIS)
            }
        }
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f'{Fore.GREEN}Report saved to owasp_analysis.json')
