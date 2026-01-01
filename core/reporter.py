# core/reporter.py
from pathlib import Path
from datetime import datetime
import difflib

class AuditReporter:
    def __init__(self, filename: str):
        self.filename = filename
        self.report_path = Path(f"reports/AUDIT_{Path(filename).stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        self.report_path.parent.mkdir(exist_ok=True)
        self.content = [f"# AI CODE AUDIT REPORT: {filename}", f"**Date:** {datetime.now()}"]

    def add_section(self, title, content, level="##"):
        self.content.append(f"\n{level} {title}\n")
        self.content.append(content)

    def add_diff(self, original: str, fixed: str):
        self.content.append("\n## 🔍 CHANGE LOG (DIFF)\n")
        diff = difflib.unified_diff(
            original.splitlines(), 
            fixed.splitlines(), 
            lineterm="", 
            fromfile="Original", 
            tofile="Fixed by AI"
        )
        diff_text = "\n".join(list(diff))
        if diff_text:
            self.content.append("```diff\n" + diff_text + "\n```")
        else:
            self.content.append("**No code changes were applied.**")

    def save(self):
        self.report_path.write_text("\n".join(self.content), encoding="utf-8")
        return self.report_path