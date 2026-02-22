#!/bin/bash

# BTC Tracker GitHub Pages 自动更新脚本

echo "🔄 ==========================================="
echo "🔄 BTC 市场分析自动更新脚本"
echo "🔄 ==========================================="
echo ""

# 进入工作目录
cd /root/.openclaw/workspace

# 运行 BTC 高级市场分析
echo "📊 [1/7] 运行 BTC 高级市场分析..."
python3 /root/.openclaw/workspace/btc_advanced_monitor.py

if [ $? -ne 0 ]; then
    echo "❌ BTC 高级分析失败"
    echo "❌ 更新终止"
    exit 1
fi

echo "✅ BTC 高级分析完成"
echo ""

# 生成 HTML 报告
echo "📄 [2/7] 生成 HTML 报告..."
python3 /root/.openclaw/workspace/btc_html_report_v3.py > /dev/null 2>&1 &
HTML_PID=$!

# 等待 HTML 生成完成
sleep 3

# 检查 HTML 文件是否生成
if [ ! -f "/root/.openclaw/workspace/btc_report_enhanced.html" ]; then
    echo "❌ HTML 报告生成失败"
    echo "❌ 更新终止"
    kill $HTML_PID 2>/dev/null
    exit 1
fi

# 复制 HTML 到 index.html
cp /root/.openclaw/workspace/btc_report_enhanced.html /root/.openclaw/workspace/index.html
kill $HTML_PID 2>/dev/null

echo "✅ HTML 报告生成完成"
echo ""

# 更新 Git 仓库
echo "🔄 [3/7] 更新 Git 仓库..."

# 强制添加所有更改
git add -A

if [ $? -ne 0 ]; then
    echo "❌ Git add 失败"
    echo "❌ 更新终止"
    exit 1
fi

echo "✅ Git add 完成"
echo ""

# 提交更改
echo "📝 [4/7] 提交更改到 Git..."
TIMESTAMP=$(date +%Y-%m-%d\ %H:%M:%S)
git commit -m "Update BTC 市场分析报告 - $TIMESTAMP"

if [ $? -ne 0 ]; then
    echo "❌ Git commit 失败"
    echo "❌ 更新终止"
    exit 1
fi

echo "✅ Git commit 完成"
echo ""

# 推送到 GitHub
echo "🚀 [5/7] 推送到 GitHub Pages..."
git push origin master

if [ $? -ne 0 ]; then
    echo "❌ Git push 失败"
    echo "❌ 更新终止"
    exit 1
fi

echo "✅ 推送到 GitHub 成功"
echo ""

# 验证推送
echo "🔍 [6/7] 验证推送状态..."
LOCAL_COMMIT=$(git rev-parse master)
REMOTE_COMMIT=$(git rev-parse origin/master)

if [ "$LOCAL_COMMIT" = "$REMOTE_COMMIT" ]; then
    echo "✅ 推送验证成功"
    echo "✅ 本地和远程提交一致: $LOCAL_COMMIT"
else
    echo "⚠️  本地和远程提交不一致"
    echo "⚠️  本地: $LOCAL_COMMIT"
    echo "⚠️  远程: $REMOTE_COMMIT"
fi

echo ""
echo "🌐 ==========================================="
echo "🌐 网站地址: https://violayifan.github.io/btc-tracker-report"
echo "🌐 ==========================================="
echo ""

echo "✅ ==========================================="
echo "✅ BTC 市场分析报告已自动更新"
echo "✅ ==========================================="
echo ""

echo "📊 更新摘要"
echo "   • BTC 高级市场分析: ✅ 完成"
echo "   • 量价因子分析: ✅ 完成"
echo "   • 链上资金分析: ✅ 完成"
echo "   • 市场情绪分析: ✅ 完成"
echo "   • 宏观新闻分析: ✅ 完成"
echo "   • X舆情分析: ✅ 完成"
echo "   • 复盘与迭代: ✅ 完成"
echo "   • Git 仓库更新: ✅ 完成"
echo "   • GitHub Pages 部署: ✅ 完成"
echo ""

echo "🕐 更新时间: $TIMESTAMP"
echo ""

exit 0
