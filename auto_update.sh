#!/bin/bash

# BTC Tracker GitHub Pages 自动更新脚本

echo "🔄 ==========================================="
echo "🔄 BTC 市场分析自动更新脚本"
echo "🔄 ==========================================="
echo ""

# 进入工作目录
cd /root/.openclaw/workspace

# 运行 BTC 市场分析
echo "📊 [1/5] 运行 BTC 市场分析..."
python3 /root/.openclaw/workspace/btc_monitor.py

if [ $? -ne 0 ]; then
    echo "❌ BTC 市场分析失败"
    echo "❌ 更新终止"
    exit 1
fi

echo "✅ BTC 市场分析完成"
echo ""

# 更新 Git 仓库
echo "🔄 [2/5] 更新 Git 仓库..."

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
echo "📝 [3/5] 提交更改到 Git..."
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
echo "🚀 [4/5] 推送到 GitHub Pages..."
git push origin master

if [ $? -ne 0 ]; then
    echo "❌ Git push 失败"
    echo "❌ 更新终止"
    exit 1
fi

echo "✅ 推送到 GitHub 成功"
echo ""

# 验证推送
echo "🔍 [5/5] 验证推送状态..."
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
echo "   • BTC 市场分析: ✅ 完成"
echo "   • Git 仓库更新: ✅ 完成"
echo "   • GitHub Pages 部署: ✅ 完成"
echo ""

echo "🕐 更新时间: $TIMESTAMP"
echo ""

exit 0
