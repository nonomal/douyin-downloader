#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
抖音Cookie获取工具 - 手动输入版
通过手动输入账号密码或从浏览器复制Cookie
"""

import json
import yaml
import re
from pathlib import Path
from typing import Dict, Optional
import requests


class ManualCookieManager:
    """手动Cookie管理器"""

    def __init__(self):
        self.required_cookies = ['msToken', 'ttwid']
        self.important_cookies = ['sessionid', 'sessionid_ss']
        self.optional_cookies = ['odin_tt', 'passport_csrf_token', 'sid_guard']
        self.cookies = {}

    def parse_cookie_string(self, cookie_str: str) -> Dict[str, str]:
        """解析Cookie字符串"""
        cookies = {}

        # 移除可能的引号和空白
        cookie_str = cookie_str.strip().strip('"').strip("'")

        # 支持多种分隔符
        if '; ' in cookie_str:
            pairs = cookie_str.split('; ')
        elif ';' in cookie_str:
            pairs = cookie_str.split(';')
        elif ', ' in cookie_str:
            pairs = cookie_str.split(', ')
        else:
            pairs = [cookie_str]

        for pair in pairs:
            pair = pair.strip()
            if '=' in pair:
                name, value = pair.split('=', 1)
                name = name.strip()
                value = value.strip()

                # 只保存我们需要的Cookie
                if name in self.required_cookies + self.important_cookies + self.optional_cookies:
                    cookies[name] = value

        return cookies

    def validate_cookies(self, cookies: Dict[str, str]) -> bool:
        """验证Cookie是否有效"""
        # 检查必需的Cookie
        has_required = all(c in cookies for c in self.required_cookies)
        has_session = any(c in cookies for c in self.important_cookies)

        if not has_required:
            missing = [c for c in self.required_cookies if c not in cookies]
            print(f"⚠️ 缺少必需的Cookie: {', '.join(missing)}")
            return False

        if not has_session:
            print("⚠️ 警告：缺少sessionid，可能无法下载用户主页内容")

        return True

    def test_cookies(self, cookies: Dict[str, str]) -> bool:
        """测试Cookie是否能正常工作"""
        print("\n🔍 测试Cookie有效性...")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Cookie': '; '.join([f'{k}={v}' for k, v in cookies.items()])
        }

        try:
            # 测试访问抖音API
            test_url = 'https://www.douyin.com/aweme/v1/web/tab/feed/'
            response = requests.get(test_url, headers=headers, timeout=10)

            if response.status_code == 200:
                print("✅ Cookie测试通过！")
                return True
            else:
                print(f"⚠️ Cookie可能无效 (状态码: {response.status_code})")
                return True  # 仍然保存，可能是API变化
        except Exception as e:
            print(f"⚠️ 测试失败: {e}")
            return True  # 仍然保存

    def save_cookies(self, cookies: Dict[str, str]):
        """保存Cookie到多个文件"""
        # 保存到config_douyin.yml
        config_path = Path('config_douyin.yml')
        config = {}

        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}

        config['cookies'] = cookies

        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)

        print(f"✅ Cookie已保存到: {config_path}")

        # 保存到cookies.json
        json_path = Path('cookies.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=2, ensure_ascii=False)

        print(f"✅ Cookie备份已保存到: {json_path}")

        # 保存到cookies.txt
        txt_path = Path('cookies.txt')
        cookie_str = '; '.join([f'{k}={v}' for k, v in cookies.items()])
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(cookie_str)

        print(f"✅ Cookie文本已保存到: {txt_path}")

    def load_existing_cookies(self) -> Optional[Dict[str, str]]:
        """加载已存在的Cookie"""
        # 尝试从多个来源加载
        sources = [
            ('config_douyin.yml', self._load_from_yaml),
            ('cookies.json', self._load_from_json),
            ('cookies.txt', self._load_from_txt)
        ]

        for filename, loader in sources:
            path = Path(filename)
            if path.exists():
                cookies = loader(path)
                if cookies:
                    return cookies

        return None

    def _load_from_yaml(self, path: Path) -> Optional[Dict[str, str]]:
        """从YAML文件加载"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config.get('cookies') if config else None
        except:
            return None

    def _load_from_json(self, path: Path) -> Optional[Dict[str, str]]:
        """从JSON文件加载"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None

    def _load_from_txt(self, path: Path) -> Optional[Dict[str, str]]:
        """从文本文件加载"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                cookie_str = f.read().strip()
                return self.parse_cookie_string(cookie_str)
        except:
            return None

    def run(self):
        """运行主程序"""
        print("="*60)
        print("🍪 抖音Cookie配置工具 - 手动输入版")
        print("="*60)

        while True:
            print("\n请选择操作:")
            print("1. 从浏览器复制Cookie")
            print("2. 查看现有Cookie")
            print("3. 测试Cookie有效性")
            print("4. 从文件导入Cookie")
            print("0. 退出")

            choice = input("\n请输入选项 (0-4): ").strip()

            if choice == '0':
                print("\n👋 再见！")
                break

            elif choice == '1':
                self.input_cookies_manually()

            elif choice == '2':
                self.view_existing_cookies()

            elif choice == '3':
                self.test_existing_cookies()

            elif choice == '4':
                self.import_from_file()

            else:
                print("❌ 无效选项，请重试")

    def input_cookies_manually(self):
        """手动输入Cookie"""
        print("\n" + "="*60)
        print("📝 获取Cookie的方法:")
        print("1. 打开浏览器，访问 https://www.douyin.com")
        print("2. 登录你的账号")
        print("3. 按F12打开开发者工具")
        print("4. 切换到Network标签")
        print("5. 刷新页面")
        print("6. 找到任意请求，查看Request Headers中的Cookie")
        print("7. 复制整个Cookie字段的值")
        print("="*60)

        print("\n请粘贴完整的Cookie字符串:")
        print("(支持格式: msToken=xxx; ttwid=xxx; ...)")

        cookie_str = input("\nCookie: ").strip()

        if not cookie_str:
            print("❌ Cookie不能为空")
            return

        # 解析Cookie
        cookies = self.parse_cookie_string(cookie_str)

        if not cookies:
            print("❌ 无法解析Cookie，请检查格式")
            return

        print(f"\n📋 解析到 {len(cookies)} 个Cookie:")
        print("-"*40)
        for name, value in cookies.items():
            display_value = value[:30] + "..." if len(value) > 30 else value
            status = "✅" if name in self.required_cookies else "📎"
            print(f"{status} {name}: {display_value}")
        print("-"*40)

        # 验证Cookie
        if self.validate_cookies(cookies):
            # 测试Cookie
            self.test_cookies(cookies)

            # 保存Cookie
            confirm = input("\n是否保存这些Cookie? (y/n): ").strip().lower()
            if confirm == 'y':
                self.save_cookies(cookies)
                print("\n🎉 Cookie配置完成！")
                print("\n下一步:")
                print("1. 使用V1.0: python DouYinCommand.py")
                print("2. 使用V2.0: python downloader.py --config")

    def view_existing_cookies(self):
        """查看现有Cookie"""
        cookies = self.load_existing_cookies()

        if not cookies:
            print("\n❌ 未找到已保存的Cookie")
            return

        print(f"\n📋 当前保存的Cookie ({len(cookies)} 个):")
        print("-"*40)
        for name, value in cookies.items():
            display_value = value[:30] + "..." if len(value) > 30 else value
            status = "✅" if name in self.required_cookies else "📎"
            print(f"{status} {name}: {display_value}")
        print("-"*40)

    def test_existing_cookies(self):
        """测试现有Cookie"""
        cookies = self.load_existing_cookies()

        if not cookies:
            print("\n❌ 未找到已保存的Cookie")
            return

        self.test_cookies(cookies)

    def import_from_file(self):
        """从文件导入Cookie"""
        print("\n请输入Cookie文件路径:")
        file_path = input("文件路径: ").strip()

        path = Path(file_path)
        if not path.exists():
            print(f"❌ 文件不存在: {file_path}")
            return

        # 根据文件扩展名选择加载方式
        ext = path.suffix.lower()

        if ext == '.json':
            cookies = self._load_from_json(path)
        elif ext in ['.yml', '.yaml']:
            cookies = self._load_from_yaml(path)
        else:
            cookies = self._load_from_txt(path)

        if not cookies:
            print("❌ 无法从文件加载Cookie")
            return

        print(f"\n✅ 从文件加载了 {len(cookies)} 个Cookie")

        # 验证和保存
        if self.validate_cookies(cookies):
            self.test_cookies(cookies)
            confirm = input("\n是否保存这些Cookie? (y/n): ").strip().lower()
            if confirm == 'y':
                self.save_cookies(cookies)
                print("\n🎉 Cookie导入成功！")


def main():
    """主函数"""
    manager = ManualCookieManager()
    manager.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，退出程序")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()