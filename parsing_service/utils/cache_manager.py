#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
缓存管理器
"""

import json
import hashlib
import time
import logging
from typing import Any, Optional, Dict
import redis

logger = logging.getLogger(__name__)


class CacheManager:
    """缓存管理器"""

    def __init__(self, redis_client: redis.Redis, prefix: str = "douyin:cache:"):
        """
        初始化缓存管理器

        Args:
            redis_client: Redis客户端
            prefix: 缓存键前缀
        """
        self.redis = redis_client
        self.prefix = prefix
        self.default_ttl = 3600  # 默认1小时
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
        self.memory_cache = {}  # 内存缓存作为后备
        self.use_memory_cache = False

        # 测试Redis连接
        try:
            if self.redis:
                self.redis.ping()
                logger.info("Redis连接成功")
        except Exception as e:
            logger.warning(f"Redis连接失败，使用内存缓存: {e}")
            self.use_memory_cache = True

    def _make_key(self, key: str) -> str:
        """生成缓存键"""
        # 对URL进行哈希以生成稳定的键
        if key.startswith('http'):
            hash_key = hashlib.md5(key.encode()).hexdigest()
            return f"{self.prefix}url:{hash_key}"
        return f"{self.prefix}{key}"

    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存

        Args:
            key: 缓存键

        Returns:
            缓存值，如果不存在返回None
        """
        # 如果使用内存缓存
        if self.use_memory_cache:
            cache_key = self._make_key(key)
            if cache_key in self.memory_cache:
                cache_data = self.memory_cache[cache_key]
                # 检查是否过期
                if time.time() - cache_data['cached_at'] < cache_data['ttl']:
                    self.stats['hits'] += 1
                    logger.debug(f"Memory cache hit: {key}")
                    return cache_data['value']
                else:
                    # 过期了，删除
                    del self.memory_cache[cache_key]
            self.stats['misses'] += 1
            return None

        # 使用Redis
        try:
            cache_key = self._make_key(key)
            value = self.redis.get(cache_key)

            if value:
                self.stats['hits'] += 1
                logger.debug(f"Cache hit: {key}")
                cache_data = json.loads(value)
                # 兼容旧格式
                if isinstance(cache_data, dict) and 'value' in cache_data:
                    return cache_data['value']
                return cache_data
            else:
                self.stats['misses'] += 1
                logger.debug(f"Cache miss: {key}")
                return None

        except Exception as e:
            logger.error(f"Cache get error: {e}")
            # 尝试使用内存缓存
            self.use_memory_cache = True
            return self.get(key)

    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """
        设置缓存

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒）

        Returns:
            是否设置成功
        """
        cache_key = self._make_key(key)
        ttl = ttl or self.default_ttl

        # 添加元数据
        cache_data = {
            'value': value,
            'cached_at': time.time(),
            'ttl': ttl
        }

        # 如果使用内存缓存
        if self.use_memory_cache:
            self.memory_cache[cache_key] = cache_data
            self.stats['sets'] += 1
            logger.debug(f"Memory cache set: {key} (TTL: {ttl}s)")
            # 清理过期的缓存
            self._cleanup_memory_cache()
            return True

        # 使用Redis
        try:
            self.redis.setex(
                cache_key,
                ttl,
                json.dumps(cache_data, ensure_ascii=False)
            )

            self.stats['sets'] += 1
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return True

        except Exception as e:
            logger.error(f"Cache set error: {e}")
            # 切换到内存缓存
            self.use_memory_cache = True
            return self.set(key, value, ttl)

    def delete(self, key: str) -> bool:
        """
        删除缓存

        Args:
            key: 缓存键

        Returns:
            是否删除成功
        """
        try:
            cache_key = self._make_key(key)
            result = self.redis.delete(cache_key)

            if result:
                self.stats['deletes'] += 1
                logger.debug(f"Cache delete: {key}")
                return True
            return False

        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    def clear(self, pattern: str = None) -> int:
        """
        清除缓存

        Args:
            pattern: 匹配模式，如果为None则清除所有

        Returns:
            清除的键数量
        """
        try:
            if pattern:
                search_pattern = f"{self.prefix}{pattern}*"
            else:
                search_pattern = f"{self.prefix}*"

            keys = self.redis.keys(search_pattern)
            if keys:
                count = self.redis.delete(*keys)
                logger.info(f"Cleared {count} cache keys")
                return count
            return 0

        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return 0

    def exists(self, key: str) -> bool:
        """
        检查缓存是否存在

        Args:
            key: 缓存键

        Returns:
            是否存在
        """
        try:
            cache_key = self._make_key(key)
            return bool(self.redis.exists(cache_key))
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False

    def get_ttl(self, key: str) -> int:
        """
        获取缓存剩余TTL

        Args:
            key: 缓存键

        Returns:
            剩余秒数，-1表示永不过期，-2表示不存在
        """
        try:
            cache_key = self._make_key(key)
            return self.redis.ttl(cache_key)
        except Exception as e:
            logger.error(f"Cache TTL error: {e}")
            return -2

    def get_stats(self) -> Dict:
        """
        获取缓存统计

        Returns:
            统计信息
        """
        total = self.stats['hits'] + self.stats['misses']
        hit_rate = self.stats['hits'] / total if total > 0 else 0

        return {
            **self.stats,
            'total_requests': total,
            'hit_rate': f"{hit_rate:.2%}",
            'cache_size': self._get_cache_size()
        }

    def _get_cache_size(self) -> int:
        """
        获取缓存大小（键数量）

        Returns:
            缓存键数量
        """
        try:
            keys = self.redis.keys(f"{self.prefix}*")
            return len(keys)
        except:
            return 0

    def warmup(self, urls: list, fetcher_func) -> int:
        """
        预热缓存

        Args:
            urls: URL列表
            fetcher_func: 获取数据的函数

        Returns:
            预热成功的数量
        """
        success_count = 0

        for url in urls:
            try:
                # 检查是否已缓存
                if not self.exists(url):
                    # 获取数据
                    data = fetcher_func(url)
                    if data:
                        self.set(url, data)
                        success_count += 1
                        logger.info(f"Cache warmed: {url}")
            except Exception as e:
                logger.error(f"Cache warmup error for {url}: {e}")

        return success_count

    def _cleanup_memory_cache(self):
        """
        清理过期的内存缓存
        """
        if len(self.memory_cache) > 1000:  # 限制最大1000个缓存项
            current_time = time.time()
            expired_keys = [
                k for k, v in self.memory_cache.items()
                if current_time - v['cached_at'] > v['ttl']
            ]
            for k in expired_keys:
                del self.memory_cache[k]

            # 如果还是太多，删除最旧的
            if len(self.memory_cache) > 800:
                sorted_items = sorted(
                    self.memory_cache.items(),
                    key=lambda x: x[1]['cached_at']
                )
                for k, _ in sorted_items[:200]:
                    del self.memory_cache[k]