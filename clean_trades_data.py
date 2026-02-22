#!/usr/bin/env python3
"""
交易数据清理与净值计算脚本（完全修复版）
排除测试数据，重新计算净值曲线和回测指标
"""

import json
import os
from datetime import datetime

# 路径配置
TRADES_FILE = "/root/.openclaw/workspace/btc_trades.json"
CLEAN_TRADES_FILE = "/root/.openclaw/workspace/btc_trades_clean.json"
BACKTEST_REPORT_FILE = "/root/.openclaw/workspace/reports/btc_backtest_report_clean.txt"


def load_trades():
    """加载交易记录"""
    with open(TRADES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def filter_test_data(trades):
    """过滤测试数据，保留实际交易"""
    real_trades = []
    test_trades = []

    for trade in trades:
        strategy = trade.get('strategy', '')
        if '测试' in strategy:
            test_trades.append(trade)
        else:
            real_trades.append(trade)

    return real_trades, test_trades


def calculate_backtest(trades, initial_capital=10000):
    """计算回测数据（净值曲线）"""
    if not trades:
        return {
            "capital_history": [],
            "final_capital": initial_capital
        }

    current_capital = initial_capital
    capital_history = [(datetime.now(), initial_capital)]

    for trade in trades:
        action = trade.get('action', '')
        price = trade.get('price', 0)

        # 简化的盈亏计算
        if action in ['LONG', 'LONG_DIP']:
            # 做多：假设持有到下一个信号
            next_trade = None
            # 找下一个交易
            for t in trades:
                if t['timestamp'] > trade['timestamp']:
                    next_trade = t
                    break

            if next_trade:
                next_price = next_trade.get('price', price)
                if next_price > price:
                    pnl = (next_price - price) / price * current_capital * 0.1  # 10% 仓位
                else:
                    pnl = (next_price - price) / price * current_capital * 0.1
            else:
                pnl = 0

        elif action == 'SHORT':
            # 做空
            next_trade = None
            for t in trades:
                if t['timestamp'] > trade['timestamp']:
                    next_trade = t
                    break

            if next_trade:
                next_price = next_trade.get('price', price)
                if next_price < price:
                    pnl = (price - next_price) / price * current_capital * 0.1
                else:
                    pnl = (price - next_price) / price * current_capital * 0.1
            else:
                pnl = 0

        # 等待策略（WAIT_PULLBACK, HOLD）
        else:
            pnl = 0

        # 更新资金
        current_capital += pnl
        capital_history.append([
            datetime.strptime(trade['datetime'], "%Y-%m-%d %H:%M:%S"),
            current_capital
        ])

        # 标记交易状态
        trade['status'] = 'completed'
        trade['pnl'] = pnl
        trade['capital'] = current_capital

    return {
        "capital_history": capital_history,
        "final_capital": current_capital
    }


def calculate_metrics(backtest_result):
    """计算回测指标"""
    capital_history = backtest_result.get('capital_history', [])
    if not capital_history:
        return {}

    values = [c[1] for c in capital_history]
    initial_capital = values[0]
    final_capital = values[-1]

    # 总收益率
    total_return = ((final_capital - initial_capital) / initial_capital) * 100

    # 最大净值和最小净值
    max_capital = max(values) if values else initial_capital
    min_capital = min(values) if values else initial_capital

    # 最大回撤
    max_drawdown_pct = 0
    for i, val in enumerate(values):
        if i == 0:
            peak = val
        else:
            if val > peak:
                peak = val
            drawdown = (peak - val) / peak * 100
            if drawdown > max_drawdown_pct:
                max_drawdown_pct = drawdown

    # 回撤持续时间
    max_drawdown_duration = 0
    current_drawdown_duration = 0
    for i, val in enumerate(values):
        if i == 0:
            peak = val
        else:
            if val >= peak:
                if current_drawdown_duration > max_drawdown_duration:
                    max_drawdown_duration = current_drawdown_duration
                current_drawdown_duration = 0
                peak = val
            else:
                current_drawdown_duration += 1

    # 盈利交易统计
    total_trades = len(values) - 1
    profit_trades = 0
    for i in range(1, len(values)):
        if values[i] > values[i-1]:
            profit_trades += 1
    
    total_trades_count = total_trades
    win_count = profit_trades
    win_rate = (win_count / total_trades_count) * 100 if total_trades_count > 0 else 0

    # 盈亏比
    gains = 0
    losses = 0
    for i in range(1, len(values)):
        change = values[i] - values[i-1]
        if change > 0:
            gains += change
        else:
            losses += abs(change)
    
    profit_loss_ratio = round(gains / losses, 2) if losses > 0 else 0

    # 简化年化收益率
    annualized_return = total_return * 24 * 365

    # 简化夏普比率
    sharpe_ratio = round(total_return / max_drawdown_pct if max_drawdown_pct > 0 else 0, 4)

    return {
        "total_return": round(total_return, 2),
        "annualized_return": round(annualized_return, 2),
        "max_drawdown": round(max_drawdown_pct, 2),
        "max_drawdown_duration_hours": max_drawdown_duration,
        "sharpe_ratio": sharpe_ratio,
        "total_trades": total_trades_count,
        "win_rate": round(win_rate, 2),
        "win_count": win_count,
        "initial_capital": initial_capital,
        "final_capital": round(final_capital, 2),
        "max_capital": max_capital,
        "min_capital": min_capital,
        "profit_loss_ratio": profit_loss_ratio
    }


def generate_backtest_report(metrics, real_trades, test_trades):
    """生成回测报告"""
    report = f"""
========================================
📊 清理后的回测统计报告
========================================

📋 数据统计
----------------------------------------
  • 总交易数（原始）: {len(real_trades) + len(test_trades)}
  • 实际交易数: {len(real_trades)}
  • 测试数据: {len(test_trades)} (已排除)
  • 有效交易数: {len(real_trades)}

========================================
📈 回测指标（仅基于实际交易）
========================================

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
========================================

  • 总交易次数: {metrics.get('total_trades', 0)}
  • 盈利交易: {metrics.get('win_count', 0)}
  • 胜率: {metrics.get('win_rate', 0):.2f}%

========================================
💰 资金曲线
========================================

  • 最高净值: ${metrics.get('max_capital', 0):,.2f}
  • 最低净值: ${metrics.get('min_capital', 0):,.2f}

========================================
⏰ 数据时间范围
========================================

"""

    if real_trades:
        first_trade = real_trades[0]
        last_trade = real_trades[-1]
        report += f"  • 最早交易: {first_trade.get('datetime', 'N/A')}\n"
        report += f"  • 最新交易: {last_trade.get('datetime', 'N/A')}\n"

    if test_trades:
        report += f"\n========================================\n"
        report += f"⚠️  已排除测试数据\n"
        report += f"========================================\n"
        report += f"  • 测试数据数量: {len(test_trades)} 笔\n"
        report += f"  • 测试数据时间: {test_trades[0].get('datetime', 'N/A')}\n"
        report += f"  • 说明: 测试数据不参与回测计算\n"

    report += f"\n========================================\n"
    report += f"✅ 清理完成！回测统计仅基于 {len(real_trades)} 笔实际交易。\n"
    report += f"========================================\n"

    return report


def main():
    """主函数"""
    print("="*70)
    print("📊 交易数据清理与净值计算")
    print("="*70)
    print()

    # 1. 加载交易数据
    print("1️⃣ 加载交易数据...")
    trades = load_trades()
    print(f"   ✅ 总交易数: {len(trades)} 笔")

    # 2. 过滤测试数据
    print()
    print("2️⃣ 过滤测试数据...")
    real_trades, test_trades = filter_test_data(trades)
    print(f"   ✅ 实际交易: {len(real_trades)} 笔")
    print(f"   ✅ 测试数据: {len(test_trades)} 笔（已排除）")

    # 3. 保存清理后的交易数据
    print()
    print("3️⃣ 保存清理后的交易数据...")
    with open(CLEAN_TRADES_FILE, 'w', encoding='utf-8') as f:
        json.dump(real_trades, f, indent=2, default=str, ensure_ascii=False)
    print(f"   ✅ 已保存: {CLEAN_TRADES_FILE}")

    # 4. 计算回测数据（净值曲线）
    print()
    print("4️⃣ 计算回测数据（净值曲线）...")
    backtest_result = calculate_backtest(real_trades)
    print(f"   ✅ 净值曲线: {len(backtest_result['capital_history'])} 个数据点")
    print(f"   ✅ 最终资金: ${backtest_result['final_capital']:,.2f}")

    # 5. 计算回测指标
    print()
    print("5️⃣ 计算回测指标...")
    metrics = calculate_metrics(backtest_result)
    print(f"   ✅ 总收益率: {metrics['total_return']:.2f}%")
    print(f"   ✅ 胜率: {metrics['win_rate']:.2f}%")
    print(f"   ✅ 夏普比率: {metrics['sharpe_ratio']:.4f}")

    # 6. 生成回测报告
    print()
    print("6️⃣ 生成回测报告...")
    report = generate_backtest_report(metrics, real_trades, test_trades)

    # 7. 保存回测报告
    print()
    print("7️⃣ 保存回测报告...")
    os.makedirs(os.path.dirname(BACKTEST_REPORT_FILE), exist_ok=True)
    with open(BACKTEST_REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"   ✅ 已保存: {BACKTEST_REPORT_FILE}")

    print()
    print(report)

    print()
    print("="*70)
    print("✅ 数据清理与净值计算完成！")
    print("="*70)
    print()
    print(f"💾 清理后的交易数据: {CLEAN_TRADES_FILE}")
    print(f"📄 回测统计报告: {BACKTEST_REPORT_FILE}")


if __name__ == "__main__":
    main()
