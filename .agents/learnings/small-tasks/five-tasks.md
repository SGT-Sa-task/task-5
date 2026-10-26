Để triển khai hoàn chỉnh Task 5 với phương án **FastAPI + XML-RPC**, bạn có thể chia thành 4 nhóm nhiệm vụ chính sau đây:

**1. Khởi tạo dự án và cấu hình môi trường**

- Tạo thư mục dự án và thiết lập môi trường ảo (Virtual Environment) cho Python.
- Cài đặt các thư viện cần thiết: `pip install fastapi uvicorn pydantic python-dotenv`.
- Tạo file `.env` để lưu trữ an toàn các thông tin cấu hình của hệ thống Odoo: `ODOO_URL`, `ODOO_DB`, `ODOO_USERNAME`, `ODOO_PASSWORD`.
- Tạo cấu trúc thư mục cơ bản (ví dụ: `main.py` cho API, `odoo_client.py` cho xử lý XML-RPC, `schemas.py` cho Pydantic model).

**2. Xây dựng module kết nối Odoo (XML-RPC)**

- **Viết hàm xác thực (Authenticate):** Sử dụng `xmlrpc.client` để gửi thông tin đăng nhập từ `.env` lên Odoo và lấy về `uid`. Thêm `try...except` để bắt lỗi đăng nhập sai hoặc sai tên Database.
- **Viết hàm tạo Lead:** Sử dụng `execute_kw` với phương thức `create` nhắm vào model `crm.lead`.
- **Xử lý ngoại lệ (Error Handling):** Bắt các lỗi cụ thể như Odoo server không phản hồi (timeout), cấu trúc dữ liệu gửi lên bị từ chối, hoặc kết nối mạng bị gián đoạn.

**3. Xây dựng REST API Endpoint (FastAPI)**

- **Định nghĩa Schema (Pydantic):** Tạo class `LeadCreate` chứa các trường cần thiết: `name`, `contact_name`, `phone`, `email`, `event`, `event_location`. Khai báo rõ trường nào là bắt buộc (Required), trường nào là tùy chọn (Optional) để FastAPI tự động validate (xử lý lỗi thiếu field).
- **Tạo API Endpoint:** Viết hàm định tuyến `POST /api/leads`.
- **Ghép nối logic:** Nhận payload từ request, kiểm tra hợp lệ, sau đó gọi hàm tạo Lead ở bước 2 để đẩy vào Odoo.
- **Chuẩn hóa Response:** Trả về HTTP status 200 kèm `lead_id` và trạng thái `success` nếu thành công. Nếu thất bại, trả về HTTP status 400 hoặc 500 kèm thông báo lỗi rõ ràng.

**4. Hoàn thiện sản phẩm bàn giao (Deliverables)**

- **Viết file README.md:** Hướng dẫn chi tiết cách cài đặt môi trường, cấu hình file `.env`, cách chạy server (`uvicorn main:app --reload`), và cách kiểm thử.
- **Tạo Sample Payload:** Lưu lại một đoạn JSON mẫu dùng để test việc tạo Lead.
- **Kiểm thử và Demo:** Truy cập Swagger UI (FastAPI tự động tạo ở đường dẫn `/docs`) để test gửi request thực tế, chụp ảnh màn hình hoặc quay video chứng minh Lead đã được tạo thành công trong Odoo.

Bạn muốn bắt tay vào việc tạo cấu trúc thư mục và file `.env` trước, hay muốn mình viết luôn mã nguồn cho phần kết nối Odoo bằng XML-RPC?
