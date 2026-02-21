
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
