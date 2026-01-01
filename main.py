import sys
import argparse
import time
from pathlib import Path
from colorama import init, Fore, Style
from core.analyzer import ValidationOrchestrator
from core.fixer import AutoFixer
from utils import extract_critical_issues

init(autoreset=True)

class CLI:
    """Class giúp in ấn đẹp mắt trong CMD"""
    @staticmethod
    def header(text):
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'='*10} {text} {'='*10}{Style.RESET_ALL}")

    @staticmethod
    def step(icon, text):
        print(f"{Fore.YELLOW}{icon} {text}...{Style.RESET_ALL}")

    @staticmethod
    def success(text):
        print(f"{Fore.GREEN}{Style.BRIGHT}✅ {text}{Style.RESET_ALL}")

    @staticmethod
    def fail(text):
        print(f"{Fore.RED}{Style.BRIGHT}❌ {text}{Style.RESET_ALL}")

    @staticmethod
    def info(text):
        print(f"{Fore.WHITE}{Style.DIM}ℹ️  {text}{Style.RESET_ALL}")

    @staticmethod
    def box_output(title, content):
        color = Fore.BLUE
        if "CRITICAL" in content or "HIGH" in content:
            color = Fore.RED
        elif "PASS" in title:
            color = Fore.GREEN

        print(f"\n{color}┌─ {title} {'─'*(60-len(title))}┐")
        for line in content.splitlines():
            print(f"│ {line[:75]:<75} │") 
        print(f"└{'─'*78}┘{Style.RESET_ALL}")

def main():
    parser = argparse.ArgumentParser(description="AI Code Validator Pro")
    parser.add_argument("file", help="Đường dẫn file Python cần kiểm tra")
    parser.add_argument("--mode", choices=['audit', 'fix', 'deep'], default='audit', 
                        help="Chế độ chạy: audit (kiểm tra), fix (tự sửa), deep (sửa sâu nhiều vòng)")
    
    args = parser.parse_args()
    
    file_path = Path(args.file)
    if not file_path.exists():
        CLI.fail(f"Không tìm thấy file: {file_path}")
        sys.exit(1)

    code = file_path.read_text(encoding="utf-8")
    validator = ValidationOrchestrator()
    
    max_iter = 1
    if args.mode == 'fix':
        max_iter = 3
        fixer = AutoFixer()
    elif args.mode == 'deep':
        max_iter = 5
        fixer = AutoFixer()
    else:
        fixer = None

    start_time = time.time()
    CLI.header(f"BẮT ĐẦU QUY TRÌNH: {args.mode.upper().strip()}")
    CLI.info(f"Mục tiêu: {file_path.name}")

    for i in range(max_iter):
        if max_iter > 1:
            CLI.header(f"VÒNG LẶP THỨ {i+1}/{max_iter}")

        report = validator.run(code)
        
        if report.get("syntax"):
            CLI.box_output("SYNTAX REPORT", report["syntax"])
        
        if report.get("logic"):
            CLI.box_output("LOGIC ANALYSIS (DeepSeek-R1)", report["logic"])

        if report.get("performance"):
             CLI.box_output("PERFORMANCE TIPS", report["performance"])

        if report["verdict"] == "PASS":
            CLI.success("CODE ĐẠT CHUẨN! KHÔNG CÓ LỖI NGHIÊM TRỌNG.")
            break
        else:
            CLI.fail("PHÁT HIỆN LỖI TRONG CODE.")
            
            if args.mode == 'audit':
                CLI.info("Gợi ý: Chạy lại với chế độ '--mode fix' để AI tự sửa lỗi.")
                break

            issues = extract_critical_issues(report)
            if not issues:
                CLI.success("Không còn lỗi nào AI có thể tự sửa được.")
                break

            CLI.step("🔧", "Đang gọi AI để sửa code (Qwen-Coder)")
            new_code = fixer.apply_fix(code, issues)
            
            if new_code.strip() == code.strip():
                CLI.info("AI không đưa ra thay đổi nào mới. Dừng lại.")
                break
            
            code = new_code
            # Lưu backup
            backup_file = file_path.with_suffix(f".bak.{i+1}.py")
            file_path.write_text(code, encoding="utf-8")
            CLI.success(f"Đã vá lỗi và lưu đè vào file gốc. (Backup: {backup_file.name})")

    end_time = time.time()
    CLI.info(f"Hoàn thành trong {end_time - start_time:.2f} giây.")

if __name__ == "__main__":
    main()