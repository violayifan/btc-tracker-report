#!/bin/bash
# Arxiv 论文日报 + 飞书消息发送
# 每天早上 8 点执行

WORKSPACE="/root/.openclaw/workspace"
cd "$WORKSPACE"

echo "[$(date)] 🚀 开始执行 Arxiv 论文日报任务..."

# 1. 运行 Arxiv 分析脚本
python3 arxiv_quant_daily.py

# 2. 检查是否生成了飞书报告
if [ -f "temp_feishu_report.md" ]; then
    echo "[$(date)] ✅ 飞书报告已生成，准备发送..."

    # 3. 使用 OpenClaw 的 cron 工具发送飞书消息
    # 创建一个临时消息文件
    REPORT_CONTENT=$(cat temp_feishu_report.md)

    # 使用 message 工具发送（通过调用 OpenClaw CLI）
    /root/.openclaw/bin/openclaw message send \
        --channel feishu \
        --target "ou_9cde50d77f516edcf3a661ca32f83b2a" \
        --message "$REPORT_CONTENT"

    if [ $? -eq 0 ]; then
        echo "[$(date)] ✅ 飞书消息发送成功"
    else
        echo "[$(date)] ❌ 飞书消息发送失败"
    fi

    # 4. 清理待处理标记（如果存在）
    rm -f .arxiv_pending
else
    echo "[$(date)] ⚠️ 飞书报告未生成，跳过发送"
fi

echo "[$(date)] ✅ Arxiv 论文日报任务完成"
