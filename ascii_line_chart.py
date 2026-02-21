#!/usr/bin/env python3
"""生成 ASCII 版本的净值折线图（简化版）"""

def generate_ascii_line_chart(capital_history, metrics):
    """生成 ASCII 版本的净值折线图"""
    if not capital_history:
        return "没有数据生成图表"
    
    # 提取净值值
    values = [c[1] for c in capital_history]
    
    # 找到最大和最小值用于归一化
    min_val = min(values)
    max_val = max(values)
    val_range = max_val - min_val if max_val > min_val else 1
    
    # 图表参数
    width = 50
    height = 15
    
    chart = """
╔════════════════════════════════════════════════════════════╗
║         BTC 交易净值曲线（ASCII 版）                    ║
╚════════════════════════════════════════════════════════════╝

📈 净值走势
"""

    # 生成数据点
    for i, (time, value) in enumerate(capital_history):
        # 归一化到 0-height
        normalized = int(((value - min_val) / val_range) * height)
        bar = "█" * normalized
        
        # 时间标签
        if hasattr(time, 'strftime'):
            time_label = time.strftime("%H:%M")
        else:
            time_label = f"T{i+1}"
        
        chart += f"{time_label:>6s} | ${value:>8,.2f} | {bar}\n"
    
    # 统计数据
    chart += f"""
{'='*70}
📊 统计数据
"""

    metrics_list = [
        ("总收益率", f"{metrics.get('total_return', 0)}%"),
        ("年化收益率", f"{metrics.get('annualized_return', 0)}%"),
        ("最大回撤", f"{metrics.get('max_drawdown', 0)}%"),
        ("回撤持续", f"{metrics.get('max_drawdown_duration_hours', 0)} 小时"),
        ("夏普比率", f"{metrics.get('sharpe_ratio', 0)}"),
        ("总交易次数", f"{metrics.get('total_trades', 0)}"),
        ("胜率", f"{metrics.get('win_rate', 0)}%"),
        ("初始资金", f"${metrics.get('initial_capital', 0):,.2f}"),
        ("最终资金", f"${metrics.get('final_capital', 0):,.2f}")
    ]
    
    for key, value in metrics_list:
        chart += f"• {key:<12s}: {value}\n"
    
    # 简单的曲线示意
    chart += f"""
{'='*70}
📈 曲线示意

"""
    
    if values:
        # 归一化的值用于曲线
        normalized_values = [((v - min_val) / val_range) * (width - 10) for v in values]
        positions = [int(v) + 5 for v in normalized_values]
        
        # 绘制多条曲线
        for row in range(height):
            line = "     "
            for col in range(width):
                # 检查是否有数据点在这个位置
                is_data_point = False
                for pos in positions:
                    if pos == col:
                        is_data_point = True
                        break
                
                # 检查是否在曲线上
                is_on_line = False
                for i in range(len(positions) - 1):
                    x1, x2 = positions[i], positions[i + 1]
                    y1, y2 = height - row - 1, height - row - 1
                    if x1 <= col <= x2 and min(y1, y2) <= row <= max(y1, y2):
                        is_on_line = True
                        break
                
                if is_data_point:
                    line += "●"
                elif is_on_line:
                    line += "*"
                elif col == 5 or col == width - 5:
                    line += "│"
                elif row == 0 or row == height - 1:
                    line += "─"
                else:
                    line += " "
            
            chart += line + "\n"
        
        # 时间轴
        chart += "     "
        for i in range(0, len(capital_history), len(capital_history) // 10):
            if i < len(capital_history):
                if hasattr(capital_history[i][0], 'strftime'):
                    time_label = capital_history[i][0].strftime("%H:%M")
                else:
                    time_label = f"T{i+1}"
                chart += f"{time_label:>8s}"
        
        chart += "\n\n"
    
    chart += f"{'='*70}\n"
    
    return chart

def main():
    """主函数 - 使用测试数据"""
    # 模拟净值曲线数据
    from datetime import datetime, timedelta
    
    base_time = datetime.now().replace(minute=0, second=0, microsecond=0)
    capital_history = [
        (base_time + timedelta(hours=i), value)
        for i, value in enumerate([10000, 10029, 10085, 10108, 10132, 10085, 10008, 10030, 10115, 10100])
    ]
    
    # 模拟指标
    metrics = {
        "total_return": 1.00,
        "annualized_return": 0,
        "max_drawdown": 0.76,
        "max_drawdown_duration_hours": 0.13,
        "sharpe_ratio": -0.0634,
        "total_trades": 9,
        "win_rate": 22.22,
        "initial_capital": 10000,
        "final_capital": 10100
    }
    
    # 生成折线图
    chart = generate_ascii_line_chart(capital_history, metrics)
    print(chart)
    
    # 保存
    output_path = "/root/.openclaw/workspace/ascii_line_chart.txt"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(chart)
    print(f"\n图表已保存: {output_path}")

if __name__ == "__main__":
    main()
