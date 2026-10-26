> **Ngày: 25/10/2026, Giờ: 17:28**
>
> - **Mô tả lỗi:** Lỗi `invalid tool call` khi tạo file dự án `requirements.txt` do có kèm theo `ArtifactMetadata`.
> - **Nguyên nhân:** `ArtifactMetadata` chỉ hợp lệ khi đường dẫn file đích nằm trong thư mục artifact (`<appDataDir>/brain/<conversation-id>/`). Các file mã nguồn/cấu hình trong workspace không phải là artifact.
> - **Cách khắc phục:** Loại bỏ trường `ArtifactMetadata` trong tool call `write_to_file` khi thao tác với file thuộc workspace dự án.
> - **Bài học rút ra:** Luôn chỉ sử dụng `ArtifactMetadata` cho các file tài liệu/báo cáo lưu trong thư mục `brain`, không đính kèm vào file mã nguồn hoặc cấu hình của repository.

> **Ngày: 26/10/2026, Giờ: 11:58**
>
> - **Mô tả lỗi:** Lỗi `ModuleNotFoundError: No module named 'email_validator'` khi chạy test schema Lead.
> - **Nguyên nhân:** Trường `email` trong `LeadBase` sử dụng kiểu dữ liệu `EmailStr` của Pydantic, kiểu này phụ thuộc vào package `email-validator` nhưng package này chưa được cài đặt trong môi trường.
> - **Cách khắc phục:** Cài đặt package `email-validator` vào môi trường ảo `.venv` và cập nhật vào `requirements.txt`, hoặc cấu hình `pydantic[email]`.
> - **Bài học rút ra:** Khi sử dụng `EmailStr` của Pydantic, cần đảm bảo phụ thuộc `email-validator` được khai báo trong requirements ngay từ đầu.
