#!/usr/bin/env python3
"""
Entry point for running dy-downloader as a module.
Usage: python -m dy_downloader [args]
"""
import sys
from pathlib import Path

# Add current directory to path if running as module
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

if __name__ == '__main__':
    from cli.main import main
    exit_code = main()
    sys.exit(exit_code if exit_code is not None else 0)

