from typing import Dict, Any

DEFAULT_CONFIG: Dict[str, Any] = {
    'path': './Downloaded/',
    'music': True,
    'cover': True,
    'avatar': True,
    'json': True,
    'start_time': '',
    'end_time': '',
    'folderstyle': True,
    'mode': ['post'],
    'number': {
        'post': 0,
        'like': 0,
        'allmix': 0,
        'mix': 0,
        'music': 0,
    },
    'increase': {
        'post': False,
        'like': False,
        'allmix': False,
        'mix': False,
        'music': False,
    },
    'thread': 5,
    'retry_times': 3,
    'database': True,
    'auto_cookie': False,
    'log_level': 'INFO',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    'log_file': None,  # Optional log file path
    'download_timeout': 300,  # Download timeout in seconds
    'filename_max_length': 200,  # Maximum filename length
}
