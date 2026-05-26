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

  JSON file (`rfid_nfc_lab/test_results.json`) will contain entries like:
  ```json
  {
    "simulators": {
      "RFID EM4100": {"status":"PASS","details":"UID=..."},
      "NFC NTAG213": {"status":"PASS","details":"UID=..."}
    },
    "attacks": {...},
    "defense": {...}
  }
  ```

- `final_report.py` (báo cáo tổng hợp)

  Command:
  ```bash
  python rfid_nfc_lab/final_report.py
  ```

  Expected output (example):
  ```text
  RFID/NFC SECURITY LAB — FINAL COMPREHENSIVE REPORT
  [PASS] 1. SIMULATOR MODULES
  [PASS] 3. FIVE ATTACK TYPES
  FINAL EVALUATION SUMMARY
  Overall Score: 6/6
  ```
# 🔐 RFID/NFC Security Lab — Hướng dẫn chi tiết (File duy nhất)

Mục tiêu: khoá học / lab mô phỏng hệ thống RFID & NFC hoàn chỉnh bằng Python, bao gồm các mô-đun giả lập, demo tấn công, biện pháp phòng chống, dashboard và bộ kiểm thử tự động. Tài liệu này là file README duy nhất trong repository — các bản README trùng lặp đã được dọn.

Lưu ý: Chỉ sử dụng cho mục đích giáo dục và nghiên cứu — không dùng trong môi trường sản xuất.

---

## Mục lục

- Giới thiệu
- Yêu cầu hệ thống
- Thiết lập (virtualenv)
- Cài đặt phụ thuộc
- Chạy từng thành phần (simulators, readers, dashboard)
- Chạy bộ kiểm thử tự động
- Giải thích kết quả và ý nghĩa
- Vị trí lưu kết quả
- Khắc phục sự cố phổ biến

---

## Giới thiệu

Repository chứa một lab mô phỏng đầy đủ các thành phần RFID/NFC:

- `rfid/` — RFID EM4100 tag, reader, cloner
- `nfc/` — NFC NTAG213 tag, reader, injector
- `access_control/` — Access Control server (UID-based)
- `attacks/` — các script tấn công mô phỏng
- `defense/` — các module phòng thủ (anti-replay, secure tag)
- `dashboard/` — Flask dashboard giám sát realtime
- `test_lab.py` — bộ kiểm thử end-to-end
- `final_report.py` — báo cáo tóm tắt kết quả và yêu cầu

---

## Yêu cầu hệ thống

- Python 3.8+ (đã thử nghiệm với Python 3.12)
- pip
- Quyền khởi tạo sockets trên localhost

Khuyến nghị: sử dụng virtual environment để cô lập phụ thuộc.

---

## Thiết lập (virtualenv)

```bash
# Tạo và kích hoạt venv (Linux/macOS)
python3 -m venv venv
source venv/bin/activate

# (Windows PowerShell)
# python -m venv venv
# .\venv\Scripts\Activate.ps1
```

---

## Cài đặt phụ thuộc

```bash
pip install -r rfid_nfc_lab/requirements.txt
```

Nếu gặp lỗi `ModuleNotFoundError: No module named 'colorama'`, chạy thêm:

```bash
pip install colorama
```

---

## Chạy từng thành phần (mở nhiều terminal song song)

1) RFID Tag Simulator (EM4100) — lắng nghe `127.0.0.1:6001`

```bash
python rfid/rfid_tag.py
```

2) NFC Tag Simulator (NTAG213) — lắng nghe `127.0.0.1:6011`

```bash
python nfc/nfc_tag.py
```

3) Access Control Server — lắng nghe `127.0.0.1:7001`

```bash
python access_control/ac_server.py
```

4) Dashboard (Flask) — mặc định `http://localhost:8080`

```bash
python dashboard/dashboard.py
```

5) Readers / Attacks / Defense (chạy khi cần):

```bash
python rfid/rfid_reader.py
python nfc/nfc_reader.py
python attacks/eavesdropper.py
python attacks/replay_attack.py
python attacks/relay_attack.py
python rfid/rfid_cloner.py
python nfc/nfc_injector.py
python defense/secure_reader.py
python defense/secure_tag.py
```

---

### Kết quả mong đợi cho từng lệnh (ví dụ chi tiết)

- Khởi động `RFID Tag`:

  Command:
  ```bash
  python rfid/rfid_tag.py
  ```

  Expected console output (example):
  ```text
  [TAG] RFID Tag online @ 127.0.0.1:6001
  [TAG] UID=A1B2C3D4E5 Owner=Nguyen Van A
  [TAG] Waiting for readers...
  ```

- Khởi động `NFC Tag`:

  Command:
  ```bash
  python nfc/nfc_tag.py
  ```

  Expected console output (example):
  ```text
  [NFC TAG] NTAG213 simulator @ 127.0.0.1:6011
  [NFC TAG] UID=04A1B2C3D4E5F6
  [NFC TAG] Reader connected: ('127.0.0.1', 52344)   # when a reader connects
  ```

- Khởi động `Access Control`:

  Command:
  ```bash
  python access_control/ac_server.py
  ```

  Expected console output (example):
  ```text
  [AC] Access Control Server @ 127.0.0.1:7001
  [AC] Loaded 3 cards in database
  [AC] 2026-05-26 12:34:56 GRANTED uid=A1B2C3D4E5 owner=Nguyen Van A   # when auth occurs
  ```

- Chạy `rfid_reader` (kết nối vào tag và AC):

  Command:
  ```bash
  python rfid/rfid_reader.py
  ```

  Expected console output (example):
  ```text
  [READER] Scanned UID=A1B2C3D4E5 -> Sent AUTH to AC
  [AC] GRANTED uid=A1B2C3D4E5
  ```

---

## Chạy toàn bộ phụ thuộc một lần và kiểm tra

1) Cài tất cả các phụ thuộc (một lần) trong venv:

```bash
source venv/bin/activate
python3 -m pip install -r rfid_nfc_lab/requirements.txt
```

Expected output: pip will download and install packages including `Flask`, `pycryptodome`, `requests`, `colorama`, `ndef`. Near the end you should see lines like:

```text
Successfully installed Flask-2.3.0 pycryptodome-3.18.0 requests-2.32.5 colorama-0.4.6 ndef-<version>
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
