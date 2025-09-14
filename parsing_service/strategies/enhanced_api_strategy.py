#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强版API策略 - 支持用户、直播、评论、搜索等功能
"""

import asyncio
import aiohttp
import json
import time
import random
import string
import logging
import re
from typing import Dict, Optional, List, Any
from urllib.parse import urlparse, parse_qs
from .base_strategy import BaseStrategy
import sys
import os

# 添加父目录到路径以导入签名生成器
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from xbogus_generator import generate_x_bogus, generate_a_bogus

logger = logging.getLogger(__name__)


class EnhancedAPIStrategy(BaseStrategy):
    """增强版API策略，支持更多抖音功能"""

    def __init__(self):
        """初始化增强版API策略"""
        super().__init__()
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        self.device_platform = "webapp"
        self.aid = "6383"
        self.version_code = "170400"
        self.version_name = "17.4.0"

        # API端点
        self.endpoints = {
            'video_detail': 'https://www.douyin.com/aweme/v1/web/aweme/detail/',
            'user_info': 'https://www.douyin.com/aweme/v1/web/user/profile/other/',
            'user_posts': 'https://www.douyin.com/aweme/v1/web/aweme/post/',
            'user_favorite': 'https://www.douyin.com/aweme/v1/web/aweme/favorite/',
            'user_like': 'https://www.douyin.com/aweme/v1/web/aweme/like/',
            'comments': 'https://www.douyin.com/aweme/v1/web/comment/list/',
            'comment_reply': 'https://www.douyin.com/aweme/v1/web/comment/list/reply/',
            'search_general': 'https://www.douyin.com/aweme/v1/web/general/search/single/',
            'search_user': 'https://www.douyin.com/aweme/v1/web/discover/search/',
            'search_video': 'https://www.douyin.com/aweme/v1/web/search/item/',
            'search_live': 'https://www.douyin.com/aweme/v1/web/live/search/',
            'music_info': 'https://www.douyin.com/aweme/v1/web/music/detail/',
            'music_videos': 'https://www.douyin.com/aweme/v1/web/music/aweme/',
            'live_room_info': 'https://webcast.amemv.com/webcast/room/reflow/info/',
            'live_room_detail': 'https://webcast.amemv.com/webcast/room/web/enter/',
            'suggest_words': 'https://www.douyin.com/aweme/v1/web/api/suggest_words/',
            'hot_search': 'https://www.douyin.com/aweme/v1/web/hot/search/list/',
            'related_video': 'https://www.douyin.com/aweme/v1/web/aweme/related/',
            'follow_list': 'https://www.douyin.com/aweme/v1/web/user/following/list/',
            'follower_list': 'https://www.douyin.com/aweme/v1/web/user/follower/list/',
            'friend_feed': 'https://www.douyin.com/aweme/v1/web/familiar/feed/'
        }

    async def get_video_detail(self, video_id: str, options: Dict = None) -> Dict:
        """获取视频详情"""
        params = self._build_common_params()
        params['aweme_id'] = video_id

        result = await self._make_request(
            self.endpoints['video_detail'],
            params,
            options
        )

        if result and 'aweme_detail' in result:
            return self.normalize_video_info(result)
        return None

    async def get_user_info(self, user_id: str, options: Dict = None) -> Dict:
        """获取用户信息"""
        params = self._build_common_params()
        params['source_page'] = 'user_detail'
        params['sec_user_id'] = user_id if user_id.startswith('MS4wLjABAAAA') else await self._get_sec_user_id(user_id)

        result = await self._make_request(
            self.endpoints['user_info'],
            params,
            options
        )

        if result and 'user' in result:
            return self._normalize_user_info(result['user'])
        return None

    async def get_user_posts(self, user_id: str, cursor: int = 0, count: int = 20, options: Dict = None) -> Dict:
        """获取用户作品列表"""
        sec_user_id = user_id if user_id.startswith('MS4wLjABAAAA') else await self._get_sec_user_id(user_id)

        params = self._build_common_params()
        params.update({
            'sec_user_id': sec_user_id,
            'count': count,
            'max_cursor': cursor,
            'aid': self.aid,
            'cut_version': '1',
            'source_page': 'user_detail'
        })

        # 设置请求类型，用于过滤session cookie
        if options is None:
            options = {}
        options['request_type'] = 'user_posts'

        result = await self._make_request(
            self.endpoints['user_posts'],
            params,
            options
        )

        if result and 'aweme_list' in result:
            return {
                'posts': [self.normalize_video_info({'aweme_detail': item}) for item in result['aweme_list']],
                'has_more': result.get('has_more', False),
                'max_cursor': result.get('max_cursor', 0),
                'total': result.get('total', 0)
            }
        return None

    async def get_user_likes(self, user_id: str, cursor: int = 0, count: int = 20, options: Dict = None) -> Dict:
        """获取用户点赞作品列表"""
        sec_user_id = user_id if user_id.startswith('MS4wLjABAAAA') else await self._get_sec_user_id(user_id)

        params = self._build_common_params()
        params.update({
            'sec_user_id': sec_user_id,
            'count': count,
            'max_cursor': cursor
        })

        result = await self._make_request(
            self.endpoints['user_like'],
            params,
            options
        )

        if result and 'aweme_list' in result:
            return {
                'likes': [self.normalize_video_info({'aweme_detail': item}) for item in result['aweme_list']],
                'has_more': result.get('has_more', False),
                'max_cursor': result.get('max_cursor', 0)
            }
        return None

    async def get_video_comments(self, video_id: str, cursor: int = 0, count: int = 20, options: Dict = None) -> Dict:
        """获取视频评论列表"""
        params = self._build_common_params()
        params.update({
            'aweme_id': video_id,
            'cursor': cursor,
            'count': count,
            'item_type': 0
        })

        result = await self._make_request(
            self.endpoints['comments'],
            params,
            options
        )

        if result and 'comments' in result:
            return {
                'comments': [self._normalize_comment(comment) for comment in result['comments']],
                'has_more': result.get('has_more', False),
                'cursor': result.get('cursor', 0),
                'total': result.get('total', 0)
            }
        return None

    async def get_comment_replies(self, item_id: str, comment_id: str, cursor: int = 0, count: int = 20, options: Dict = None) -> Dict:
        """获取评论回复列表"""
        params = self._build_common_params()
        params.update({
            'item_id': item_id,
            'comment_id': comment_id,
            'cursor': cursor,
            'count': count
        })

        result = await self._make_request(
            self.endpoints['comment_reply'],
            params,
            options
        )

        if result and 'comments' in result:
            return {
                'replies': [self._normalize_comment(comment) for comment in result['comments']],
                'has_more': result.get('has_more', False),
                'cursor': result.get('cursor', 0)
            }
        return None

    async def search_general(self, keyword: str, offset: int = 0, count: int = 20, search_type: int = 0, options: Dict = None) -> Dict:
        """综合搜索
        search_type: 0-综合 1-视频 2-用户 3-直播 4-话题 5-商品
        """
        params = self._build_common_params()
        params.update({
            'keyword': keyword,
            'offset': offset,
            'count': count,
            'search_channel': 'aweme_general',
            'enable_history': '1',
            'is_filter_search': '0',
            'search_source': 'normal_search'
        })

        if search_type > 0:
            params['search_type'] = search_type

        result = await self._make_request(
            self.endpoints['search_general'],
            params,
            options
        )

        if result:
            return self._normalize_search_result(result)
        return None

    async def search_videos(self, keyword: str, offset: int = 0, count: int = 20, sort_type: int = 0, options: Dict = None) -> Dict:
        """搜索视频
        sort_type: 0-综合排序 1-最多点赞 2-最新发布
        """
        params = self._build_common_params()
        params.update({
            'keyword': keyword,
            'offset': offset,
            'count': count,
            'sort_type': sort_type,
            'publish_time': 0,
            'search_source': 'normal_search'
        })

        result = await self._make_request(
            self.endpoints['search_video'],
            params,
            options
        )

        if result and 'data' in result:
            videos = []
            for item in result['data']:
                if 'aweme_info' in item:
                    videos.append(self.normalize_video_info({'aweme_detail': item['aweme_info']}))

            return {
                'videos': videos,
                'has_more': result.get('has_more', False),
                'cursor': result.get('cursor', 0)
            }
        return None

    async def search_users(self, keyword: str, offset: int = 0, count: int = 20, options: Dict = None) -> Dict:
        """搜索用户"""
        params = self._build_common_params()
        params.update({
            'keyword': keyword,
            'offset': offset,
            'count': count,
            'search_source': 'normal_search',
            'type': 1
        })

        result = await self._make_request(
            self.endpoints['search_user'],
            params,
            options
        )

        if result and 'user_list' in result:
            return {
                'users': [self._normalize_user_info(user['user_info']) for user in result['user_list']],
                'has_more': result.get('has_more', False),
                'cursor': result.get('cursor', 0)
            }
        return None

    async def search_live_rooms(self, keyword: str, offset: int = 0, count: int = 20, options: Dict = None) -> Dict:
        """搜索直播间"""
        params = self._build_common_params()
        params.update({
            'keyword': keyword,
            'offset': offset,
            'count': count
        })

        result = await self._make_request(
            self.endpoints['search_live'],
            params,
            options
        )

        if result and 'data' in result:
            return {
                'live_rooms': [self._normalize_live_room(room) for room in result['data']],
                'has_more': result.get('has_more', False),
                'cursor': result.get('cursor', 0)
            }
        return None

    async def get_live_room_info(self, room_id: str, options: Dict = None) -> Dict:
        """获取直播间信息"""
        params = {
            'room_id': room_id,
            'app_id': '1128'
        }

        result = await self._make_request(
            self.endpoints['live_room_info'],
            params,
            options,
            use_bogus=False  # 直播API不需要X-Bogus
        )

        if result and 'data' in result:
            return self._normalize_live_room(result['data'])
        return None

    async def get_music_info(self, music_id: str, options: Dict = None) -> Dict:
        """获取音乐信息"""
        params = self._build_common_params()
        params['music_id'] = music_id

        result = await self._make_request(
            self.endpoints['music_info'],
            params,
            options
        )

        if result and 'music_info' in result:
            return self._normalize_music_info(result['music_info'])
        return None

    async def get_music_videos(self, music_id: str, cursor: int = 0, count: int = 20, options: Dict = None) -> Dict:
        """获取音乐下的视频列表"""
        params = self._build_common_params()
        params.update({
            'music_id': music_id,
            'cursor': cursor,
            'count': count
        })

        result = await self._make_request(
            self.endpoints['music_videos'],
            params,
            options
        )

        if result and 'aweme_list' in result:
            return {
                'videos': [self.normalize_video_info({'aweme_detail': item}) for item in result['aweme_list']],
                'has_more': result.get('has_more', False),
                'cursor': result.get('cursor', 0)
            }
        return None

    async def get_hot_search(self, options: Dict = None) -> Dict:
        """获取热搜榜"""
        params = self._build_common_params()
        params['detail_list'] = '1'

        result = await self._make_request(
            self.endpoints['hot_search'],
            params,
            options
        )

        if result and 'data' in result:
            return {
                'word_list': result['data'].get('word_list', []),
                'trending_list': result['data'].get('trending_list', [])
            }
        return None

    async def get_suggest_words(self, keyword: str, options: Dict = None) -> Dict:
        """获取搜索建议词"""
        params = self._build_common_params()
        params.update({
            'query': keyword,
            'count': 20,
            'source': 'search_input'
        })

        result = await self._make_request(
            self.endpoints['suggest_words'],
            params,
            options
        )

        if result and 'sug_list' in result:
            return {
                'suggestions': result['sug_list']
            }
        return None

    async def get_related_videos(self, video_id: str, count: int = 20, options: Dict = None) -> Dict:
        """获取相关推荐视频"""
        params = self._build_common_params()
        params.update({
            'aweme_id': video_id,
            'count': count,
            'filterGids': video_id
        })

        result = await self._make_request(
            self.endpoints['related_video'],
            params,
            options
        )

        if result and 'aweme_list' in result:
            return {
                'videos': [self.normalize_video_info({'aweme_detail': item}) for item in result['aweme_list']]
            }
        return None

    async def get_following_list(self, user_id: str, cursor: int = 0, count: int = 20, options: Dict = None) -> Dict:
        """获取用户关注列表"""
        sec_user_id = user_id if user_id.startswith('MS4wLjABAAAA') else await self._get_sec_user_id(user_id)

        params = self._build_common_params()
        params.update({
            'user_id': sec_user_id,
            'sec_user_id': sec_user_id,
            'offset': cursor,
            'count': count,
            'source_type': '1'
        })

        result = await self._make_request(
            self.endpoints['follow_list'],
            params,
            options
        )

        if result and 'followings' in result:
            return {
                'users': [self._normalize_user_info(user) for user in result['followings']],
                'has_more': result.get('has_more', False),
                'offset': result.get('offset', 0),
                'total': result.get('total', 0)
            }
        return None

    async def get_follower_list(self, user_id: str, cursor: int = 0, count: int = 20, options: Dict = None) -> Dict:
        """获取用户粉丝列表"""
        sec_user_id = user_id if user_id.startswith('MS4wLjABAAAA') else await self._get_sec_user_id(user_id)

        params = self._build_common_params()
        params.update({
            'user_id': sec_user_id,
            'sec_user_id': sec_user_id,
            'offset': cursor,
            'count': count,
            'source_type': '2'
        })

        result = await self._make_request(
            self.endpoints['follower_list'],
            params,
            options
        )

        if result and 'followers' in result:
            return {
                'users': [self._normalize_user_info(user) for user in result['followers']],
                'has_more': result.get('has_more', False),
                'offset': result.get('offset', 0),
                'total': result.get('total', 0)
            }
        return None

    async def _make_request(self, url: str, params: Dict, options: Dict = None, use_bogus: bool = True) -> Dict:
        """发送HTTP请求"""
        options = options or {}

        # 生成签名
        params_str = '&'.join([f"{k}={v}" for k, v in params.items()])

        if use_bogus:
            x_bogus = generate_x_bogus(params_str, self.user_agent)
            full_url = f"{url}?{params_str}&X-Bogus={x_bogus}"
        else:
            full_url = f"{url}?{params_str}"

        # 构建请求头
        headers = self._build_headers(options)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    full_url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=15),
                    proxy=options.get('proxy')
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Request failed with status {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Request error: {e}")
            return None

    def _build_common_params(self) -> Dict:
        """构建通用请求参数"""
        mstoken = ''.join(random.choices(string.ascii_letters + string.digits + '-_=', k=107))

        return {
            'device_platform': self.device_platform,
            'aid': self.aid,
            'channel': 'channel_pc_web',
            'pc_client_type': '1',
            'version_code': self.version_code,
            'version_name': self.version_name,
            'cookie_enabled': 'true',
            'screen_width': '1920',
            'screen_height': '1080',
            'browser_language': 'zh-CN',
            'browser_platform': 'MacIntel',
            'browser_name': 'Chrome',
            'browser_version': '122.0.0.0',
            'browser_online': 'true',
            'engine_name': 'Blink',
            'engine_version': '122.0.0.0',
            'os_name': 'Mac OS',
            'os_version': '10.15.7',
            'cpu_core_num': '8',
            'device_memory': '8',
            'platform': 'PC',
            'downlink': '10',
            'effective_type': '4g',
            'round_trip_time': '50',
            'msToken': mstoken
        }

    def _build_headers(self, options: Dict = None) -> Dict:
        """构建请求头"""
        options = options or {}

        headers = {
            'User-Agent': self.user_agent,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.douyin.com/',
            'Origin': 'https://www.douyin.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        }

        # 添加自定义头部
        if options.get('headers'):
            headers.update(options['headers'])

        # 添加Cookie
        if options.get('cookies'):
            if isinstance(options['cookies'], dict):
                cookie_str = '; '.join([f"{k}={v}" for k, v in options['cookies'].items()])
                headers['Cookie'] = cookie_str
            elif isinstance(options['cookies'], str):
                headers['Cookie'] = options['cookies']

        return headers

    async def _get_sec_user_id(self, user_id: str) -> str:
        """获取sec_user_id"""
        # 这里需要实现从用户ID获取sec_user_id的逻辑
        # 可以通过用户主页URL或其他API获取
        # 暂时返回原值
        return user_id

    def _normalize_user_info(self, user_data: Dict) -> Dict:
        """标准化用户信息"""
        return {
            'user_id': user_data.get('uid'),
            'sec_uid': user_data.get('sec_uid'),
            'nickname': user_data.get('nickname'),
            'signature': user_data.get('signature'),
            'avatar': user_data.get('avatar_larger', {}).get('url_list', [''])[0],
            'following_count': user_data.get('following_count', 0),
            'follower_count': user_data.get('follower_count', 0),
            'total_favorited': user_data.get('total_favorited', 0),
            'aweme_count': user_data.get('aweme_count', 0),
            'favoriting_count': user_data.get('favoriting_count', 0),
            'verification_type': user_data.get('verification_type', 0),
            'custom_verify': user_data.get('custom_verify', ''),
            'enterprise_verify_reason': user_data.get('enterprise_verify_reason', ''),
            'is_gov_media_vip': user_data.get('is_gov_media_vip', False)
        }

    def _normalize_comment(self, comment_data: Dict) -> Dict:
        """标准化评论信息"""
        return {
            'comment_id': comment_data.get('cid'),
            'text': comment_data.get('text'),
            'create_time': comment_data.get('create_time'),
            'digg_count': comment_data.get('digg_count', 0),
            'reply_count': comment_data.get('reply_comment_total', 0),
            'user': self._normalize_user_info(comment_data.get('user', {})),
            'reply_to': comment_data.get('reply_to', []),
            'image_list': comment_data.get('image_list', [])
        }

    def _normalize_search_result(self, search_data: Dict) -> Dict:
        """标准化搜索结果"""
        result = {
            'has_more': search_data.get('has_more', False),
            'cursor': search_data.get('cursor', 0),
            'data': []
        }

        if 'data' in search_data:
            for item in search_data['data']:
                if 'aweme_info' in item:
                    result['data'].append({
                        'type': 'video',
                        'data': self.normalize_video_info({'aweme_detail': item['aweme_info']})
                    })
                elif 'user_list' in item:
                    for user in item['user_list']:
                        result['data'].append({
                            'type': 'user',
                            'data': self._normalize_user_info(user['user_info'])
                        })
                elif 'live_list' in item:
                    for live in item['live_list']:
                        result['data'].append({
                            'type': 'live',
                            'data': self._normalize_live_room(live['live_room'])
                        })

        return result

    def _normalize_live_room(self, live_data: Dict) -> Dict:
        """标准化直播间信息"""
        room = live_data.get('room', live_data)
        owner = room.get('owner', {})
        stats = room.get('stats', {})
        stream_url = room.get('stream_url', {})

        return {
            'room_id': room.get('id_str', room.get('id')),
            'title': room.get('title'),
            'cover': room.get('cover', {}).get('url_list', [''])[0] if isinstance(room.get('cover'), dict) else room.get('cover'),
            'user_count': stats.get('user_count_str', stats.get('user_count', 0)),
            'like_count': stats.get('like_count', 0),
            'status': room.get('status', 0),
            'owner': {
                'user_id': owner.get('id_str', owner.get('id')),
                'nickname': owner.get('nickname'),
                'avatar': owner.get('avatar_thumb', {}).get('url_list', [''])[0] if isinstance(owner.get('avatar_thumb'), dict) else ''
            },
            'stream_url': {
                'flv': stream_url.get('flv_pull_url', {}),
                'hls': stream_url.get('hls_pull_url_map', {}),
                'rtmp': stream_url.get('rtmp_pull_url', '')
            },
            'create_time': room.get('create_time', 0),
            'share_url': f"https://www.douyin.com/share/live/{room.get('id_str', room.get('id'))}"
        }

    def _normalize_music_info(self, music_data: Dict) -> Dict:
        """标准化音乐信息"""
        return {
            'music_id': music_data.get('id_str', music_data.get('id')),
            'title': music_data.get('title'),
            'author': music_data.get('author'),
            'album': music_data.get('album'),
            'cover': music_data.get('cover_large', {}).get('url_list', [''])[0] if isinstance(music_data.get('cover_large'), dict) else '',
            'play_url': music_data.get('play_url', {}).get('url_list', [''])[0] if isinstance(music_data.get('play_url'), dict) else '',
            'duration': music_data.get('duration', 0),
            'user_count': music_data.get('user_count', 0),
            'share_url': f"https://www.douyin.com/music/{music_data.get('id_str', music_data.get('id'))}"
        }

    async def parse(self, url: str, options: Dict = None) -> Dict:
        """解析URL并返回相应数据"""
        # 判断URL类型
        url_type = self._identify_url_type(url)

        if url_type == 'video':
            video_id = self.extract_video_id(url)
            return await self.get_video_detail(video_id, options)

        elif url_type == 'user':
            user_id = self._extract_user_id(url)
            return await self.get_user_info(user_id, options)

        elif url_type == 'live':
            room_id = self._extract_live_room_id(url)
            return await self.get_live_room_info(room_id, options)

        elif url_type == 'music':
            music_id = self._extract_music_id(url)
            return await self.get_music_info(music_id, options)

        else:
            # 默认作为视频处理
            video_id = self.extract_video_id(url)
            if video_id:
                return await self.get_video_detail(video_id, options)

            raise ValueError(f"无法识别的URL类型: {url}")

    def _identify_url_type(self, url: str) -> str:
        """识别URL类型"""
        if '/video/' in url or 'v.douyin.com' in url:
            return 'video'
        elif '/user/' in url:
            return 'user'
        elif '/live/' in url or 'live.douyin.com' in url:
            return 'live'
        elif '/music/' in url:
            return 'music'
        else:
            return 'unknown'

    def _extract_user_id(self, url: str) -> str:
        """从URL提取用户ID"""
        # 匹配用户主页URL
        patterns = [
            r'/user/(MS4wLjABAAAA[\w-]+)',
            r'sec_uid=(MS4wLjABAAAA[\w-]+)',
            r'/share/user/(\d+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    def _extract_live_room_id(self, url: str) -> str:
        """从URL提取直播间ID"""
        patterns = [
            r'/live/(\d+)',
            r'room_id=(\d+)',
            r'reflow/(\d+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    def _extract_music_id(self, url: str) -> str:
        """从URL提取音乐ID"""
        patterns = [
            r'/music/(\d+)',
            r'music_id=(\d+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None