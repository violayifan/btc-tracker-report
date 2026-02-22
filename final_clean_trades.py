#!/usr/bin/env python3
"""
生成包含完整字段的清理后交易数据
确保包含 pnl 和 capital 字段
"""

import json
import os
from datetime import datetime

# 路径配置
TRADES_FILE = "/root/.openclaw/workspace/btc_trades.json"
CLEAN_TRADES_FILE = "/root/.openclaw/workspace/btc_trades_clean.json"


def load_trades():
    """加载交易记录"""
    with open(TRADES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def filter_and_enhance_trades(trades):
    """过滤测试数据并增强交易记录（添加 pnl 和 capital）"""
    real_trades = []
    test_trades = []

    # 简化的回测计算
    initial_capital = 10000
    current_capital = initial_capital

    for trade in trades:
        strategy = trade.get('strategy', '')
        action = trade.get('action', '')
        price = trade.get('price', 0)

        # 过滤测试数据
        if '测试' in strategy:
            test_trades.append(trade)
        else:
            # 计算 pnl
            if action in ['LONG', 'LONG_DIP']:
                # 做多：假设持有到下一个信号
                next_trade = None
                for t in trades:
                    if t['timestamp'] > trade['timestamp']:
                        next_trade = t
                        break

                if next_trade:
                    next_price = next_trade.get('price', price)
                    if next_price > price:
                        pnl = (next_price - price) / price * current_capital * 0.1
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

            else:
                # 等待策略（WAIT_PULLBACK, HOLD）
                pnl = 0

            # 更新资金
            current_capital += pnl

            # 增强交易记录
            trade['pnl'] = round(pnl, 2)
            trade['capital'] = round(current_capital, 2)
            trade['status'] = 'completed'

            real_trades.append(trade)

    return real_trades, test_trades


def calculate_metrics(trades):
    """计算回测指标"""
    if not trades:
        return {}

    # 提取资金曲线
    capital_values = [t.get('capital', 10000) for t in trades]
    initial_capital = capital_values[0] if capital_values else 10000
    final_capital = capital_values[-1] if capital_values else 10000

    # 总收益率
    total_return = ((final_capital - initial_capital) / initial_capital) * 100

    # 最大回撤
    max_drawdown_pct = 0
    for i, val in enumerate(capital_values):
        if i == 0:
            peak = val
        else:
            if val > peak:
                peak = val
            drawdown = (peak - val) / peak * 100
            if drawdown > max_drawdown_pct:
                max_drawdown_pct = drawdown

    # 盈利交易统计
    profit_trades = sum(1 for t in trades if t.get('pnl', 0) > 0)
    total_trades_count = len(trades)
    win_count = profit_trades
    win_rate = (win_count / total_trades_count) * 100 if total_trades_count > 0 else 0

    # 盈亏比
    gains = sum(t.get('pnl', 0) for t in trades if t.get('pnl', 0) > 0)
    losses = sum(abs(t.get('pnl', 0)) for t in trades if t.get('pnl', 0) < 0)
    profit_loss_ratio = round(gains / losses, 2) if losses > 0 else 0

    # 简化年化收益率
    annualized_return = total_return * 24 * 365

    # 简化夏普比率
    sharpe_ratio = round(total_return / max_drawdown_pct if max_drawdown_pct > 0 else 0, 4)

    return {
        "total_return": round(total_return, 2),
        "annualized_return": round(annualized_return, 2),
        "max_drawdown": round(max_drawdown_pct, 2),
        "sharpe_ratio": sharpe_ratio,
        "total_trades": total_trades_count,
        "win_rate": round(win_rate, 2),
        "win_count": win_count,
        "initial_capital": initial_capital,
        "final_capital": round(final_capital, 2),
        "max_capital": max(capital_values) if capital_values else initial_capital,
        "min_capital": min(capital_values) if capital_values else initial_capital,
        "profit_loss_ratio": profit_loss_ratio
    }


def generate_report(real_trades, test_trades, metrics):
    """生成报告"""
    report = f"""
========================================
交易数据清理与增强报告
========================================

📋 数据统计
----------------------------------------
  • 总交易数（原始）: {len(real_trades) + len(test_trades)}
  • 实际交易数: {len(real_trades)}
  • 测试数据: {len(test_trades)} (已排除）
  • 有效交易数: {len(real_trades)}

========================================
📈 回测指标（基于清理后的实际交易）
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
    report += f"✅ 数据清理与增强完成！回测统计仅基于 {len(real_trades)} 笔实际交易。\n"
    report += f"========================================\n"

    return report


def main():
    """主函数"""
    print("="*70)
    print("📊 交易数据清理与增强（完整字段版）")
    print("="*70)
    print()

    # 1. 加载交易数据
    print("1️⃣  加载交易数据...")
    trades = load_trades()
    print(f"   ✅ 总交易数: {len(trades)} 笔")

    # 2. 过滤并增强交易数据
    print()
    print("2️⃣  过滤测试数据并增强交易记录...")
    real_trades, test_trades = filter_and_enhance_trades(trades)
    print(f"   ✅ 实际交易: {len(real_trades)} 笔")
    print(f"   ✅ 测试数据: {len(test_trades)} 笔（已排除）")
    print(f"   ✅ 已添加 pnl 和 capital 字段")

    # 3. 保存清理后的交易数据
    print()
    print("3️⃣  保存清理后的交易数据...")
    with open(CLEAN_TRADES_FILE, 'w', encoding='utf-8') as f:
        json.dump(real_trades, f, indent=2, default=str, ensure_ascii=False)
    print(f"   ✅ 已保存: {CLEAN_TRADES_FILE}")

    # 4. 计算回测指标
    print()
    print("4️⃣  计算回测指标...")
    metrics = calculate_metrics(real_trades)
    print(f"   ✅ 盈亏比: {metrics['profit_loss_ratio']:.2f}")
    print(f"   ✅ 胜率: {metrics['win_rate']:.2f}%")
    print(f"   ✅ 夏普比率: {metrics['sharpe_ratio']:.4f}")

    # 5. 生成报告
    print()
    print("5️⃣  生成报告...")
    report = generate_report(real_trades, test_trades, metrics)

    # 6. 保存报告
    print()
    print("6️⃣  保存报告...")
    report_file = "/root/.openclaw/workspace/reports/btc_backtest_report_with_fields.txt"
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"   ✅ 已保存: {report_file}")

    print()
    print(report)

    print()
    print("="*70)
    print("✅ 交易数据清理与增强完成！")
    print("="*70)
    print()
    print(f"💾 清理后的交易数据: {CLEAN_TRADES_FILE}")
    print(f"📊 回测统计报告: {report_file}")
    print()
    print(f"💾 数据文件结构:")
    print(f"   • 包含完整的字段：timestamp, datetime, action, price")
    print(f"   • 增强字段：pnl, capital, status, stop_loss, take_profit, strategy")
    print()
    print(f"📈 关键指标:")
    print(f"   • 盈亏比: {metrics['profit_loss_ratio']:.2f}")
    print(f"   • 胜率: {metrics['win_rate']:.2f}%")
    print(f"   • 总收益率: {metrics['total_return']:.2f}%")


if __name__ == "__main__":
    main()
