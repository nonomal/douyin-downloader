#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
抖音Cookie获取工具 - 扫码登录版
自动打开浏览器，扫码登录后自动获取并保存Cookie
"""

import asyncio
import json
import yaml
import time
from pathlib import Path
from typing import Dict, List, Optional

try:
    from playwright.async_api import async_playwright, Page
except ImportError:
    print("❌ 请先安装Playwright:")
    print("   pip3 install playwright")
    print("   playwright install chromium")
    exit(1)


class DouyinCookieExtractor:
    """抖音Cookie提取器"""

    def __init__(self):
        self.cookies = {}
        self.required_cookies = ['msToken', 'ttwid', 'sessionid']
        self.optional_cookies = ['odin_tt', 'passport_csrf_token', 'sid_guard']

    async def extract_cookies(self, page: Page) -> Dict[str, str]:
        """从页面提取Cookie"""
        cookies_list = await page.context.cookies()
        cookies_dict = {}

        for cookie in cookies_list:
            if cookie['name'] in self.required_cookies + self.optional_cookies:
                cookies_dict[cookie['name']] = cookie['value']

        return cookies_dict

    async def wait_for_login(self, page: Page) -> bool:
        """等待用户登录"""
        print("\n⏳ 等待登录...")
        print("   请在浏览器中完成登录（扫码/账号密码）")

        # 等待登录成功的标志
        max_wait = 300  # 最多等待5分钟
        start_time = time.time()

        while time.time() - start_time < max_wait:
            # 检查是否有sessionid（登录成功的标志）
            cookies = await self.extract_cookies(page)
            if 'sessionid' in cookies or 'sessionid_ss' in cookies:
                print("✅ 检测到登录成功！")
                return True

            # 检查页面URL或元素变化
            try:
                # 尝试查找用户头像或其他登录后才有的元素
                user_element = await page.query_selector('[class*="avatar"]')
                if user_element:
                    print("✅ 检测到用户已登录！")
                    return True
            except:
                pass

            await asyncio.sleep(2)

        print("❌ 登录超时")
        return False

    async def save_cookies(self, cookies: Dict[str, str]):
        """保存Cookie到文件"""
        # 保存为YAML格式（用于config）
        config_path = Path('config_douyin.yml')
        config = {}

        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}

        config['cookies'] = cookies

        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)

        print(f"\n✅ Cookie已保存到: {config_path}")

        # 同时保存为JSON格式（备用）
        json_path = Path('cookies.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=2, ensure_ascii=False)

        print(f"✅ Cookie备份已保存到: {json_path}")

        # 保存为文本格式（用于其他工具）
        txt_path = Path('cookies.txt')
        cookie_str = '; '.join([f'{k}={v}' for k, v in cookies.items()])
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(cookie_str)

        print(f"✅ Cookie文本已保存到: {txt_path}")

    async def run(self):
        """运行提取器"""
        print("="*60)
        print("🍪 抖音Cookie获取工具 - 扫码登录版")
        print("="*60)

        async with async_playwright() as p:
            print("\n📱 启动浏览器...")
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=site-per-process',
                    '--window-size=1280,720'
                ]
            )

            context = await browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            # 注入反检测脚本
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)

            page = await context.new_page()

            print("📍 访问抖音网页版...")
            await page.goto('https://www.douyin.com', wait_until='networkidle')

            print("\n" + "="*60)
            print("📱 请在浏览器中登录抖音:")
            print("   1. 点击右上角【登录】按钮")
            print("   2. 选择扫码登录或账号密码登录")
            print("   3. 完成登录后程序会自动获取Cookie")
            print("="*60)

            # 等待用户登录
            if await self.wait_for_login(page):
                # 提取所有Cookie
                all_cookies = await self.extract_cookies(page)

                if all_cookies:
                    print("\n📋 获取到的Cookie:")
                    print("-"*40)
                    for name, value in all_cookies.items():
                        display_value = value[:30] + "..." if len(value) > 30 else value
                        status = "✅" if name in self.required_cookies else "📎"
                        print(f"{status} {name}: {display_value}")
                    print("-"*40)

                    # 检查必需的Cookie
                    missing = [c for c in self.required_cookies if c not in all_cookies]
                    if missing and 'sessionid_ss' not in all_cookies:
                        print(f"\n⚠️ 缺少必需的Cookie: {', '.join(missing)}")
                        print("   请确保已完全登录")
                    else:
                        # 保存Cookie
                        await self.save_cookies(all_cookies)
                        print("\n🎉 Cookie获取成功！")
                        print("\n下一步:")
                        print("1. 使用V1.0: python DouYinCommand.py")
                        print("2. 使用V2.0: python downloader.py --config")
                else:
                    print("❌ 未能获取到Cookie")
            else:
                print("❌ 登录失败或超时")

            print("\n按Enter键关闭浏览器...")
            input()
            await browser.close()


async def main():
    """主函数"""
    extractor = DouyinCookieExtractor()
    await extractor.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，退出程序")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()