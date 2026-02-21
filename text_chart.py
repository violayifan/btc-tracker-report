# 文本版净值曲线生成器（避免 matplotlib 依赖）

def generate_text_chart(capital_history, metrics):
    """生成文本版的净值曲线图"""
    if not capital_history:
        return "没有数据生成图表"
    
    times = [c[0].strftime("%H:%M") for c in capital_history]
    values = [c[1] for c in capital_history]
    
    # 找到最大和最小值用于归一化
    min_val = min(values)
    max_val = max(values)
    val_range = max_val - min_val if max_val > min_val else 1
    
    # 图表宽度
    width = 60
    
    chart = f"""
{'='*80}
📊 BTC 交易净值曲线（文本版）
{'='*80}

📈 净值走势
"""
    
    for time, value in capital_history:
        # 归一化到 0-100
        normalized = int((value - min_val) / val_range * 100)
        bar_length = int(normalized / 100 * width)
        bar = "█" * bar_length + "░" * (width - bar_length)
        chart += f"{time} | ${value:,.2f} | {bar}\n"
    
    chart += f"\n📋 绩效指标\n"
    chart += f"{'-'*40}\n"
    
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
        chart += f"• {key:.<12s}: {value}\n"
    
    chart += f"\n{'='*80}\n"
    
    return chart
