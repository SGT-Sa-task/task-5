# Tech Stack

## Ngôn ngữ & Nền tảng
- **Python**: 3.11.x
- **Môi trường ảo**: `.venv` (virtualenv)

## Backend & API
- **FastAPI** (`>=0.115.0,<1.0.0`): Web framework chính tạo RESTful API endpoints.
- **Uvicorn (standard)** (`>=0.30.0,<1.0.0`): ASGI Server với uvloop, httptools.
- **Pydantic** (`>=2.7.0,<3.0.0`): Khai báo Schema, validate dữ liệu đầu vào.
- **Python-dotenv** (`>=1.0.0,<2.0.0`): Đọc và quản lý biến môi trường từ `.env`.
- **xmlrpc.client**: Thư viện chuẩn tích hợp sẵn trong Python kết nối Odoo qua giao thức XML-RPC.

## Code Quality & Dev Tools
- **Black** (`>=24.4.0,<25.0.0`): Code Formatter (line-length: 88, PEP 8).
- **Flake8** (`>=7.0.0,<8.0.0`): Linter (ignore: E203, W503).
