#!/bin/bash
# Arxiv 量化投资论文日报脚本 - 辅助脚本

# 设置工作目录
cd /root/.openclaw/workspace

# 运行 Python 脚本
python3 arxiv_quant_daily.py

# 获取最新生成的 Markdown 文件
LATEST_MD=$(ls -t knowledge_base/arxiv_quant/arxiv_quant_*.md 2>/dev/null | head -1)

if [ -f "$LATEST_MD" ]; then
    echo "找到最新的 Markdown 文件: $LATEST_MD"

    # 读取内容
    MD_CONTENT=$(cat "$LATEST_MD")

    # 创建飞书文档
    echo "开始创建飞书文档..."

    # 使用 openclaw 命令创建文档
    # 这里我们需要通过某种方式创建文档并发送给用户
    # 由于 openclaw feishu doc 命令可能不支持直接从命令行读取内容
    # 我们需要另想办法

    echo "注意: 飞书文档需要通过 OpenClaw 工具创建"
    echo "文档内容已保存到: $LATEST_MD"
else
    echo "未找到 Markdown 文件"
fi
