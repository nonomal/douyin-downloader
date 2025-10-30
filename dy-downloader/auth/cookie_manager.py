import json
from pathlib import Path
from typing import Dict, Optional
from utils.logger import setup_logger

logger = setup_logger('CookieManager')


class CookieManager:
    def __init__(self, cookie_file: Optional[str] = None):
        if cookie_file is None:
            # Default to config/cookies.json instead of root
            cookie_file = 'config/cookies.json'
        self.cookie_file = Path(cookie_file)
        # Ensure parent directory exists
        self.cookie_file.parent.mkdir(parents=True, exist_ok=True)
        self.cookies: Dict[str, str] = {}

    def set_cookies(self, cookies: Dict[str, str]):
        self.cookies = cookies
        self._save_cookies()

    def get_cookies(self) -> Dict[str, str]:
        if not self.cookies:
            self._load_cookies()
        return self.cookies

    def get_cookie_string(self) -> str:
        cookies = self.get_cookies()
        return '; '.join([f"{k}={v}" for k, v in cookies.items()])

    def _save_cookies(self):
        try:
            # Ensure parent directory exists
            self.cookie_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cookie_file, 'w', encoding='utf-8') as f:
                json.dump(self.cookies, f, ensure_ascii=False, indent=2)
            logger.debug(f"Cookies saved to {self.cookie_file}")
        except Exception as e:
            logger.error(f"Failed to save cookies to {self.cookie_file}: {e}")

    def _load_cookies(self):
        if not self.cookie_file.exists():
            logger.debug(f"Cookie file not found: {self.cookie_file}")
            return

        try:
            with open(self.cookie_file, 'r', encoding='utf-8') as f:
                self.cookies = json.load(f)
            logger.debug(f"Cookies loaded from {self.cookie_file}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in cookie file {self.cookie_file}: {e}")
        except Exception as e:
            logger.error(f"Failed to load cookies from {self.cookie_file}: {e}")

    def validate_cookies(self) -> bool:
        required_keys = {'msToken', 'ttwid', 'odin_tt', 'passport_csrf_token'}
        cookies = self.get_cookies()
        missing = [key for key in required_keys if key not in cookies or not cookies.get(key)]
        if missing:
            logger.warning(f"Cookie validation failed, missing: {', '.join(missing)}")
            return False
        return True

    def clear_cookies(self):
        self.cookies = {}
        if self.cookie_file.exists():
            self.cookie_file.unlink()
