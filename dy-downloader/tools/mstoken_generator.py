#!/usr/bin/env python3
"""
msToken生成器
基于研究抖音网站的msToken生成逻辑
"""
import random
import string
import time


def generate_random_str(length: int) -> str:
    """生成指定长度的随机字符串"""
    characters = string.ascii_letters + string.digits + '_-'
    return ''.join(random.choice(characters) for _ in range(length))


def generate_mstoken(length: int = 107) -> str:
    """
    生成msToken
    
    msToken通常是一个长随机字符串，格式类似：
    710-fIIacqPfoNUNM8EKjH2ev0veFV2YZCtCfs_HoN7kjpBKubLAODdh0nStKywolHK2nsJFHmdimUN23q-lo41pxjuiNMoqG1p_yUoIKU0CJ9bX-Q0638LXozcxspQnrzDnHB4M_3Hu3GljVuPYvv-8nHrxp4Xqkw-Bcr0MeothxDuPtHlEBA==
    
    观察到的模式：
    - 长度约107-110字符
    - 包含字母（大小写）、数字、下划线、连字符
    - 可能以数字开头
    - 通常以==结尾（Base64填充）
    
    注意：这是一个简化的实现，真实的msToken可能由服务器端验证
    """
    # 生成主体部分
    main_part = generate_random_str(length - 2)
    
    # 添加Base64风格的结尾
    return main_part + '=='


def generate_mstoken_simple() -> str:
    """
    生成简化版msToken
    某些情况下，较短的msToken也可能工作
    """
    timestamp = str(int(time.time() * 1000))
    random_part = generate_random_str(80)
    return f"{timestamp[:3]}-{random_part}"


if __name__ == "__main__":
    print("msToken生成器测试\n")
    
    print("方法1：标准长度msToken")
    token1 = generate_mstoken()
    print(f"长度: {len(token1)}")
    print(f"Token: {token1}\n")
    
    print("方法2：简化版msToken")
    token2 = generate_mstoken_simple()
    print(f"长度: {len(token2)}")
    print(f"Token: {token2}\n")
    
    print("注意：msToken可能需要由抖音服务器签发才有效")
    print("建议：使用Playwright从实际登录会话中提取msToken")


