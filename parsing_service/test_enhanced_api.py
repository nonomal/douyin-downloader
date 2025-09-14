#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试增强版API功能
"""

import asyncio
import aiohttp
import json
import sys

# API基础URL
BASE_URL = "http://localhost:5001"


async def test_user_info():
    """测试获取用户信息"""
    print("\n=== 测试获取用户信息 ===")
    url = f"{BASE_URL}/user/info"
    data = {
        "user_id": "MS4wLjABAAAA8U_l6rBzmy7bcy6xOJel4v0RzoR_wfAubGPeJimN__4"  # 示例用户ID
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            result = await response.json()
            if result.get('success'):
                user = result['data']
                print(f"用户昵称: {user.get('nickname')}")
                print(f"粉丝数: {user.get('follower_count')}")
                print(f"作品数: {user.get('aweme_count')}")
            else:
                print(f"错误: {result.get('error')}")


async def test_user_posts():
    """测试获取用户作品"""
    print("\n=== 测试获取用户作品 ===")
    url = f"{BASE_URL}/user/posts"
    data = {
        "user_id": "MS4wLjABAAAA8U_l6rBzmy7bcy6xOJel4v0RzoR_wfAubGPeJimN__4",
        "count": 5
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            result = await response.json()
            if result.get('success'):
                posts = result['data'].get('posts', [])
                print(f"获取到 {len(posts)} 个作品")
                for i, post in enumerate(posts[:3], 1):
                    print(f"{i}. {post.get('title', '无标题')}")
            else:
                print(f"错误: {result.get('error')}")


async def test_search():
    """测试搜索功能"""
    print("\n=== 测试搜索功能 ===")
    url = f"{BASE_URL}/search"
    data = {
        "keyword": "美食",
        "type": "video",
        "count": 5
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            result = await response.json()
            if result.get('success'):
                videos = result['data'].get('videos', [])
                print(f"搜索到 {len(videos)} 个视频")
                for i, video in enumerate(videos[:3], 1):
                    print(f"{i}. {video.get('title', '无标题')}")
            else:
                print(f"错误: {result.get('error')}")


async def test_hot_search():
    """测试热搜榜"""
    print("\n=== 测试热搜榜 ===")
    url = f"{BASE_URL}/hot/search"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            result = await response.json()
            if result.get('success'):
                word_list = result['data'].get('word_list', [])
                print(f"热搜榜前10:")
                for i, item in enumerate(word_list[:10], 1):
                    print(f"{i}. {item.get('word')} - 热度: {item.get('hot_value')}")
            else:
                print(f"错误: {result.get('error')}")


async def test_video_comments():
    """测试获取视频评论"""
    print("\n=== 测试获取视频评论 ===")
    url = f"{BASE_URL}/video/comments"
    data = {
        "video_id": "7123456789012345",  # 示例视频ID
        "count": 5
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            result = await response.json()
            if result.get('success'):
                comments = result['data'].get('comments', [])
                print(f"获取到 {len(comments)} 条评论")
                for i, comment in enumerate(comments[:3], 1):
                    print(f"{i}. {comment.get('text', '')[:50]}...")
            else:
                print(f"错误: {result.get('error')}")


async def test_suggest_words():
    """测试搜索建议"""
    print("\n=== 测试搜索建议 ===")
    url = f"{BASE_URL}/suggest"
    data = {
        "keyword": "美"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            result = await response.json()
            if result.get('success'):
                suggestions = result['data'].get('suggestions', [])
                print(f"搜索建议:")
                for i, suggestion in enumerate(suggestions[:5], 1):
                    print(f"{i}. {suggestion}")
            else:
                print(f"错误: {result.get('error')}")


async def main():
    """主测试函数"""
    print("开始测试增强版API功能...")
    print("请确保解析服务正在运行 (python app.py)")
    print("-" * 50)

    # 运行测试
    tests = [
        test_hot_search,  # 先测试不需要特定ID的接口
        test_suggest_words,
        test_user_info,
        test_user_posts,
        test_search,
        test_video_comments
    ]

    for test in tests:
        try:
            await test()
        except Exception as e:
            print(f"测试失败: {e}")

    print("\n" + "=" * 50)
    print("测试完成!")


if __name__ == "__main__":
    # 检查服务是否运行
    import requests
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            print("✅ 解析服务正在运行")
            asyncio.run(main())
        else:
            print("❌ 解析服务响应异常")
    except:
        print("❌ 解析服务未运行，请先启动服务:")
        print("   cd parsing_service")
        print("   python app.py")