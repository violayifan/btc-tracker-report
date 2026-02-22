#!/usr/bin/env python3
"""
重新计算交易统计（修复版）
只计算开平仓的交易，HOLD 阶段不算
"""

import json
import os
from datetime import datetime

# 路径配置
TRADES_FILE = "/root/.openclaw/workspace/btc_trades.json"
CLEAN_TRADES_FILE = "/root/.openclaw/workspace/btc_trades_corrected.json"
BACKTEST_REPORT_FILE = "/root/.openclaw/workspace/reports/btc_backtest_report_corrected.txt"


def load_trades():
    """加载交易记录"""
    with open(TRADES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def filter_signals(trades):
    """过滤出交易信号（排除 HOLD 和 WAIT）"""
    signals = []
    for trade in trades:
        action = trade.get('action', '')
        # 只保留开仓信号
        if action in ['LONG', 'SHORT', 'LONG_DIP', 'SHORT_DIP']:
            signals.append(trade)
    return signals


def calculate_completed_trades(signals, initial_capital=10000, position_size=0.1):
    """
    计算完整的开平仓交易
    
    规则：
    - LONG/SHORT 开仓
    - 只有在遇到相反信号、止盈或止损时才平仓
    - HOLD/WAIT 阶段不算交易
    """
    if not signals:
        return {
            "completed_trades": [],
            "final_capital": initial_capital
        }

    current_position = None  # 'LONG' or 'SHORT' or None
    entry_price = None
    entry_time = None
    current_capital = initial_capital
    capital_history = [(datetime.now(), initial_capital)]
    
    completed_trades = []
    
    for i, signal in enumerate(signals):
        action = signal.get('action', '')
        price = signal.get('price', 0)
        timestamp = signal.get('timestamp', '')
        datetime_str = signal.get('datetime', '')
        strategy = signal.get('strategy', '')
        stop_loss = signal.get('stop_loss')
        take_profit = signal.get('take_profit')
        
        # 检查止盈止损
        if current_position:
            # 有持仓的情况
            
            # 检查止损
            if stop_loss and price <= stop_loss:
                # 止损平仓
                if current_position == 'LONG':
                    pnl = (stop_loss - entry_price) / entry_price * current_capital * position_size
                else:  # SHORT
                    pnl = (entry_price - stop_loss) / entry_price * current_capital * position_size
                
                current_capital += pnl
                capital_history.append([datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S"), current_capital])
                
                completed_trades.append({
                    "entry_time": entry_time,
                    "exit_time": datetime_str,
                    "position": current_position,
                    "entry_price": entry_price,
                    "exit_price": stop_loss,
                    "exit_reason": "stop_loss",
                    "pnl": round(pnl, 2),
                    "capital": round(current_capital, 2),
                    "strategy": signal.get('strategy', '')
                })
                
                # 平仓
                current_position = None
                entry_price = None
                entry_time = None
                
            # 检查止盈
            elif take_profit and price >= take_profit:
                # 止盈平仓
                if current_position == 'LONG':
                    pnl = (take_profit - entry_price) / entry_price * current_capital * position_size
                else:  # SHORT
                    pnl = (entry_price - take_profit) / entry_price * current_capital * position_size
                
                current_capital += pnl
                capital_history.append([datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S"), current_capital])
                
                completed_trades.append({
                    "entry_time": entry_time,
                    "exit_time": datetime_str,
                    "position": current_position,
                    "entry_price": entry_price,
                    "exit_price": take_profit,
                    "exit_reason": "take_profit",
                    "pnl": round(pnl, 2),
                    "capital": round(current_capital, 2),
                    "strategy": signal.get('strategy', '')
                })
                
                # 平仓
                current_position = None
                entry_price = None
                entry_time = None
                
            # 检查反向信号（平仓）
            else:
                if action == 'LONG' and current_position == 'SHORT':
                    # 空头平多
                    pnl = (entry_price - price) / entry_price * current_capital * position_size
                    
                elif action == 'SHORT' and current_position == 'LONG':
                    # 多头平空
                    pnl = (price - entry_price) / entry_price * current_capital * position_size
                    
                else:
                    # 其他情况，继续持有
                    continue
                
                current_capital += pnl
                capital_history.append([datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S"), current_capital])
                
                completed_trades.append({
                    "entry_time": entry_time,
                    "exit_time": datetime_str,
                    "position": current_position,
                    "entry_price": entry_price,
                    "exit_price": price,
                    "exit_reason": "signal_reverse",
                    "pnl": round(pnl, 2),
                    "capital": round(current_capital, 2),
                    "strategy": signal.get('strategy', '')
                })
                
                # 平仓后立即开新仓
                if action in ['LONG', 'SHORT']:
                    current_position = action
                    entry_price = price
                    entry_time = datetime_str
                else:
                    current_position = None
                    entry_price = None
                    entry_time = None
        
        # 没有持仓的情况
        else:
            # 没有持仓，直接开仓
            if action in ['LONG', 'SHORT']:
                current_position = action
                entry_price = price
                entry_time = datetime_str
            
            # 其他信号（HOLD, WAIT 等）忽略
    
    return {
        "completed_trades": completed_trades,
        "final_capital": current_capital
    }


def calculate_metrics(completed_trades, initial_capital=10000):
    """计算回测指标"""
    if not completed_trades:
        return {}
    
    final_capital = completed_trades[-1]['capital'] if completed_trades else initial_capital
    
    # 总收益率
    total_return = ((final_capital - initial_capital) / initial_capital) * 100
    
    # 资金曲线
    capital_values = [t['capital'] for t in completed_trades]
    if not capital_values:
        capital_values = [initial_capital]
    
    # 最大净值和最小净值
    max_capital = max(capital_values) if capital_values else initial_capital
    min_capital = min(capital_values) if capital_values else initial_capital
    
    # 最大回撤
    max_drawdown_pct = 0
    for val in capital_values:
        if val > max_capital:
            max_capital = val
        if max_capital > 0:
            drawdown = (max_capital - val) / max_capital * 100
            if drawdown > max_drawdown_pct:
                max_drawdown_pct = drawdown
    
    # 回撤持续时间（简化）
    max_drawdown_duration = len(completed_trades) * 0.5  # 假设每笔交易平均0.5小时
    
    # 盈亏统计
    profit_trades = [t for t in completed_trades if t.get('pnl', 0) > 0]
    total_trades_count = len(completed_trades)
    win_count = len(profit_trades)
    win_rate = (win_count / total_trades_count) * 100 if total_trades_count > 0 else 0
    
    # 盈亏比
    total_profit = sum(t.get('pnl', 0) for t in profit_trades)
    total_loss = sum(abs(t.get('pnl', 0)) for t in completed_trades if t.get('pnl', 0) < 0)
    profit_loss_ratio = round(total_profit / abs(total_loss), 2) if total_loss != 0 else 0
    
    # 简化年化收益率
    annualized_return = total_return * 24 * 365  # 假设每小时更新
    
    # 夏普比率
    sharpe_ratio = round(total_return / max_drawdown_pct if max_drawdown_pct > 0 else 0, 4)
    
    return {
        "total_return": round(total_return, 2),
        "annualized_return": round(annualized_return, 2),
        "max_drawdown": round(max_drawdown_pct, 2),
        "max_drawdown_duration_hours": round(max_drawdown_duration, 2),
        "sharpe_ratio": sharpe_ratio,
        "total_trades": total_trades_count,
        "win_rate": round(win_rate, 2),
        "win_count": win_count,
        "initial_capital": initial_capital,
        "final_capital": round(final_capital, 2),
        "max_capital": max_capital,
        "min_capital": min_capital,
        "profit_loss_ratio": profit_loss_ratio,
        "capital_history": capital_values
    }


def generate_report(completed_trades, metrics):
    """生成回测报告"""
    report = f"""
========================================
📊 开平仓交易回测统计报告
========================================

📋 数据统计
----------------------------------------
  • 总信号数: {len(completed_trades)}
  • 完成交易数: {metrics.get('total_trades', 0)}
  • 初始资金: ${metrics.get('initial_capital', 0):,.2f}
  • 最终资金: ${metrics.get('final_capital', 0):,.2f}
  • 净值变化: ${metrics.get('final_capital', 0) - metrics.get('initial_capital', 0):,.2f}

========================================
📊 收益统计
----------------------------------------

  • 总收益率: {metrics.get('total_return', 0):.2f}%
  • 年化收益率: {metrics.get('annualized_return', 0):.2f}%
  • 最大回撤: {metrics.get('max_drawdown', 0):.2f}%
  • 回撤持续时间: {metrics.get('max_drawdown_duration_hours', 0):.2f} 小时
  • 夏普比率: {metrics.get('sharpe_ratio', 0):.4f}
  • 盈亏比: {metrics.get('profit_loss_ratio', 0):.2f}

========================================
🎯 交易统计
----------------------------------------

  • 总交易次数: {metrics.get('total_trades', 0)}
  • 盈利交易: {metrics.get('win_count', 0)}
  • 胜率: {metrics.get('win_rate', 0):.2f}%

========================================
💰 资金曲线
========================================

  • 最高净值: ${metrics.get('max_capital', 0):,.2f}
  • 最低净值: ${metrics.get('min_capital', 0):,.2f}

========================================
📝 交易明细（最近10笔）
========================================

"""
    
    # 添加最近的交易明细
    recent_trades = completed_trades[-10:]
    for i, trade in enumerate(recent_trades, 1):
        report += f"  {i}. {trade.get('entry_time', 'N/A')} 开 {trade.get('position', 'N/A')} @ ${trade.get('entry_price', 0):,.2f}\n"
        report += f"     {trade.get('exit_time', 'N/A')} 平 {trade.get('exit_reason', 'N/A')} @ ${trade.get('exit_price', 0):,.2f} | PnL: ${trade.get('pnl', 0):,.2f} | 资金: ${trade.get('capital', 0):,.2f}\n"
    
    if completed_trades:
        first_trade = completed_trades[0]
        last_trade = completed_trades[-1]
        report += f"\n========================================\n"
        report += f"⏰ 数据时间范围\n"
        report += f"========================================\n"
        report += f"  • 最早开仓: {first_trade.get('entry_time', 'N/A')}\n"
        report += f"  • 最新平仓: {last_trade.get('exit_time', 'N/A')}\n"
    
    report += f"\n========================================\n"
    report += f"✅ 重新计算完成！\n"
    report += f"⚠️  注意：只计算开平仓的交易，HOLD/WAIT 阶段不计入\n"
    report += f"========================================\n"

    return report


def main():
    """主函数"""
    print("="*70)
    print("📊 重新计算交易统计（开平仓逻辑）")
    print("="*70)
    print()
    
    # 1. 加载交易数据
    print("1️⃣ 加载交易数据...")
    trades = load_trades()
    print(f"   ✅ 总记录数: {len(trades)}")
    
    # 2. 过滤交易信号
    print()
    print("2️⃣ 过滤交易信号（排除 HOLD/WAIT）...")
    signals = filter_signals(trades)
    print(f"   ✅ 交易信号: {len(signals)}")
    
    # 3. 计算开平仓交易
    print()
    print("3️⃣ 计算开平仓交易...")
    result = calculate_completed_trades(signals)
    completed_trades = result['completed_trades']
    print(f"   ✅ 完成交易: {len(completed_trades)}")
    
    # 4. 保存修正后的交易记录
    print()
    print("4️⃣ 保存修正后的交易记录...")
    corrected_data = {
        "completed_trades": completed_trades,
        "final_capital": result['final_capital']
    }
    with open(CLEAN_TRADES_FILE, 'w', encoding='utf-8') as f:
        json.dump(corrected_data, f, indent=2, default=str, ensure_ascii=False)
    print(f"   ✅ 已保存: {CLEAN_TRADES_FILE}")
    
    # 5. 计算回测指标
    print()
    print("5️⃣ 计算回测指标...")
    metrics = calculate_metrics(completed_trades)
    print(f"   ✅ 总收益率: {metrics['total_return']:.2f}%")
    print(f"   ✅ 胜率: {metrics['win_rate']:.2f}%")
    print(f"   ✅ 盈亏比: {metrics['profit_loss_ratio']:.2f}")
    
    # 6. 生成报告
    print()
    print("6️⃣ 生成报告...")
    report = generate_report(completed_trades, metrics)
    
    # 7. 保存报告
    print()
    print("7️⃣ 保存报告...")
    os.makedirs(os.path.dirname(BACKTEST_REPORT_FILE), exist_ok=True)
    with open(BACKTEST_REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"   ✅ 已保存: {BACKTEST_REPORT_FILE}")
    
    print()
    print(report)
    
    print()
    print("="*70)
    print("✅ 重新计算完成！")
    print("="*70)
    print()
    print(f"💾 修正后的交易数据: {CLEAN_TRADES_FILE}")
    print(f"📄 回测统计报告: {BACKTEST_REPORT_FILE}")


if __name__ == "__main__":
    main()
