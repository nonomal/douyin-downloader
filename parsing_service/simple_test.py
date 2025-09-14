#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单测试脚本 - 测试基本的解析功能
"""

import requests
import json

BASE_URL = "http://localhost:5001"

def test_health():
    """测试健康检查"""
    print("\n=== 测试健康检查 ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"响应: {response.json()}")
        print("✅ 服务正常运行")
    else:
        print("❌ 服务异常")

def test_parse_video():
    """测试视频解析"""
    print("\n=== 测试视频解析 ===")
    # 使用一个示例视频URL
    data = {
        "url": "https://www.douyin.com/video/7334736549089668406"
    }

    response = requests.post(f"{BASE_URL}/parse", json=data)
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            video_data = result['data']
            print(f"✅ 解析成功")
            print(f"视频ID: {video_data.get('video_id')}")
            print(f"标题: {video_data.get('title', '无标题')[:50]}...")
            print(f"作者: {video_data.get('author')}")
            if video_data.get('video_url'):
                print(f"视频链接: {video_data['video_url'][:50]}...")
        else:
            print(f"❌ 解析失败: {result.get('error')}")
    else:
        print(f"❌ 请求失败")

def test_stats():
    """测试统计信息"""
    print("\n=== 测试统计信息 ===")
    response = requests.get(f"{BASE_URL}/stats")
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        stats = response.json()
        print("✅ 获取统计信息成功")
        print("策略状态:")
        for strategy_name, strategy_info in stats.get('strategies', {}).items():
            print(f"  - {strategy_name}: 成功率 {strategy_info.get('success_rate', 0):.2%}")
    else:
        print("❌ 获取统计信息失败")

def test_hot_search():
    """测试热搜榜"""
    print("\n=== 测试热搜榜 ===")
    response = requests.get(f"{BASE_URL}/hot/search")
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ 获取热搜榜成功")
            word_list = result['data'].get('word_list', [])
            print(f"热搜词数量: {len(word_list)}")
            if word_list:
                print("前3个热搜词:")
                for i, item in enumerate(word_list[:3], 1):
                    print(f"  {i}. {item.get('word')}")
        else:
            print(f"❌ 获取失败: {result.get('error')}")
    else:
        print("❌ 请求失败")

def test_search_videos():
    """测试视频搜索"""
    print("\n=== 测试视频搜索 ===")
    data = {
        "keyword": "美食",
        "type": "video",
        "count": 3
    }

    response = requests.post(f"{BASE_URL}/search", json=data)
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            videos = result['data'].get('videos', [])
            print(f"✅ 搜索成功，找到 {len(videos)} 个视频")
            for i, video in enumerate(videos[:3], 1):
                print(f"  {i}. {video.get('title', '无标题')[:30]}...")
        else:
            print(f"❌ 搜索失败: {result.get('error')}")
    else:
        print("❌ 请求失败")

def main():
    """主函数"""
    print("=" * 50)
    print("抖音解析服务简单测试")
    print("=" * 50)

    # 检查服务是否运行
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code != 200:
            print("❌ 服务未正常响应")
            return
    except:
        print("❌ 无法连接到服务，请确保服务在运行")
        print(f"   尝试连接: {BASE_URL}")
        return

    # 运行测试
    test_health()
    test_stats()
    test_hot_search()
    test_search_videos()
    test_parse_video()

    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)

if __name__ == "__main__":
    main()