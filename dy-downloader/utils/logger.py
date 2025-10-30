import logging
import sys
from pathlib import Path
from typing import Optional


# Global log level that can be configured
_global_log_level = logging.INFO


def set_global_log_level(level: int):
    """Set the global log level for all loggers created by setup_logger."""
    global _global_log_level
    _global_log_level = level


def get_log_level_from_string(level_str: str) -> int:
    """Convert string log level to logging constant."""
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
    }
    return level_map.get(level_str.upper(), logging.INFO)


def setup_logger(
    name: str = 'dy-downloader', 
    level: Optional[int] = None, 
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Setup logger with optional file output.
    
    Args:
        name: Logger name
        level: Log level (defaults to global level)
        log_file: Optional log file path
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Use provided level, or fall back to global level
    if level is None:
        level = _global_log_level
    
    logger.setLevel(level)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file:
        try:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.error(f"Failed to setup file handler for {log_file}: {e}")

    return logger
