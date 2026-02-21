#!/bin/bash
# 使用 Netlify CLI 自动部署 BTC 交易报告
# 网址不变，内容自动更新

set -e

# 配置
WORKSPACE="/root/.openclaw/workspace"
HTML_FILE="btc_report_enhanced.html"
NETLIFY_DIR="$WORKSPACE/netlify_deploy"

echo "================================================"
echo "🚀 Netlify 自动部署脚本"
echo "================================================"
echo ""

# 检查 Netlify CLI 是否安装
if ! command -v netlify &> /dev/null; then
    echo "❌ Netlify CLI 未安装"
    echo ""
    echo "正在安装 Netlify CLI..."
    npm install -g netlify-cli
    echo "✅ Netlify CLI 安装完成"
fi

# 创建部署目录
echo "📁 准备部署目录..."
mkdir -p "$NETLIFY_DIR"

# 复制 HTML 文件
cp "$WORKSPACE/$HTML_FILE" "$NETLIFY_DIR/index.html"

# 创建 .nojekyll 文件（防止 GitHub Pages 处理）
touch "$NETLIFY_DIR/.nojekyll"

echo "✅ 文件准备完成"
echo ""

# 检查是否已登录
echo "🔐 检查 Netlify 登录状态..."
if ! netlify status &> /dev/null; then
    echo "⚠️  未登录 Netlify"
    echo ""
    echo "请先登录 Netlify:"
    echo "  netlify login"
    echo ""
    echo "或者使用浏览器授权:"
    echo "  1. 运行: netlify login"
    echo "  2. 复制显示的授权链接"
    echo "  3. 在浏览器中打开并授权"
    echo ""
    echo "授权完成后重新运行此脚本"
    exit 1
fi

echo "✅ 已登录 Netlify"
echo ""

# 检查是否已关联站点
if [ ! -f "$NETLIFY_DIR/.netlify/state.json" ]; then
    echo "🆕 首次部署，创建新站点..."
    echo ""

    cd "$NETLIFY_DIR"

    # 首次部署，会提示输入站点名称等信息
    netlify deploy --prod --dir=. --site=btc-tracker-report

    echo ""
    echo "✅ 首次部署完成！"
    echo ""
    echo "📋 重要信息:"
    echo "  • 请保存上面的 URL"
    echo "  • 以后更新内容，网址不变"
    echo ""
else
    echo "🔄 更新现有站点..."
    echo ""

    cd "$NETLIFY_DIR"

    # 更新现有站点
    netlify deploy --prod --dir=.

    echo ""
    echo "✅ 部署更新完成！"
    echo ""
    echo "📋 访问信息:"
    echo "  • 网址保持不变"
    echo "  • 内容已自动更新"
    echo ""
fi

# 清理
cd "$WORKSPACE"

echo "================================================"
echo "✅ 部署完成"
echo "================================================"
echo ""
echo "💡 提示:"
echo "  • 以后每次更新报告，运行此脚本即可"
echo "  • 网址不会改变"
echo "  • 内容会自动更新"
echo "  • 可以设置 cron 定时自动运行"
echo ""
echo "📝 设置定时任务（每小时更新）:"
echo "  crontab -e"
echo "  添加:"
echo "  0 * * * * $WORKSPACE/deploy_to_netlify.sh >> $WORKSPACE/netlify_deploy.log 2>&1"
echo ""
