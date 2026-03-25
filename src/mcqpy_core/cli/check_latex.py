"""
CLI command to check LaTeX installation and configuration.
"""

from mcqpy_core.cli import main

@main.command('check-latex', help="Check LaTeX installation and configuration.")
def check_latex_command():
    """
    Check if LaTeX is installed and properly configured. 
    Provides the CLI command:
    ```
    mcqpy check-latex
    ```
    This command verifies the presence of LaTeX tools such as `pdflatex` and `latexmk`,
    and attempts to compile a simple LaTeX document to ensure everything is functioning correctly.
    """

    from mcqpy_pdf.utils.check_latex import check_latex_installation
    from rich.console import Console
    
    console = Console()    
    success, details = check_latex_installation()
    
    if success:
        console.print("[bold green]✓ LaTeX is properly installed![/bold green]")
        console.print(f"[green]pdflatex version[/green]: {details['pdflatex'].version}")
        console.print(f"[green]latexmk version[/green]: {details['latexmk'].version}")
        console.print("[green]Compilation test passed successfully.[/green]")
    else:
        console.print(f"[bold red]✗ LaTeX installation issue: {details['error_message']}[/bold red]")
