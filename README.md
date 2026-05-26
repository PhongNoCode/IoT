# 🔐 RFID/NFC Security Lab

> **Mục đích giáo dục** — Mô phỏng 100% bằng Python, không cần phần cứng thực.

Đây là lab bảo mật RFID/NFC mô phỏng các kịch bản tấn công thực tế và các biện pháp phòng chống tương ứng. Toàn bộ giao tiếp dùng TCP socket nội bộ (`127.0.0.1`) thay thế sóng RF.

---

## 📁 Cấu trúc thư mục

```
rfid_nfc_lab/
├── rfid/
│   ├── rfid_tag.py         # Tag RFID EM4100 (port 6001) — CÓ LỖ HỔNG
│   ├── rfid_reader.py      # Reader client
│   └── rfid_cloner.py      # Tấn công clone thẻ
├── nfc/
│   ├── nfc_tag.py          # Tag NFC NTAG213 (port 6011) — CÓ LỖ HỔNG ghi
│   ├── nfc_reader.py       # Reader client
│   └── nfc_injector.py     # Tấn công NDEF injection
├── access_control/
│   ├── ac_server.py        # Server AC không có anti-replay (port 7001)
│   └── card_db.json
├── attacks/
│   ├── eavesdropper.py     # Nghe lén UID (passive sniff)
│   ├── replay_attack.py    # Phát lại UID đã bắt
│   ├── relay_attack.py     # Relay/proxy kéo dài khoảng cách
│   └── brute_force.py      # Dò UID brute force
├── defense/
│   ├── secure_reader.py    # Server AC có anti-replay (port 7002) ✅
│   └── secure_tag.py       # NFC tag có HMAC + write password (port 6012) ✅
├── dashboard/
│   └── dashboard.py        # Web dashboard Flask (port 8080)
├── test_lab.py             # Bộ test tự động toàn bộ lab
├── owasp_analysis.py       # Phân tích OWASP IoT Top 10
├── final_report.py         # Báo cáo tổng hợp
└── requirements.txt
```

---

## ⚙️ Cài đặt

```bash
# Tạo môi trường ảo (khuyến nghị)
python -m venv venv

# Kích hoạt (Windows)
venv\Scripts\activate

# Kích hoạt (Linux/macOS)
source venv/bin/activate

# Cài thư viện
pip install -r rfid_nfc_lab/requirements.txt
```

**Các thư viện cần thiết:**
| Package | Dùng cho |
|---|---|
| `Flask==2.3.0` | Web dashboard |
| `pycryptodome==3.18.0` | Mã hoá (AES, SHA) |
| `requests>=2.28.0` | Gửi event tới dashboard |
| `colorama==0.4.6` | Màu sắc terminal |
| `ndeflib==0.3.3` | Encode/decode NDEF message |

> ⚠️ Lưu ý: Cài `ndeflib` chứ **không phải** `ndef` (package khác). Import trong code là `import ndef` — đây là đúng với `ndeflib`.

---

## 🚀 Cách chạy nhanh (Quick Start)

Mở **5 terminal** song song, chạy lần lượt từ thư mục `rfid_nfc_lab/`:

```bash
# Terminal 1 — RFID Tag
python rfid/rfid_tag.py

# Terminal 2 — NFC Tag
python nfc/nfc_tag.py

# Terminal 3 — Access Control Server (KHÔNG có phòng chống)
python access_control/ac_server.py

# Terminal 4 — Dashboard (tùy chọn)
python dashboard/dashboard.py

# Terminal 5 — Chạy test tổng hợp
python test_lab.py
```

---

## 🎯 HƯỚNG DẪN DEMO: Defense ON vs OFF

Phần này mô tả **từng bước** cách demo sự khác biệt **khi chưa bật defense** và **khi đã bật defense** cho từng loại tấn công.

---

### Demo 1 — Replay Attack: Trước và Sau khi bật Anti-Replay

**Kịch bản:** Attacker bắt được UID hợp lệ và phát lại để qua cổng lần 2.

#### 🔴 CHƯA BẬT DEFENSE (Hệ thống dễ bị tấn công)

**Bước 1:** Khởi động AC server thông thường (cổng 7001):
```bash
# Terminal A
python rfid/rfid_tag.py
```
```bash
# Terminal B
python access_control/ac_server.py
```

**Bước 2:** Attacker thực hiện replay attack:
```bash
# Terminal C
python attacks/replay_attack.py
```

**Kết quả mong đợi (hệ thống BỊ TẤN CÔNG):**
```
[+] Frame captured for replay: {'uid': '04F3B2A1C5', 'command': 'READ'}
[+] Frame replayed: {'uid': '04F3B2A1C5', 'command': 'READ', 'replayed_at': '2026-...'}
Total replays: 1
```

Nếu replay tới AC server ở cổng 7001 với UID hợp lệ:
```bash
# Gửi tay để thấy rõ — Terminal C
python -c "
import socket, json, time
uid = 'A1B2C3D4E5'
for i in range(3):
    s = socket.socket()
    s.connect(('127.0.0.1', 7001))
    s.send(json.dumps({'cmd':'AUTH','uid':uid,'timestamp':time.time()-100}).encode())
    resp = json.loads(s.recv(512).decode())
    s.close()
    print(f'[Lần {i+1}] Status: {resp[\"status\"]}')
"
```

**Output (dễ bị tấn công):**
```
[Lần 1] Status: GRANTED   ← OK, lần đầu hợp lệ
[Lần 2] Status: GRANTED   ← ⚠️ REPLAY THÀNH CÔNG! Vẫn được vào
[Lần 3] Status: GRANTED   ← ⚠️ REPLAY THÀNH CÔNG lần 3!
```

> 💥 **Vấn đề:** `ac_server.py` không kiểm tra timestamp, không lưu token đã dùng. Cùng UID dùng lại bao nhiêu lần cũng được.

---

#### 🟢 ĐÃ BẬT DEFENSE — Anti-Replay Token + Time Window

**Bước 1:** Dừng `ac_server.py` (Ctrl+C). Khởi động **Secure AC** (cổng 7002):
```bash
# Terminal B (thay thế)
python defense/secure_reader.py
```

**Output khởi động:**
```
[SECURE AC] Running @ 127.0.0.1:7002 — Anti-replay ENABLED
```

**Bước 2:** Test với timestamp cũ (giả lập replay từ 100 giây trước):
```bash
python -c "
import socket, json, time
uid = 'A1B2C3D4E5'
old_ts = time.time() - 100   # Timestamp 100 giây trước

s = socket.socket()
s.connect(('127.0.0.1', 7002))
s.send(json.dumps({'cmd':'AUTH','uid':uid,'timestamp':old_ts}).encode())
resp = json.loads(s.recv(512).decode())
s.close()
print(f'Replay với timestamp cũ: {resp}')
"
```

**Output (đã phòng chống):**
```
Replay với timestamp cũ: {'status': 'DENIED', 'msg': 'Timestamp out of window (100.0s)'}
```
*Console server hiện:*
```
[SECURE AC] REPLAY BLOCKED: A1B2C3D4E5 ts_diff=100.0s
```

**Bước 3:** Test replay với cùng timestamp (token reuse):
```bash
python -c "
import socket, json, time
uid = 'A1B2C3D4E5'
ts = time.time()   # Timestamp hợp lệ

# Lần 1 — hợp lệ
s = socket.socket(); s.connect(('127.0.0.1', 7002))
s.send(json.dumps({'cmd':'AUTH','uid':uid,'timestamp':ts}).encode())
resp1 = json.loads(s.recv(512).decode()); s.close()
print(f'[Lần 1] {resp1[\"status\"]}')

# Lần 2 — cùng timestamp = replay
s = socket.socket(); s.connect(('127.0.0.1', 7002))
s.send(json.dumps({'cmd':'AUTH','uid':uid,'timestamp':ts}).encode())
resp2 = json.loads(s.recv(512).decode()); s.close()
print(f'[Lần 2] {resp2[\"status\"]} — {resp2.get(\"msg\",\"\")}')
"
```

**Output (đã phòng chống):**
```
[Lần 1] GRANTED   ← Lần đầu: vào được bình thường
[Lần 2] DENIED — Token already used (replay detected)   ← Bị chặn!
```
*Console server:*
```
[SECURE AC] GRANTED: Nguyen Van A
[SECURE AC] REPLAY DETECTED: A1B2C3D4E5
```

| | Chưa bật Defense | Đã bật Defense |
|---|---|---|
| Server | `ac_server.py` port **7001** | `secure_reader.py` port **7002** |
| Replay cùng UID | ✅ GRANTED mãi mãi | ❌ DENIED ngay lần 2 |
| Timestamp cũ | Không kiểm tra | ❌ DENIED nếu > 5 giây |
| Cơ chế | Chỉ check DB | Time window 5s + token blacklist 60s |

---

### Demo 2 — NFC Write Attack: Trước và Sau khi bật Write Protection

**Kịch bản:** Attacker ghi đè nội dung NDEF lên thẻ NFC (ví dụ: thay URL thành phishing URL).

#### 🔴 CHƯA BẬT DEFENSE (NFC tag không có password)

**Bước 1:** Chạy NFC tag thông thường:
```bash
python nfc/nfc_tag.py
```

**Bước 2:** Chạy NDEF injector:
```bash
python nfc/nfc_injector.py
```

**Kết quả:**
```
[INJECTOR] Connected to NFC tag @127.0.0.1:6011
[INJECTOR] Wrote NDEF payload (phishing URL) - WRITTEN
```

Hoặc ghi tay không cần password:
```bash
python -c "
import socket, json
s = socket.socket(); s.connect(('127.0.0.1', 6011))
s.send(json.dumps({'cmd':'WRITE_NDEF','ndef_hex':'d1010b5501' + '70686973682e636f6d'}).encode())
resp = json.loads(s.recv(512).decode()); s.close()
print(f'Ghi không cần password: {resp}')
"
```
**Output:**
```
Ghi không cần password: {'status': 'WRITTEN', ...}   ← ⚠️ Ghi được ngay!
```

#### 🟢 ĐÃ BẬT DEFENSE — Secure NFC Tag với NDEF HMAC + Write Password

**Bước 1:** Khởi động Secure NFC Tag (cổng 6012):
```bash
python defense/secure_tag.py
```

**Output khởi động:**
```
[SECURE NFC] NTAG213 @ 127.0.0.1:6012
[SECURE NFC] ✓ Write password protected
[SECURE NFC] ✓ NDEF HMAC signed
```

**Bước 2:** Đọc NDEF cùng với chữ ký HMAC:
```bash
python -c "
import socket, json
s = socket.socket(); s.connect(('127.0.0.1', 6012))
s.send(json.dumps({'cmd':'READ_NDEF_SECURE'}).encode())
resp = json.loads(s.recv(512).decode()); s.close()
print('Signature:', resp.get('signature','')[:32], '...')
print('Locked:', resp.get('locked'))
"
```
**Output:**
```
Signature: a3f7c8d12e45b609f1234567890abcde ...
Locked: False
```

**Bước 3:** Thử ghi mà không có password (tấn công thất bại):
```bash
python -c "
import socket, json
s = socket.socket(); s.connect(('127.0.0.1', 6012))
s.send(json.dumps({'cmd':'WRITE_NDEF_SECURE','ndef_hex':'d1010b5501phish'}).encode())
resp = json.loads(s.recv(512).decode()); s.close()
print(f'Ghi không có password: {resp}')
"
```
**Output (đã phòng chống):**
```
Ghi không có password: {'status': 'DENIED', 'msg': 'Wrong PWD (1/3)'}
```
*Console server:*
```
[SECURE NFC] ✗ Write rejected: Wrong PWD (1/3)
```

**Bước 4:** Thử 3 lần sai → thẻ bị khóa vĩnh viễn:
```
[SECURE NFC] ✗ Write rejected: Wrong PWD (1/3)
[SECURE NFC] ✗ Write rejected: Wrong PWD (2/3)
[SECURE NFC] ✗ Write rejected: Tag permanently locked!
```

**Bước 5:** Ghi với password đúng (`41424344` = `ABCD`):
```bash
python -c "
import socket, json
s = socket.socket(); s.connect(('127.0.0.1', 6012))
s.send(json.dumps({'cmd':'WRITE_NDEF_SECURE','ndef_hex':'d1010b5501','pwd':'41424344'}).encode())
resp = json.loads(s.recv(512).decode()); s.close()
print(f'Ghi với password đúng: {resp}')
"
```
**Output:**
```
Ghi với password đúng: {'status': 'WRITTEN', 'msg': 'NDEF updated (requires valid password)'}
```

| | Chưa bật Defense | Đã bật Defense |
|---|---|---|
| Server | `nfc_tag.py` port **6011** | `secure_tag.py` port **6012** |
| Ghi không cần password | ✅ Ghi được tự do | ❌ DENIED |
| Sai password 3 lần | Không kiểm tra | 🔒 Tag khóa vĩnh viễn |
| NDEF signature | Không có | ✅ HMAC-SHA256 |
| Kiểm tra tính toàn vẹn | Không thể | ✅ Verify chữ ký |

---

### Demo 3 — Brute Force UID: Trước và Sau

**Kịch bản:** Attacker dò UID bằng cách thử hàng nghìn giá trị.

#### 🔴 CHƯA BẬT DEFENSE

```bash
# Terminal A
python access_control/ac_server.py   # port 7001, không rate-limit

# Terminal B
python attacks/brute_force.py
```

**Output:**
```
=== RFID UID Brute Force ===
Range: 0x0000 -> 0x1000 (4096 IDs)

[+] FOUND VALID UID: A1B2C3D4E5 -> Nguyen Van A
[+] Total attempts: 82
[+] Valid UIDs found: 1
  ✓ A1B2C3D4E5 (Nguyen Van A)
```

> 💥 Brute force thành công vì AC thông thường không có rate limiting.

#### 🟢 ĐÃ BẬT DEFENSE — Secure AC với Time Window

```bash
# Terminal A
python defense/secure_reader.py   # port 7002
```

Khi brute force gửi request không có timestamp hợp lệ:
```bash
python -c "
import socket, json, time
for uid_int in range(0, 50):
    uid = f'{uid_int:010X}'
    try:
        s = socket.socket(); s.settimeout(0.5)
        s.connect(('127.0.0.1', 7002))
        # Gửi không có timestamp hoặc timestamp sai
        s.send(json.dumps({'cmd':'AUTH','uid':uid,'timestamp':0}).encode())
        resp = json.loads(s.recv(512).decode())
        print(f'{uid}: {resp[\"status\"]}')
        s.close()
    except: pass
"
```

**Output (đã phòng chống):**
```
0000000000: DENIED   ← Timestamp out of window
0000000001: DENIED
0000000002: DENIED
... (tất cả đều DENIED vì timestamp=0 quá cũ)
```

---

### Demo 4 — Eavesdropping: Trước và Sau

**Kịch bản:** Attacker đọc UID từ thẻ mà không cần xác thực.

#### 🔴 CHƯA BẬT DEFENSE

```bash
# Terminal A — Tag thông thường phát UID tự do
python rfid/rfid_tag.py

# Terminal B — Attacker nghe lén
python attacks/eavesdropper.py
```

**Output eavesdropper:**
```
[EAVESDROP] Starting passive scan...
[EAVESDROP] Target: RFID :6001 + NFC :6011

[10:23:45.123] RFID CAPTURED: UID=A1B2C3D4E5 type=EM4100
[10:23:46.456] NFC CAPTURED: UID=04A1B2C3D4E5F6
  -> uri: https://iotlab.edu.vn
  -> text: Employee Card - Nguyen Van A

[EAVESDROP] Saved 2 captures to uid_capture.json
```

> 💥 UID và nội dung NDEF lộ hoàn toàn vì không mã hoá.

#### 🟢 ĐÃ BẬT DEFENSE — Secure NFC Tag

Khi thẻ NFC dùng `secure_tag.py` (port 6012), attacker cố đọc NDEF:
```bash
python -c "
import socket, json
# Attacker kết nối vào secure tag
s = socket.socket(); s.connect(('127.0.0.1', 6012))
# Thử lệnh READ_NDEF thông thường (không tồn tại trên secure tag)
s.send(json.dumps({'cmd':'READ_NDEF'}).encode())
resp = json.loads(s.recv(512).decode()); s.close()
print('Kết quả:', resp)
"
```
**Output:**
```
Kết quả: {'status': 'ERROR'}   ← Lệnh không được hỗ trợ
```

Muốn đọc phải dùng `READ_NDEF_SECURE` và verify chữ ký:
```bash
python -c "
import socket, json, hmac, hashlib
s = socket.socket(); s.connect(('127.0.0.1', 6012))
s.send(json.dumps({'cmd':'READ_NDEF_SECURE'}).encode())
resp = json.loads(s.recv(512).decode()); s.close()

# Verify signature
ndef_bytes = bytes.fromhex(resp['ndef'])
key = b'SecureNDEFKey_IoTLab'
expected_sig = hmac.new(key, ndef_bytes, hashlib.sha256).digest().hex()
actual_sig = resp['signature']
print('Signature valid:', expected_sig == actual_sig)
print('NDEF data được bảo vệ toàn vẹn bằng HMAC-SHA256')
"
```

---

## 🔬 Chạy bộ test tự động

```bash
cd rfid_nfc_lab
python test_lab.py
```

**Kết quả mong đợi:**
```
╔════════════════════════════════════════════════════╗
║  RFID/NFC SECURITY LAB - COMPREHENSIVE TEST SUITE  ║
╚════════════════════════════════════════════════════╝

=== 1. TESTING SIMULATORS ===
[✓] RFID EM4100: UID=A1B2C3D4E5, Type=EM4100
[✓] NFC NTAG213: UID=04A1B2C3..., NDEF-compatible
[✓] Access Control: Status=GRANTED, DB loaded

=== 2. TESTING ATTACKS ===
[✓] Eavesdropping: Captured UID=A1B2C3D4E5 (unencrypted)
[✓] Replay Attack: Server vulnerable - Granted access to A1B2C3D4E5
[✓] Brute Force: Found 0 valid UIDs in 4096 space
[✓] RFID Cloning: Owner info leaked: Nguyen Van A

=== 3. TESTING DEFENSE ===
[✓] Anti-Replay: Token reuse blocked
[○] NDEF HMAC: Server not running (SKIP)
[PARTIAL] NFC Write Protection: NDEF readable, write control in place

============================================================
Overall: 8/10 tests passed (80%)
============================================================
```

> 📌 **Ghi chú về NDEF HMAC SKIP:** Test này cần `secure_tag.py` đang chạy sẵn (port 6012). Chạy riêng `python defense/secure_tag.py` trước rồi chạy lại `test_lab.py` để test này PASS.

---

## 🌐 Web Dashboard

```bash
python dashboard/dashboard.py
```

Truy cập: **http://localhost:8080**

Dashboard hiển thị:
- Event log realtime (cập nhật mỗi 1.5 giây)
- Số lần RFID scan, NFC read, GRANTED/DENIED
- Màu sắc phân loại sự kiện (đỏ = tấn công, xanh = hợp lệ)

---

## 📊 Phân tích bảo mật

```bash
# Phân tích OWASP IoT Top 10
python owasp_analysis.py

# Báo cáo tổng hợp
python final_report.py
```

---

## ⚠️ Tổng hợp lỗ hổng và biện pháp phòng chống

| Lỗ hổng | File có lỗi | Defense | File phòng chống |
|---|---|---|---|
| Replay Attack | `ac_server.py:7001` | Anti-Replay Token + Time Window 5s | `secure_reader.py:7002` |
| NDEF Tampering | `nfc_tag.py:6011` | HMAC-SHA256 Signing | `secure_tag.py:6012` |
| Unauthorized Write | `nfc_tag.py:6011` | Password + AUTHLIM (3 strikes lock) | `secure_tag.py:6012` |
| UID Eavesdropping | `rfid_tag.py:6001` | Không phát UID cleartext | *(cần mã hoá transport layer)* |
| Brute Force UID | `ac_server.py:7001` | Time Window chặn request không có timestamp | `secure_reader.py:7002` |

---

## 🔑 Thông tin thẻ trong database

| UID | Chủ thẻ | Level | Port AC |
|---|---|---|---|
| `A1B2C3D4E5` | Nguyen Van A | EMPLOYEE | 7001, 7002 |
| `DEADBEEF01` | Tran Thi B | ADMIN | 7001, 7002 |
| `CAFEBABE02` | Le Van C | GUEST | 7001 only |

**Write password cho Secure NFC Tag:** `41 42 43 44` (hex) = `ABCD` (ASCII)

---

## 🗺️ Sơ đồ kiến trúc

```
┌──────────────────────────────────────────────────────────────┐
│                    RFID/NFC SECURITY LAB                     │
├──────────────────┬───────────────────────────────────────────┤
│   SIMULATORS     │   DEFENSE LAYER                           │
│                  │                                           │
│  rfid_tag :6001  │   secure_reader :7002 (Anti-Replay)      │
│  nfc_tag  :6011  │   secure_tag    :6012 (HMAC+Password)    │
│  ac_server:7001  │                                           │
├──────────────────┼───────────────────────────────────────────┤
│   ATTACKS        │   MONITORING                              │
│                  │                                           │
│  eavesdropper    │   dashboard :8080 (Flask Web UI)          │
│  replay_attack   │                                           │
│  relay_attack    │                                           │
│  brute_force     │                                           │
│  nfc_injector    │                                           │
└──────────────────┴───────────────────────────────────────────┘
```

---

*Educational Use Only — Not for Production*  
*Lab Version: 1.0 | Generated: 2026-05*
