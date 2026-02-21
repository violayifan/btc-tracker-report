#!/bin/bash
# BTC 分析报告包装脚本
# 由 cron 定时调用，生成报告并发送

cd /root/.openclaw/workspace

# 运行分析脚本
python3 btc_monitor.py

# 获取最新报告
LATEST_REPORT=$(ls -t reports/btc_report_*.txt 2>/dev/null | head -1)

if [ -f "$LATEST_REPORT" ]; then
    echo "✅ 报告生成成功"
    # 输出报告内容以便 OpenClaw 捕获
    cat "$LATEST_REPORT"
else
    echo "❌ 报告生成失败"
fi
