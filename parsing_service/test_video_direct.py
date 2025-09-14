#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
直接测试视频解析功能
"""

import asyncio
import sys
import os
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from strategies.requests_strategy import RequestsStrategy
from strategies.api_strategy import APIStrategy


async def test_requests_strategy():
    """测试requests策略"""
    print("\n=== 测试 Requests 策略 ===")
    strategy = RequestsStrategy()

    # 测试URL
    test_urls = [
        "https://www.douyin.com/video/7334736549089668406",
        "https://v.douyin.com/ikL3TcUP/"  # 短链接
    ]

    for url in test_urls:
        print(f"\n测试URL: {url}")
        try:
            result = await strategy.parse(url, {})
            if result:
                print(f"✅ 解析成功")
                print(f"  视频ID: {result.get('video_id')}")
                print(f"  标题: {result.get('title', '')[:50]}")
                print(f"  作者: {result.get('author')}")
                if result.get('video_url'):
                    print(f"  视频链接: 已获取")
            else:
                print(f"❌ 解析失败: 返回空结果")
        except Exception as e:
            print(f"❌ 解析出错: {e}")


async def test_api_strategy():
    """测试API策略"""
    print("\n=== 测试 API 策略 ===")
    strategy = APIStrategy()

    # 测试URL
    test_urls = [
        "https://www.douyin.com/video/7334736549089668406"
    ]

    for url in test_urls:
        print(f"\n测试URL: {url}")
        try:
            result = await strategy.parse(url, {})
            if result:
                print(f"✅ 解析成功")
                print(f"  视频ID: {result.get('video_id')}")
                print(f"  标题: {result.get('title', '')[:50]}")
                print(f"  作者: {result.get('author')}")
            else:
                print(f"❌ 解析失败: 返回空结果")
        except Exception as e:
            print(f"❌ 解析出错: {e}")


async def test_direct_api_call():
    """直接测试API调用"""
    print("\n=== 直接测试API调用 ===")

    import aiohttp
    import json
    from xbogus_generator import generate_x_bogus

    video_id = "7334736549089668406"

    # 构建参数
    params = {
        'aweme_id': video_id,
        'device_platform': 'webapp',
        'aid': '6383',
        'channel': 'channel_pc_web',
        'version_code': '170400',
        'version_name': '17.4.0',
        'browser_language': 'zh-CN',
        'browser_platform': 'MacIntel',
        'browser_name': 'Chrome',
        'browser_version': '122.0.0.0'
    }

    params_str = '&'.join([f"{k}={v}" for k, v in params.items()])
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

    try:
        # 生成X-Bogus
        x_bogus = generate_x_bogus(params_str, user_agent)
        print(f"生成的X-Bogus: {x_bogus[:20]}...")

        # 构建URL
        url = f"https://www.douyin.com/aweme/v1/web/aweme/detail/?{params_str}&X-Bogus={x_bogus}"

        # 发送请求
        headers = {
            'User-Agent': user_agent,
            'Accept': 'application/json',
            'Referer': f'https://www.douyin.com/video/{video_id}'
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                print(f"响应状态码: {response.status}")
                print(f"响应类型: {response.content_type}")

                if response.status == 200:
                    text = await response.text()
                    print(f"响应长度: {len(text)}")

                    # 尝试解析JSON
                    try:
                        data = json.loads(text)
                        if 'aweme_detail' in data:
                            print("✅ 成功获取视频详情")
                            detail = data['aweme_detail']
                            print(f"  视频ID: {detail.get('aweme_id')}")
                            print(f"  描述: {detail.get('desc', '')[:50]}")
                        elif 'status_code' in data:
                            print(f"❌ API返回错误: {data.get('status_msg', 'Unknown')}")
                        else:
                            print(f"❌ 响应格式不符: {list(data.keys())}")
                    except json.JSONDecodeError:
                        print(f"❌ 无法解析JSON响应")
                        print(f"响应内容前100字符: {text[:100]}")
                else:
                    print(f"❌ HTTP错误: {response.status}")

    except Exception as e:
        print(f"❌ 请求失败: {e}")


async def main():
    """主函数"""
    print("=" * 50)
    print("直接测试视频解析功能")
    print("=" * 50)

    # 运行测试
    await test_direct_api_call()
    await test_api_strategy()
    await test_requests_strategy()

    print("\n" + "=" * 50)
    print("测试完成！")


if __name__ == "__main__":
    asyncio.run(main())