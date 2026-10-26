# Folder Structure

```
task-5/
├── sample_data/
│   └── sample_lead.json        # Dữ liệu JSON mẫu phục vụ kiểm thử CLI
├── secrets/
│   └── .env                    # Biến môi trường thực tế (quản lý trong secrets/, ignored by git)
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routers/
│   │       ├── __init__.py
│   │       └── leads.py          # REST API endpoints cho CRM Lead
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py             # Quản lý cấu hình & biến môi trường
│   │   └── exceptions.py       # Custom exceptions cho Odoo integration
│   ├── features/
│   │   ├── __init__.py
│   │   └── create_lead_with_json.py # CLI script tạo Lead từ file JSON / chuỗi JSON
│   ├── services/
│   │   ├── __init__.py
│   │   └── odoo_client.py      # Client kết nối Odoo qua XML-RPC
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── lead.py             # Pydantic models cho CRM Lead
│   ├── __init__.py
│   └── main.py                 # FastAPI application entrypoint (Task 3)
├── tests/
│   ├── __init__.py
│   └── test_odoo_client.py     # Unit test suite cho Odoo integration
├── .flake8                     # Flake8 linter configuration
├── .gitignore                  # Git ignore rules
├── pyproject.toml              # Tool configurations
├── README.md                   # Hướng dẫn chi tiết cài đặt, cấu hình & chạy dự án
├── requirements.txt            # Production dependencies
└── requirements-dev.txt        # Development dependencies
```
