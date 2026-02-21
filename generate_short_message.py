#!/usr/bin/env python3
"""
生成精简版的飞书消息（直接发送，无需链接）
"""

import os
import base64
from datetime import datetime
import json
import glob

def generate_short_message():
    """生成精简的飞书消息（<2000 字符）"""

    # 读取最新报告
    output_dir = "/root/.openclaw/workspace/reports"

    # 获取市场分析
    market_files = sorted(glob.glob(os.path.join(output_dir, "btc_report_*.txt")))
    market_report = ""
    if market_files:
        with open(market_files[-1], 'r', encoding='utf-8') as f:
            content = f.read()
            # 只提取关键信息
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('💰') or line.startswith('📈') or line.startswith('🎯'):
                    market_report += line + '\n'
                elif i > 0 and lines[i-1].startswith('📈'):
                    # 包含技术指标信息
                    if '•' in line and ':' in line:
                        market_report += line + '\n'
                if line.startswith('⚠️'):
                    break  # 只到风险提示

    # 构建简短消息
    msg_parts = []

    msg_parts.append("📊 BTC 分析报告（精简版）")
    msg_parts.append("")

    # 市场分析摘要
    if market_report:
        msg_parts.append("💰 当前市场")
        msg_parts.append(market_report[:300])  # 限制长度
        msg_parts.append("")

    # 交易回测摘要
    backtest_files = sorted(glob.glob(os.path.join(output_dir, "btc_backtest_report_*.txt")))
    if backtest_files:
        with open(backtest_files[-1], 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            for line in lines:
                if line.startswith('💰') or line.startswith('📉') or line.startswith('⚡'):
                    if '收益率' in line or '回撤' in line or '夏普' in line or '胜率' in line:
                        msg_parts.append(line)

    msg_parts.append("")
    msg_parts.append("📊 最近交易（3笔）")

    # 读取交易记录
    trades_path = "/root/.openclaw/workspace/btc_trades.json"
    try:
        with open(trades_path, 'r', encoding='utf-8') as f:
            trades = json.load(f)

        if trades:
            for trade in trades[-3:]:
                msg_parts.append(f"  {trade['datetime']} | {trade['action']} @ ${trade['price']}")
    except:
        pass

    msg_parts.append("")
    msg_parts.append("📊 简单净值曲线")

    # 生成简单的文本图表
    try:
        with open(backtest_files[-1], 'r', encoding='utf-8') as f:
            content = f.read()
            # 提取净值数据
            import re
            values = []
            for line in content.split('\n'):
                if '• 初始资金' in line:
                    values.append(10000)
                elif '• 最终资金' in line:
                    match = re.search(r'\$(\d+[.,]\d+)', line)
                    if match:
                        values.append(float(match.group(1).replace(',', '')))

            if values:
                # 生成简单趋势
                if values[1] > values[0]:
                    trend = "📈 上升"
                else:
                    trend = "📉 下降"
                
                msg_parts.append(f"  {trend}")
                msg_parts.append(f"  起始: ${values[0]:,.0f}")
                msg_parts.append(f"  当前: ${values[1]:,.0f}")
                msg_parts.append(f"  收益: {((values[1] - values[0]) / values[0] * 100):.2f}%")
    except:
        msg_parts.append("  暂无数据")

    msg_parts.append("")
    msg_parts.append("⚠️ 风险提示：本报告仅供参考，不构成投资建议")
    msg_parts.append("🔄 每小时自动更新")

    return "\n".join(msg_parts)

def main():
    """主函数"""
    message = generate_short_message()

    # 保存消息
    output_path = "/root/.openclaw/workspace/feishu_short_message.txt"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(message)

    print(f"✅ 精简消息已生成")
    print(f"消息长度：{len(message)} 字符")
    print(f"文件路径：{output_path}")
    print(f"\n消息预览：\n{message}")

    return message

if __name__ == "__main__":
    main()
