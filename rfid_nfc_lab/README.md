# RFID/NFC Security Lab

Một dự án lab hoàn chỉnh để học tập và thực nghiệm các kỹ thuật tấn công và phòng chống RFID/NFC.

## Cấu trúc Dự án

```
rfid_nfc_lab/
├── rfid/                     # Simulators RFID
│   ├── rfid_tag.py          # Tag RFID simulator
│   ├── rfid_reader.py       # Reader RFID simulator
│   └── rfid_cloner.py       # Công cụ clone tag (attacker)
├── nfc/                      # Simulators NFC
│   ├── nfc_tag.py           # Tag NFC simulator (NDEF)
│   ├── nfc_reader.py        # Reader NFC simulator
│   └── nfc_injector.py      # Công cụ inject NDEF (attacker)
├── access_control/
│   ├── ac_server.py         # Server kiểm soát truy cập
│   └── card_db.json         # Database thẻ hợp lệ
├── attacks/                  # Công cụ tấn công
│   ├── eavesdropper.py      # Passive sniffer
│   ├── replay_attack.py     # Replay attack tool
│   ├── relay_attack.py      # Relay attack (2 socket proxy)
│   └── brute_force.py       # UID brute-force
├── defense/                  # Công cụ phòng chống
│   ├── secure_tag.py        # Tag với AES encryption
│   └── secure_reader.py     # Reader với mutual auth
├── dashboard/
│   └── dashboard.py         # Flask web dashboard
├── requirements.txt         # Dependencies
└── README.md               # Tài liệu này
```

## Yêu Cầu

- Python 3.8+
- pip

## Cài Đặt

1. Tạo virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate  # Windows
```

2. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

## Hướng Dẫn Sử Dụng

### 1. Simulators RFID/NFC

```python
# RFID Tag
from rfid.rfid_tag import RFIDTag
from rfid.rfid_reader import RFIDReader

tag = RFIDTag("04F3B2A1C5")
tag.write_data("name", "Alice")

reader = RFIDReader("READER001")
print(reader.read_tag(tag))
```

### 2. Công Cụ Tấn Công

```python
# Eavesdropping
from attacks.eavesdropper import Eavesdropper

eaves = Eavesdropper()
eaves.start_listening()
eaves.capture_frame({"uid": "04F3B2A1C5", "type": "RFID"})
print(eaves.extract_uid())
```

### 3. Công Cụ Phòng Chống

```python
# Secure Tag
from defense.secure_tag import SecureTag

tag = SecureTag("SECURE001")
tag.write_secure_data("employee_id", "EMP12345")
decrypted = tag.read_secure_data("employee_id")
```

### 4. Access Control Server

```python
from access_control.ac_server import AccessControlServer

server = AccessControlServer()
server.register_card("04F3B2A1C5", "Alice", 3)
result = server.check_access("04F3B2A1C5")
```

### 5. Web Dashboard

```bash
python dashboard/dashboard.py
```

Truy cập: http://127.0.0.1:5000

## Các Loại Tấn Công

### 1. **Eavesdropping** (Nghe lén)
- Bắt giữ thụ động các tín hiệu RFID/NFC
- Trích xuất UID và dữ liệu

### 2. **Replay Attack** (Tấn công lặp lại)
- Ghi lại các lệnh hợp lệ
- Phát lại để giả mạo truy cập

### 3. **Relay Attack** (Tấn công chuyển tiếp)
- Sử dụng 2 socket proxy
- Giả mạo người dùng từ xa

### 4. **Brute Force**
- Quét toàn bộ không gian UID
- Tìm thẻ hợp lệ

### 5. **Cloning** (Sao chép)
- Sao chép thẻ RFID
- Sửa đổi UID

### 6. **NDEF Injection** (Tiêm)
- Tiêm payload độc hại vào tag NFC
- Phishing links, malware

## Công Cụ Phòng Chống

### 1. **Secure Tag (AES Encryption)**
- Mã hóa dữ liệu với AES
- Chặn sao chép trái phép

### 2. **Secure Reader (Mutual Authentication)**
- Xác thực lẫn nhau
- Challenge-response protocol
- HMAC validation

## Dự Án Học Tập

Dự án này thiết kế cho:
- Học tập về bảo mật RFID/NFC
- Nghiên cứu các lỗ hổng bảo mật
- Phát triển cách phòng chống
- Thực hành kỹ thuật hacking đạo đức

## Cảnh Báo

⚠️ **Chỉ sử dụng cho mục đích giáo dục và nghiên cứu trong môi trường được kiểm soát!**

## License

MIT

## Tác Giả

RFID/NFC Security Lab
