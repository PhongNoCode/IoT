## Kết quả mong đợi cho các script tấn công và defense

- `attacks/eavesdropper.py`

  Command:
  ```bash
  python attacks/eavesdropper.py
  ```

  Expected output (example):
  ```text
  [EAVESDROP] Listening on 127.0.0.1:6001
  [EAVESDROP] Captured UID=A1B2C3D4E5
  ```

- `attacks/replay_attack.py`

  Command:
  ```bash
  python attacks/replay_attack.py
  ```

  Expected output (example):
  ```text
  [REPLAY] Replaying UID=A1B2C3D4E5 -> Received GRANTED from AC
  ```

- `rfid/rfid_cloner.py`

  Command:
  ```bash
  python rfid/rfid_cloner.py
  ```

  Expected output (example):
  ```text
  [CLONER] Read UID=A1B2C3D4E5 from original tag
  [CLONER] Emulating cloned tag on 127.0.0.1:6003
  ```

- `nfc/nfc_injector.py`

  Command:
  ```bash
  python nfc/nfc_injector.py
  ```

  Expected output (example):
  ```text
  [INJECTOR] Connected to NFC tag @127.0.0.1:6011
  [INJECTOR] Wrote NDEF payload (phishing URL) - bytes written: 64
  ```

---

### Kết quả mong đợi khi chạy `test_lab.py` và `final_report.py`

- `rfid_nfc_lab/test_lab.py` (toàn bộ suite)

  Command:
  ```bash
  python3 rfid_nfc_lab/test_lab.py
  ```

  Expected console summary (example):
  ```text
  Overall: 8/10 tests passed (80%)
  Results saved to rfid_nfc_lab/test_results.json
  ```

  # HƯỚNG DẪN TUẦN TỰ CHẠY LAB RFID/NFC (TỪ TRÊN XUỐNG DƯỚI)

  Mục tiêu: hướng dẫn từng bước, tuần tự, để bạn khởi tạo môi trường, chạy từng server/simulator, thực hiện các test/attack/defense và hiểu ý nghĩa từng kết quả in ra.

  Ghi chú: chạy các lệnh dưới đây từ thư mục gốc repository. Mỗi bước có lệnh, kết quả mong đợi và ý nghĩa của kết quả.

  ---

  1) Chuẩn bị môi trường (chỉ cần làm 1 lần)

  Command:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  python3 -m pip install -r rfid_nfc_lab/requirements.txt
  ```

  Expected output (tóm tắt):
  ```text
  Collecting Flask==2.3.0
  Collecting pycryptodome==3.18.0
  Collecting requests>=2.28.0
  Collecting colorama==0.4.6
  Installing collected packages: ...
  Successfully installed Flask-2.3.0 pycryptodome-3.18.0 requests-... colorama-0.4.6 ndef-0.2
  ```

  Ý nghĩa: môi trường Python đã có đủ thư viện cần thiết; nếu thiếu package, các script sẽ ném ModuleNotFoundError.

  ---

  2) (Bước A) Chạy RFID Tag Simulator

  Command:
  ```bash
  python rfid/rfid_tag.py
  ```

  Expected console output:
  ```text
  [TAG] RFID Tag online @ 127.0.0.1:6001
  [TAG] UID=A1B2C3D4E5 Owner=Nguyen Van A
  [TAG] Waiting for readers...
  ```

  Ý nghĩa: server thẻ đã lắng nghe cổng 6001; khi reader kết nối và gửi `{'cmd':'QUERY'}`, server sẽ trả về UID. Nếu không thấy thông báo này, không có thẻ hoạt động trên cổng 6001.

  ---

  3) (Bước B) Chạy NFC Tag Simulator

  Command:
  ```bash
  python nfc/nfc_tag.py
  ```

  Expected console output:
  ```text
  [NFC TAG] NTAG213 simulator @ 127.0.0.1:6011
  [NFC TAG] UID=04A1B2C3D4E5F6
  [NFC TAG] Waiting for readers...
  ```

  Ý nghĩa: thẻ NFC mô phỏng có NDEF trong bộ nhớ; khi nhận lệnh `READ_NDEF` sẽ trả về danh sách record. Nếu server báo lỗi bind hoặc thoát, cổng có thể bị chiếm.

  ---

  4) (Bước C) Chạy Access Control Server

  Command:
  ```bash
  python access_control/ac_server.py
  ```

  Expected console output:
  ```text
  [AC] Access Control Server @ 127.0.0.1:7001
  [AC] Loaded 3 cards in database
  ```

  Ý nghĩa: server AC sẵn sàng nhận yêu cầu `{'cmd':'AUTH','uid':'...'}`. Khi nhận uid hợp lệ sẽ in `GRANTED` và trả JSON chứa `status: GRANTED`. Nếu server không khởi động vì `Address already in use`, kill tiến trình chiếm cổng.

  ---

  5) (Bước D) (Tuỳ chọn) Khởi động Dashboard (Flask)

  Command:
  ```bash
  python dashboard/dashboard.py
  ```

  Expected console output (tóm tắt):
  ```text
   * Serving Flask app 'dashboard' ...
   * Running on http://127.0.0.1:8080/ (Press CTRL+C to quit)
  ```

  Ý nghĩa: mở trình duyệt đến `http://localhost:8080` để xem event logs, thống kê scans và các alert.

  ---

  6) (Bước E) Chạy Reader đơn giản để kiểm tra luồng end-to-end

  Command (RFID reader):
  ```bash
  python rfid/rfid_reader.py
  ```

  Expected console output (example):
  ```text
  [READER] Connecting to RFID tag @127.0.0.1:6001
  [READER] Scanned UID=A1B2C3D4E5 -> Sent AUTH to AC
  [AC] GRANTED uid=A1B2C3D4E5 owner=Nguyen Van A
  ```

  Ý nghĩa: reader đọc UID từ Tag, gửi đến AC, và AC quyết định `GRANTED`/`DENIED`. Nếu reader không kết nối, kiểm tra status của Tag và AC server.

  ---

  7) (Bước F) Chạy script tấn công (một ví dụ: eavesdropper)

  Command:
  ```bash
  python attacks/eavesdropper.py
  ```

  Expected console output (example):
  ```text
  [EAVESDROP] Listening on 127.0.0.1:6001
  [EAVESDROP] Captured UID=A1B2C3D4E5
  ```

  Ý nghĩa: attacker có thể nghe lén giao tiếp clear-text; nếu dòng `Captured UID` xuất hiện, giao tiếp không được mã hoá.

- `attacks/brute_force.py` (Tấn công brute force UID)

  Command:
  ```bash
  python attacks/brute_force.py
  ```

  Expected console output (example):
  ```text
  === RFID UID Brute Force ===
  Range: 0x0000 -> 0x1000 (4096 IDs)
  Sample rate: mỗi 50 ID

  [+] FOUND VALID UID: A1B2C3D4E5 -> Nguyen Van A
  [+] Total attempts: 80
  [+] Valid UIDs found: 1
    ✓ A1B2C3D4E5 (Nguyen Van A)
  ```

  Ý nghĩa: attacker quét hệ thống để tìm UID hợp lệ bằng brute force; nếu tìm được, có thể sử dụng chúng để truy cập.

- `attacks/relay_attack.py` (Tấn công relay — kéo dài khoảng cách)

  Command:
  ```bash
  python attacks/relay_attack.py
  ```

  Expected console output (example):
  ```text
  === RFID Relay Attack (Distance Extension) ===
  [RELAY] Proxy listening on port 6101
  [RELAY] Forwarding to 127.0.0.1:6001
  [RELAY] ⚠ This allows distance extension attacks!
  [RELAY] Reader connected from 127.0.0.1:...
  ```

  Ý nghĩa: relay hoạt động như proxy giữa reader và tag, cho phép kéo dài khoảng cách tấn công; attacker có thể giao tiếp với tag từ khoảng cách xa.

- `defense/secure_reader.py` (Bảo vệ: Server AC chống replay)

  Command:
  ```bash
  python defense/secure_reader.py
  ```

  Expected console output (example):
  ```text
  [SECURE AC] Running @ 127.0.0.1:7002 — Anti-replay ENABLED
  [SECURE AC] GRANTED: Nguyen Van A
  [SECURE AC] REPLAY DETECTED: A1B2C3D4E5
  ```

  Ý nghĩa: server AC bảo mật chạy trên cổng 7002 với chức năng chống replay; yêu cầu phải có timestamp hợp lệ trong time window, token đã dùng sẽ bị chặn nếu dùng lại.

- `defense/secure_tag.py` (Bảo vệ: NFC tag với NDEF HMAC + write protection)

  Command:
  ```bash
  python defense/secure_tag.py
  ```

  Expected console output (example):
  ```text
  [SECURE NFC] NTAG213 @ 127.0.0.1:6012
  [SECURE NFC] ✓ Write password protected
  [SECURE NFC] ✓ NDEF HMAC signed
  [SECURE NFC] Tag locked, write denied
  ```

  Ý nghĩa: NFC tag bảo mật chạy trên cổng 6012 với khóa ghi và chữ ký NDEF; ghi vào tag yêu cầu password đúng, và NDEF được bảo vệ bằng HMAC-SHA256.

  ---

  8) (Bước G) Chạy bộ kiểm thử tổng hợp (toàn bộ quy trình tự động)

  Command:
  ```bash
  python3 rfid_nfc_lab/test_lab.py
  ```

  Expected console summary (example):
  ```text
  === 1. TESTING SIMULATORS ===
  [✓] RFID EM4100: UID=A1B2C3D4E5, Type=EM4100
  [✓] NFC NTAG213: UID=04A1B2C3..., NDEF-compatible
  [✓] Access Control: Status=GRANTED, DB loaded

  === 2. TESTING ATTACKS ===
  [✓] Eavesdropping: Captured UID=A1B2C3D4E5
  [✓] Replay Attack: Server vulnerable - Granted
  [✓] Brute Force: Found 0 valid UIDs...
  [✓] RFID Cloning: Owner info leaked

  === 3. TESTING DEFENSE ===
  [✓] Anti-Replay: Token reuse blocked
  [✗] NDEF HMAC: Server not running (SKIP)
  [PARTIAL] NFC Write Protection: NDEF readable, write control partial

  Overall: 8/10 tests passed (80%)
  Results saved to rfid_nfc_lab/test_results.json
  ```

  Meaning of results (tóm tắt):

  - `simulators` PASS: các module mô phỏng hoạt động, lắng nghe cổng và trả đúng JSON responses.
  - `attacks` PASS: tấn công tái hiện được lỗ hổng (ví dụ replay cho thấy AC không chống replay).
  - `defense` PARTIAL/SKIP: defense chưa đầy đủ hoặc chưa khởi động; `Anti-Replay` PASS nghĩa là server secure chặn replay.

  File `rfid_nfc_lab/test_results.json` chứa chi tiết từng test (status, details, timestamp).
