import re
from urllib.parse import urlparse
from typing import Optional


def validate_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def sanitize_filename(filename: str, max_length: int = 200) -> str:
    """
    Sanitize filename to be safe for file systems.
    
    Args:
        filename: Original filename
        max_length: Maximum allowed length
        
    Returns:
        Sanitized filename safe for use on filesystems
    """
    if not filename:
        return 'untitled'
    
    # Remove invalid characters for Windows, macOS, and Linux
    invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
    filename = re.sub(invalid_chars, '_', filename)
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Truncate if too long, but preserve extension if present
    if len(filename) > max_length:
        # Try to preserve file extension
        parts = filename.rsplit('.', 1)
        if len(parts) == 2 and len(parts[1]) <= 10:
            # Has a reasonable extension
            ext = '.' + parts[1]
            name = parts[0][:max_length - len(ext)]
            filename = name + ext
        else:
            filename = filename[:max_length]
    
    return filename or 'untitled'


def parse_url_type(url: str) -> Optional[str]:
    if 'v.douyin.com' in url:
        return 'video'

    path = urlparse(url).path

    if '/video/' in path:
        return 'video'
    if '/user/' in path:
        return 'user'
    if '/note/' in path or '/gallery/' in path:
        return 'gallery'
    return None
