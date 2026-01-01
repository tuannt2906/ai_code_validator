import re

def extract_critical_issues(report):
    """
    Tổng hợp các lỗi quan trọng từ báo cáo Audit để gửi cho AI sửa (Fixer).
    """
    issues = []
    
    # 1. Lấy lỗi cú pháp (Syntax)
    if report.get("syntax"):
        issues.append(f"SYNTAX ISSUES:\n{report['syntax']}")
        
    # 2. Lấy lỗi logic (Logic)
    if report.get("logic"):
        issues.append(f"LOGIC ISSUES:\n{report['logic']}")
        
    # Trả về chuỗi tổng hợp lỗi
    return "\n\n".join(issues)

def clean_markdown(text):
    """
    Loại bỏ các ký tự Markdown thừa như **bold**, ## Header để text dễ đọc hơn trong CMD.
    (Optional - dùng nếu muốn log sạch hơn)
    """
    # Loại bỏ **text**
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    # Loại bỏ ## Header
    text = re.sub(r'#+\s', '', text)
    return text