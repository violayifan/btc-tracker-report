# BTC 交易分析报告 - 访问解决方案

## 问题说明
网址 http://47.90.150.51:8081/btc_report_enhanced.html 无法从外部访问

## 原因分析
1. **防火墙限制** - 8081 端口未开放
2. **云服务商安全组** - 需要在控制台添加入站规则
3. **服务器权限** - 需要绑定 80 端口（通常需要 root）

---

## 🎯 推荐解决方案

### 方案 1：直接下载 HTML 文件（推荐）

**HTML 文件位置**：
```
/root/.openclaw/workspace/btc_report_enhanced.html
```

**操作步骤**：
1. 使用 SFTP/SCP 工具连接到服务器
2. 下载文件：`btc_report_enhanced.html`
3. 用浏览器打开下载的 HTML 文件

**优点**：
- ✅ 完全无需服务器
- ✅ 可以离线查看
- ✅ 包含所有数据和图表
- ✅ 响应式设计，手机电脑都支持

**SFTP 命令示例**：
```bash
# 从服务器下载
scp root@47.90.150.51:/root/.openclaw/workspace/btc_report_enhanced.html ./

# 使用 SFTP 客户端（FileZilla, WinSCP 等）
# 服务器信息：
#   主机: 47.90.150.51
#   用户: root
#   端口: 22
#   文件路径: /root/.openclaw/workspace/btc_report_enhanced.html
```

---

### 方案 2：配置防火墙开放 8081 端口

#### 步骤 1：开放防火墙

```bash
# 检查防火墙状态
sudo firewall-cmd --list-all

# 临时开放 8081 端口（重启后失效）
sudo firewall-cmd --add-port=8081/tcp

# 永久开放 8081 端口
sudo firewall-cmd --permanent --add-port=8081/tcp
sudo firewall-cmd --reload
```

#### 步骤 2：配置云服务商安全组

在阿里云控制台：
1. 登录阿里云控制台
2. 找到你的 ECS 实例
3. 点击"安全组"
4. 添加入站规则：
   - 协议：TCP
   - 端口：8081/8081
   - 源：0.0.0.0/0（允许所有 IP）
   - 优先级：1

#### 步骤 3：启动服务器

```bash
cd /root/.openclaw/workspace
python3 start_download_server.py
```

然后访问：http://47.90.150.51:8081/btc_report_enhanced.html

---

### 方案 3：使用免费的静态托管服务

#### 3.1 使用 GitHub Pages（免费）

**步骤**：
1. 注册 GitHub 账号
2. 创建新仓库：`btc-tracker-report`
3. 上传 `btc_report_enhanced.html`
4. 在仓库设置中启用 GitHub Pages
5. 访问生成的 URL

**优点**：
- ✅ 完全免费
- ✅ HTTPS 自动
- ✅ 全球 CDN
- ✅ 域名自定义

**缺点**：
- ❌ 需要每次手动上传更新

---

#### 3.2 使用 Netlify（拖拽部署）

**步骤**：
1. 访问 https://www.netlify.com
2. 注册/登录
3. 将 `btc_report_enhanced.html` 拖拽到部署区域
4. 等待几秒，获取 URL

**优点**：
- ✅ 极其简单（拖拽即可）
- ✅ 免费
- ✅ HTTPS 自动
- ✅ 全球 CDN

---

#### 3.3 使用 Vercel

**步骤**：
1. 安装 Vercel CLI：
```bash
npm install -g vercel
```

2. 部署：
```bash
cd /root/.openclaw/workspace
vercel --prod
```

**优点**：
- ✅ 现代化部署平台
- ✅ 免费
- ✅ 全球边缘网络
- ✅ 自动 HTTPS

---

### 方案 4：使用 Ngrok 内网穿透（快速测试）

#### 4.1 安装 Ngrok

```bash
# 下载 Ngrok
wget https://bin.ngrok.com/ngrok-stable-linux-amd64.tgz -O /tmp/ngrok.tgz
tar -xzf /tmp/ngrok.tgz -C /tmp/
sudo mv /tmp/ngrok /usr/local/bin/
chmod +x /usr/local/bin/ngrok
```

#### 4.2 注册 Ngrok

1. 访问：https://ngrok.com/signup
2. 免费注册
3. 登录获取 authtoken

#### 4.3 启动 Ngrok

```bash
# 启动 Ngrok（映射 8081 端口）
ngrok http 8081
```

#### 4.4 获取访问网址

终端会显示类似：
```
Forwarding  https://abc123.ngrok.io -> http://localhost:8081
```

复制 `https://abc123.ngrok.io` 即可从外部访问！

**优点**：
- ✅ 配置简单
- ✅ 无需修改防火墙
- ✅ 自动 HTTPS
- ✅ 临时使用很方便

**缺点**：
- ❌ 免费版域名随机变化
- ❌ 需要每次手动启动
- ❌ 有流量限制

---

## 📋 快速对比

| 方案 | 难度 | 稳定性 | 持久化 | 推荐度 |
|------|--------|--------|---------|--------|
| 直接下载 HTML | ⭐ 简单 | ✅ 完美 | ✅ 永久 | 🥇 强烈推荐 |
| 配置防火墙 | ⭐⭐⭐ 复杂 | ✅ 好 | ✅ 永久 | 🥈 推荐 |
| Netlify 部署 | ⭐ 简单 | ✅ 完美 | ✅ 永久 | 🥈 推荐 |
| GitHub Pages | ⭐⭐ 中等 | ✅ 好 | ✅ 永久 | 🥉 一般 |
| Ngrok 穿透 | ⭐ 简单 | ⚠️ 一般 | ❌ 临时 | ⚠️ 测试用 |

---

## 🎯 最佳实践建议

**对于你的场景，我推荐以下优先级**：

1. **首选：直接下载 HTML 文件**
   - 最简单可靠
   - 无需配置任何东西
   - 可以离线随时查看

2. **次选：Netlify 部署**
   - 拖拽即可部署
   - 获得永久访问网址
   - 全球 CDN 加速

3. **长期：配置防火墙 + 定时任务**
   - 适合需要频繁更新的场景
   - 可以设置 cron 自动更新

---

## 🔄 自动更新方案

如果使用 Netlify 或 GitHub Pages，可以设置自动更新：

### 创建自动部署脚本

```bash
#!/bin/bash
# update_and_deploy.sh

# 1. 运行市场分析
cd /root/.openclaw/workspace
python3 btc_monitor.py

# 2. 生成 HTML 报告
python3 btc_html_report_v2.py

# 3. 上传到 Netlify（使用 Netlify CLI）
netlify deploy --prod --dir=. --site=btc-report
```

### 添加到 Cron

```bash
# 编辑 crontab
crontab -e

# 添加每小时更新
0 * * * * /root/.openclaw/workspace/update_and_deploy.sh
```

---

## ❓ 常见问题

### Q1: 为什么 80 端口也无法访问？
A: 云服务商安全组需要开放 80 端口。在阿里云控制台添加规则。

### Q2: HTML 文件可以直接用浏览器打开吗？
A: 可以！HTML 文件是完全独立的，双击即可用任何浏览器打开。

### Q3: 报告数据会自动更新吗？
A: 如果下载 HTML 文件，数据是静态的。需要重新运行 `python3 btc_auto_report_with_server.py` 生成新报告。

### Q4: 如何获取最新的报告？
A: 运行命令：
```bash
cd /root/.openclaw/workspace
python3 btc_auto_report_with_server.py
```

---

## 📞 需要帮助？

如果以上方案都无法解决，请告诉我：
1. 你的访问场景（手机/电脑/公司网络）
2. 是否有云服务商控制台访问权限
3. 是否可以接受使用第三方服务

我可以提供更针对性的解决方案！
