
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
