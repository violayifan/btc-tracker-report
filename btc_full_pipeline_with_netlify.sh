#!/bin/bash
# BTC 市场分析 + Netlify 自动部署完整流程
# 一键完成：市场分析 → HTML 生成 → Netlify 部署

set -e

WORKSPACE="/root/.openclaw/workspace"
NETLIFY_DIR="$WORKSPACE/netlify_deploy"

echo "================================================"
echo "🚀 BTC 分析 + Netlify 自动部署"
echo "================================================"
echo "🕐 开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# ========== 步骤 1: 运行 BTC 市场分析 ==========
echo "================================================"
echo "步骤 1: 运行 BTC 市场分析"
echo "================================================"
echo ""

cd "$WORKSPACE"
python3 btc_monitor.py

echo ""
echo "✅ BTC 市场分析完成"
echo ""

# ========== 步骤 2: 生成 HTML 报告 ==========
echo "================================================"
echo "步骤 2: 生成增强版 HTML 报告"
echo "================================================"
echo ""

python3 btc_html_report_v2.py

echo ""
echo "✅ HTML 报告生成完成"
echo ""

# ========== 步骤 3: 准备 Netlify 部署 ==========
echo "================================================"
echo "步骤 3: 准备 Netlify 部署"
echo "================================================"
echo ""

# 创建部署目录
mkdir -p "$NETLIFY_DIR"

# 复制 HTML 文件
cp "$WORKSPACE/btc_report_enhanced.html" "$NETLIFY_DIR/index.html"

# 创建 .nojekyll 文件
touch "$NETLIFY_DIR/.nojekyll"

echo "✅ 部署文件准备完成"
echo ""

# ========== 步骤 4: 检查 Netlify CLI ==========
echo "================================================"
echo "步骤 4: 检查 Netlify CLI"
echo "================================================"
echo ""

if ! command -v netlify &> /dev/null; then
    echo "⚠️  Netlify CLI 未安装，正在安装..."
    npm install -g netlify-cli
    echo "✅ Netlify CLI 安装完成"
else
    echo "✅ Netlify CLI 已安装"
fi

echo ""

# ========== 步骤 5: 检查登录状态 ==========
echo "================================================"
echo "步骤 5: 检查 Netlify 登录状态"
echo "================================================"
echo ""

if ! netlify status &> /dev/null; then
    echo "❌ 未登录 Netlify"
    echo ""
    echo "请先登录 Netlify:"
    echo "  netlify login"
    echo ""
    echo "或者，如果你有 Netlify auth token，可以设置环境变量:"
    echo "  export NETLIFY_AUTH_TOKEN=your_token_here"
    echo ""
    exit 1
fi

echo "✅ 已登录 Netlify"
echo ""

# ========== 步骤 6: 部署到 Netlify ==========
echo "================================================"
echo "步骤 6: 部署到 Netlify"
echo "================================================"
echo ""

cd "$NETLIFY_DIR"

# 检查是否是首次部署
if [ ! -f ".netlify/state.json" ]; then
    echo "🆕 首次部署，创建新站点..."
    echo ""

    # 首次部署
    DEPLOY_OUTPUT=$(netlify deploy --prod --dir=. --site=btc-tracker-report 2>&1)

    echo ""
    echo "$DEPLOY_OUTPUT"

    # 提取 URL
    URL=$(echo "$DEPLOY_OUTPUT" | grep -oP 'https://[^"]+\.netlify\.app' || echo "")

    if [ -n "$URL" ]; then
        # 保存 URL 到文件
        echo "$URL" > "$WORKSPACE/netlify_url.txt"
        echo ""
        echo "✅ 首次部署完成！"
        echo ""
        echo "📋 重要信息:"
        echo "  • URL: $URL"
        echo "  • 请保存这个 URL"
        echo "  • 以后更新内容，网址不会改变"
        echo ""
    fi
else
    echo "🔄 更新现有站点..."
    echo ""

    # 更新部署
    DEPLOY_OUTPUT=$(netlify deploy --prod --dir=. 2>&1)

    echo ""
    echo "$DEPLOY_OUTPUT"

    # 提取 URL
    URL=$(echo "$DEPLOY_OUTPUT" | grep -oP 'https://[^"]+\.netlify\.app' || echo "")

    if [ -z "$URL" ]; then
        # 从保存的文件读取 URL
        if [ -f "$WORKSPACE/netlify_url.txt" ]; then
            URL=$(cat "$WORKSPACE/netlify_url.txt")
        fi
    fi

    echo ""
    echo "✅ 部署更新完成！"
    echo ""
    echo "📋 访问信息:"
    echo "  • URL: $URL"
    echo "  • 网址保持不变"
    echo "  • 内容已自动更新"
    echo ""
fi

# 清理
cd "$WORKSPACE"

# ========== 完成 ==========
echo "================================================"
echo "✅ 全部完成"
echo "================================================"
echo "🕐 完成时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "📋 总结:"
echo "  ✅ BTC 市场分析完成"
echo "  ✅ HTML 报告生成完成"
echo "  ✅ Netlify 部署完成"
echo ""
echo "🌐 访问网址:"
echo "  $URL"
echo ""
echo "💡 提示:"
echo "  • 以后每次运行此脚本，内容会自动更新"
echo "  • 网址保持不变"
echo "  • 可以设置 cron 定时自动运行"
echo ""
echo "📝 设置定时任务（每小时更新）:"
echo "  crontab -e"
echo "  添加:"
echo "  0 * * * * $WORKSPACE/btc_full_pipeline_with_netlify.sh >> $WORKSPACE/netlify_deploy.log 2>&1"
echo ""
echo "================================================"
