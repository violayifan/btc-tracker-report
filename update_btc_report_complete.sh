#!/bin/bash
# 完整的 BTC 交易报告自动化脚本（包含策略复盘和优化）

WORKSPACE="/root/.openclaw/workspace"
NETLIFY_DIR="$WORKSPACE/netlify_deploy"
AUTH_TOKEN="nfc_6XkaoNi5ZKPmqtMYKTrUBUb9fGsmsM5rc5e6"

echo "=============================================="
echo "🔄 更新 BTC 交易报告"
echo "=============================================="
echo ""

# 步骤 1: 运行 BTC 市场分析
echo "步骤 1: 运行 BTC 市场分析..."
cd "$WORKSPACE"
python3 btc_monitor.py

# 步骤 2: 策略复盘（分析策略绩效）
echo ""
echo "步骤 2: 策略复盘..."
python3 btc_strategy_reviewer.py

# 步骤 3: 策略参数优化（基于复盘结果自动调整）
echo ""
echo "步骤 3: 策略参数优化..."
python3 btc_strategy_optimizer.py

# 步骤 4: 生成增强版 HTML 报告
echo ""
echo "步骤 4: 生成增强版 HTML 报告..."
python3 btc_html_report_fixed.py

# 步骤 5: 准备部署文件
echo ""
echo "步骤 5: 准备部署文件..."
mkdir -p "$NETLIFY_DIR"
cp "$WORKSPACE/btc_report_enhanced.html" "$NETLIFY_DIR/index.html"
touch "$NETLIFY_DIR/.nojekyll"

# 步骤 6: 部署到 Netlify
echo ""
echo "步骤 6: 部署到 Netlify..."
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
echo "📊 本次更新内容:"
echo "  • 市场分析完成"
echo "  • 策略复盘完成"
echo "  • 策略参数自动优化"
echo "  • 增强版 HTML 报告生成"
echo "  • 已部署到 Netlify"
echo ""
echo "📋 新增功能:"
echo "  • 策略绩效分析（胜率、盈亏比、夏普比率）"
echo "  • 自动策略复盘（识别优势和劣势）"
echo "  • 自动参数优化（基于绩效自动调整）"
echo "  • 策略迭代历史记录"
echo ""
echo "💡 提示:"
echo "  • 网址保持不变"
echo "  • 内容已自动更新"
echo "  • 可以在浏览器中刷新查看"
echo ""
echo "⚠️ 本报告仅供参考，不构成投资建议"
echo "=============================================="
echo ""
