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

  Thực hiện thêm: replay, cloning, injector, relay — chạy tương tự và quan sát `GRANTED` hay `DENIED` trên AC.

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

  ---

  9) Ghi chú khắc phục lỗi nhanh

  - Nếu gặp `ModuleNotFoundError: No module named 'colorama'`:

  ```bash
  source venv/bin/activate
  pip install colorama
  ```

  - Nếu gặp `OSError: [Errno 98] Address already in use` khi chạy một server:

  ```bash
  ss -ltnp | grep -E '6001|6011|7001'
  kill <PID>
  ```

  - Nếu test runner báo `Connection refused` cho một service, đảm bảo service đó đã được khởi chạy và lắng nghe trước khi test runner kết nối (xem thứ tự ở trên).

  ---

  10) Tệp kết quả và kiểm tra nhanh

  - Xem file kết quả:

  ```bash
  cat rfid_nfc_lab/test_results.json | jq
  ```

  - Kiểm tra import thư viện (sau khi cài):

  ```bash
  python3 -c "import colorama, ndef; print('colorama', colorama.__version__)"
  ```

  If you want, I can:
  - Tự chạy `python3 rfid_nfc_lab/test_lab.py` ngay bây giờ và gửi kết quả, hoặc
  - Thêm các phần logs/chỉ dẫn debug nâng cao vào README.

  Hãy chọn hành động tiếp theo bạn muốn tôi làm.
```

2) Quick import check:

```bash
python3 -c "import colorama, ndef; print('colorama', colorama.__version__)"
```

Expected output (example):

```text
colorama 0.4.6
```


---

## Chạy bộ kiểm thử toàn diện

File kiểm thử: `rfid_nfc_lab/test_lab.py` — chạy từ thư mục gốc:

```bash
python3 rfid_nfc_lab/test_lab.py
```

Hành động của test runner:

- Khởi động các server cần thiết như subprocess (RFID, NFC, AC)
- Thực hiện các kết nối TCP để kiểm tra response
- Chạy các kịch bản tấn công và kiểm tra defense
- Lưu kết quả vào `rfid_nfc_lab/test_results.json`

---

## Giải thích chi tiết kết quả đầu ra

File log trên console + `rfid_nfc_lab/test_results.json` chứa chi tiết. Các trạng thái phổ biến:

- `PASS`: test đạt yêu cầu (mô-đun phản hồi và hành vi mong đợi xảy ra).
- `FAIL`: test không đạt (không kết nối được, thiếu trường dữ liệu, hoặc response sai).
- `SKIP`: test bị bỏ qua (phụ trợ chưa chạy hoặc không cấu hình).
- `PARTIAL`: chỉ đạt 1 phần mong đợi (ví dụ: NDEF vẫn đọc được nhưng write bị hạn chế).

Ví dụ ý nghĩa:

- `RFID EM4100: PASS, UID=A1B2C3D4E5` → thẻ mô phỏng phát UID (không xác thực).
- `Eavesdropping: PASS` → attacker có thể bắt UID/plaintext.
- `Replay Attack: PASS` → server chấp nhận replay (nếu không bật anti-replay).
- `Anti-Replay: PASS` → defense hoạt động, replay bị chặn.

Thống kê tóm tắt thường thấy (ví dụ tham chiếu): `8/10 tests passed (80%)`.

---

## Ví dụ truy vấn TCP (JSON) giữa client và servers

- RFID Tag: gửi `{'cmd':'QUERY'}` → nhận `{'status':'TAG_PRESENT','uid':..., 'type':..., 'frame':...}`
- NFC Tag: gửi `{'cmd':'READ_NDEF'}` → nhận `{'records':[...records...]}`
- Access Control: gửi `{'cmd':'AUTH','uid':'A1B2C3D4E5'}` → nhận `{'status':'GRANTED','owner':...}`

---

## Vị trí lưu kết quả

- `rfid_nfc_lab/test_results.json` — kết quả chi tiết dạng JSON của lần chạy test gần nhất.

---

## Khắc phục sự cố thường gặp

- ModuleNotFoundError: No module named 'colorama'

  - Nguyên nhân: package chưa được cài trong virtualenv.
  - Khắc phục:

    ```bash
    source venv/bin/activate
    pip install colorama
    # hoặc cài toàn bộ requirements
    pip install -r rfid_nfc_lab/requirements.txt
    ```

- Address already in use / Connection refused

  - Kiểm tra tiến trình đang chiếm cổng và dừng nó.

    ```bash
    ss -ltnp | grep -E '6001|6011|7001'
    kill <PID>
    ```

- Nếu muốn chạy sạch, xóa file kết quả cũ trước khi chạy test:

```bash
rm -f rfid_nfc_lab/test_results.json
```

---

## Ghi chú cuối

- Tôi đã dọn dẹp để chỉ giữ một README duy nhất ở gốc repository. Nếu bạn muốn, tôi có thể:
  - Thêm `colorama` vào `rfid_nfc_lab/requirements.txt` và cài tự động; hoặc
  - Viết thêm phần FAQ / troubleshooting chi tiết hơn.

Hãy cho tôi biết muốn tôi làm bước nào tiếp theo.
