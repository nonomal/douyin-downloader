# 抖音下载器 - 无水印批量下载工具

![douyin-downloader](https://socialify.git.ci/jiji262/douyin-downloader/image?custom_description=%E6%8A%96%E9%9F%B3%E6%89%B9%E9%87%8F%E4%B8%8B%E8%BD%BD%E5%B7%A5%E5%85%B7%EF%BC%8C%E5%8E%BB%E6%B0%B4%E5%8D%B0%EF%BC%8C%E6%94%AF%E6%8C%81%E8%A7%86%E9%A2%91%E3%80%81%E5%9B%BE%E9%9B%86%E3%80%81%E5%90%88%E9%9B%86%E3%80%81%E9%9F%B3%E4%B9%90%28%E5%8E%9F%E5%A3%B0%29%E3%80%82%0A%E5%85%8D%E8%B4%B9%EF%BC%81%E5%85%8D%E8%B4%B9%EF%BC%81%E5%85%8D%E8%B4%B9%EF%BC%81&description=1&font=Jost&forks=1&logo=https%3A%2F%2Fraw.githubusercontent.com%2Fjiji262%2Fdouyin-downloader%2Frefs%2Fheads%2Fmain%2Fimg%2Flogo.png&name=1&owner=1&pattern=Circuit+Board&pulls=1&stargazers=1&theme=Light)

一个功能强大的抖音内容批量下载工具，支持视频、图集、音乐、直播等多种内容类型的下载。提供两个版本：V1.0（稳定版）和 V2.0（增强版）。

## 📋 目录

- [快速开始](#-快速开始)
- [版本说明](#-版本说明)
- [V1.0 使用指南](#-v10-使用指南)
- [V2.0 使用指南](#-v20-使用指南)
- [Cookie 配置工具](#-cookie-配置工具)
- [支持的链接类型](#-支持的链接类型)
- [常见问题](#-常见问题)
- [更新日志](#-更新日志)

## ⚡ 快速开始

### 环境要求

- **Python 3.9+**
- **操作系统**：Windows、macOS、Linux

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/jiji262/douyin-downloader.git
cd douyin-downloader
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **准备 Cookie**（首次使用必需）

抖音下载需要有效的登录Cookie才能正常工作。您可以选择：
- **V1.0**：需要手动配置Cookie到配置文件
- **V2.0**：支持自动获取Cookie或从浏览器提取

## 📦 版本说明

### V1.0 (DouYinCommand.py) - 稳定版
- ✅ **经过验证**：稳定可靠，经过大量测试
- ✅ **简单易用**：配置文件驱动，使用简单
- ✅ **功能完整**：支持所有内容类型下载
- ✅ **单个视频下载**：完全正常工作
- ⚠️ **需要手动配置**：需要手动获取和配置 Cookie

### V2.0 (downloader.py) - 增强版
- 🚀 **自动 Cookie 管理**：支持自动获取和刷新 Cookie
- 🚀 **统一入口**：整合所有功能到单一脚本
- 🚀 **异步架构**：性能更优，支持并发下载
- 🚀 **智能重试**：自动重试和错误恢复
- 🚀 **增量下载**：支持增量更新，避免重复下载
- ⚠️ **单个视频下载**：目前 API 返回空响应（已知问题）
- ✅ **用户主页下载**：完全正常工作

## 🎯 V1.0 使用指南（稳定版）

### 第一步：准备配置文件

```bash
# 复制示例配置文件
cp config_douyin_example.yml config_douyin.yml

# 编辑配置文件
nano config_douyin.yml  # 或使用任何文本编辑器
```

### 第二步：配置文件详解

```yaml
# ===== 下载链接配置 =====
link:
  - https://v.douyin.com/xxxxx/           # 短链接
  - https://www.douyin.com/video/xxxxx    # 视频直链
  - https://www.douyin.com/user/xxxxx     # 用户主页
  - https://www.douyin.com/collection/xxx # 合集链接

# ===== 保存路径配置 =====
path: ./Downloaded/                       # 下载保存目录

# ===== Cookie配置（必填）=====
cookies:
  msToken: xxx                            # 必需
  ttwid: xxx                              # 必需
  odin_tt: xxx                            # 可选但推荐
  passport_csrf_token: xxx                # 可选但推荐
  sid_guard: xxx                          # 可选但推荐
  sessionid: xxx                          # 登录状态标识

# ===== 下载选项 =====
music: true                               # 下载背景音乐
cover: true                               # 下载视频封面
avatar: true                              # 下载作者头像
json: true                                # 保存元数据JSON

# ===== 下载模式 =====
mode:
  - post                                  # 下载发布作品
  # - like                                # 下载喜欢作品（需要账号权限）
  # - mix                                 # 下载合集作品

# ===== 数量限制 =====
number:
  post: 0                                 # 0表示下载全部
  like: 20                                # 限制下载20个
  allmix: 5                               # 下载5个合集
  mix: 10                                 # 每个合集下载10个

# ===== 性能设置 =====
thread: 5                                 # 并发下载线程数
retry: 3                                  # 失败重试次数
timeout: 10                               # 请求超时时间（秒）

# ===== 其他设置 =====
database: true                            # 启用数据库记录
proxy: null                               # 代理设置（可选）
```

### 第三步：获取Cookie

#### 方法1：手动从浏览器获取
1. 打开Chrome/Edge浏览器，访问 https://www.douyin.com
2. 登录你的抖音账号
3. 按F12打开开发者工具
4. 切换到Network标签
5. 刷新页面，找到任意请求
6. 在Request Headers中找到Cookie
7. 复制需要的cookie值到配置文件

#### 方法2：使用辅助工具（如果有）
```bash
python get_cookie.py          # 自动扫码登录获取
python manual_login_cookie.py # 手动输入账号密码
```

### 第四步：运行下载

```bash
# 基本运行（使用config_douyin.yml）
python DouYinCommand.py

# 指定配置文件
python DouYinCommand.py -c custom_config.yml

# 命令行模式（交互式）
python DouYinCommand.py --cmd
```

### 实际使用示例

#### 示例1：下载单个视频
```yaml
# config_douyin.yml
link:
  - https://v.douyin.com/iRN8bKvR/
path: ./videos/
cookies:
  msToken: your_token_here
  # ... 其他cookie
```

#### 示例2：批量下载用户作品
```yaml
# config_douyin.yml
link:
  - https://www.douyin.com/user/MS4wLjABAAAA1234567890
mode:
  - post
number:
  post: 50  # 只下载最新50个作品
```

#### 示例3：下载多个合集
```yaml
# config_douyin.yml
link:
  - https://www.douyin.com/collection/7123456789
  - https://www.douyin.com/collection/7987654321
mode:
  - mix
number:
  mix: 0  # 下载合集内全部作品
```

### 高级功能

#### 增量下载（避免重复）
```yaml
increase:
  post: true   # 只下载新发布的作品
  like: false  # 重新下载所有喜欢的
```

#### 使用代理
```yaml
proxy: http://127.0.0.1:7890
```

#### 自定义命名规则
```yaml
naming: '{create}_{desc}'  # 时间_描述
# 可用变量：{create}, {desc}, {id}, {author}
```

## 🚀 V2.0 使用指南（增强版）

### 三种使用方式

#### 方式1：命令行直接下载（最简单）

```bash
# 自动获取Cookie并下载用户主页
python downloader.py --auto-cookie -u "https://www.douyin.com/user/xxxxx"

# 使用浏览器Cookie下载（自动从Chrome提取）
python downloader.py --cookies "browser:chrome" -u "https://v.douyin.com/xxxxx/"

# 从Firefox提取Cookie
python downloader.py --cookies "browser:firefox" -u "链接"

# 指定保存路径和数量
python downloader.py -u "链接" --path "./videos/" --number 20

# 批量下载多个链接
python downloader.py -u "链接1" "链接2" "链接3" --path "./batch/"
```

#### 方式2：配置文件模式（批量任务）

```bash
# 1. 创建配置文件
cp config_downloader_example.yml config_downloader.yml

# 2. 编辑配置文件（见下方详细说明）

# 3. 运行
python downloader.py --config
```

#### 方式3：混合模式（配置+命令行）

```bash
# 使用配置文件但覆盖某些参数
python downloader.py --config --path "./custom/" --number 10
```

### 配置文件详解

```yaml
# ===== 下载目标 =====
link:
  - https://v.douyin.com/xxxxx/           # 短链接
  - https://www.douyin.com/user/xxxxx     # 用户主页
  - https://www.douyin.com/video/xxxxx    # 视频直链
  - https://www.douyin.com/collection/xxx # 合集

# ===== Cookie配置（三选一）=====
# 方式1：自动获取（Playwright）
auto_cookie: true

# 方式2：浏览器提取（yt-dlp方式）
cookies: "browser:chrome"  # 或 firefox, edge, safari

# 方式3：手动配置
cookies:
  msToken: xxx
  ttwid: xxx
  sessionid: xxx

# ===== 下载设置 =====
path: ./Downloaded/                       # 保存路径
mode:
  - post                                  # 下载发布作品
  - like                                  # 下载喜欢作品
  - mix                                   # 下载合集

# ===== 数量控制 =====
number:
  post: 0                                 # 0=全部，数字=限制数量
  like: 50                                # 最多下载50个喜欢
  allmix: 10                              # 下载10个合集
  mix: 20                                 # 每个合集20个视频

# ===== 增量更新 =====
increase:
  post: true                              # 只下载新发布的
  like: false                             # 重新下载所有
  mix: true                               # 合集增量更新

# ===== 下载内容 =====
music: true                               # 背景音乐
cover: true                               # 视频封面
avatar: true                              # 作者头像
json: true                                # 元数据
comment: true                             # 评论数据

# ===== 性能优化 =====
thread: 10                                # 并发线程数
retry: 5                                  # 重试次数
timeout: 15                               # 超时时间
chunk_size: 1024000                       # 下载块大小

# ===== 高级设置 =====
database: true                            # 数据库记录
proxy: null                               # 代理设置
headless: false                           # 无头浏览器模式
log_level: INFO                           # 日志级别
```

### 实际使用案例

#### 案例1：首次使用，自动配置
```bash
# 自动打开浏览器，扫码登录，然后下载
python downloader.py --auto-cookie -u "https://www.douyin.com/user/MS4wLjAB"
```

#### 案例2：日常使用，浏览器Cookie
```bash
# 直接从已登录的Chrome提取Cookie
python downloader.py --cookies "browser:chrome" \
  -u "https://v.douyin.com/iRN8bKvR/" \
  --path "./today/"
```

#### 案例3：批量下载任务
```yaml
# config_downloader.yml
link:
  - https://www.douyin.com/user/user1
  - https://www.douyin.com/user/user2
  - https://www.douyin.com/user/user3
cookies: "browser:chrome"
mode: [post]
number:
  post: 100  # 每个用户下载100个
increase:
  post: true  # 增量下载
```

```bash
python downloader.py --config
```

#### 案例4：定时任务脚本
```bash
#!/bin/bash
# daily_download.sh
cd /path/to/douyin-downloader
python downloader.py --config --cookies "browser:chrome"
```

### 高级功能

#### 1. 断点续传
V2.0自动支持断点续传，中断后重新运行会从上次位置继续。

#### 2. 智能去重
使用数据库记录已下载内容，避免重复下载。

#### 3. 自适应限速
自动检测并适应抖音的访问限制。

#### 4. 并发控制
```yaml
thread: 5     # 保守设置
thread: 10    # 推荐设置
thread: 20    # 激进设置（可能触发限制）
```

#### 5. 代理支持
```yaml
proxy: http://127.0.0.1:7890      # HTTP代理
proxy: socks5://127.0.0.1:1080    # SOCKS5代理
```

### 命令行参数完整列表

```bash
python downloader.py [选项]

基本选项：
  -h, --help                显示帮助信息
  -u, --url URL            下载链接（可多个）
  -p, --path PATH          保存路径
  -c, --config             使用配置文件

Cookie选项：
  --auto-cookie            自动获取Cookie（Playwright）
  --cookies COOKIES        指定Cookie来源
    示例：
    --cookies "browser:chrome"     从Chrome提取
    --cookies "msToken=xxx;..."    直接提供Cookie字符串
    --cookies "cookies.txt"        从文件读取

下载选项：
  --mode MODE              下载模式（post/like/mix）
  --number NUMBER          下载数量限制
  --increase              启用增量下载
  --no-music              不下载音乐
  --no-cover              不下载封面
  --no-avatar             不下载头像

性能选项：
  --thread N              并发线程数
  --retry N               重试次数
  --timeout N             超时时间（秒）

其他选项：
  --proxy PROXY           代理服务器
  --log-level LEVEL       日志级别（DEBUG/INFO/WARNING/ERROR）
  --headless              无头浏览器模式
  --database              启用数据库记录
```

## 🍪 Cookie 配置工具

### Cookie获取方式总览

| 方式 | V1.0支持 | V2.0支持 | 难度 | 推荐度 |
|------|---------|---------|------|--------|
| V2.0内置自动获取 | ❌ | ✅ | 简单 | ⭐⭐⭐⭐⭐ |
| V2.0浏览器提取 | ❌ | ✅ | 简单 | ⭐⭐⭐⭐ |
| 手动复制Cookie | ✅ | ✅ | 中等 | ⭐⭐⭐ |
| 辅助工具获取 | ✅ | ✅ | 简单 | ⭐⭐⭐⭐ |

### 方法一：V2.0内置自动获取（最推荐）

仅适用于V2.0，无需额外工具：

```bash
# 方式1：使用Playwright自动登录
python downloader.py --auto-cookie -u "下载链接"
# 会自动打开浏览器，扫码登录后自动保存Cookie

# 方式2：从已登录的浏览器提取
python downloader.py --cookies "browser:chrome" -u "下载链接"
# 支持：chrome, firefox, edge, safari, brave
```

### 方法二：手动从浏览器获取

适用于V1.0和V2.0：

1. **打开抖音网页版**
   - 访问 https://www.douyin.com
   - 登录你的账号

2. **获取Cookie**
   - 按F12打开开发者工具
   - 切换到Network标签
   - 刷新页面
   - 找到任意请求，查看Request Headers
   - 复制Cookie字段

3. **配置到程序**

   **V1.0配置方式**：
   ```yaml
   # config_douyin.yml
   cookies:
     msToken: 你的msToken值
     ttwid: 你的ttwid值
     sessionid: 你的sessionid值
   ```

   **V2.0配置方式**：
   ```yaml
   # config_downloader.yml
   cookies:
     msToken: 你的msToken值
     ttwid: 你的ttwid值
     sessionid: 你的sessionid值
   ```

   或命令行：
   ```bash
   python downloader.py --cookies "msToken=xxx;ttwid=xxx" -u "链接"
   ```

### 方法三：使用辅助工具（如果存在）

项目可能包含以下辅助工具：

```bash
# 扫码登录获取
python get_cookie.py

# 账号密码登录
python manual_login_cookie.py

# 简单Cookie获取器
python simple_cookie_getter.py
```

### Cookie有效性说明

#### 必需的Cookie字段
- **msToken**：必需，用于API访问
- **ttwid**：必需，设备标识
- **sessionid**：登录状态，下载用户主页时必需

#### 可选但推荐的字段
- **odin_tt**：提高成功率
- **passport_csrf_token**：防CSRF令牌
- **sid_guard**：会话保护

#### Cookie过期处理
- V1.0：需要手动更新Cookie
- V2.0：使用`--auto-cookie`可自动刷新

### 常见Cookie问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| “Cookie无效” | Cookie过期或不完整 | 重新获取完整Cookie |
| “无法下载用户主页” | 缺少sessionid | 登录后获取sessionid |
| “API返回空” | msToken失效 | 使用V2.0自动获取 |
| “被风控限制” | 访问过于频繁 | 减少并发数，使用代理 |

## 📋 支持的链接类型

### 🎬 视频内容
- **单个视频分享链接**：`https://v.douyin.com/xxxxx/`
- **单个视频直链**：`https://www.douyin.com/video/xxxxx`
- **图集作品**：`https://www.douyin.com/note/xxxxx`

### 👤 用户内容
- **用户主页**：`https://www.douyin.com/user/xxxxx`
  - 支持下载用户发布的所有作品
  - 支持下载用户喜欢的作品（需要权限）

### 📚 合集内容
- **用户合集**：`https://www.douyin.com/collection/xxxxx`
- **音乐合集**：`https://www.douyin.com/music/xxxxx`

### 🔴 直播内容
- **直播间**：`https://live.douyin.com/xxxxx`

## 🔧 常见问题

### 下载问题

#### Q: V1.0和V2.0该选择哪个？
**A**:
- **首次使用**：推荐V2.0，支持自动获取Cookie
- **稳定性要求高**：使用V1.0，经过大量测试
- **单个视频下载**：V1.0更稳定
- **批量下载**：V2.0效率更高

#### Q: 为什么下载失败？
**A**: 常见原因及解决方案：

| 错误提示 | 原因 | 解决方案 |
|---------|------|----------|
| Cookie无效 | Cookie过期或不完整 | 重新获取Cookie |
| API返回空 | 单视频API问题 | 使用用户主页下载 |
| 网络超时 | 网络不稳定 | 检查网络或使用代理 |
| 权限不足 | 缺少sessionid | 登录后获取完整Cookie |
| 风控限制 | 访问过于频繁 | 减少并发数，增加延迟 |

#### Q: 如何提高下载速度？
**A**:
```yaml
# 优化配置
thread: 10       # 增加并发数（默认5）
chunk_size: 2048000  # 增大块大小
timeout: 20      # 增加超时时间
```

### Cookie问题

#### Q: Cookie多久过期？
**A**:
- 通常有1-7天有效期
- V2.0使用`--auto-cookie`可自动刷新
- 建议定期更新Cookie

#### Q: 怎么判断Cookie是否有效？
**A**:
- 看是否能正常获取用户信息
- 出现"Cookie无效"提示时需更新
- V2.0会自动检测并提示

### 功能问题

#### Q: 支持哪些内容类型？
**A**:
- ✅ 视频作品（MP4无水印）
- ✅ 图集作品（JPG高清）
- ✅ 背景音乐（MP3）
- ✅ 作者头像
- ✅ 视频封面
- ✅ 元数据（JSON）
- ✅ 评论数据（V2.0）
- ⚠️ 直播录制（开发中）

#### Q: 如何批量下载？
**A**:

**V1.0批量下载**：
```yaml
# config_douyin.yml
link:
  - 链接1
  - 链接2
  - 链接3
```

**V2.0批量下载**：
```bash
# 命令行方式
python downloader.py -u "链接1" "链接2" "链接3"

# 配置文件方式
python downloader.py --config
```

#### Q: 如何只下载最新内容？
**A**: 使用增量下载功能：
```yaml
increase:
  post: true  # 只下载新发布的
```

### 故障排除

#### 错误："No module named 'xxx'"
```bash
# 安装缺失的依赖
pip install -r requirements.txt
```

#### 错误："Playwright not installed"
```bash
# 安装Playwright和浏览器
pip install playwright
playwright install chromium
```

#### 错误："无法连接到抖音"
- 检查网络连接
- 尝试使用代理
- 检查是否被风控

#### 错误："文件保存失败"
- 检查磁盘空间
- 检查路径权限
- 确保路径存在

### 性能优化建议

| 场景 | 推荐配置 | 说明 |
|------|---------|------|
| 少量下载 | thread: 3-5 | 稳定不被限制 |
| 批量下载 | thread: 8-10 | 平衡速度和稳定 |
| 大量下载 | thread: 5 + 代理 | 避免风控 |
| 增量更新 | increase: true | 节省时间和流量 |

## 📝 更新日志

### V2.0 (2025-08)
- ✅ **统一入口**：整合所有功能到 `downloader.py`
- ✅ **自动 Cookie 管理**：支持自动获取和刷新
- ✅ **异步架构**：性能优化，支持并发下载
- ✅ **智能重试**：自动重试和错误恢复
- ✅ **增量下载**：支持增量更新
- ✅ **用户主页下载**：完全正常工作
- ⚠️ **单个视频下载**：API 返回空响应（已知问题）

### V1.0 (2024-12)
- ✅ **稳定可靠**：经过大量测试验证
- ✅ **功能完整**：支持所有内容类型
- ✅ **单个视频下载**：完全正常工作
- ✅ **配置文件驱动**：简单易用
- ✅ **数据库支持**：记录下载历史

## ⚖️ 法律声明

- 本项目仅供**学习交流**使用
- 请遵守相关法律法规和平台服务条款
- 不得用于商业用途或侵犯他人权益
- 下载内容请尊重原作者版权

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 报告问题
- 使用 [Issues](https://github.com/jiji262/douyin-downloader/issues) 报告 bug
- 请提供详细的错误信息和复现步骤

### 功能建议
- 在 Issues 中提出新功能建议
- 详细描述功能需求和使用场景

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源许可证。

---

<div align="center">

**如果这个项目对你有帮助，请给个 ⭐ Star 支持一下！**

[🐛 报告问题](https://github.com/jiji262/douyin-downloader/issues) • [💡 功能建议](https://github.com/jiji262/douyin-downloader/issues) • [📖 查看文档](https://github.com/jiji262/douyin-downloader/wiki)

Made with ❤️ by [jiji262](https://github.com/jiji262)

</div>
