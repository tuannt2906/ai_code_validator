import sys
import argparse
import time
import difflib
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from core.analyzer import ValidationOrchestrator
from core.fixer import AutoFixer
from core.reporter import AuditReporter
from utils import extract_critical_issues

console = Console()

def process_single_file(file_path: Path, args, orchestrator, fixer):
    console.rule(f"[bold cyan]Processing: {file_path.name}[/bold cyan]")
    
    original_code = file_path.read_text(encoding="utf-8")
    current_code = original_code
    reporter = AuditReporter(file_path.name)
    
    max_iter = 3 if args.mode == 'fix' else (5 if args.mode == 'deep' else 1)

    for i in range(max_iter):
        reporter.add_section(f"Iteration {i+1}", f"Analysis run at {time.strftime('%H:%M:%S')}")

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
            progress.add_task(description=f"Auditing {file_path.name}...", total=None)
            if i > 0: file_path.write_text(current_code, encoding="utf-8")
            report = orchestrator.run(current_code, str(file_path))

        table = Table(title=f"Audit Summary #{i+1} - {file_path.name}", expand=True)
        table.add_column("Category", style="cyan", width=15)
        table.add_column("Status", justify="center", width=10)
        table.add_column("Brief", style="dim")

        syn_txt = report.get('syntax', '')
        if "⛔" in syn_txt: status_syn = "[red]FAIL[/]"
        elif "⚠️" in syn_txt: status_syn = "[yellow]WARN[/]"
        else: status_syn = "[green]PASS[/]"
        table.add_row("Syntax (Ruff)", status_syn, "Clean" if "PASS" in status_syn else "Issues found (See details below)")

        log_txt = report.get('logic', '')
        if "Skipped" in log_txt: status_log = "[dim]SKIP[/]"
        elif "CRITICAL" in log_txt or "High" in log_txt: status_log = "[red]FAIL[/]"
        else: status_log = "[green]PASS[/]"
        table.add_row("Logic", status_log, "Skipped" if "SKIP" in status_log else "Analysis Complete")

        console.print(table)

        if "PASS" not in report['syntax']:
            console.print(Panel(report['syntax'], title="[bold red]🔍 SYNTAX DETAILS[/bold red]", border_style="red", expand=False))

        if "Skipped" not in report['logic']:
            console.print(Panel(report['logic'], title="[bold blue]🧠 LOGIC ANALYSIS[/bold blue]", border_style="blue", expand=False))
            
        if "Skipped" not in report['performance']:
            console.print(Panel(report['performance'], title="[bold magenta]🚀 PERFORMANCE REVIEW[/bold magenta]", border_style="magenta", expand=False))

        reporter.add_section("Findings", f"**Verdict:** {report['verdict']}\n\n**Logic:**\n{report.get('logic')}")

        if args.mode == 'audit' or report["verdict"] == "PASS":
            if report["verdict"] == "PASS": console.print("[bold green]✨ CODE IS CLEAN![/bold green]")
            break
            
        issues = extract_critical_issues(report)
        if not issues: 
            console.print("[bold green]No fixable issues found.[/bold green]")
            break
        
        with console.status(f"[bold blue]🤖 Fixing {file_path.name}...[/bold blue]"):
            new_code = fixer.apply_fix(current_code, issues)
            
        if new_code.strip() == current_code.strip():
            console.print("[yellow]⚠️ AI could not improve the code further.[/yellow]")
            break
        
        current_code = new_code
        console.print("[green]🔧 Fix applied internally.[/green]")

    reporter.add_diff(original_code, current_code)
    reporter.save()

    if current_code != original_code and args.mode != 'audit':
        file_path.write_text(current_code, encoding="utf-8")
        console.print(f"[bold green]✅ Applied fixes to {file_path.name}[/bold green]")
    elif current_code != original_code:
         file_path.write_text(original_code, encoding="utf-8")

def main():
    parser = argparse.ArgumentParser(description="AI Code Validator Pro")
    parser.add_argument("target", help="Python file or Directory path")
    parser.add_argument("--mode", choices=['audit', 'fix', 'deep'], default='audit')
    args = parser.parse_args()
    
    target_path = Path(args.target)
    if not target_path.exists():
        console.print(f"[bold red]❌ Path not found: {target_path}[/bold red]")
        sys.exit(1)

    orchestrator = ValidationOrchestrator()
    fixer = AutoFixer() if args.mode in ['fix', 'deep'] else None

    files_to_process = []
    if target_path.is_file():
        files_to_process.append(target_path)
    else:
        console.print(f"[yellow]📂 Scanning directory: {target_path}[/yellow]")
        for p in target_path.rglob("*.py"):
            if "venv" not in p.parts and ".git" not in p.parts and "__pycache__" not in p.parts:
                files_to_process.append(p)

    console.print(Panel.fit(f"[bold cyan]AI CODE VALIDATOR PRO[/bold cyan]\nTarget: {target_path}\nFiles: {len(files_to_process)}\nMode: {args.mode.upper()}", border_style="cyan"))
    
    start_time = time.time()
    
    # Backup toàn bộ file gốc trước khi chạy fix
    if args.mode != 'audit':
        for f in files_to_process:
            bak = f.with_suffix(".py.bak")
            if not bak.exists():
                bak.write_text(f.read_text(encoding="utf-8"), encoding="utf-8")

    for py_file in files_to_process:
        try:
            process_single_file(py_file, args, orchestrator, fixer)
        except Exception as e:
            console.print(f"[red]❌ Error processing {py_file.name}: {e}[/red]")

    console.print(f"\n[bold cyan]All Done in {time.time() - start_time:.2f}s[/bold cyan]")

if __name__ == "__main__":
    main()