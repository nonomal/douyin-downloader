# 抖音解析服务 API 文档

## 概述

本解析服务提供了完整的抖音数据获取功能，包括视频、用户、直播、评论、搜索等多个维度的数据接口。

## 基础信息

- **基础URL**: `http://localhost:5000`
- **请求格式**: JSON
- **响应格式**: JSON
- **速率限制**: 根据接口不同，有不同的速率限制

## API 端点

### 1. 视频相关

#### 1.1 解析视频信息
- **端点**: `/parse`
- **方法**: POST
- **速率限制**: 10次/分钟
- **请求参数**:
```json
{
    "url": "视频URL",
    "use_proxy": false,
    "force_refresh": false,
    "cookies": {},
    "headers": {}
}
```
- **响应示例**:
```json
{
    "success": true,
    "data": {
        "video_id": "123456",
        "title": "视频标题",
        "author": "作者",
        "video_url": "无水印视频链接",
        "cover_url": "封面图片",
        "statistics": {
            "play_count": 1000,
            "like_count": 100,
            "comment_count": 50,
            "share_count": 20
        }
    }
}
```

#### 1.2 批量解析视频
- **端点**: `/batch_parse`
- **方法**: POST
- **速率限制**: 5次/分钟
- **请求参数**:
```json
{
    "urls": ["url1", "url2", "url3"],
    "use_proxy": false,
    "cookies": {}
}
```

#### 1.3 获取视频评论
- **端点**: `/video/comments`
- **方法**: POST
- **速率限制**: 30次/分钟
- **请求参数**:
```json
{
    "video_id": "视频ID",
    "cursor": 0,
    "count": 20
}
```

#### 1.4 获取相关推荐视频
- **端点**: `/related/videos`
- **方法**: POST
- **速率限制**: 30次/分钟
- **请求参数**:
```json
{
    "video_id": "视频ID",
    "count": 20
}
```

### 2. 用户相关

#### 2.1 获取用户信息
- **端点**: `/user/info`
- **方法**: POST
- **速率限制**: 20次/分钟
- **请求参数**:
```json
{
    "user_id": "用户ID或sec_user_id"
}
```
- **响应示例**:
```json
{
    "success": true,
    "data": {
        "user_id": "123456",
        "nickname": "用户昵称",
        "signature": "个性签名",
        "avatar": "头像URL",
        "follower_count": 10000,
        "following_count": 100,
        "aweme_count": 50
    }
}
```

#### 2.2 获取用户作品列表
- **端点**: `/user/posts`
- **方法**: POST
- **速率限制**: 20次/分钟
- **请求参数**:
```json
{
    "user_id": "用户ID",
    "cursor": 0,
    "count": 20
}
```

#### 2.3 获取用户点赞列表
- **端点**: `/user/likes`
- **方法**: POST
- **速率限制**: 20次/分钟
- **请求参数**:
```json
{
    "user_id": "用户ID",
    "cursor": 0,
    "count": 20
}
```

#### 2.4 获取用户关注列表
- **端点**: `/user/following`
- **方法**: POST
- **速率限制**: 20次/分钟
- **请求参数**:
```json
{
    "user_id": "用户ID",
    "cursor": 0,
    "count": 20
}
```

#### 2.5 获取用户粉丝列表
- **端点**: `/user/followers`
- **方法**: POST
- **速率限制**: 20次/分钟
- **请求参数**:
```json
{
    "user_id": "用户ID",
    "cursor": 0,
    "count": 20
}
```

### 3. 搜索相关

#### 3.1 综合搜索
- **端点**: `/search`
- **方法**: POST
- **速率限制**: 30次/分钟
- **请求参数**:
```json
{
    "keyword": "搜索关键词",
    "type": "general",  // general/video/user/live
    "offset": 0,
    "count": 20,
    "sort_type": 0  // 0-综合 1-最多点赞 2-最新发布
}
```

#### 3.2 获取热搜榜
- **端点**: `/hot/search`
- **方法**: GET
- **速率限制**: 60次/分钟
- **响应示例**:
```json
{
    "success": true,
    "data": {
        "word_list": [
            {
                "word": "热搜词",
                "hot_value": 1000000
            }
        ]
    }
}
```

#### 3.3 获取搜索建议
- **端点**: `/suggest`
- **方法**: POST
- **速率限制**: 60次/分钟
- **请求参数**:
```json
{
    "keyword": "关键词"
}
```

### 4. 直播相关

#### 4.1 获取直播间信息
- **端点**: `/live/info`
- **方法**: POST
- **速率限制**: 30次/分钟
- **请求参数**:
```json
{
    "room_id": "直播间ID"
}
```
- **响应示例**:
```json
{
    "success": true,
    "data": {
        "room_id": "123456",
        "title": "直播间标题",
        "cover": "封面图片",
        "user_count": "10000",
        "status": 2,  // 2-直播中
        "owner": {
            "user_id": "789",
            "nickname": "主播昵称",
            "avatar": "头像URL"
        },
        "stream_url": {
            "flv": {},
            "hls": {},
            "rtmp": ""
        }
    }
}
```

### 5. 音乐相关

#### 5.1 获取音乐信息
- **端点**: `/music/info`
- **方法**: POST
- **速率限制**: 30次/分钟
- **请求参数**:
```json
{
    "music_id": "音乐ID"
}
```

#### 5.2 获取音乐下的视频
- **端点**: `/music/videos`
- **方法**: POST
- **速率限制**: 20次/分钟
- **请求参数**:
```json
{
    "music_id": "音乐ID",
    "cursor": 0,
    "count": 20
}
```

### 6. 系统相关

#### 6.1 健康检查
- **端点**: `/health`
- **方法**: GET
- **响应示例**:
```json
{
    "status": "healthy",
    "timestamp": "2024-01-01T00:00:00"
}
```

#### 6.2 获取统计信息
- **端点**: `/stats`
- **方法**: GET
- **响应示例**:
```json
{
    "strategies": {
        "api_with_signature": {
            "enabled": true,
            "priority": 1,
            "success": 100,
            "failure": 10,
            "success_rate": 0.91
        }
    },
    "cache_stats": {},
    "proxy_stats": {},
    "metrics": {}
}
```

#### 6.3 清除缓存
- **端点**: `/clear_cache`
- **方法**: POST
- **速率限制**: 1次/小时

#### 6.4 Prometheus指标
- **端点**: `/metrics`
- **方法**: GET
- **响应格式**: text/plain

## 错误码

| 错误码 | 说明 |
|-------|------|
| 400 | 请求参数错误 |
| 429 | 请求频率超限 |
| 500 | 服务器内部错误 |

## 使用示例

### Python示例
```python
import requests
import json

# 获取视频信息
url = "http://localhost:5000/parse"
data = {
    "url": "https://www.douyin.com/video/7123456789"
}
response = requests.post(url, json=data)
result = response.json()
print(result)

# 搜索视频
url = "http://localhost:5000/search"
data = {
    "keyword": "美食",
    "type": "video",
    "count": 10
}
response = requests.post(url, json=data)
result = response.json()
print(result)
```

### cURL示例
```bash
# 获取用户信息
curl -X POST http://localhost:5000/user/info \
  -H "Content-Type: application/json" \
  -d '{"user_id": "MS4wLjABAAAA..."}'

# 获取热搜榜
curl -X GET http://localhost:5000/hot/search
```

## 注意事项

1. **速率限制**: 请遵守各接口的速率限制，避免被封禁
2. **Cookie使用**: 某些接口可能需要有效的Cookie才能获取完整数据
3. **代理使用**: 在请求频繁时建议使用代理
4. **缓存机制**: 系统内置缓存机制，相同请求会返回缓存数据
5. **错误处理**: 请妥善处理各种错误情况，实现重试机制

## 更新日志

### v2.0.0 (2024-01-XX)
- 新增用户相关API（信息、作品、点赞、关注、粉丝）
- 新增直播间信息API
- 新增评论获取API
- 新增搜索功能（综合、视频、用户、直播）
- 新增音乐相关API
- 新增热搜榜和搜索建议API
- 优化API策略，提高成功率

### v1.0.0
- 基础视频解析功能
- 批量解析支持
- 多策略自动切换