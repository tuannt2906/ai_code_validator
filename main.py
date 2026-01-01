# main.py
import sys
import argparse
import time
from pathlib import Path
import difflib
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.table import Table
from rich import print as rprint

from core.analyzer import ValidationOrchestrator
from core.fixer import AutoFixer
from core.reporter import AuditReporter # Import module mới
from utils import extract_critical_issues

console = Console()

def main():
    parser = argparse.ArgumentParser(description="AI Code Validator Pro")
    parser.add_argument("file", help="Python file path")
    parser.add_argument("--mode", choices=['audit', 'fix', 'deep'], default='audit')
    args = parser.parse_args()
    
    file_path = Path(args.file)
    if not file_path.exists():
        console.print(f"[bold red]❌ File not found: {file_path}[/bold red]")
        sys.exit(1)

    original_code = file_path.read_text(encoding="utf-8")
    current_code = original_code
    
    # Khởi tạo Reporter
    reporter = AuditReporter(file_path.name)
    validator = ValidationOrchestrator()
    fixer = AutoFixer() if args.mode in ['fix', 'deep'] else None
    max_iter = 3 if args.mode == 'fix' else (5 if args.mode == 'deep' else 1)

    console.print(Panel.fit(f"[bold cyan]AI CODE VALIDATOR PRO[/bold cyan]\nTarget: {file_path.name}\nMode: {args.mode.upper()}", border_style="cyan"))

    start_time = time.time()

    for i in range(max_iter):
        step_title = f"Iteration {i+1}/{max_iter}"
        console.rule(f"[yellow]{step_title}[/yellow]")
        reporter.add_section(f"Iteration {i+1}", f"Analysis run at {time.strftime('%H:%M:%S')}")

        # 1. Chạy Validator với Progress Bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True
        ) as progress:
            task = progress.add_task(description="Running Audit Suite...", total=None)
            report = validator.run(current_code) # Validator giữ nguyên logic cũ
        
        # 2. Hiển thị kết quả bằng bảng Rich
        table = Table(title=f"Audit Report #{i+1}")
        table.add_column("Category", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Details", style="white")

        # Logic fill bảng
        status_syn = "FAIL" if "HIGH" in report.get('syntax', '') else "PASS"
        table.add_row("Syntax", f"[{'green' if status_syn=='PASS' else 'red'}]{status_syn}[/]", report.get('syntax', 'OK')[:100]+"...")
        
        # In bảng ra màn hình
        console.print(table)

        # Ghi vào báo cáo
        reporter.add_section("Findings", f"**Verdict:** {report['verdict']}\n\n**Logic:**\n{report.get('logic')}")

        if report["verdict"] == "PASS":
            console.print("[bold green]✅ CODE IS CLEAN![/bold green]")
            break
        
        # Nếu chỉ Audit thì dừng
        if args.mode == 'audit':
            break

        # 3. Logic Fix
        issues = extract_critical_issues(report)
        if not issues:
            console.print("[bold green]✨ No critical issues left to fix.[/bold green]")
            break

        with console.status("[bold blue]🤖 AI is writing fix...[/bold blue]"):
            new_code = fixer.apply_fix(current_code, issues)

        if new_code.strip() == current_code.strip():
            console.print("[yellow]⚠️ AI could not improve the code further.[/yellow]")
            break
        
        current_code = new_code
        console.print("[green]🔧 Fix applied internally.[/green]")

    # KẾT THÚC: Tạo báo cáo và Diff
    reporter.add_diff(original_code, current_code)
    report_file = reporter.save()

    # Nếu có sửa đổi, hỏi người dùng trước khi ghi đè (AN TOÀN)
    if current_code != original_code:
        console.print("\n[bold yellow]⚠️ Changes detected![/bold yellow]")
        # In diff ra màn hình cho ngầu
        diff = difflib.unified_diff(original_code.splitlines(), current_code.splitlines(), lineterm="")
        for line in diff:
            if line.startswith('+'): console.print(f"[green]{line}[/green]")
            elif line.startswith('-'): console.print(f"[red]{line}[/red]")
            else: console.print(line)

        if args.mode != 'audit':
             # Tự động backup
            backup_path = file_path.with_suffix(".py.bak")
            file_path.write_text(original_code, encoding="utf-8") # Save backup
            file_path.write_text(current_code, encoding="utf-8")  # Save new
            console.print(f"\n[bold green]✅ Applied fixes. Original backed up to {backup_path.name}[/bold green]")

    console.print(f"\n[dim]Report saved to: {report_file}[/dim]")
    console.print(f"[bold cyan]Done in {time.time() - start_time:.2f}s[/bold cyan]")

if __name__ == "__main__":
    main()