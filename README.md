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
│   └── rfid_cloner.py      # Tấn công clone thẻ (→ port 6003)
├── nfc/
│   ├── nfc_tag.py          # Tag NFC NTAG213 (port 6011) — CÓ LỖ HỔNG ghi
│   ├── nfc_reader.py       # Reader client
│   └── nfc_injector.py     # Tấn công NDEF injection [--secure flag]
├── access_control/
│   ├── ac_server.py        # Server AC không có anti-replay (port 7001)
│   └── card_db.json
├── attacks/
│   ├── eavesdropper.py     # Nghe lén UID (→ port 6001, 6011)
│   ├── replay_attack.py    # Phát lại UID đã bắt [--secure flag]
│   ├── relay_attack.py     # Relay/proxy kéo dài khoảng cách
│   └── brute_force.py      # Dò UID brute force [--secure flag]
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

> ⚠️ Cài `ndeflib` chứ **không phải** `ndef`. Import trong code là `import ndef` — đây là đúng với `ndeflib`.

---

## 🗺️ Sơ đồ kiến trúc & luồng tấn công

```
                    ┌─────────────────────────────────────┐
                    │         KHÔNG CÓ DEFENSE            │
                    │                                     │
  rfid_tag :6001 ──┼── eavesdropper.py  (sniff UID)      │
  nfc_tag  :6011 ──┼── eavesdropper.py  (sniff NDEF)     │
                   │── nfc_injector.py  (ghi đè NDEF)    │
  ac_server:7001 ──┼── replay_attack.py (phát lại UID)   │
                   │── brute_force.py   (dò UID)         │
                    └─────────────────────────────────────┘
                    ┌─────────────────────────────────────┐
                    │           CÓ DEFENSE ✅              │
                    │                                     │
  secure_tag :6012 ─┼── nfc_injector.py --secure → DENIED │
  secure_reader:7002┼── replay_attack.py --secure → DENIED│
                   │── brute_force.py   --secure → DENIED │
                    └─────────────────────────────────────┘
```

---

## 🚀 Quick Start — Chạy toàn bộ lab tự động

```bash
cd rfid_nfc_lab
python test_lab.py
```

---

## 🎯 HƯỚNG DẪN DEMO: Defense ON vs OFF

Mỗi demo gồm 2 pha: **chạy attack vào hệ thống không có defense → thấy bị tấn công**, rồi **chạy cùng attack vào hệ thống có defense → thấy bị chặn**.

---

### Demo 1 — Replay Attack

**Kịch bản:** Attacker bắt được UID hợp lệ từ eavesdropper, sau đó phát lại để qua cổng lần 2, lần 3 mà không cần thẻ thật.

#### 🔴 CHƯA BẬT DEFENSE

Mở **2 terminal**:

```bash
# Terminal 1 — Khởi động RFID Tag + AC server thường
python rfid/rfid_tag.py
```
```bash
# Terminal 2 — Khởi động AC server (port 7001, KHÔNG có anti-replay)
python access_control/ac_server.py
```
```bash
# Terminal 3 — Chạy replay attack nhắm vào AC port 7001
python attacks/replay_attack.py
```

**Output (bị tấn công):**
```
=== RFID Replay Attack ===
Target: AC Server (port 7001) - No Defense

[+] Frame captured for replay: {'uid': 'A1B2C3D4E5', 'command': 'AUTH'}
[*] Attempt 1 - fresh timestamp (1779812769.7)...
[Attempt 1] -> GRANTED Nguyen Van A

[*] REPLAY: Resend AUTH with SAME timestamp (1779812769.7)...
[Attempt 2 - Replay] -> GRANTED - Nguyen Van A [!] ATTACK SUCCEEDED

[*] REPLAY with OLD timestamp (100s ago: 1779812670.8)...
[Attempt 3 - Old TS] -> GRANTED - Nguyen Van A [!] ATTACK SUCCEEDED
```

> 💥 Server `ac_server.py` chấp nhận cùng UID với bất kỳ timestamp nào — không có kiểm tra gì cả.

#### 🟢 ĐÃ BẬT DEFENSE

```bash
# Terminal 1 — Khởi động Secure AC (port 7002, có anti-replay)
python defense/secure_reader.py
```
```bash
# Terminal 2 — Chạy replay attack nhắm vào Secure AC port 7002
python attacks/replay_attack.py --secure
```

**Output (bị chặn):**
```
=== RFID Replay Attack ===
Target: SECURE AC (port 7002) - Defense ON

[+] Frame captured for replay: {'uid': 'A1B2C3D4E5', 'command': 'AUTH'}
[*] Attempt 1 - fresh timestamp (1779812791.2)...
[Attempt 1] -> GRANTED Nguyen Van A

[*] REPLAY: Resend AUTH with SAME timestamp (1779812791.2)...
[Attempt 2 - Replay] -> DENIED - Token already used (replay detected) [OK] BLOCKED

[*] REPLAY with OLD timestamp (100s ago: 1779812691.2)...
[Attempt 3 - Old TS] -> DENIED - Timestamp out of window (100.0s) [OK] BLOCKED
```

*Console `secure_reader.py`:*
```
[SECURE AC] Running @ 127.0.0.1:7002
[SECURE AC] Anti-replay ENABLED  (time window: 5.0s)
[SECURE AC] Rate limiting ENABLED (max 5 req / 10s, lockout 30s)
[SECURE AC] GRANTED: Nguyen Van A from 127.0.0.1
[SECURE AC] REPLAY DETECTED: A1B2C3D4E5
[SECURE AC] REPLAY BLOCKED: A1B2C3D4E5 ts_diff=100.0s
```

| | Chưa bật Defense | Đã bật Defense |
|---|---|---|
| File server | `access_control/ac_server.py` `:7001` | `defense/secure_reader.py` `:7002` |
| Flag attack | `python attacks/replay_attack.py` | `python attacks/replay_attack.py --secure` |
| Replay cùng timestamp | ✅ GRANTED | ❌ DENIED |
| Timestamp cũ 100s | ✅ GRANTED | ❌ DENIED (time window 5s) |

---

### Demo 2 — NDEF Injection Attack

**Kịch bản:** Attacker ghi đè NDEF lên thẻ NFC — thay URL thật bằng phishing URL, thêm text giả mạo.

#### 🔴 CHƯA BẬT DEFENSE

```bash
# Terminal 1 — NFC Tag thường (port 6011, ghi tự do)
python nfc/nfc_tag.py
```
```bash
# Terminal 2 — Inject phishing URL vào NFC tag
python nfc/nfc_injector.py
```

**Output (bị tấn công):**
```
=== NFC NDEF Injection Attack ===
Target: NFC Tag (port 6011) — No Defense

[INJECT] Overwriting with: phishing_url
[INJECT] Result: {'status': 'WRITTEN', 'msg': 'NDEF updated'}
[VERIFY] New NDEF: [{'type': 'uri', 'value': 'https://evil.attacker.com/steal-credentials'}]

[INJECT] Overwriting with: malicious_text
[INJECT] Result: {'status': 'WRITTEN', 'msg': 'NDEF updated'}
[VERIFY] New NDEF: [{'type': 'text', 'data': 'Hệ thống đã cập nhật. Truy cập: bit.ly/fake'}]
```

> 💥 Thẻ không yêu cầu password — bất kỳ ai cũng có thể ghi đè nội dung.

#### 🟢 ĐÃ BẬT DEFENSE

```bash
# Terminal 1 — Secure NFC Tag (port 6012, password + HMAC)
python defense/secure_tag.py
```
```bash
# Terminal 2 — Thử inject vào Secure NFC Tag
python nfc/nfc_injector.py --secure
```

**Output (bị chặn):**
```
=== NFC NDEF Injection Attack ===
Target: SECURE NFC Tag (port 6012) — Defense ON

[INJECT] Overwriting with: phishing_url
[INJECT] Result: {'status': 'DENIED', 'msg': 'Wrong PWD (1/3)'}
[VERIFY] New NDEF: ...  ← NDEF không thay đổi

[INJECT] Overwriting with: malicious_text
[INJECT] Result: {'status': 'DENIED', 'msg': 'Wrong PWD (2/3)'}
```

*Console server `secure_tag.py` hiện:*
```
[SECURE NFC] ✗ Write rejected: Wrong PWD (1/3)
[SECURE NFC] ✗ Write rejected: Wrong PWD (2/3)
```

| | Chưa bật Defense | Đã bật Defense |
|---|---|---|
| File server | `nfc/nfc_tag.py` `:6011` | `defense/secure_tag.py` `:6012` |
| Flag attack | `python nfc/nfc_injector.py` | `python nfc/nfc_injector.py --secure` |
| Ghi không cần password | ✅ WRITTEN | ❌ DENIED |
| Sai password 3 lần | Không kiểm tra | 🔒 Tag khóa vĩnh viễn |
| NDEF có chữ ký HMAC | ❌ Không có | ✅ HMAC-SHA256 |

---

### Demo 3 — UID Brute Force

**Kịch bản:** Attacker dò UID bằng cách gửi hàng nghìn giá trị ngẫu nhiên — tìm UID hợp lệ để giả mạo vào.

#### 🔴 CHƯA BẬT DEFENSE

```bash
# Terminal 1 — AC server thường (không có rate limiting)
python access_control/ac_server.py
```
```bash
# Terminal 2 — Brute force vào port 7001
python attacks/brute_force.py
```

**Output (bị tấn công — tìm ra UID hợp lệ):**
```
Target: AC Server (port 7001) - No Defense

=== RFID UID Brute Force ===
Range: 0xA1B2C3D4E0 -> 0xA1B2C3D4F0 (16 IDs)
Sample rate: every 1 ID

[?] Interesting response: A1B2C3D4E0 -> UID A1B2C3D4E0 not authorized
[?] Interesting response: A1B2C3D4E1 -> UID A1B2C3D4E1 not authorized
...
[+] FOUND VALID UID: A1B2C3D4E5 -> Nguyen Van A
...
[+] Total attempts: 16
[+] Valid UIDs found: 1
  [*] A1B2C3D4E5 (Nguyen Van A)
```

> 💥 Server không có rate limiting — brute force thoải mái, quét từng UID một, tìm ra UID hợp lệ trong range.

#### 🟢 ĐÃ BẬT DEFENSE — Rate Limiting + Anti-Replay

```bash
# Terminal 1 — Secure AC (rate limit: max 5 req/10s, lockout 30s)
python defense/secure_reader.py
```
```bash
# Terminal 2 — Brute force vào port 7002
python attacks/brute_force.py --secure
```

**Output (bị chặn — không tìm ra gì):**
```
Target: SECURE AC (port 7002) - Defense ON

=== RFID UID Brute Force ===
Range: 0xA1B2C3D4E0 -> 0xA1B2C3D4F0 (16 IDs)
Sample rate: every 1 ID

[*] Tried 5 IDs, found 0...
[?] Interesting response: A1B2C3D4E5 -> Too many attempts - locked out for 30.0s
[?] Interesting response: A1B2C3D4E6 -> IP locked out for 30s (brute force detected)
[?] Interesting response: A1B2C3D4E7 -> IP locked out for 30s (brute force detected)
...
[+] Total attempts: 16
[+] Valid UIDs found: 0
```

*Console `secure_reader.py`:*
```
[SECURE AC] RATE LIMIT: 127.0.0.1 locked out for 30.0s
[SECURE AC] BLOCKED 127.0.0.1: Too many attempts - locked out for 30.0s
```

> ✅ Sau 5 request trong 10 giây, IP bị khóa 30 giây. UID hợp lệ `A1B2C3D4E5` bị bỏ lỡ vì request đến lúc đã bị lockout.

| | Chưa bật Defense | Đã bật Defense |
|---|---|---|
| File server | `access_control/ac_server.py` `:7001` | `defense/secure_reader.py` `:7002` |
| Flag attack | `python attacks/brute_force.py` | `python attacks/brute_force.py --secure` |
| Rate limiting | ❌ Không có | ✅ Max 5 req/10s, lockout 30s |
| Anti-replay | ❌ Không có | ✅ Time window 5s + token blacklist |
| Brute force tìm UID | ✅ Tìm ra `A1B2C3D4E5` | ❌ Bị lockout, 0 UID tìm ra |

---

### Demo 4 — Eavesdropping (Nghe lén)

**Kịch bản:** Attacker đọc UID và toàn bộ nội dung NDEF từ thẻ mà không cần xác thực — giống như đưa điện thoại cạnh thẻ.

#### 🔴 CHƯA BẬT DEFENSE

```bash
# Terminal 1 — RFID Tag thường (phát UID tự do, không mã hoá)
python rfid/rfid_tag.py

# Terminal 2 — NFC Tag thường (NDEF đọc tự do)
python nfc/nfc_tag.py

# Terminal 3 — Nghe lén cả RFID lẫn NFC
python attacks/eavesdropper.py
```

**Output (bị tấn công):**
```
[EAVESDROP] Starting passive scan...
[EAVESDROP] Target: RFID :6001 + NFC :6011

[22:54:01.123] RFID CAPTURED: UID=A1B2C3D4E5 type=EM4100
[22:54:02.456] NFC CAPTURED: UID=04A1B2C3D4E5F6
  -> uri: https://iotlab.edu.vn
  -> text: Employee Card - Nguyen Van A

[EAVESDROP] Saved 10 captures to uid_capture.json
```

> 💥 UID, tên chủ thẻ, URL đều bị lộ vì không mã hoá.

#### 🟢 ĐÃ BẬT DEFENSE — Secure NFC Tag

```bash
# Terminal 1 — Secure NFC Tag (port 6012)
python defense/secure_tag.py
```

`eavesdropper.py` kết nối vào port 6011 (NFC tag thường) — nếu chỉ chạy `secure_tag.py`, eavesdropper sẽ không thấy NFC (port 6011 không có server). Để demo rõ sự khác biệt, so sánh lệnh đọc NDEF:

```bash
# Đọc NDEF từ tag thường (port 6011) — lộ toàn bộ:
python nfc/nfc_reader.py

# Đọc từ Secure Tag (port 6012) — chỉ trả về NDEF + chữ ký, không có cleartext:
python -c "
import socket, json
s = socket.socket(); s.connect(('127.0.0.1', 6012))
s.send(json.dumps({'cmd':'READ_NDEF_SECURE'}).encode())
resp = json.loads(s.recv(512).decode()); s.close()
print('Signature:', resp['signature'][:32], '...')
print('Locked:', resp['locked'])
print('(NDEF là bytes hex — không đọc được nếu không có key HMAC)')
"
```

---

### Demo 5 — RFID Cloning (Clone thẻ)

**Kịch bản:** Sau khi bắt được UID qua eavesdropper, attacker tạo thẻ clone phát UID giả.

```bash
# Terminal 1 — RFID Tag gốc đang chạy
python rfid/rfid_tag.py

# Terminal 2 — Cloner: đọc UID thẻ gốc, sau đó phát clone trên port 6003
python rfid/rfid_cloner.py
```

**Output:**
```
[*] Step 1: Reading original card UID...
[*] Captured UID: A1B2C3D4E5
[*] Step 2: Starting clone tag...
[CLONE TAG] Running on port 6003
[CLONE TAG] Broadcasting STOLEN UID=A1B2C3D4E5
```

Thẻ clone trên port 6003 bây giờ giả mạo hoàn toàn thẻ gốc — bất kỳ reader nào kết nối vào sẽ nhận được UID của Nguyen Van A.

---

### Demo 6 — Relay Attack (Kéo dài khoảng cách)

**Kịch bản:** Attacker proxy giao tiếp giữa reader và tag qua mạng — cho phép dùng thẻ từ xa.

```bash
# Terminal 1 — RFID Tag gốc
python rfid/rfid_tag.py

# Terminal 2 — Relay proxy (lắng nghe port 6101, forward tới 6001)
python attacks/relay_attack.py
```

**Output:**
```
=== RFID Relay Attack (Distance Extension) ===
Attacker tại vị trí A với proxy:6101
Thẻ tại vị trí B (có proxy:6102)

[RELAY] Proxy listening on port 6101
[RELAY] Forwarding to 127.0.0.1:6001
[RELAY] ⚠ This allows distance extension attacks!
[RELAY] Reader connected from 127.0.0.1:...
[RELAY] Relayed response: UID=A1B2C3D4E5
```

> Reader ở port 6101 nhận được UID y hệt tag thật ở port 6001 — attacker có thể đặt reader ở cửa, tag ở xa 100m vẫn hoạt động.

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
[✓] NDEF HMAC: Signature a3f7c8d12e45b609...
[PARTIAL] NFC Write Protection: NDEF readable, write control in place

============================================================
Overall: 9/10 tests passed (90%)
============================================================
```

---

## 🌐 Web Dashboard

```bash
python dashboard/dashboard.py
# Mở trình duyệt: http://localhost:8080
```

---

## 📊 Phân tích OWASP IoT Top 10

```bash
python owasp_analysis.py   # Phân tích 10 lỗ hổng với CVSS score
python final_report.py     # Báo cáo tổng hợp đầy đủ
```

---

## 🔑 Thông tin thẻ trong database

| UID | Chủ thẻ | Level |
|---|---|---|
| `A1B2C3D4E5` | Nguyen Van A | EMPLOYEE |
| `DEADBEEF01` | Tran Thi B | ADMIN |
| `CAFEBABE02` | Le Van C | GUEST |

**Write password Secure NFC Tag:** `41424344` hex = `ABCD` ASCII

---

## ⚠️ Tổng hợp — Attack vs Defense

| Tấn công | File tấn công | Server bị lỗ hổng | Server có phòng chống | Cơ chế defense |
|---|---|---|---|---|
| Replay | `attacks/replay_attack.py` | `ac_server.py :7001` | `defense/secure_reader.py :7002` | Time window 5s + token blacklist |
| NDEF Injection | `nfc/nfc_injector.py` | `nfc/nfc_tag.py :6011` | `defense/secure_tag.py :6012` | Write password + HMAC-SHA256 |
| Brute Force | `attacks/brute_force.py` | `ac_server.py :7001` | `defense/secure_reader.py :7002` | Rate limit 5 req/10s, lockout 30s |
| Eavesdropping | `attacks/eavesdropper.py` | `rfid/rfid_tag.py :6001` | *(cần mã hoá transport layer)* | — |
| Relay | `attacks/relay_attack.py` | `rfid/rfid_tag.py :6001` | *(cần distance bounding protocol)* | — |
| Cloning | `rfid/rfid_cloner.py` | `rfid/rfid_tag.py :6001` | *(cần mutual authentication)* | — |

> **Cờ `--secure`** có trên: `replay_attack.py`, `brute_force.py`, `nfc_injector.py`
> Dùng **cùng 1 file attack**, thêm `--secure` → chuyển sang nhắm server đã có defense → thấy ngay sự khác biệt.


---

*Educational Use Only — Not for Production*  
*Lab Version: 1.0*
