#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
抖音视频解析服务
集成多种解析策略，自动切换以提高成功率
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import asyncio
import logging
import time
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
import redis
import json
from concurrent.futures import ThreadPoolExecutor
import os

# 导入解析策略
from strategies.api_strategy import APIStrategy
from strategies.enhanced_api_strategy import EnhancedAPIStrategy
# from strategies.playwright_strategy import PlaywrightStrategy  # 暂时禁用，避免依赖问题
# from strategies.selenium_strategy import SeleniumStrategy  # 暂时禁用，避免依赖问题
from strategies.requests_strategy import RequestsStrategy
from utils.cache_manager import CacheManager
from utils.proxy_manager import ProxyManager
from utils.metrics_collector import MetricsCollector

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app)

# 速率限制
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Redis连接（用于缓存和分布式锁）
try:
    redis_client = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        db=0,
        decode_responses=True
    )
    redis_client.ping()
    logger.info("Redis连接成功")
except:
    logger.warning("Redis不可用，使用内存缓存")
    redis_client = None

# 初始化组件
cache_manager = CacheManager(redis_client)
proxy_manager = ProxyManager()
metrics_collector = MetricsCollector()

# 线程池
executor = ThreadPoolExecutor(max_workers=10)


class ParsingService:
    """解析服务核心类"""

    def __init__(self):
        """初始化解析服务"""
        self.strategies = self._initialize_strategies()
        self.strategy_weights = self._initialize_weights()
        self.failure_counts = {}
        self.success_counts = {}

    def _initialize_strategies(self) -> List:
        """初始化所有解析策略"""
        strategies = []

        # 策略1: API + 签名
        strategies.append({
            'name': 'api_with_signature',
            'handler': APIStrategy(),
            'priority': 1,
            'timeout': 10,
            'enabled': True
        })

        # 策略2: Playwright浏览器自动化（暂时禁用）
        # if os.getenv('ENABLE_PLAYWRIGHT', 'true').lower() == 'true':
        #     strategies.append({
        #         'name': 'playwright',
        #         'handler': PlaywrightStrategy(),
        #         'priority': 2,
        #         'timeout': 30,
        #         'enabled': True
        #     })

        # 策略3: Selenium浏览器自动化（暂时禁用）
        # if os.getenv('ENABLE_SELENIUM', 'false').lower() == 'true':
        #     strategies.append({
        #         'name': 'selenium',
        #         'handler': SeleniumStrategy(),
        #         'priority': 3,
        #         'timeout': 30,
        #         'enabled': True
        #     })

        # 策略4: 简单requests请求
        strategies.append({
            'name': 'requests',
            'handler': RequestsStrategy(),
            'priority': 4,
            'timeout': 15,
            'enabled': True
        })

        return strategies

    def _initialize_weights(self) -> Dict[str, float]:
        """初始化策略权重"""
        return {
            'api_with_signature': 1.0,
            'playwright': 0.8,
            'selenium': 0.6,
            'requests': 0.4
        }

    async def parse_video(self, url: str, options: Dict = None) -> Dict:
        """
        解析视频信息

        Args:
            url: 视频URL
            options: 解析选项

        Returns:
            视频信息字典
        """
        start_time = time.time()
        options = options or {}

        # 检查缓存
        cached_result = cache_manager.get(url)
        if cached_result and not options.get('force_refresh', False):
            logger.info(f"Cache hit for URL: {url}")
            metrics_collector.record_cache_hit()
            return cached_result

        # 获取代理
        proxy = None
        if options.get('use_proxy', False):
            proxy = proxy_manager.get_proxy()

        # 按权重排序策略
        sorted_strategies = self._sort_strategies_by_weight()

        # 尝试每个策略
        last_error = None
        for strategy in sorted_strategies:
            if not strategy['enabled']:
                continue

            strategy_name = strategy['name']
            logger.info(f"Trying strategy: {strategy_name}")

            try:
                # 设置超时
                timeout = strategy.get('timeout', 15)

                # 执行策略
                result = await asyncio.wait_for(
                    self._execute_strategy(strategy, url, proxy, options),
                    timeout=timeout
                )

                if result and self._validate_result(result):
                    # 记录成功
                    self._record_success(strategy_name)

                    # 缓存结果
                    cache_manager.set(url, result, ttl=3600)

                    # 记录指标
                    elapsed = time.time() - start_time
                    metrics_collector.record_parse_success(strategy_name, elapsed)

                    logger.info(f"Successfully parsed with {strategy_name} in {elapsed:.2f}s")
                    return result

            except asyncio.TimeoutError:
                logger.warning(f"Strategy {strategy_name} timed out")
                self._record_failure(strategy_name)
                last_error = f"Strategy {strategy_name} timed out"

            except Exception as e:
                logger.error(f"Strategy {strategy_name} failed: {e}")
                self._record_failure(strategy_name)
                last_error = str(e)

        # 所有策略都失败
        metrics_collector.record_parse_failure()
        raise Exception(f"All strategies failed. Last error: {last_error}")

    async def _execute_strategy(self, strategy: Dict, url: str, proxy: Optional[str], options: Dict) -> Dict:
        """执行单个策略"""
        handler = strategy['handler']

        # 构建策略选项
        strategy_options = {
            'proxy': proxy,
            'cookies': options.get('cookies'),
            'headers': options.get('headers'),
            **options
        }

        # 执行解析
        result = await handler.parse(url, strategy_options)

        return result

    def _validate_result(self, result: Dict) -> bool:
        """验证解析结果"""
        if not result:
            return False

        # 检查必要字段
        required_fields = ['video_id', 'title', 'author']
        for field in required_fields:
            if field not in result:
                return False

        # 检查视频URL
        if 'video_url' in result:
            if not result['video_url'] or result['video_url'] == 'None':
                return False

        return True

    def _sort_strategies_by_weight(self) -> List[Dict]:
        """按权重排序策略"""
        # 计算动态权重
        strategies_with_score = []

        for strategy in self.strategies:
            name = strategy['name']
            base_weight = self.strategy_weights.get(name, 0.5)

            # 根据成功率调整权重
            success_count = self.success_counts.get(name, 0)
            failure_count = self.failure_counts.get(name, 0)

            if success_count + failure_count > 0:
                success_rate = success_count / (success_count + failure_count)
                dynamic_weight = base_weight * (0.5 + success_rate * 0.5)
            else:
                dynamic_weight = base_weight

            strategies_with_score.append({
                **strategy,
                'score': dynamic_weight
            })

        # 排序
        return sorted(strategies_with_score, key=lambda x: x['score'], reverse=True)

    def _record_success(self, strategy_name: str):
        """记录成功"""
        self.success_counts[strategy_name] = self.success_counts.get(strategy_name, 0) + 1

        # 减少失败计数（给策略恢复的机会）
        if strategy_name in self.failure_counts:
            self.failure_counts[strategy_name] = max(0, self.failure_counts[strategy_name] - 0.5)

    def _record_failure(self, strategy_name: str):
        """记录失败"""
        self.failure_counts[strategy_name] = self.failure_counts.get(strategy_name, 0) + 1

    def get_stats(self) -> Dict:
        """获取统计信息"""
        stats = {
            'strategies': {},
            'cache_stats': cache_manager.get_stats(),
            'proxy_stats': proxy_manager.get_stats(),
            'metrics': metrics_collector.get_metrics()
        }

        for strategy in self.strategies:
            name = strategy['name']
            success = self.success_counts.get(name, 0)
            failure = self.failure_counts.get(name, 0)
            total = success + failure

            stats['strategies'][name] = {
                'enabled': strategy['enabled'],
                'priority': strategy['priority'],
                'success': success,
                'failure': failure,
                'total': total,
                'success_rate': success / total if total > 0 else 0,
                'weight': self.strategy_weights.get(name, 0)
            }

        return stats


# 创建解析服务实例
parsing_service = ParsingService()

# 创建增强API策略实例
enhanced_api = EnhancedAPIStrategy()


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/parse', methods=['POST'])
@limiter.limit("10 per minute")
async def parse_video():
    """解析视频接口"""
    try:
        data = request.json
        url = data.get('url')

        if not url:
            return jsonify({'error': 'URL is required'}), 400

        # 解析选项
        options = {
            'use_proxy': data.get('use_proxy', False),
            'force_refresh': data.get('force_refresh', False),
            'cookies': data.get('cookies'),
            'headers': data.get('headers')
        }

        # 执行解析
        result = await parsing_service.parse_video(url, options)

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        logger.error(f"Parse error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/batch_parse', methods=['POST'])
@limiter.limit("5 per minute")
async def batch_parse():
    """批量解析接口"""
    try:
        data = request.json
        urls = data.get('urls', [])

        if not urls:
            return jsonify({'error': 'URLs are required'}), 400

        # 限制批量数量
        if len(urls) > 10:
            return jsonify({'error': 'Maximum 10 URLs per batch'}), 400

        # 并发解析
        tasks = []
        for url in urls:
            options = {
                'use_proxy': data.get('use_proxy', False),
                'cookies': data.get('cookies')
            }
            tasks.append(parsing_service.parse_video(url, options))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理结果
        parsed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                parsed_results.append({
                    'url': urls[i],
                    'success': False,
                    'error': str(result)
                })
            else:
                parsed_results.append({
                    'url': urls[i],
                    'success': True,
                    'data': result
                })

        return jsonify({
            'success': True,
            'results': parsed_results
        })

    except Exception as e:
        logger.error(f"Batch parse error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/stats', methods=['GET'])
def get_stats():
    """获取统计信息"""
    stats = parsing_service.get_stats()
    return jsonify(stats)


@app.route('/clear_cache', methods=['POST'])
@limiter.limit("1 per hour")
def clear_cache():
    """清除缓存"""
    try:
        cache_manager.clear()
        return jsonify({
            'success': True,
            'message': 'Cache cleared'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus指标端点"""
    return metrics_collector.export_prometheus(), 200, {'Content-Type': 'text/plain'}


# ================== 新增API端点 ==================

@app.route('/user/info', methods=['POST'])
@limiter.limit("20 per minute")
async def get_user_info():
    """获取用户信息"""
    try:
        data = request.json
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        result = await enhanced_api.get_user_info(user_id, data.get('options'))

        if result:
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to get user info'
            }), 500

    except Exception as e:
        logger.error(f"Get user info error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/user/posts', methods=['POST'])
@limiter.limit("20 per minute")
async def get_user_posts():
    """获取用户作品列表"""
    try:
        data = request.json
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        result = await enhanced_api.get_user_posts(
            user_id,
            cursor=data.get('cursor', 0),
            count=data.get('count', 20),
            options=data.get('options')
        )

        if result:
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to get user posts'
            }), 500

    except Exception as e:
        logger.error(f"Get user posts error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/user/likes', methods=['POST'])
@limiter.limit("20 per minute")
async def get_user_likes():
    """获取用户点赞作品列表"""
    try:
        data = request.json
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        result = await enhanced_api.get_user_likes(
            user_id,
            cursor=data.get('cursor', 0),
            count=data.get('count', 20),
            options=data.get('options')
        )

        if result:
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to get user likes'
            }), 500

    except Exception as e:
        logger.error(f"Get user likes error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/video/comments', methods=['POST'])
@limiter.limit("30 per minute")
async def get_video_comments():
    """获取视频评论列表"""
    try:
        data = request.json
        video_id = data.get('video_id')

        if not video_id:
            return jsonify({'error': 'video_id is required'}), 400

        result = await enhanced_api.get_video_comments(
            video_id,
            cursor=data.get('cursor', 0),
            count=data.get('count', 20),
            options=data.get('options')
        )

        if result:
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to get comments'
            }), 500

    except Exception as e:
        logger.error(f"Get comments error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/search', methods=['POST'])
@limiter.limit("30 per minute")
async def search():
    """综合搜索"""
    try:
        data = request.json
        keyword = data.get('keyword')

        if not keyword:
            return jsonify({'error': 'keyword is required'}), 400

        search_type = data.get('type', 'general')  # general, video, user, live

        if search_type == 'video':
            result = await enhanced_api.search_videos(
                keyword,
                offset=data.get('offset', 0),
                count=data.get('count', 20),
                sort_type=data.get('sort_type', 0),
                options=data.get('options')
            )
        elif search_type == 'user':
            result = await enhanced_api.search_users(
                keyword,
                offset=data.get('offset', 0),
                count=data.get('count', 20),
                options=data.get('options')
            )
        elif search_type == 'live':
            result = await enhanced_api.search_live_rooms(
                keyword,
                offset=data.get('offset', 0),
                count=data.get('count', 20),
                options=data.get('options')
            )
        else:
            result = await enhanced_api.search_general(
                keyword,
                offset=data.get('offset', 0),
                count=data.get('count', 20),
                search_type=data.get('search_type', 0),
                options=data.get('options')
            )

        if result:
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Search failed'
            }), 500

    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/live/info', methods=['POST'])
@limiter.limit("30 per minute")
async def get_live_info():
    """获取直播间信息"""
    try:
        data = request.json
        room_id = data.get('room_id')

        if not room_id:
            return jsonify({'error': 'room_id is required'}), 400

        result = await enhanced_api.get_live_room_info(
            room_id,
            options=data.get('options')
        )

        if result:
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to get live room info'
            }), 500

    except Exception as e:
        logger.error(f"Get live info error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/music/info', methods=['POST'])
@limiter.limit("30 per minute")
async def get_music_info():
    """获取音乐信息"""
    try:
        data = request.json
        music_id = data.get('music_id')

        if not music_id:
            return jsonify({'error': 'music_id is required'}), 400

        result = await enhanced_api.get_music_info(
            music_id,
            options=data.get('options')
        )

        if result:
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to get music info'
            }), 500

    except Exception as e:
        logger.error(f"Get music info error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/music/videos', methods=['POST'])
@limiter.limit("20 per minute")
async def get_music_videos():
    """获取音乐下的视频列表"""
    try:
        data = request.json
        music_id = data.get('music_id')

        if not music_id:
            return jsonify({'error': 'music_id is required'}), 400

        result = await enhanced_api.get_music_videos(
            music_id,
            cursor=data.get('cursor', 0),
            count=data.get('count', 20),
            options=data.get('options')
        )

        if result:
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to get music videos'
            }), 500

    except Exception as e:
        logger.error(f"Get music videos error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/hot/search', methods=['GET'])
@limiter.limit("60 per minute")
async def get_hot_search():
    """获取热搜榜"""
    try:
        result = await enhanced_api.get_hot_search()

        if result:
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to get hot search'
            }), 500

    except Exception as e:
        logger.error(f"Get hot search error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/suggest', methods=['POST'])
@limiter.limit("60 per minute")
async def get_suggest_words():
    """获取搜索建议词"""
    try:
        data = request.json
        keyword = data.get('keyword')

        if not keyword:
            return jsonify({'error': 'keyword is required'}), 400

        result = await enhanced_api.get_suggest_words(
            keyword,
            options=data.get('options')
        )

        if result:
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to get suggestions'
            }), 500

    except Exception as e:
        logger.error(f"Get suggestions error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/related/videos', methods=['POST'])
@limiter.limit("30 per minute")
async def get_related_videos():
    """获取相关推荐视频"""
    try:
        data = request.json
        video_id = data.get('video_id')

        if not video_id:
            return jsonify({'error': 'video_id is required'}), 400

        result = await enhanced_api.get_related_videos(
            video_id,
            count=data.get('count', 20),
            options=data.get('options')
        )

        if result:
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to get related videos'
            }), 500

    except Exception as e:
        logger.error(f"Get related videos error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/user/following', methods=['POST'])
@limiter.limit("20 per minute")
async def get_following_list():
    """获取用户关注列表"""
    try:
        data = request.json
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        result = await enhanced_api.get_following_list(
            user_id,
            cursor=data.get('cursor', 0),
            count=data.get('count', 20),
            options=data.get('options')
        )

        if result:
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to get following list'
            }), 500

    except Exception as e:
        logger.error(f"Get following list error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/user/followers', methods=['POST'])
@limiter.limit("20 per minute")
async def get_follower_list():
    """获取用户粉丝列表"""
    try:
        data = request.json
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        result = await enhanced_api.get_follower_list(
            user_id,
            cursor=data.get('cursor', 0),
            count=data.get('count', 20),
            options=data.get('options')
        )

        if result:
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to get follower list'
            }), 500

    except Exception as e:
        logger.error(f"Get follower list error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'

    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )