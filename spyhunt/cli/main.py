import argparse
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint
from rich.markdown import Markdown

from ..core.config import Config, get_config, set_config
from ..core.logger import setup_logging, get_logger
from ..core.engine import SpyHuntEngine, ScanJob
from ..modules import register_builtin_modules
from ..core.exceptions import SpyHuntException, ValidationError
from ..core.version import (
    SPYHUNT_VERSION,
    SPYHUNT_NAME,
    SPYHUNT_AUTHOR,
    SPYHUNT_TAGLINE,
)

# Initialize console with proper configuration
console = Console(highlight=False, log_path=False)


def display_banner() -> None:
    """Display the SpyHunt banner with version information."""
    banner = f"""
[bold magenta]
    ███████╗██████╗ ██╗   ██╗    ██╗  ██╗██╗   ██╗███╗   ██╗████████╗
    ██╔════╝██╔══██╗╚██╗ ██╔╝    ██║  ██║██║   ██║████╗  ██║╚══██╔══╝
    ███████╗██████╔╝ ╚████╔╝     ███████║██║   ██║██╔██╗ ██║   ██║   
    ╚════██║██╔═══╝   ╚██╔╝      ██╔══██║██║   ██║██║╚██╗██║   ██║   
    ███████║██║        ██║       ██║  ██║╚██████╔╝██║ ╚████║   ██║   
    ╚══════╝╚═╝        ╚═╝       ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   
[/bold magenta]

[cyan]🛡️  {SPYHUNT_TAGLINE}[/cyan]
[dim]Version {SPYHUNT_VERSION}[/dim]
[dim]By {SPYHUNT_AUTHOR} | Built for professional security assessments[/dim]
"""
    console.print(
        Panel(
            banner,
            title=f"[bold red]{SPYHUNT_NAME} Framework[/bold red]",
            title_align="center",
            border_style="cyan",
            padding=(1, 2),
        )
    )
