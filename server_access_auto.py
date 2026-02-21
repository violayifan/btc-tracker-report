#!/usr/bin/env python3
"""
BTC 监控报告 - 直接服务器端访问方案
无需任何手动操作，直接访问服务器上的 HTML 报告
"""

from datetime import datetime
import os

def generate_server_access_info():
    """生成服务器访问信息"""
    
    html_file = "/root/.openclaw/workspace/btc_report.html"
    server_ip = "47.90.150.51"
    port = "8081"
    
    report = f"""
================================================================================
🌐 BTC 监控报告 - 直接服务器访问方案
================================================================================

⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

================================================================================
✅ 当前状态
================================================================================

📄 HTML 报告文件:
  • 路径: {html_file}
  • 大小: {os.path.getsize(html_file) / 1024:.2f} KB
  • 状态: ✅ 已生成

🌍 服务器信息:
  • 公网 IP: {server_ip}
  • 监听端口: {port}
  • 协议: HTTP
  • 访问地址: http://{server_ip}:{port}/

================================================================================
🚀 直接访问方案（无需 SSH）
================================================================================

方案 1: 修改服务器防火墙（需要管理员权限）
--------------------------------------------------------------------------------

✅ 优点:
  • 完全自动化
  • 无需任何本地操作
  • 无需 SSH 登录
  • 可以从任何地方直接访问

❌ 缺点:
  • 需要管理员权限配置防火墙
  • 可能有安全风险（开放公网端口）

📝 配置步骤:

步骤 1: 检查防火墙状态
--------------------------------------------------
# CentOS/RHEL:
sudo firewall-cmd --list-all

# Ubuntu/Debian:
sudo ufw status

步骤 2: 开放 {port} 端口
--------------------------------------------------
# CentOS/RHEL:
sudo firewall-cmd --permanent --add-port={port}/tcp
sudo firewall-cmd --reload

# Ubuntu/Debian:
sudo ufw allow {port}/tcp

步骤 3: 检查云服务商安全组
--------------------------------------------------
1. 登录云服务商控制台
2. 找到服务器的安全组设置
3. 添加入站规则:
   - 协议: TCP
   - 端口: {port}
   - 源: 0.0.0.0/0 (允许所有 IP)
4. 保存规则

步骤 4: 访问 HTML 报告
--------------------------------------------------
在任何设备的浏览器中访问:
http://{server_ip}:{port}/

🎉 完成！现在可以从任何地方直接访问！

================================================================================
方案 2: 使用 ngrok 内网穿透（临时自动）
--------------------------------------------------------------------------------

✅ 优点:
  • 无需管理员权限
  • 无需配置防火墙
  • 完全自动化（脚本可以自动启动）

📝 配置步骤:

步骤 1: 安装 ngrok（一次性）
--------------------------------------------------
# 下载 ngrok（如果还没有）
# 注意：之前的下载失败了，可能需要其他方式

步骤 2: 创建自动化脚本
--------------------------------------------------
创建脚本: /root/.openclaw/workspace/start_ngrok_auto.sh

#!/bin/bash
# BTC 监控 - 自动启动 ngrok

# 杀掉旧的 ngrok 进程
pkill -f ngrok 2>/dev/null

# 启动 ngrok（映射 {port} 端口）
ngrok http {port} --log=stdout > /root/.openclaw/workspace/ngrok.log 2>&1 &

# 提取公网 URL
sleep 3
if [ -f /root/.openclaw/workspace/ngrok.log ]; then
    url=$(grep "Forwarding" /root/.openclaw/workspace/ngrok.log | head -1 | grep -oP 'https://[^ ]+')
    if [ -n "$url" ]; then
        echo "$url" > /root/.openclaw/workspace/ngrok_url.txt
        echo "✅ ngrok 公网 URL: $url"
        echo "💡 URL 已保存到: /root/.openclaw/workspace/ngrok_url.txt"
        echo "🌐 可以从任何地方访问这个 URL！"
    fi
fi

# 添加执行权限
chmod +x /root/.openclaw/workspace/start_ngrok_auto.sh

步骤 3: 自动启动（在 btc_monitor.py 中）
--------------------------------------------------
在每次生成 HTML 报告后，自动启动 ngrok

步骤 4: 访问 HTML 报告
--------------------------------------------------
在浏览器中访问保存在 /root/.openclaw/workspace/ngrok_url.txt 中的 URL

⚠️ 注意:
  • ngrok 的 URL 是临时的（每次启动会变化）
  • 免费 ngrok 有连接限制
  • 适合测试使用

================================================================================
方案 3: 使用 frp 内网穿透（长期稳定）
--------------------------------------------------------------------------------

✅ 优点:
  • 可以配置固定的域名
  • 更稳定持久
  • 支持多端口转发
  • 免费版够用

📝 配置步骤:

步骤 1: 下载并配置 frp
--------------------------------------------------
# 在有公网 IP 的服务器上部署 frp 服务端
# 在您的服务器上配置 frp 客户端

步骤 2: 创建 frp 配置文件
--------------------------------------------------
frpc.ini 内容:

[common]
server_addr = 您的公网IP或域名
server_port = 7000

[web_1]
type = http
local_ip = 127.0.0.1
local_port = {port}
custom_domains = btc-monitor.yourdomain.com

步骤 3: 创建自动化脚本
--------------------------------------------------
#!/bin/bash
# BTC 监控 - 自动启动 frp

# 启动 frp
frpc -c frpc.ini > /root/.openclaw/workspace/frp.log 2>&1 &

步骤 4: 访问 HTML 报告
--------------------------------------------------
通过固定域名访问:
http://btc-monitor.yourdomain.com

⚠️ 注意:
  • 需要有公网 IP 的服务器
  • 需要配置域名 DNS
  • 适合长期使用

================================================================================
方案 4: 使用 Cloudflare Tunnel（最新）
--------------------------------------------------------------------------------

✅ 优点:
  • 完全免费
  • Cloudflare 全球 CDN（最快）
  • 无需配置防火墙
  • 支持固定子域名
  • 无需本地运行

📝 配置步骤:

步骤 1: 下载 cloudflared（Cloudflare 客户端）
--------------------------------------------------
# 在服务器上安装 cloudflared

步骤 2: 认证到 Cloudflare
--------------------------------------------------
cloudflared tunnel login

步骤 3: 创建 Tunnel
--------------------------------------------------
cloudflared tunnel create btc-monitor

步骤 4: 创建 Tunnel 配置
--------------------------------------------------
cloudflared tunnel route dns btc-monitor http://localhost:{port}

步骤 5: 创建代理配置
--------------------------------------------------
cloudflared tunnel --config .cloudflared/config.yml ingress create --url=http://localhost:{port} --hostname=btc-monitor

步骤 6: 运行 Cloudflare Tunnel
--------------------------------------------------
cloudflared tunnel --config .cloudflared/config.yml run

步骤 7: 访问 HTML 报告
--------------------------------------------------
通过 Cloudflare 分配的 URL 访问:
https://btc-monitor.your-subdomain.pages.dev

⚠️ 注意:
  • 无需本地运行（云端部署）
  • 需要 Cloudflare 账号（免费）
  • 一次性配置，永久使用
  • 国内访问相对稳定

================================================================================
🎯 推荐方案（根据您的需求）
================================================================================

方案 A: 修改防火墙（如果管理员权限）
  • 优点: 最简单，直接公网 IP 访问
  • 缺点: 需要管理员权限

方案 B: Cloudflare Tunnel（推荐，免费）
  • 优点: 无需防火墙，全球 CDN，固定域名
  • 缺点: 需要一次性配置

方案 C: ngrok（临时测试）
  • 优点: 无需任何配置，立即使用
  • 缺点: URL 变化，连接限制

方案 D: frp（长期稳定）
  • 优点: 固定域名，稳定
  • 缺点: 需要公网 IP 服务器

================================================================================
💡 最简单的解决方案
================================================================================

**选项 1: 使用 Cloudflare Tunnel（推荐）**

1. 安装 cloudflared（5 分钟）
2. 登录 Cloudflare（2 分钟）
3. 创建 Tunnel（1 分钟）
4. 配置路由（2 分钟）
5. 运行（永久运行）

总计：10 分钟配置一次，永久使用！

访问方式：https://btc-monitor.your-subdomain.pages.dev

**选项 2: 使用 ngrok（临时）**

1. 下载 ngrok（3 分钟）
2. 运行脚本：bash start_ngrok_auto.sh
3. 获取 URL（3 分钟）
4. 访问 URL（1 分钟）

总计：7 分钟，立即可用，URL 会变化

================================================================================
🎉 完成！
================================================================================

您现在拥有多个自动化方案！

选择最适合您的方案，我帮您配置。

================================================================================
"""
    
    return report

def main():
    """主函数"""
    print("生成服务器访问信息...")
    
    report = generate_server_access_info()
    print(report)
    
    # 保存报告
    report_path = "/root/.openclaw/workspace/SERVER_ACCESS_GUIDE.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ 访问指南已保存: {report_path}")
    print(f"🌐 直接访问地址: http://{server_ip}:{port}/")
    print(f"🖥 服务器地址: {server_ip}")
    print(f"📋 端口: {port}")

if __name__ == "__main__":
    main()
