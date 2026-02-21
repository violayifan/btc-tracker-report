#!/usr/bin/env python3
"""
HTML 网址外部访问解决方案
"""

def generate_html_external_access_solutions():
    """生成多种 HTML 外部访问方案"""
    
    solutions = """
================================================================================
🌐 HTML 网址外部访问解决方案
================================================================================

当前问题：
  • 生成的 HTML 文件：/root/.openclaw/workspace/btc_report.html
  • 服务器地址：http://47.90.150.51:8080
  • 问题：从外部无法访问（防火墙、端口限制等）

================================================================================
解决方案对比表
================================================================================

方案 1：使用内网穿透工具（推荐用于测试）
--------------------------------------------------------------------------------
工具推荐：
  • ngrok（最简单）
  • localtunnel
  • frp（适合长期使用）

配置步骤（以 ngrok 为例）：

1. 安装 ngrok：
   # 下载：https://ngrok.com/download
   # 或在 Linux 上：
   wget https://bin.equinox.io/c/4VmDzA7iaHbngng9DqMqEeMYnaPq1IW64A3/ngrok-v3-stable-linux-amd64.zip
   unzip ngrok-v3-stable-linux-amd64.zip
   sudo mv ngrok /usr/local/bin/

2. 注册 ngrok 账号：
   • 访问：https://dashboard.ngrok.com/signup
   • 免费注册
   • 登录获取 authtoken

3. 启动 ngrok（映射 8080 端口）：
   ngrok http 8080
   
   或者指定域名：
   ngrok http 8080 -region=us

4. 获取外网访问地址：
   终端会显示类似：
   Forwarding  https://abc123.ngrok.io -> http://localhost:8080
   
   ✅ 优点：
   • 配置简单，一条命令
   • 免费版就够用
   • 自动 HTTPS
   • 无需配置防火墙

   ❌ 缺点：
   • 需要每次启动服务器时运行 ngrok
   • 免费版域名随机变化
   • 内网穿透有延迟

--------------------------------------------------------------------------------

方案 2：使用云服务托管（推荐用于生产）
--------------------------------------------------------------------------------
平台推荐：
  • GitHub Pages（免费，静态网站）
  • Vercel（免费，自动部署）
  • Netlify（免费，拖拽部署）
  • Cloudflare Pages（免费，全球 CDN）
  • 阿里云 OSS + CDN（国内稳定）

方案 2.1：GitHub Pages 部署
--------------------------------------------------------------------------------

1. 创建 GitHub 仓库：
   • 访问：https://github.com/new
   • 仓库名：btc-tracker-report
   • 设为 Public（公开）
   • 选择初始化为 README

2. 上传 HTML 文件：
   # 在服务器上运行：
   cd /root/.openclaw/workspace
   
   # 初始化 Git（如果还没有）
   git init
   git add btc_report.html
   git commit -m "Add BTC tracker report"
   
   # 关联远程仓库（替换 YOUR_USERNAME）
   git remote add origin https://github.com/YOUR_USERNAME/btc-tracker-report.git
   git push -u origin main

3. 启用 GitHub Pages：
   • 在仓库页面，点击 Settings
   • 滚动到 GitHub Pages 部分
   • Source 选择：Deploy from a branch
   • Branch 选择：main
   • 点击 Save

4. 访问网站：
   • 等待 1-2 分钟
   • 访问：https://YOUR_USERNAME.github.io/btc-tracker-report/

✅ 优点：
  • 完全免费
  • 自动 HTTPS
  • 全球 CDN 加速
  • 速度快
  • 自定义域名支持

❌ 缺点：
  • 只支持静态网站（HTML/CSS/JS）
  • 国内访问可能不稳定
  • 每次更新需要 git push

--------------------------------------------------------------------------------

方案 2.2：Vercel 部署（更现代化）
--------------------------------------------------------------------------------

1. 安装 Vercel CLI：
   npm install -g vercel

2. 部署项目：
   cd /root/.openclaw/workspace
   vercel

3. 按提示操作：
   • Set up and deploy? (Y/n) y
   • Link to existing project? n
   • What's your project's name? btc-tracker-report
   • In which directory is your code? ./

4. 访问网站：
   • 部署成功后会显示 URL
   • 类似：https://btc-tracker-report.vercel.app

✅ 优点：
  • 完全免费
  • 全球边缘网络（速度快）
  • 自动 HTTPS
  • 支持自定义域名
  • 部署快

❌ 缺点：
  • 国内访问可能不稳定

--------------------------------------------------------------------------------

方案 3：修改服务器防火墙配置（需要管理员权限）
--------------------------------------------------------------------------------

1. 检查防火墙状态：
   # CentOS/RHEL:
   sudo firewall-cmd --list-all
   
   # Ubuntu:
   sudo ufw status

2. 开放 8080 端口：
   # CentOS/RHEL:
   sudo firewall-cmd --permanent --add-port=8080/tcp
   sudo firewall-cmd --reload
   
   # Ubuntu:
   sudo ufw allow 8080/tcp

3. 检查云服务商安全组：
   • 登录云服务商控制台
   • 找到实例的安全组设置
   • 添加入站规则：
     * 协议：TCP
     * 端口：8080
     * 源：0.0.0.0/0 (允许所有 IP)
     * 或指定你的 IP 地址

4. 确保监听所有网络接口：
   # 检查服务器监听地址
   netstat -tulnp | grep 8080
   
   # 如果只监听 127.0.0.1，修改为监听 0.0.0.0
   # 在服务器脚本中，将 bind 地址改为 '0.0.0.0' 或 ''

✅ 优点：
  • 无需额外服务
  • 直接访问
  • 国内访问稳定

❌ 缺点：
  • 需要管理员权限
  • 可能有安全风险
  • 需要 IP 地址或公网

--------------------------------------------------------------------------------

方案 4：使用飞书云文档（与飞书集成）
--------------------------------------------------------------------------------

1. 创建飞书云文档：
   • 在飞书中，创建一个新云文档
   • 命名为：BTC 交易监控报告

2. 嵌入 HTML 内容：
   • 直接将 HTML 源代码粘贴到文档中
   • 或创建富文本格式的报告

3. 设置定时更新：
   • 使用飞书机器人定时更新文档内容
   • 分享文档链接

✅ 优点：
  • 与飞书完美集成
  • 无需外部访问
  • 访问速度快
  • 支持协作编辑

❌ 缺点：
  • 不是纯 HTML（格式可能丢失）
  • 需要配置机器人更新

================================================================================
推荐方案排序
================================================================================

对于您的场景（BTC 监控报告），我推荐以下优先级：

🥇 第一推荐：Vercel 部署
  • 原因：现代化、部署快、全球 CDN
  • 适用：长期稳定运行

🥈 第二推荐：ngrok 内网穿透
  • 原因：配置简单、即时可用
  • 适用：快速测试和开发

🥉 第三推荐：修改防火墙
  • 原因：直接访问、无延迟
  • 适用：有管理员权限且 IP 固定

❌ 不推荐：GitHub Pages
  • 原因：国内访问不稳定
  • 适用：面向海外用户

================================================================================
下一步操作
================================================================================

选择一个方案后，我可以为您提供详细的配置步骤！

或者告诉我：
1. 您是否有管理员权限配置防火墙？
2. 您是否需要国内稳定的访问？
3. 这个报告是否需要长期稳定运行？
4. 您是否有公网 IP？

根据您的回答，我可以推荐最适合您的方案。
================================================================================
"""
    
    return solutions

def create_deployment_script(solution="vercel"):
    """创建部署脚本"""
    
    if solution == "vercel":
        script = """
#!/bin/bash
# Vercel 部署脚本

cd /root/.openclaw/workspace

# 检查是否安装了 Node.js
if ! command -v node &> /dev/null; then
    echo "Node.js 未安装，请先安装："
    echo "curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -"
    exit 1
fi

# 检查是否安装了 Vercel CLI
if ! command -v vercel &> /dev/null; then
    echo "安装 Vercel CLI..."
    npm install -g vercel
fi

# 开始部署
echo "开始部署到 Vercel..."
vercel

echo "部署完成！"
echo "请访问显示的 URL"
"""
    elif solution == "ngrok":
        script = """
#!/bin/bash
# Ngrok 内网穿透脚本

# 检查 ngrok 是否安装
if ! command -v ngrok &> /dev/null; then
    echo "下载 ngrok..."
    wget https://bin.equinox.io/c/4VmDzA7iaHbngng9DqMqEeMYnaPq1IW64A3/ngrok-v3-stable-linux-amd64.zip -O /tmp/ngrok.zip
    unzip /tmp/ngrok.zip -d /tmp/
    sudo mv /tmp/ngrok /usr/local/bin/
    
    # 提示注册
    echo "请先访问 https://dashboard.ngrok.com/signup 注册免费账户"
    echo "然后运行: ngrok authtoken <YOUR_TOKEN>"
fi

# 启动 ngrok（映射 8080 端口）
echo "启动 ngrok..."
echo "请复制显示的 HTTPS URL（类似：https://abc123.ngrok.io）"
echo "这个 URL 可以从外部访问！"
echo ""
echo "按 Ctrl+C 停止"

ngrok http 8080
"""
    else:
        script = "# 无效的方案\n"
    
    return script

def main():
    """主函数"""
    print("生成 HTML 外部访问解决方案...\n")
    
    solutions = generate_html_external_access_solutions()
    print(solutions)
    
    print("\n" + "=" * 80)
    print("📝 创建部署脚本\n")
    print("=" * 80)
    
    # 创建 Vercel 部署脚本
    vercel_script = create_deployment_script("vercel")
    vercel_path = "/root/.openclaw/workspace/deploy_to_vercel.sh"
    with open(vercel_path, 'w', encoding='utf-8') as f:
        f.write(vercel_script)
    os.chmod(vercel_path, 0o755)  # 添加执行权限
    print(f"✅ Vercel 部署脚本: {vercel_path}")
    
    # 创建 ngrok 脚本
    ngrok_script = create_deployment_script("ngrok")
    ngrok_path = "/root/.openclaw/workspace/start_ngrok.sh"
    with open(ngrok_path, 'w', encoding='utf-8') as f:
        f.write(ngrok_script)
    os.chmod(ngrok_path, 0o755)
    print(f"✅ Ngrok 启动脚本: {ngrok_path}")
    
    print("\n" + "=" * 80)
    print("📝 使用说明\n")
    print("=" * 80)
    print("Vercel 部署:")
    print(f"  bash {vercel_script}")
    print("")
    print("Ngrok 内网穿透:")
    print(f"  bash {ngrok_script}")
    print("")
    print("请根据上面的详细说明选择最适合您的方案！")
    print("=" * 80)

if __name__ == "__main__":
    main()
