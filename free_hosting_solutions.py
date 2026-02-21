#!/usr/bin/env python3
"""
无需 SSH 登录的 HTML 报告托管方案（真正公网访问）
"""

def generate_free_hosting_solutions():
    """生成免费云托管方案"""
    
    solutions = """
================================================================================
🌐 无需 SSH 登录的真正公网访问方案
================================================================================

当前问题：
  • SSH 端口转发需要登录
  • 内网穿透需要本地运行
  • 防火墙配置复杂
  • 需要服务器 IP

================================================================================
✅ 推荐方案（完全免费，无需登录，无需服务器）
================================================================================

方案 1: Vercel 部署（最推荐）
--------------------------------------------------------------------------------
✅ 优势：
  • 完全免费
  • 全球 CDN（速度极快）
  • 自动 HTTPS
  • 支持自定义域名
  • 部署快（几秒钟）
  • 完全托管，无需任何本地操作
  • 自动 CI/CD

📝 配置步骤（一次配置，永久使用）：

1. 注册 Vercel 账号：
   • 访问：https://vercel.com/signup
   • 使用 GitHub 或 GitLab 登录（推荐）
   • 选择免费计划

2. 导入项目：
   • 登录后，点击 "Add New Project"
   • 选择 "Import Git Repository"
   • 如果没有仓库，点击 "Create Empty Project"
   • 项目名称：btc-tracker-report

3. 连接 GitHub 仓库（如果有）：
   • 在 Vercel 控制台，点击 "Settings" → "Git"
   • 连接您的 GitHub 账号
   • 选择或创建仓库

4. 配置自动部署：
   • Vercel 会自动监听仓库的推送
   • 每次推送时自动部署
   • 部署时间：通常 30-60 秒

5. 获取访问 URL：
   • 部署成功后，Vercel 会显示 URL
   • 格式：https://btc-tracker-report.vercel.app
   • 或自定义域名：https://yourdomain.com

💡 工作流程：
  1. BTC 监控脚本每小时生成 HTML 报告
  2. 脚本自动将 HTML 推送到 GitHub 仓库
  3. Vercel 检测到推送，自动重新部署
  4. 几分钟后，用户访问的就是最新的报告

✅ 无需任何手动操作！

--------------------------------------------------------------------------------

方案 2: Netlify 部署
--------------------------------------------------------------------------------
✅ 优势：
  • 完全免费
  • 拖拽部署（超级简单）
  • 全球 CDN
  • 自动 HTTPS
  • 支持表单处理

📝 配置步骤（最简单）：

1. 注册 Netlify 账号：
   • 访问：https://app.netlify.com/signup
   • 使用邮箱注册

2. 创建新站点：
   • 点击 "Add new site" → "Deploy manually"

3. 上传 HTML 文件：
   • 选择 "Upload folder"
   • 选择 BTC 报告 HTML 文件所在的文件夹
   • 点击 "Deploy site"

4. 获取访问 URL：
   • 部署成功后，Netlify 会显示 URL
   • 格式：https://random-name.netlify.app
   • 可以在 Site settings 中修改

💡 持续更新方案：
  • 使用 Netlify CLI：`netlify-cli deploy`
  • 或使用 Git：Netlify 也会自动检测推送
  • 手动拖拽更新也很简单

--------------------------------------------------------------------------------

方案 3: Cloudflare Pages（稳定）
--------------------------------------------------------------------------------
✅ 优势：
  • 完全免费
  • Cloudflare 全球 CDN（最快）
  • 原生支持自定义域名
  • 带宽无限
  • DDoS 防护
  • 国内访问相对稳定

📝 配置步骤：

1. 登录 Cloudflare：
   • 访问：https://dash.cloudflare.com/
   • 使用 Cloudflare 账号登录（如果没有，注册一个）

2. 创建 Pages 项目：
   • 左侧菜单选择 "Workers & Pages"
   • 点击 "Create application"
   • 点击 "Pages" → "Create a project"
   • 选择 "Upload assets"

3. 上传 HTML 文件：
   • 点击 "Add assets"
   • 选择 BTC 报告 HTML 文件
   • 等待上传完成
   • 点击 "Deploy site"

4. 获取访问 URL：
   • 格式：https://your-project.pages.dev
   • 可以在项目设置中配置自定义域名

💡 持续更新：
  • 使用 Git 连接（推荐）
  • 或使用 Wrangler CLI 工具
  • 手动上传也很简单

--------------------------------------------------------------------------------

方案 4: GitHub Pages（最传统）
--------------------------------------------------------------------------------
✅ 优势：
  • 完全免费
  • 与 GitHub 集成最好
  • 支持自定义域名
  • 无限带宽

❌ 缺点：
  • 国内访问可能不稳定
  • 部署时间较慢（1-2 分钟）

📝 配置步骤：

1. 创建 GitHub 仓库：
   • 访问：https://github.com/new
   • 仓库名：btc-tracker-report
   • 设为 Public（公开）
   • 初始化为 README

2. 上传 HTML 文件：
   • 使用 GitHub 网页界面上传
   • 或使用 Git 命令行

3. 启用 GitHub Pages：
   • 仓库页面 → Settings
   • 滚动到 GitHub Pages 部分
   • Source：Deploy from a branch
   • Branch：main
   • 点击 Save

4. 访问网站：
   • URL：https://yourusername.github.io/btc-tracker-report/
   • 等待 1-2 分钟部署完成

================================================================================
🎯 推荐方案对比
================================================================================

方案              | 免费 | 速度 | 国内访问 | 部署难度 | 自动化 | 推荐度
---------------|------|------|---------|---------|--------|--------
**Vercel**     | ✅  | 🚀 极快 | ⚠️  中等 | 🥉 简单   | 🥇 第一
**Netlify**    | ✅  | 🚀 快   | ⚠️  中等 | 🚀 最简   | 🥈 第二
**Cloudflare** | ✅  | 🚀 快   | ✅ 较好 | 🥉 简单   | 🥉 第三
**GitHub**     | ✅  | 🐢 中等 | ❌ 不稳  | 🔴 中等   | 🔴 第四

================================================================================
🚀 最简单方案（推荐立即使用）
================================================================================

使用 Netlify 的拖拽部署：

1. 访问：https://app.netlify.com/drop
2. 将 BTC 报告 HTML 文件拖到网页上
3. 等待 10-30 秒
4. 获得 URL（类似：https://btc-tracker-report-abc123.netlify.app）
5. 完成！

就这么简单，无需任何配置，无需代码，无需 Git！

================================================================================
📝 自动化更新方案
================================================================================

为了实现每小时自动更新，我们可以：

方案 A: 使用 Git + GitHub + Vercel
  • 最稳定，最专业
  • 完全自动化
  • 需要配置 Git 和 GitHub
  • 我可以为您编写自动推送脚本

方案 B: 使用 Vercel CLI 自动部署
  • 需要安装 Vercel CLI
  • 可以在服务器脚本中直接调用
  • 每次生成报告后自动部署

方案 C: 使用 Netlify Drop 手动上传
  • 每小时生成后，手动拖拽上传
  • 最简单，但需要手动操作

方案 D: 使用 wrangler 自动部署到 Cloudflare Pages
  • 需要 Cloudflare 账号
  • 完全自动化

================================================================================
🎯 我的建议
================================================================================

1. **短期方案（立即可用）**：
   → 使用 Netlify Drop 拖拽部署
   • 耗时：1 分钟
   • 无需任何配置

2. **长期方案（自动化）**：
   → 配置 Vercel + Git
   → 编写自动推送脚本
   → 实现每小时自动更新

3. **如果想要最稳定的国内访问**：
   → 配置 Cloudflare Pages
   → 或使用阿里云 OSS（需要配置，可能有费用）

================================================================================
❓ 您想选择哪个方案？
================================================================================

选项 A: Netlify 拖拽（最简单，立即用）
选项 B: Vercel + Git 自动化（专业，稳定）
选项 C: Cloudflare Pages（国内稳定）
选项 D: GitHub Pages（传统，但国内可能慢）

请告诉我您的选择，我可以为您提供详细的配置步骤！
================================================================================
"""
    
    return solutions

def create_automation_script():
    """创建自动化部署脚本"""
    
    script = """
#!/bin/bash
# 自动上传 HTML 到 Vercel 的脚本

# 1. 将 HTML 复制到 Git 仓库
cp /root/.openclaw/workspace/btc_report.html /root/.openclaw/workspace/btc-tracker-report/

# 2. 进入 Git 仓库
cd /root/.openclaw/workspace/btc-tracker-report

# 3. 初始化 Git（如果还没有）
if [ ! -d ".git" ]; then
    git init
    git add .
    git commit -m "Initial commit: BTC tracker report HTML"
    echo "📦 Git 仓库已初始化"
fi

# 4. 拉取最新
git pull origin main

# 5. 复制新的 HTML 文件
cp /root/.openclaw/workspace/btc_report.html index.html

# 6. 提交更改
git add index.html
git commit -m "Update BTC tracker report - $(date +'%Y-%m-%d %H:%M:%S')"

# 7. 推送到 GitHub
# 注意：第一次需要配置远程仓库
if ! git remote | grep origin; then
    echo "⚠️  请先配置 Git 远程仓库："
    echo "   git remote add origin https://github.com/YOUR_USERNAME/btc-tracker-report.git"
    echo "   git push -u origin main"
    echo "   然后重新运行此脚本"
    exit 1
fi

git push origin main

echo "✅ HTML 已推送到 GitHub！"
echo "📦 Vercel 将自动检测到更改并重新部署"
echo "⏱️  预计部署时间：30-60 秒"
echo ""
echo "💡 提示："
echo "   • 确保在 Vercel 中连接了此 GitHub 仓库"
echo "   • Vercel 会自动部署，无需手动操作"
echo "   • 可以在 Vercel 控制台查看部署状态"
"""
    
    return script

def main():
    """主函数"""
    print("生成无需 SSH 的公网访问方案...")
    print()
    
    solutions = generate_free_hosting_solutions()
    print(solutions)
    
    print("\n" + "=" * 80)
    print("📝 创建自动化部署脚本")
    print("=" * 80)
    
    script = create_automation_script()
    
    script_path = "/root/.openclaw/workspace/auto_deploy.sh"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script)
    
    os.chmod(script_path, 0o755)
    
    print(f"✅ 自动化部署脚本已创建: {script_path}")
    print(f"🚀 用法: bash {script_path}")
    print()

if __name__ == "__main__":
    main()
