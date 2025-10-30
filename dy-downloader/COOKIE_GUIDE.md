# Cookie获取指南 / Cookie Acquisition Guide

## 为什么需要Cookie？ / Why Cookies are Needed?

抖音API需要有效的用户认证信息才能访问内容。Cookie包含了必要的认证令牌，使得程序能够模拟浏览器访问并下载内容。

Douyin's API requires valid user authentication to access content. Cookies contain necessary authentication tokens that allow the program to simulate browser access and download content.

---

## 必需的Cookie字段 / Required Cookie Fields

以下Cookie字段是必需的（Required）：

1. **msToken** - 主要的认证令牌 / Main authentication token
2. **ttwid** - 抖音跟踪ID / Douyin tracking ID  
3. **odin_tt** - 用户设备标识 / User device identifier
4. **passport_csrf_token** - CSRF防护令牌 / CSRF protection token

推荐但非必需（Recommended but optional）：

5. **sid_guard** - 会话保护令牌 / Session protection token

---

## 方法1：自动获取（推荐）/ Method 1: Automatic Acquisition (Recommended)

### 前置要求 / Prerequisites

首先安装Playwright（如果尚未安装）：

```bash
pip install playwright
playwright install chromium
```

### 使用Cookie获取工具 / Using the Cookie Fetcher Tool

1. 运行Cookie获取工具：
   ```bash
   cd dy-downloader
   python -m tools.cookie_fetcher --config config.yml
   ```

2. 浏览器会自动打开抖音网站
3. **手动登录您的抖音账号**，完成所有验证（扫码或账号密码登录）
4. 登录成功后，返回终端按 **Enter** 键
5. Cookie将自动保存到 `config/cookies.json`

### 注意事项 / Notes

- 确保登录成功并能正常访问抖音主页
- 如果遇到验证码或风控，需要手动完成验证
- Cookie会自动保存，下次无需重新获取（除非失效）

---

## 方法2：手动获取 / Method 2: Manual Acquisition

### 步骤 / Steps

1. **打开浏览器** / Open your browser
   - 推荐使用 Chrome、Edge 或 Firefox

2. **登录抖音** / Login to Douyin
   - 访问 https://www.douyin.com
   - 使用您的账号登录

3. **打开开发者工具** / Open Developer Tools
   - Windows/Linux: 按 `F12` 或 `Ctrl+Shift+I`
   - macOS: 按 `Cmd+Option+I`

4. **切换到Network（网络）标签** / Switch to Network Tab
   - 点击顶部的 "Network" / "网络" 标签

5. **刷新页面** / Refresh the page
   - 按 `F5` 或点击刷新按钮

6. **选择任意请求** / Select any request
   - 在Network列表中选择任意一个请求（通常选择第一个）

7. **查找Cookie** / Find Cookies
   - 在右侧面板中找到 "Headers" / "请求头"
   - 向下滚动找到 "Request Headers" / "请求标头"
   - 找到 "Cookie:" 字段

8. **复制Cookie值** / Copy Cookie Values
   - 从Cookie字符串中找到并复制以下字段的值：
     - `msToken=值;`
     - `ttwid=值;`
     - `odin_tt=值;`
     - `passport_csrf_token=值;`
     - `sid_guard=值;` (可选)

### 示例Cookie格式 / Example Cookie Format

Cookie字符串看起来像这样（已脱敏）：

```
msToken=abcd1234...; ttwid=1%7Cxyz789...; odin_tt=fedcba...; passport_csrf_token=c2a7091f...; sid_guard=5e5adf6c...
```

---

## 配置Cookie / Configuring Cookies

### 在config.yml中配置 / Configure in config.yml

编辑 `config.yml` 文件，在 `cookies` 部分填入获取的值：

```yaml
cookies:
  msToken: "YOUR_MS_TOKEN_VALUE_HERE"
  ttwid: "YOUR_TTWID_VALUE_HERE"
  odin_tt: "YOUR_ODIN_TT_VALUE_HERE"
  passport_csrf_token: "YOUR_CSRF_TOKEN_HERE"
  sid_guard: "YOUR_SID_GUARD_HERE"  # 可选 / Optional
```

### 或使用config/cookies.json / Or use config/cookies.json

创建或编辑 `config/cookies.json` 文件：

```json
{
  "msToken": "YOUR_MS_TOKEN_VALUE_HERE",
  "ttwid": "YOUR_TTWID_VALUE_HERE",
  "odin_tt": "YOUR_ODIN_TT_VALUE_HERE",
  "passport_csrf_token": "YOUR_CSRF_TOKEN_HERE",
  "sid_guard": "YOUR_SID_GUARD_HERE"
}
```

---

## Cookie有效期 / Cookie Validity

- Cookie通常有效期为 **几天到几周**
- 如果遇到以下情况，需要重新获取Cookie：
  - 下载失败，提示认证错误
  - 程序显示 "Cookie validation failed"
  - API返回 401/403 错误

---

## 安全与隐私 / Security & Privacy

⚠️ **重要提示 / Important Notes**：

1. **请勿分享Cookie** / DO NOT share your cookies
   - Cookie等同于登录凭证，可用于访问您的账号
   
2. **保护配置文件** / Protect your config files
   - 不要将包含Cookie的配置文件上传到公开仓库
   - `.gitignore` 已配置忽略 `config.yml` 和 `config/cookies.json`

3. **定期更换** / Regular rotation
   - 建议定期重新获取Cookie以保证安全

4. **使用小号** / Use secondary account
   - 如果担心安全问题，建议使用备用抖音账号

---

## 常见问题 / FAQ

### Q1: Cookie获取后仍然无法下载？

**A:** 检查以下几点：
- Cookie是否完整（包含所有必需字段）
- 是否正确粘贴（没有多余空格或换行）
- 账号是否正常（未被限制）
- 网络连接是否正常

### Q2: 多久需要更新一次Cookie？

**A:** 通常Cookie可以使用几天到几周。当程序提示Cookie无效时，需要重新获取。

### Q3: 可以使用多个账号的Cookie吗？

**A:** 当前版本一次只能使用一个账号的Cookie。如需切换账号，需要更新配置文件中的Cookie。

### Q4: Cookie泄露会有什么风险？

**A:** Cookie泄露相当于账号密码泄露，他人可以通过Cookie访问您的抖音账号。请务必妥善保管。

---

## 测试Cookie / Testing Cookies

运行以下命令测试Cookie是否有效：

```bash
cd dy-downloader
python3 -c "
from auth import CookieManager
from config import ConfigLoader

config = ConfigLoader('config.yml')
cookies = config.get_cookies()
cookie_manager = CookieManager()
cookie_manager.set_cookies(cookies)

if cookie_manager.validate_cookies():
    print('✓ Cookie validation passed!')
else:
    print('✗ Cookie validation failed - missing required fields')
"
```

---

## 技术支持 / Technical Support

如果您在获取或使用Cookie时遇到问题，请：

1. 查看项目的 [README.md](README.md) 和 [故障排除](README.md#故障排除) 部分
2. 在项目仓库提交 Issue
3. 确保不要在公开Issue中包含您的Cookie信息

---

**最后更新 / Last Updated**: 2025-10-17


