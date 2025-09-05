import sys
import time
from typing import Optional


class Colors:
    """ANSI color codes for terminal output"""
    
    # Basic colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Styles
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    
    @classmethod
    def disable(cls):
        """Disable all colors (for non-terminal output)"""
        for attr in dir(cls):
            if not attr.startswith('_') and attr != 'disable':
                setattr(cls, attr, '')


class Logger:
    """Enhanced logger with colorful output and formatting"""
    
    def __init__(self, enable_colors: bool = True):
        self.enable_colors = enable_colors and sys.stdout.isatty()
        if not self.enable_colors:
            Colors.disable()
    
    def _format_timestamp(self) -> str:
        """Get formatted timestamp"""
        return time.strftime("%H:%M:%S")
    
    def info(self, message: str, prefix: Optional[str] = None):
        """Log an info message"""
        timestamp = f"{Colors.DIM}[{self._format_timestamp()}]{Colors.RESET}"
        prefix_str = f" {Colors.BLUE}[{prefix}]{Colors.RESET}" if prefix else ""
        print(f"{timestamp}{prefix_str} {Colors.CYAN}ℹ{Colors.RESET}  {message}")
    
    def success(self, message: str, prefix: Optional[str] = None):
        """Log a success message"""
        timestamp = f"{Colors.DIM}[{self._format_timestamp()}]{Colors.RESET}"
        prefix_str = f" {Colors.BLUE}[{prefix}]{Colors.RESET}" if prefix else ""
        print(f"{timestamp}{prefix_str} {Colors.GREEN}✓{Colors.RESET}  {message}")
    
    def warning(self, message: str, prefix: Optional[str] = None):
        """Log a warning message"""
        timestamp = f"{Colors.DIM}[{self._format_timestamp()}]{Colors.RESET}"
        prefix_str = f" {Colors.BLUE}[{prefix}]{Colors.RESET}" if prefix else ""
        print(f"{timestamp}{prefix_str} {Colors.YELLOW}⚠{Colors.RESET}  {message}")
    
    def error(self, message: str, prefix: Optional[str] = None):
        """Log an error message"""
        timestamp = f"{Colors.DIM}[{self._format_timestamp()}]{Colors.RESET}"
        prefix_str = f" {Colors.BLUE}[{prefix}]{Colors.RESET}" if prefix else ""
        print(f"{timestamp}{prefix_str} {Colors.RED}✗{Colors.RESET}  {message}")
    
    def critical(self, message: str, prefix: Optional[str] = None):
        """Log a critical message"""
        timestamp = f"{Colors.DIM}[{self._format_timestamp()}]{Colors.RESET}"
        prefix_str = f" {Colors.BLUE}[{prefix}]{Colors.RESET}" if prefix else ""
        print(f"{timestamp}{prefix_str} {Colors.RED}{Colors.BOLD}🚨 CRITICAL:{Colors.RESET} {message}")
    
    def section(self, title: str):
        """Print a section header"""
        border = "=" * 60
        print(f"\n{Colors.BRIGHT_BLUE}{border}{Colors.RESET}")
        print(f"{Colors.BRIGHT_BLUE}{Colors.BOLD}{title.center(60)}{Colors.RESET}")
        print(f"{Colors.BRIGHT_BLUE}{border}{Colors.RESET}\n")
    
    def subsection(self, title: str):
        """Print a subsection header"""
        border = "-" * 40
        print(f"\n{Colors.CYAN}{border}{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}{title}{Colors.RESET}")
        print(f"{Colors.CYAN}{border}{Colors.RESET}")
    
    def file_status(self, file_path: str, status: str, message: str):
        """Log file validation status with proper formatting"""
        if status.lower() in ['valid', 'passed', 'success', 'ok']:
            icon = f"{Colors.GREEN}✓{Colors.RESET}"
            status_color = Colors.GREEN
        elif status.lower() in ['invalid', 'failed', 'error']:
            icon = f"{Colors.RED}✗{Colors.RESET}"
            status_color = Colors.RED
        else:
            icon = f"{Colors.YELLOW}•{Colors.RESET}"
            status_color = Colors.YELLOW
        
        # Format file path with proper indentation
        formatted_path = f"{Colors.DIM}└─{Colors.RESET} {Colors.BRIGHT_WHITE}{file_path}{Colors.RESET}"
        formatted_message = f"   {icon} {status_color}{message}{Colors.RESET}"
        
        print(formatted_path)
        print(formatted_message)
    
    def progress(self, current: int, total: int, item: str):
        """Show progress with a progress indicator"""
        import shutil
        percentage = (current / total) * 100
        bar_length = 30
        filled_length = int(bar_length * current // total)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        # Get terminal width and calculate max item length
        terminal_width = shutil.get_terminal_size().columns
        progress_prefix = f"Progress: [{bar}] {current}/{total} ({percentage:.1f}%) - "
        max_item_length = terminal_width - len(progress_prefix) - 10  # 10 chars buffer
        
        # Truncate item if too long
        if len(item) > max_item_length > 0:
            item = item[:max_item_length-3] + "..."
        
        # Clear the entire line before writing new progress
        print(f"\r\033[K{Colors.CYAN}Progress:{Colors.RESET} [{Colors.GREEN}{bar}{Colors.RESET}] "
              f"{Colors.BRIGHT_WHITE}{current}/{total}{Colors.RESET} "
              f"({Colors.YELLOW}{percentage:.1f}%{Colors.RESET}) - {item}", end='', flush=True)
        
        if current == total:
            print()  # New line when complete
    
    def summary(self, passed: int, failed: int, total: int):
        """Print a summary of results"""
        if failed == 0:
            status_icon = f"{Colors.GREEN}✓{Colors.RESET}"
            status_text = f"{Colors.GREEN}{Colors.BOLD}ALL PASSED{Colors.RESET}"
        else:
            status_icon = f"{Colors.RED}✗{Colors.RESET}"
            status_text = f"{Colors.RED}{Colors.BOLD}SOME FAILED{Colors.RESET}"
        
        print(f"\n{Colors.BRIGHT_WHITE}{'='*50}{Colors.RESET}")
        print(f"{Colors.BOLD}SUMMARY{Colors.RESET}")
        print(f"{Colors.BRIGHT_WHITE}{'='*50}{Colors.RESET}")
        print(f"{status_icon} Status: {status_text}")
        print(f"{Colors.GREEN}✓{Colors.RESET} Passed: {Colors.BRIGHT_GREEN}{passed}{Colors.RESET}")
        if failed > 0:
            print(f"{Colors.RED}✗{Colors.RESET} Failed: {Colors.BRIGHT_RED}{failed}{Colors.RESET}")
        print(f"{Colors.CYAN}•{Colors.RESET} Total:  {Colors.BRIGHT_WHITE}{total}{Colors.RESET}")
        print(f"{Colors.BRIGHT_WHITE}{'='*50}{Colors.RESET}")


# Global logger instance
logger = Logger()