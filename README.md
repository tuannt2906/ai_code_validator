ai_code_validator/
├── config.py              # (MỚI) Quản lý cấu hình tập trung
├── client.py              # (NÂNG CẤP) Ollama API Client (dùng requests)
├── core/                  # (GỘP) Chứa toàn bộ logic xử lý
│   ├── __init__.py
│   ├── analyzer.py        # Chứa Logic, Syntax, Perf validators (Gộp 3 file cũ)
│   ├── fixer.py           # Code Fixer
│   └── parser.py          # (NÂNG CẤP) Preprocessor dùng AST mạnh hơn
├── utils.py               # Các hàm tiện ích (clean code, extract error)
├── prompts/               # Giữ nguyên các file .txt
├── main.py                # File chạy chính
└── requirements.txt


1. Chế độ audit (Chỉ kiểm tra, không sửa)
Dùng khi bạn muốn xem code có lỗi gì không để tự sửa.

PowerShell

python main.py examples/sample_code.py --mode audit
Hiển thị: Sẽ hiện các bảng màu Xanh/Đỏ báo lỗi logic và syntax.

2. Chế độ fix (Kiểm tra & Tự sửa 3 vòng)
Dùng cho lỗi thông thường. Nó sẽ kiểm tra -> sửa -> kiểm tra lại (tối đa 3 lần).

PowerShell

python main.py examples/sample_code.py --mode fix
Hiển thị: Bạn sẽ thấy thông báo 🔧 "Đang gọi AI sửa code..." và ✅ "Đã vá lỗi".

3. Chế độ deep (Sửa sâu 5 vòng)
Dùng cho các lỗi logic "cứng đầu" cần DeepSeek suy luận nhiều lần.

PowerShell

python main.py examples/sample_code.py --mode deep

4. Quét folder
python main.py ./examples --mode audit