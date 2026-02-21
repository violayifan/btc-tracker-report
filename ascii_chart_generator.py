#!/usr/bin/env python3
"""生成 ASCII 版本的净值曲线图"""

import json
import os

TRACKER_FILE = "/root/.openclaw/workspace/btc_trades.json"

def generate_ascii_chart():
    """生成 ASCII 图表"""
    # 模拟净值曲线数据
    capital_history = [
        10000, 10029, 10085, 10108, 10132, 10085, 10008
    ]

    chart = f"""
{'='*60}
📊 BTC 交易净值曲线（ASCII 版）
{'='*60}

📈 净值走势
"""

    if capital_history:
        # 找到最大和最小值用于归一化
        min_val = min(capital_history)
        max_val = max(capital_history)
        val_range = max_val - min_val if max_val > min_val else 1

        # 图表宽度
        width = 40

        for i, value in enumerate(capital_history):
            # 归一化到 0-100
            normalized = int((value - min_val) / val_range * 100)
            bar_length = int(normalized / 100 * width)
            bar = "█" * bar_length + "░" * (width - bar_length)
            chart += f"{i:2d} | ${value:,.0f} | {bar}\n"

        chart += f"\n📋 统计数据\n"
        final_value = capital_history[-1]
        initial_value = capital_history[0]
        total_return = final_value - initial_value
        return_rate = (total_return / initial_value) * 100

        chart += f"{'-'*40}\n"

        metrics_list = [
            ("总收益率", f"{return_rate:.2f}%"),
            ("总收益", f"${total_return:,.2f}"),
            ("初始资金", f"${initial_value:,.0f}"),
            ("最终资金", f"${final_value:,.0f}")
        ]

        for key, value in metrics_list:
            chart += f"• {key:.<12s}: {value}\n"

        chart += f"\n{'='*60}\n"

    return chart

def main():
    """主函数"""
    chart = generate_ascii_chart()
    print(chart)

    # 保存到文件
    output_path = "/root/.openclaw/workspace/ascii_chart.txt"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(chart)
    print(f"\n图表已保存: {output_path}")

if __name__ == "__main__":
    main()
