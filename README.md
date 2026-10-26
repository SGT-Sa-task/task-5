# SaigonTrade - Odoo CRM Lead Integration Service

Hệ thống dịch vụ tích hợp dữ liệu khách hàng tiềm năng (**CRM Lead**) vào hệ thống **Odoo ERP** thông qua giao thức **XML-RPC**, cung cấp 2 phương thức giao tiếp linh hoạt:

1. **RESTful API** hiện đại xây dựng trên nền tảng **FastAPI**.
2. **Command Line Interface (CLI)** tiện lợi hỗ trợ nhập dữ liệu từ file JSON, chuỗi JSON thô, hoặc tự động sinh dữ liệu ngẫu nhiên.

---

## 📌 Mục Lục

- [Tính Năng Nổi Bật](#-tính-năng-nổi-bật)
- [Công Nghệ & Thư Viện](#-công-nghệ--thư-viện)
- [Cấu Trúc Thư Mục](#-cấu-trúc-thư-mục)
- [Cài Đặt & Cấu Hình Môi Trường](#-cài-đặt--cấu-hình-môi-trường)
  - [1. Khởi tạo môi trường ảo Python](#1-khởi-tạo-môi-trường-ảo-python)
  - [2. Cài đặt các thư viện phụ thuộc](#2-cài-đặt-các-thư-viện-phụ-thuộc)
  - [3. Cấu hình biến môi trường (.env)](#3-cấu-hình-biến-môi-trường-env)
- [Hướng Dẫn Chạy REST API](#-hướng-dẫn-chạy-rest-api)
  - [Khởi động Uvicorn Server](#khởi-động-uvicorn-server)
  - [Tài liệu API tương tác (Swagger UI)](#tài-liệu-api-tương-tác-swagger-ui)
  - [Endpoints & Sample Payload](#endpoints--sample-payload)
- [Hướng Dẫn Sử Dụng Công Cụ CLI](#-hướng-dẫn-sử-dụng-công-cụ-cli)
- [Chạy Kiểm Thử (Unit Tests)](#-chạy-kiểm-thử-unit-tests)
- [Quy Chuẩn Code & Linter](#-quy-chuẩn-code--linter)

---

## ✨ Tính Năng Nổi Bật

- **FastAPI REST API**: Endpoint `POST /api/leads` hiệu năng cao, tự động validate dữ liệu đầu vào qua Pydantic v2.
- **Tương tác Odoo XML-RPC an toàn**: Lớp `OdooClient` tự động xác thực, lưu cache `uid`, xử lý lỗi kết nối và Odoo Fault chi tiết.
- **Công cụ dòng lệnh CLI**:
  - Hỗ trợ đọc từ file JSON tùy chỉnh (`-f` / `--file`).
  - Hỗ trợ truyền chuỗi JSON thô trực tiếp (`-j` / `--json`).
  - Hỗ trợ tự sinh dữ liệu Lead tiếng Việt ngẫu nhiên phục vụ kiểm thử nhanh (`-r` / `--random`).
- **Bảo mật**: Tuyệt đối không hard-code thông tin nhạy cảm; quản lý tập trung qua biến môi trường.

---

## 🛠 Công Nghệ & Thư Viện

| Thành phần        | Phiên bản / Thư viện       | Mục đích                             |
| :---------------- | :------------------------- | :----------------------------------- |
| **Ngôn ngữ**      | Python 3.11+               | Ngôn ngữ phát triển chính            |
| **Web Framework** | FastAPI (`>=0.115.0`)      | Xây dựng RESTful API                 |
| **ASGI Server**   | Uvicorn (`>=0.30.0`)       | Máy chủ ứng dụng bất đồng bộ         |
| **Validation**    | Pydantic v2 (`>=2.7.0`)    | Validate dữ liệu và sinh schema      |
| **Tích hợp Odoo** | `xmlrpc.client` (built-in) | Giao tiếp từ xa với Odoo qua XML-RPC |
| **Môi trường**    | `python-dotenv`            | Nạp cấu hình từ file `.env`          |
| **Code Style**    | Black & Flake8             | Chuẩn hóa định dạng mã nguồn (PEP 8) |

---

## 📂 Cấu Trúc Thư Mục

```text
task-5/
├── sample_data/
│   └── sample_lead.json          # File JSON mẫu phục vụ kiểm thử
├── secrets/
│   └── .env                      # File biến môi trường thực tế (bảo mật, ignore git)
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routers/
│   │       ├── __init__.py
│   │       └── leads.py          # REST API endpoints cho CRM Lead
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py             # Quản lý cấu hình & biến môi trường
│   │   └── exceptions.py         # Custom exceptions cho Odoo
│   ├── features/
│   │   ├── __init__.py
│   │   └── create_lead_with_json.py # CLI script tạo Lead từ JSON hoặc sinh ngẫu nhiên
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── lead.py               # Pydantic Schemas (LeadBase, LeadCreate, LeadResponse)
│   ├── services/
│   │   ├── __init__.py
│   │   └── odoo_client.py        # Client kết nối Odoo qua giao thức XML-RPC
│   ├── __init__.py
│   └── main.py                   # FastAPI Application Entrypoint
├── tests/
│   ├── __init__.py
│   └── test_odoo_client.py       # Bộ Unit test kiểm thử OdooClient
├── .env.example                  # Mẫu cấu hình biến môi trường
├── .flake8                       # Cấu hình linter Flake8
├── .gitignore                    # Cấu hình bỏ qua các file nhạy cảm và cache
├── pyproject.toml                # Cấu hình công cụ Black
├── requirements.txt              # Thư viện cho môi trường Production
├── requirements-dev.txt          # Thư viện phát triển và kiểm thử
└── README.md                     # Tài liệu hướng dẫn dự án
```

---

## ⚙️ Cài Đặt & Cấu Hình Môi Trường

### 1. Khởi tạo môi trường ảo Python

Tại thư mục gốc của dự án:

```bash
# Trên Windows
python -m venv .venv
.venv\Scripts\activate

# Trên Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Cài đặt các thư viện phụ thuộc

```bash
pip install -r requirements-dev.txt
```

### 3. Cấu hình biến môi trường (.env)

Tạo file `secrets/.env` (hoặc `.env` tại thư mục gốc) dựa trên file mẫu `.env.example`:

```env
# Cấu hình kết nối Odoo XML-RPC
ODOO_URL=http://localhost:8069
ODOO_DB=odoo_db
ODOO_USERNAME=admin
ODOO_PASSWORD=admin_password

# Thiết lập timeout mạng (giây)
ODOO_TIMEOUT=30
```

---

## 🚀 Hướng Dẫn Chạy REST API

### Khởi động Uvicorn Server

Kích hoạt môi trường ảo và chạy lệnh:

```bash
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

Server sẽ lắng nghe tại địa chỉ: `http://127.0.0.1:8000`

### Tài liệu API tương tác (Swagger UI)

Khi server đang chạy, truy cập trình duyệt tại:

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### Endpoints & Sample Payload

#### `POST /api/leads`

Tạo một CRM Lead mới vào hệ thống Odoo.

- **Request Headers**: `Content-Type: application/json`
- **Request Body (JSON mẫu)**:

```json
{
  "name": "Tư vấn triển khai hệ thống ERP Odoo - SaigonTrade",
  "contact_name": "Nguyễn Hoàng Nam",
  "phone": "0987654321",
  "email": "nam.nguyen@example.com",
  "event": "Vietnam Tech Expo 2026",
  "event_location": "Trung tâm Hội chợ và Triển lãm Sài Gòn (SECC)"
}
```

- **Response thành công (HTTP 201 Created)**:

```json
{
  "success": true,
  "lead_id": 12,
  "message": "Lead created successfully in Odoo CRM"
}
```

- **Mã lỗi phản hồi (Error Codes)**:
  - `400 Bad Request`: Dữ liệu không hợp lệ hoặc Odoo từ chối xử lý.
  - `422 Unprocessable Entity`: Sai kiểu dữ liệu trường hoặc thiếu trường bắt buộc (`name`).
  - `502 Bad Gateway`: Không thể kết nối tới máy chủ Odoo (mạng ngắt quãng, timeout).
  - `500 Internal Server Error`: Lỗi xác thực tài khoản Odoo hoặc lỗi hệ thống bất ngờ.

---

## 💻 Hướng Dẫn Sử Dụng Công Cụ CLI

Script [create_lead_with_json.py](../task-5/src/features/create_lead_with_json.py) cho phép thao tác tạo Lead nhanh chóng qua dòng lệnh.

### Xem màn hình trợ giúp:

```bash
python -m src.features.create_lead_with_json --help
```

### 1. Tạo Lead ngẫu nhiên (Random Mode)

Tự động sinh dữ liệu tiếng Việt hợp lệ và gửi thẳng lên Odoo:

```bash
python -m src.features.create_lead_with_json -r
```

### 2. Tạo Lead từ file JSON

```bash
python -m src.features.create_lead_with_json -f sample_data/sample_lead.json
```

### 3. Tạo Lead từ chuỗi JSON thô

```bash
python -m src.features.create_lead_with_json -j "{\"name\": \"Dự án ERP 2026\", \"contact_name\": \"Trần Bình\", \"phone\": \"0912345678\", \"email\": \"binh.tran@example.com\"}"
```

---

## 🧪 Chạy Kiểm Thử (Unit Tests)

Bộ unit test kiểm thử toàn diện lớp `OdooClient` và xử lý ngoại lệ:

```bash
pytest
```

hoặc chạy kiểm tra chi tiết:

```bash
pytest tests/ -v
```

---

## 🎨 Quy Chuẩn Code & Linter

Dự án tuân thủ tiêu chuẩn mã nguồn Python quốc tế:

- **PEP 8**: Giới hạn độ dài dòng 88 ký tự (`Black`).
- **Flake8**: Cấu hình bỏ qua `E203` và `W503` để đồng bộ với Black.
- **Docstrings**: Toàn bộ tài liệu mã nguồn (classes, methods) được viết bằng tiếng Anh chuẩn.
