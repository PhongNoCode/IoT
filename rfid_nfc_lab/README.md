# 🔐 RFID/NFC Security Lab

Dự án lab thực hành bảo mật RFID/NFC — mô phỏng 100% bằng Python, không cần phần cứng thực tế. Dự án đáp ứng đầy đủ 6 yêu cầu tính năng cốt lõi.

> ⚠️ **Chỉ sử dụng cho mục đích giáo dục và nghiên cứu!**

---

## ⚙️ Hướng Dẫn Cài Đặt Ban Đầu

**Yêu cầu hệ thống:** Python 3.8+ và pip

**1. Tạo Virtual Environment (Khuyến nghị)**
```powershell
# Trên Windows
python -m venv venv
venv\Scripts\activate

# Trên Ubuntu/Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

**2. Cài đặt thư viện**
```powershell
pip install -r requirements.txt
```
*(Gồm `Flask`, `colorama`, `ndeflib`, `pycryptodome`...)*

---

## 🧪 Chi Tiết Các Bước Test (Theo 6 Yêu Cầu Tính Năng)

> **Lưu ý quan trọng cho Windows:** Vui lòng sử dụng lệnh `python` thay cho `python3`. Hãy mở **nhiều cửa sổ Terminal (Command Prompt/PowerShell)** khác nhau để chạy song song các server.

### 1. Triển khai thành công 6 module Python mô phỏng hoàn chỉnh
Hệ thống bao gồm 6 module chính có thể chạy độc lập, giao tiếp qua TCP Socket localhost.

**Bước thực hiện:**
- **Terminal 1 (RFID Tag):** Khởi động thẻ RFID (Mô phỏng EM4100 qua port 6001)
  ```powershell
  python rfid/rfid_tag.py
  ```
- **Terminal 2 (NFC Tag):** Khởi động thẻ NFC (Mô phỏng NTAG213 qua port 6011)
  ```powershell
  python nfc/nfc_tag.py
  ```
- **Terminal 3 (Access Control Server):** Khởi động máy chủ kiểm soát truy cập (port 7001)
  ```powershell
  python access_control/ac_server.py
  ```
- **Terminal 4 (RFID Reader):** Chạy thử đầu đọc RFID (sẽ tự quét thẻ và báo về AC Server)
  ```powershell
  python rfid/rfid_reader.py
  # Kết quả: Báo ACCESS GRANTED nếu thẻ hợp lệ
  ```
- **Terminal 5 (NFC Reader):** Chạy thử đầu đọc NFC (quét dữ liệu NDEF)
  ```powershell
  python nfc/nfc_reader.py
  # Kết quả: Hiển thị URL/NDEF data từ thẻ NFC
  ```
- **Terminal 6 (Dashboard):** Xem mục số 6 bên dưới.

### 2. Hiểu sâu cơ chế RFID EM4100, NFC NTAG213 và giao thức Access Control
Các đoạn mã đã được thiết kế phản ánh đúng bản chất giao thức ở cấp độ bytes.

**Bước thực hiện:**
- **RFID EM4100 (UID-only):** Khi chạy `rfid/rfid_reader.py`, bạn sẽ thấy thẻ chỉ phát duy nhất UID (`A1B2C3D4E5`) mà không hề yêu cầu xác thực người đọc. 
- **NFC NTAG213:** Có cấu trúc Page, hỗ trợ NDEF (NFC Data Exchange Format). 
  - Xem kết quả ở Terminal 5, bạn sẽ thấy Reader trích xuất được `URI: https://iotlab.edu.vn/checkin` từ cấu trúc NDEF.
- **Access Control:** Phân quyền theo JSON. Khi thẻ hợp lệ quét, log ở Terminal 3 sẽ in: `[AC] ... GRANTED uid=A1B2C3D4E5 owner=Nguyen Van A`.

### 3. Thực hành 5 loại tấn công: eavesdropping, replay, cloning, NDEF injection, relay
*(Hãy giữ nguyên Terminal 1, 2, 3 đang chạy các server)*

**Bước thực hiện (sử dụng 1 Terminal mới cho Attacker):**
- **3.1 Eavesdropping (Nghe lén):**
  ```powershell
  python attacks/eavesdropper.py
  # Kết quả: Thu thập được UID RFID và dữ liệu NDEF từ thẻ NFC do thẻ phát sóng clear-text.
  ```
- **3.2 Replay Attack (Tấn công lặp lại):**
  ```powershell
  python attacks/replay_attack.py
  # Kết quả: Capture được frame chứa UID, và gửi lại lệnh lên server. Server trả về GRANTED cho attacker dù attacker không có thẻ.
  ```
- **3.3 Cloning (Sao chép thẻ):**
  ```powershell
  python rfid/rfid_cloner.py
  # Kết quả: Đọc UID từ thẻ thật, sau đó tạo một thẻ clone giả mạo UID đó ở port 6003. Lộ thông tin chủ thẻ.
  ```
- **3.4 NDEF Injection (Tiêm mã độc NFC):**
  ```powershell
  python nfc/nfc_injector.py
  # Kết quả: Ghi đè thành công đường link độc hại (phishing URL) vào thẻ NFC (vì thẻ không bật mật khẩu bảo vệ).
  ```
- **3.5 Relay Attack (Tấn công chuyển tiếp):**
  ```powershell
  python attacks/relay_attack.py
  # Kết quả: Thiết lập 2 cổng Proxy, nhận tín hiệu từ Reader, chuyển tiếp cho Tag ở xa để đánh lừa khoảng cách.
  ```

### 4. Phân tích lỗ hổng theo OWASP IoT Top 10 với CVSS score
Dự án có module tự động phân tích và xuất báo cáo điểm số CVSS cho các lỗ hổng tồn tại.

**Bước thực hiện:**
```powershell
python owasp_analysis.py
```
**Kết quả mong đợi:** 
- In ra danh sách 10 lỗ hổng nghiêm trọng (như Insecure Network Services: 8.6, Weak Credentials: 7.5...).
- Xuất toàn bộ chi tiết phân tích ra file `owasp_analysis.json`.

### 5. Triển khai 3 biện pháp phòng thủ
Tắt các Server hiện tại và chạy các phiên bản Server an toàn (Secure) để khắc phục lỗ hổng.

**Bước thực hiện:**
- **5.1 Anti-replay token (Chống tấn công lặp lại):**
  ```powershell
  python defense/secure_reader.py
  ```
  *(Server AC mới sẽ có Time Window & Token. Nếu chạy lại script `attacks/replay_attack.py`, lần gửi lặp lại sẽ bị block với lỗi "Token already used")*
- **5.2 NFC write protection (Chống ghi đè) & 5.3 NDEF HMAC signing (Chống giả mạo NDEF):**
  ```powershell
  python defense/secure_tag.py
  ```
  *(Thẻ NFC lúc này yêu cầu Mật khẩu 4-byte (ABCD) để ghi đè, và mọi dữ liệu đọc ra đều đính kèm chữ ký mã hóa HMAC-SHA256. Attacker không thể dùng `nfc_injector.py` để tiêm mã độc được nữa)*

### 6. Web dashboard Flask giám sát realtime tất cả event
Hệ thống log toàn bộ hành vi, sự kiện, tấn công ra giao diện web thời gian thực.

**Bước thực hiện:**
- Khởi động server Web:
  ```powershell
  python dashboard/dashboard.py
  ```
- Mở trình duyệt và truy cập: **http://localhost:8080**
- Giao diện Dashboard sẽ hiển thị:
  - Tổng số lượng thẻ được quét (RFID / NFC)
  - Biểu đồ thống kê số lượt truy cập (Granted / Denied)
  - Số lượng các đợt tấn công bị chặn (Replay Blocked / NDEF Injected)
  - Cửa sổ Log nhảy thời gian thực mỗi 1.5 giây.

*(Mẹo: Bạn có thể vừa mở Dashboard, vừa chạy các script tấn công ở Bước 3, hoặc quét thẻ ở Bước 1, để thấy số liệu và log nhảy liên tục trên web).*

---

### 🚀 (Tùy Chọn) Chạy File Đánh Giá Toàn Diện
Nếu muốn hệ thống tự động kiểm tra nhanh tất cả các yêu cầu trên, chạy lệnh:
```powershell
python final_report.py
```
Sẽ xuất ra báo cáo `final_report.json` xác nhận Pass 100% các tiêu chí của Lab.

---
**License:** MIT — Educational Use Only.
