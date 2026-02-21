#!/bin/bash
# 更新 BTC 交易报告到 Netlify
# 网址不变，内容自动更新

WORKSPACE="/root/.openclaw/workspace"
NETLIFY_DIR="$WORKSPACE/netlify_deploy"
AUTH_TOKEN="nfc_6XkaoNi5ZKPmqtMYKTrUBUb9fGsmsM5rc5e6"
SITE_NAME="btc-tracker-report"

echo "=============================================="
echo "🔄 更新 BTC 交易报告"
echo "=============================================="
echo ""

# 步骤 1: 运行 BTC 市场分析
echo "步骤 1: 运行 BTC 市场分析..."
cd "$WORKSPACE"
python3 btc_monitor.py
echo "✅ 完成"
echo ""

# 步骤 2: 生成 HTML 报告
echo "步骤 2: 生成 HTML 报告..."
python3 btc_html_report_v2.py
echo "✅ 完成"
echo ""

# 步骤 3: 准备部署文件
echo "步骤 3: 准备部署文件..."
mkdir -p "$NETLIFY_DIR"
cp "$WORKSPACE/btc_report_enhanced.html" "$NETLIFY_DIR/index.html"
touch "$NETLIFY_DIR/.nojekyll"
echo "✅ 完成"
echo ""

# 步骤 4: 部署到 Netlify
echo "步骤 4: 部署到 Netlify..."
cd "$NETLIFY_DIR"

# 使用已链接的项目（不指定 site name，自动使用 siteId）
DEPLOY_OUTPUT=$(netlify deploy --prod --dir=. --auth="$AUTH_TOKEN" 2>&1)

echo "$DEPLOY_OUTPUT"
echo ""

echo "=============================================="
echo "✅ 更新完成！"
echo "=============================================="
echo ""
echo "🌐 访问网址:"
echo "  https://btc-tracker-report.netlify.app"
echo ""
echo "💡 提示:"
echo "  • 网址保持不变"
echo "  • 内容已自动更新"
echo "  • 可以在浏览器中刷新查看"
echo ""
