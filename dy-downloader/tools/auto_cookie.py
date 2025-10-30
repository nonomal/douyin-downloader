#!/usr/bin/env python3
"""
自动Cookie获取工具 - Automatic Cookie Fetcher
打开浏览器，用户登录后自动提取并保存Cookie
"""
import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Dict

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("❌ Playwright未安装。请先运行：pip install playwright")
    print("❌ Playwright not installed. Please run: pip install playwright")
    print("   然后运行: playwright install chromium")
    print("   Then run: playwright install chromium")
    sys.exit(1)

try:
    import yaml
except ImportError:
    print("❌ PyYAML未安装。请先运行：pip install pyyaml")
    sys.exit(1)


REQUIRED_COOKIES = {"msToken", "ttwid", "odin_tt", "passport_csrf_token"}
RECOMMENDED_COOKIES = REQUIRED_COOKIES | {"sid_guard", "sessionid", "sid_tt"}


def print_banner():
    """打印欢迎横幅"""
    banner = """
╔══════════════════════════════════════════════════════╗
║     抖音Cookie自动获取工具                          ║
║     Douyin Cookie Auto Fetcher                      ║
║                                                      ║
║     1. 浏览器将自动打开                             ║
║     2. 请在浏览器中登录您的抖音账号                 ║
║     3. 登录成功后，Cookie将自动保存                 ║
╚══════════════════════════════════════════════════════╝
    """
    print(banner)


async def wait_for_login(page, timeout=180):
    """
    等待用户登录完成（3分钟）
    用户可以通过在终端按Enter键来确认登录完成
    """
    print("\n" + "="*60)
    print("⏳ 请在浏览器中登录您的抖音账号")
    print("   Please login to your Douyin account in the browser")
    print()
    print("💡 登录完成后，请回到此终端窗口按 Enter 键确认")
    print("   After logging in, return to this terminal and press Enter")
    print()
    print(f"⏰ 等待时间限制：{timeout}秒（约{timeout//60}分钟）")
    print(f"   Time limit: {timeout}s (about {timeout//60} minutes)")
    print("="*60)
    
    # 创建两个任务：一个等待用户按Enter，一个超时
    async def wait_for_user_input():
        """等待用户按Enter键"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, input, "\n👉 登录完成后按 Enter 键继续... (Press Enter when logged in): ")
        return True
    
    async def wait_with_timeout():
        """等待超时"""
        await asyncio.sleep(timeout)
        return False
    
    # 同时运行两个任务，哪个先完成就用哪个
    try:
        done, pending = await asyncio.wait(
            [
                asyncio.create_task(wait_for_user_input()),
                asyncio.create_task(wait_with_timeout())
            ],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # 取消未完成的任务
        for task in pending:
            task.cancel()
        
        # 检查是否是用户确认
        result = list(done)[0].result()
        if result:
            print("\n✅ 用户已确认登录完成！")
            print("   User confirmed login!")
            return True
        else:
            print(f"\n⚠️  等待超时（{timeout}秒）")
            print("   Time limit reached")
            print("   将尝试提取Cookie...")
            print("   Will try to extract cookies anyway...")
            return False
            
    except EOFError:
        # 如果是非交互式环境，等待完整的超时时间
        print(f"\n⚠️  检测到非交互式终端")
        print("   Non-interactive terminal detected")
        print(f"   浏览器将保持打开 {timeout} 秒，请在浏览器中完成登录")
        print(f"   Browser will stay open for {timeout} seconds, please login")
        print()
        
        # 显示倒计时
        for remaining in range(timeout, 0, -10):
            print(f"   剩余时间: {remaining} 秒... (Time remaining: {remaining}s)")
            await asyncio.sleep(10)
        
        print("\n⏰ 时间到！正在提取Cookie...")
        print("   Time's up! Extracting cookies...")
        return False
        
    except Exception as e:
        print(f"\n⚠️  等待过程中出错: {e}")
        print(f"   Error during wait: {e}")
        print(f"   浏览器将保持打开 {timeout} 秒")
        print(f"   Browser will stay open for {timeout} seconds")
        await asyncio.sleep(timeout)
        return False


def filter_cookies(all_cookies: Dict[str, str]) -> Dict[str, str]:
    """筛选需要的Cookie"""
    # 首先尝试获取推荐的Cookie
    filtered = {k: v for k, v in all_cookies.items() if k in RECOMMENDED_COOKIES}
    
    # 如果推荐的Cookie不全，添加所有可能有用的Cookie
    if len(filtered) < len(REQUIRED_COOKIES):
        # 保留所有Cookie，让用户自己决定
        print("⚠️  推荐Cookie不全，将保存所有抖音Cookie")
        print("   Recommended cookies incomplete, saving all douyin cookies")
        return all_cookies
    
    # 如果有推荐的Cookie但不全，补充其他Cookie
    for key in all_cookies:
        if key not in filtered and len(key) > 2:  # 避免保存单字符cookie
            filtered[key] = all_cookies[key]
    
    return filtered


def validate_cookies(cookies: Dict[str, str]) -> tuple[bool, list[str]]:
    """验证Cookie是否包含必需字段"""
    missing = [key for key in REQUIRED_COOKIES if key not in cookies]
    is_valid = len(missing) == 0
    return is_valid, missing


def save_to_config(config_path: Path, cookies: Dict[str, str]):
    """保存Cookie到配置文件"""
    try:
        # 读取现有配置
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
        else:
            config = {}
        
        # 更新cookies部分
        config['cookies'] = cookies
        
        # 写回配置文件
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(config, f, allow_unicode=True, sort_keys=False)
        
        print(f"\n✅ Cookie已保存到配置文件: {config_path}")
        print(f"   Cookies saved to: {config_path}")
        return True
        
    except Exception as e:
        print(f"\n❌ 保存配置文件失败: {e}")
        print(f"   Failed to save config: {e}")
        return False


def save_to_json(json_path: Path, cookies: Dict[str, str]):
    """保存Cookie到JSON文件（备份）"""
    try:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)
        print(f"✅ Cookie已备份到: {json_path}")
        print(f"   Cookies backed up to: {json_path}")
        return True
    except Exception as e:
        print(f"⚠️  备份失败: {e}")
        return False


async def capture_cookies_auto():
    """自动捕获Cookie的主函数"""
    print_banner()
    
    # 确定配置文件路径
    project_root = Path(__file__).parent.parent
    config_path = project_root / "config.yml"
    backup_path = project_root / "config" / "cookies.json"
    
    print(f"\n📁 配置文件路径: {config_path}")
    print(f"📁 Config file: {config_path}\n")
    
    async with async_playwright() as p:
        print("🌐 正在启动浏览器...")
        print("   Launching browser...")
        
        # 启动浏览器（非headless模式，用户可见）
        browser = await p.chromium.launch(
            headless=False,
            args=['--start-maximized']  # 最大化窗口
        )
        
        context = await browser.new_context(
            viewport=None,  # 使用窗口大小
        )
        
        page = await context.new_page()
        
        print("✅ 浏览器已启动")
        print("   Browser launched")
        
        try:
            # 导航到抖音首页
            print("\n🔗 正在打开抖音网站...")
            print("   Opening Douyin website...")
            
            await page.goto(
                "https://www.douyin.com/",
                wait_until="domcontentloaded",
                timeout=30000
            )
            
            print("✅ 页面已加载")
            print("   Page loaded")
            
            # 等待用户登录（3分钟）
            await wait_for_login(page, timeout=180)
            
            # 额外等待，确保Cookie和JavaScript完全执行
            print("\n⏳ 等待Cookie和JavaScript完全加载...")
            await asyncio.sleep(2)
            
            # 尝试从页面中获取msToken
            print("🔍 尝试从页面获取msToken...")
            try:
                # 执行JavaScript获取msToken
                mstoken_from_js = await page.evaluate("""
                    () => {
                        // 尝试多种方式获取msToken
                        // 1. 从window对象
                        if (window._token) return window._token;
                        if (window.msToken) return window.msToken;
                        
                        // 2. 从localStorage
                        try {
                            const token = localStorage.getItem('msToken');
                            if (token) return token;
                        } catch(e) {}
                        
                        // 3. 从sessionStorage
                        try {
                            const token = sessionStorage.getItem('msToken');
                            if (token) return token;
                        } catch(e) {}
                        
                        // 4. 从页面meta标签或其他地方
                        const metas = document.getElementsByTagName('meta');
                        for (let meta of metas) {
                            if (meta.name === 'msToken' || meta.getAttribute('data-token')) {
                                return meta.content || meta.getAttribute('data-token');
                            }
                        }
                        
                        return null;
                    }
                """)
                
                if mstoken_from_js:
                    print(f"   ✓ 从JavaScript获取到msToken: {mstoken_from_js[:20]}...")
            except Exception as e:
                print(f"   ⚠️  无法从JavaScript获取msToken: {e}")
                mstoken_from_js = None
            
            # 获取所有Cookie
            print("\n🔍 正在提取Cookie...")
            print("   Extracting cookies...")
            
            storage = await context.storage_state()
            all_cookies = {
                cookie["name"]: cookie["value"]
                for cookie in storage["cookies"]
                if "douyin.com" in cookie["domain"] and cookie["name"]  # 过滤掉空键
            }
            
            # 如果从JS获取到msToken但Cookie中没有，添加进去
            if mstoken_from_js and 'msToken' not in all_cookies:
                all_cookies['msToken'] = mstoken_from_js
                print("   ✓ 已添加从JavaScript获取的msToken")
            
            if not all_cookies:
                print("\n❌ 未找到任何Cookie！请确保您已成功登录。")
                print("   No cookies found! Please make sure you are logged in.")
                await browser.close()
                return 1
            
            print(f"✅ 找到 {len(all_cookies)} 个Cookie")
            print(f"   Found {len(all_cookies)} cookies")
            
            # 筛选需要的Cookie
            filtered_cookies = filter_cookies(all_cookies)
            print(f"\n📋 提取的Cookie字段: {', '.join(filtered_cookies.keys())}")
            print(f"   Extracted cookie keys: {', '.join(filtered_cookies.keys())}")
            
            # 验证Cookie
            is_valid, missing = validate_cookies(filtered_cookies)
            
            if is_valid:
                print("\n✅ Cookie验证通过！包含所有必需字段。")
                print("   Cookie validation passed! All required fields present.")
            else:
                print(f"\n⚠️  警告：缺少以下必需Cookie字段: {', '.join(missing)}")
                print(f"   Warning: Missing required cookies: {', '.join(missing)}")
                print("   继续保存现有Cookie...")
                print("   Saving available cookies anyway...")
            
            # 保存到配置文件
            print("\n💾 正在保存Cookie...")
            print("   Saving cookies...")
            
            success = save_to_config(config_path, filtered_cookies)
            
            # 同时备份到JSON
            save_to_json(backup_path, filtered_cookies)
            
            if success:
                print("\n" + "="*60)
                print("🎉 成功！Cookie已自动配置完成！")
                print("   Success! Cookies configured automatically!")
                print("="*60)
                print("\n现在您可以运行下载命令：")
                print("Now you can run the download command:")
                print("  python run.py -c config.yml")
                print("  或 (or): dy-downloader -c config.yml")
                return 0
            else:
                return 1
                
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            print(f"   Error occurred: {e}")
            import traceback
            traceback.print_exc()
            return 1
            
        finally:
            print("\n🔒 正在关闭浏览器...")
            print("   Closing browser...")
            await browser.close()
            print("✅ 浏览器已关闭")
            print("   Browser closed")


def main():
    """主入口函数"""
    try:
        exit_code = asyncio.run(capture_cookies_auto())
        return exit_code
    except KeyboardInterrupt:
        print("\n\n⚠️  用户取消操作")
        print("   Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        print(f"   Program error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

