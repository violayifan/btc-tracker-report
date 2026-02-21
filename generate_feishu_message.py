#!/usr/bin/env python3
"""
生成可以直接嵌入飞书消息的完整报告
"""

import os
import base64
from datetime import datetime
import glob

# 路径
WORKSPACE = "/root/.openclaw/workspace"
OUTPUT_DIR = os.path.join(WORKSPACE, "reports")
PNG_IMAGE = os.path.join(WORKSPACE, "backtest_chart.png")

def create_feishu_message():
    """创建完整的飞书消息（包含所有内容）"""
    
    # 读取最新报告
    reports = {}

    # 市场分析
    market_files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "btc_report_*.txt")))
    if market_files:
        with open(market_files[-1], 'r', encoding='utf-8') as f:
            reports['market'] = f.read()

    # 回测报告
    backtest_files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "btc_backtest_report_*.txt")))
    if backtest_files:
        with open(backtest_files[-1], 'r', encoding='utf-8') as f:
            reports['backtest'] = f.read()

    # 构建完整消息
    message_parts = []

    # 头部
    message_parts.append("=" * 50)
    message_parts.append("📊 BTC 交易分析报告（完整版）")
    message_parts.append(f"⏰ 报告时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    message_parts.append("=" * 50)
    message_parts.append("")

    # 市场分析部分
    if 'market' in reports:
        message_parts.append("💰 市场分析")
        message_parts.append("-" * 30)
        message_parts.append(reports['market'][:500])  # 限制长度
        message_parts.append("")

    # 回测报告部分
    if 'backtest' in reports:
        message_parts.append("📈 回测报告")
        message_parts.append("-" * 30)
        message_parts.append(reports['backtest'][:500])  # 限制长度
        message_parts.append("")

    # 文本版图表
    message_parts.append("📊 净值走势（文本版）")
    message_parts.append("-" * 30)

    # 读取交易记录生成简单图表
    try:
        import json
        trades_path = os.path.join(WORKSPACE, "btc_trades.json")
        if os.path.exists(trades_path):
            with open(trades_path, 'r', encoding='utf-8') as f:
                trades = json.load(f)

            if trades:
                # 获取最后5笔交易
                recent_trades = trades[-5:]

                message_parts.append(f"📊 最近 {len(recent_trades)} 笔交易：")
                message_parts.append("")

                # 简单的净值曲线（使用 ASCII 字符）
                message_parts.append("净值走势：")
                for i, trade in enumerate(recent_trades):
                    price = trade['price']
                    bar_length = min(int(price / 1000), 20)
                    bar = "█" * bar_length + "░" * (20 - bar_length)
                    message_parts.append(f"{i+1}. {trade['datetime']} | {trade['action']} @ ${price} | {bar}")

                message_parts.append("")
                message_parts.append("📋 统计信息：")
                message_parts.append(f"  • 总交易数：{len(trades)}")
                message_parts.append(f"  • 最后价格：${trades[-1]['price']}")
                message_parts.append(f"  • 平均价格：${sum(t['price'] for t in trades) / len(trades):.2f}")
                message_parts.append("")

    except Exception as e:
        message_parts.append(f"  ⚠️ 交易记录读取失败：{str(e)}")
        message_parts.append("")

    # HTML 链接（仍然提供）
    message_parts.append("🌐 HTML 版报告（服务器端）：")
    message_parts.append("  http://47.90.150.51:8080/btc_report.html")
    message_parts.append("")
    message_parts.append("  ⚠️ 注意：此链接需要在服务器网络环境中打开")

    # 结尾
    message_parts.append("=" * 50)
    message_parts.append("⚠️ 风险提示")
    message_parts.append("  • 加密货币市场波动极大，请严格控制仓位")
    message_parts.append("  • 本报告仅供参考，不构成投资建议")
    message_parts.append("  • 交易有风险，投资需谨慎")
    message_parts.append("=" * 50)

    return "\n".join(message_parts)

def main():
    """主函数"""
    message = create_feishu_message()

    # 保存到文件
    output_path = os.path.join(WORKSPACE, "feishu_message.txt")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(message)

    print("✅ 飞书消息已生成")
    print(f"文件路径：{output_path}")
    print(f"消息长度：{len(message)} 字符")

    return message

if __name__ == "__main__":
    main()
