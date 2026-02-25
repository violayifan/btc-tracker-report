#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全天候策略 v1.0 - 经典马丁格尔策略
作者: 策略研究团队
日期: 2026-02-25
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
import json
import os
import sys

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MartingaleStrategy:
    """经典马丁格尔策略实现"""

    def __init__(self,
                 initial_position: float = 0.001,  # 初始仓位（BTC 数量）
                 multiplier: float = 2.0,            # 加倍倍数
                 max_positions: int = 10,          # 最大开仓次数
                 stop_loss_pct: float = 0.05,     # 止损百分比（5%）
                 take_profit_pct: float = 0.01):   # 止盈百分比（1%）

        self.initial_position = initial_position
        self.multiplier = multiplier
        self.max_positions = max_positions
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct

        # 状态变量
        self.position_count = 0
        self.current_position = initial_position
        self.entry_price = 0.0
        self.stop_loss_price = 0.0
        self.take_profit_price = 0.0

    def generate_signal(self, price_history: List[float]) -> Dict:
        """
        生成交易信号

        Args:
            price_history: 历史价格数据

        Returns:
            信号字典，包含 action, position_size, reason 等
        """
        if not price_history or len(price_history) < 2:
            return {"action": "HOLD", "position_size": 0, "reason": "数据不足"}

        current_price = price_history[-1]

        # 第一次开仓
        if self.position_count == 0:
            self.entry_price = current_price
            self.stop_loss_price = current_price * (1 - self.stop_loss_pct)
            self.take_profit_price = current_price * (1 + self.take_profit_pct)

            self.position_count = 1
            self.current_position = self.initial_position

            return {
                "action": "BUY",
                "position_size": self.current_position,
                "entry_price": self.entry_price,
                "stop_loss": self.stop_loss_price,
                "take_profit": self.take_profit_price,
                "reason": f"首次开仓 - 马丁格尔第 1 单"
            }

        # 检查是否需要平仓（止盈或止损）
        if self.current_price < self.stop_loss_price or self.current_price > self.take_profit_price:
            # 平仓
            return self.close_position(current_price, reason="止盈/止损平仓")

        # 检查是否上一次是亏损
        last_price = price_history[-2]
        is_last_loss = last_price < self.entry_price

        if is_last_loss:
            # 亏损了，增加仓位（马丁格尔逻辑）
            if self.position_count >= self.max_positions:
                return {"action": "HOLD", "position_size": 0, "reason": "超过最大开仓次数"}

            self.position_count += 1
            new_position = self.initial_position * (self.multiplier ** (self.position_count - 1))
            self.current_position += new_position

            return {
                "action": "BUY",
                "position_size": new_position,
                "entry_price": self.entry_price,
                "stop_loss": self.stop_loss_price,
                "take_profit": self.take_profit_price,
                "reason": f"马丁格尔加仓 - 第 {self.position_count} 单"
            }
        else:
            # 盈利了，重置到初始仓位
            return self.close_position(current_price, reason="盈利平仓，重置仓位")

    def close_position(self, current_price: float, reason: str) -> Dict:
        """平仓"""
        total_pnl = 0.0

        # 计算盈亏
        if self.entry_price > 0:
            # 做多
            if current_price > self.entry_price:
                total_pnl = (current_price - self.entry_price) / self.entry_price
            else:
                total_pnl = (current_price - self.entry_price) / self.entry_price

        # 重置
        self.position_count = 0
        self.current_position = self.initial_position
        self.entry_price = 0.0
        self.stop_loss_price = 0.0
        self.take_profit_price = 0.0

        return {
            "action": "CLOSE",
            "position_size": 0,
            "exit_price": current_price,
            "pnl_pct": total_pnl * 100,
            "reason": reason
        }


def run_backtest(price_data: List[float],
                strategy: MartingaleStrategy,
                initial_capital: float = 10000.0,
                trading_fee: float = 0.001) -> Dict:
    """
    运行回测

    Args:
        price_data: 价格数据列表
        strategy: 策略实例
        initial_capital: 初始资金
        trading_fee: 交易手续费（0.1%）

    Returns:
        回测结果字典
    """
    capital = initial_capital
    trades = []
    position = None  # 当前持仓 {'entry_price': float, 'size': float}

    for i, price in enumerate(price_data[1:], 1):
        if not position:
            # 没有持仓，生成信号
            signal = strategy.generate_signal(price_data[:i+1])

            if signal["action"] == "BUY":
                # 开仓
                position = {
                    "entry_price": signal["entry_price"],
                    "size": signal["position_size"] * capital / price  # 按资金比例开仓
                }
                trades.append({
                    "timestamp": i,
                    "action": "BUY",
                    "price": signal["entry_price"],
                    "size": signal["position_size"],
                    "reason": signal["reason"]
                })
            elif signal["action"] == "CLOSE":
                # 无持仓时的平仓信号，忽略
                pass
        else:
            # 有持仓
            # 检查止盈止损
            stop_loss = position["entry_price"] * (1 - strategy.stop_loss_pct)
            take_profit = position["entry_price"] * (1 + strategy.take_profit_pct)

            if price <= stop_loss or price >= take_profit:
                # 平仓
                if price >= take_profit:
                    pnl = (price - position["entry_price"]) / position["entry_price"]
                    pnl_pct = pnl * 100
                else:
                    pnl = (price - position["entry_price"]) / position["entry_price"]
                    pnl_pct = pnl * 100

                # 扣除手续费
                pnl_after_fee = pnl - trading_fee

                capital *= (1 + pnl_after_fee)

                trades.append({
                    "timestamp": i,
                    "action": "CLOSE",
                    "price": price,
                    "pnl": pnl_pct,
                    "capital": capital,
                    "reason": "止盈/止损平仓"
                })

                position = None

    # 计算最终统计
    total_trades = len([t for t in trades if t["action"] == "CLOSE"])
    winning_trades = len([t for t in trades if t["action"] == "CLOSE" and t["pnl"] > 0])
    losing_trades = len([t for t in trades if t["action"] == "CLOSE" and t["pnl"] < 0])

    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

    total_return = (capital - initial_capital) / initial_capital * 100

    # 最大回撤
    capital_curve = [initial_capital]
    for trade in trades:
        if trade["action"] == "CLOSE":
            capital_curve.append(trade["capital"])

    max_drawdown = 0
    peak = capital_curve[0]

    for val in capital_curve[1:]:
        if val > peak:
            peak = val
        else:
            drawdown = (peak - val) / peak * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown

    # 夏普比率（简化）
    if max_drawdown > 0:
        sharpe_ratio = total_return / 100 / (max_drawdown / 100)  # 简化计算
    else:
        sharpe_ratio = 0

    return {
        "initial_capital": initial_capital,
        "final_capital": capital,
        "total_return": round(total_return, 2),
        "total_trades": total_trades,
        "winning_trades": winning_trades,
        "losing_trades": losing_trades,
        "win_rate": round(win_rate, 2),
        "max_drawdown": round(max_drawdown, 2),
        "sharpe_ratio": round(sharpe_ratio, 4),
        "trades": trades
    }


def simulate_market_data(start_price: float,
                         days: int = 30,
                         volatility: float = 0.02,
                         trend: float = 0.0) -> List[float]:
    """
    模拟市场数据

    Args:
        start_price: 起始价格
        days: 天数
        volatility: 波动率
        trend: 趋势（正数上涨，负数下跌）

    Returns:
        价格列表
    """
    np.random.seed(42)
    prices = [start_price]

    for i in range(days * 24):  # 每天24个数据点（每小时）
        # 随机游走
        change = np.random.normal(trend / 24, volatility / np.sqrt(24))
        new_price = prices[-1] * (1 + change)
        prices.append(new_price)

    return prices


def main():
    """主函数"""

    print("=" * 60)
    print("🎯 全天候策略 v1.0 - 经典马丁格尔策略")
    print("=" * 60)
    print()

    # 1. 生成模拟市场数据
    print("📊 [1/5] 生成模拟市场数据...")

    # 模拟不同的市场环境
    market_scenarios = [
        {"name": "震荡市场", "trend": 0.0, "volatility": 0.02},
        {"name": "震荡上涨", "trend": 0.0005, "volatility": 0.02},
        {"name": "震荡下跌", "trend": -0.0005, "volatility": 0.02},
        {"name": "单边上涨", "trend": 0.001, "volatility": 0.015},
        {"name": "单边下跌", "trend": -0.001, "volatility": 0.015},
    ]

    results = []

    for scenario in market_scenarios:
        print(f"  📈 测试市场环境: {scenario['name']}")

        prices = simulate_market_data(
            start_price=65000.0,
            days=30,
            volatility=scenario["volatility"],
            trend=scenario["trend"]
        )

        # 2. 初始化策略
        strategy = MartingaleStrategy(
            initial_position=0.0005,
            multiplier=2.0,
            max_positions=10,
            stop_loss_pct=0.05,
            take_profit_pct=0.01
        )

        # 3. 运行回测
        print(f"  🔄 运行回测...")

        backtest_result = run_backtest(
            price_data=prices,
            strategy=strategy,
            initial_capital=10000.0,
            trading_fee=0.001
        )

        results.append({
            "scenario": scenario["name"],
            "total_return": backtest_result["total_return"],
            "win_rate": backtest_result["win_rate"],
            "max_drawdown": backtest_result["max_drawdown"],
            "sharpe_ratio": backtest_result["sharpe_ratio"],
            "total_trades": backtest_result["total_trades"],
            "final_capital": backtest_result["final_capital"]
        })

        print(f"  ✅ 总收益率: {backtest_result['total_return']}%")
        print(f"  ✅ 胜率: {backtest_result['win_rate']}%")
        print(f"  ✅ 最大回撤: {backtest_result['max_drawdown']}%")
        print()

    # 4. 输出总结
    print("=" * 60)
    print("📋 回测总结")
    print("=" * 60)

    for result in results:
        scenario = result["scenario"]
        total_return = result["total_return"]
        win_rate = result["win_rate"]
        max_dd = result["max_drawdown"]
        sharpe = result["sharpe_ratio"]

        print(f"\n市场环境: {scenario}")
        print(f"  总收益率: {total_return}%")
        print(f"  胜率: {win_rate}%")
        print(f"  最大回撤: {max_dd}%")
        print(f"  夏普比率: {sharpe}")

        # 风险评估
        if max_dd > 50:
            risk = "高风险"
        elif max_dd > 30:
            risk = "中风险"
        else:
            risk = "低风险"

        print(f"  风险评级: {risk}")

    # 5. 保存结果
    print()
    print("💾 [5/5] 保存回测结果...")

    output_dir = "/root/.openclaw/workspace/all_day_strategies/backtest_results"
    os.makedirs(output_dir, exist_ok=True)

    # 保存 JSON 结果
    results_file = os.path.join(output_dir, "v1_martingale_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    # 保存详细交易记录
    for scenario in market_scenarios:
        trades = [t for t in results if t["scenario"] == scenario["name"]]

        if trades:
            df = pd.DataFrame(trades[0]["trades"]) if trades[0]["trades"] else pd.DataFrame()
            csv_file = os.path.join(output_dir, f"v1_martingale_{scenario['name']}_trades.csv")
            df.to_csv(csv_file, index=False)

    print(f"  ✅ 结果已保存: {results_file}")

    # 6. 生成报告
    report = f"""
# 全天候策略 v1.0 - 经典马丁格尔策略回测报告

## 📅 测试参数
- 初始资金: $10,000
- 交易手续费: 0.1%
- 测试周期: 30 天
- 数据频率: 每小时

## 📊 策略参数
- 初始仓位: 0.0005 BTC
- 加倍倍数: 2.0x
- 最大开仓次数: 10 次
- 止损百分比: 5%
- 止盈百分比: 1%

## 📋 回测结果

"""

    for result in results:
        scenario = result["scenario"]
        total_return = result["total_return"]
        win_rate = result["win_rate"]
        max_dd = result["max_drawdown"]
        sharpe = result["sharpe_ratio"]

        report += f"""
### {scenario}
- 总收益率: {total_return}%
- 胜率: {win_rate}%
- 最大回撤: {max_dd}%
- 夏普比率: {sharpe}

"""

    report += """

## 🔍 策略分析

### 优势
1. ✅ 逻辑简单，易于理解和实现
2. ✅ 在震荡市场中能快速回本
3. ✅ 不需要复杂的技术分析

### 劣势
1. ❌ 资金需求呈指数增长，容易爆仓
2. ❌ 在单边趋势市场容易连续亏损
3. ❌ 长期来看是负期望值策略
4. ❌ 心理压力大，容易情绪化交易

### 适用场景
- ✅ 横盘震荡市场（短期内）
- ✅ 资金充足且能承受高风险
- ✅ 严格执行止损的情况下

### 不适用场景
- ❌ 长期持有的投资
- ❌ 资金有限的交易者
- ❌ 没有设置止损的交易
- ❌ 单边趋势明显的市场

### 风险控制建议
1. ⚠️ 必须设置硬止损，避免无限加仓
2. ⚠️ 限制最大开仓次数，防止爆仓
3. ⚠️ 不要用全部资金做马丁格尔
4. ⚠️ 严格执行止盈止损，不要情绪化
5. ⚠️ 做好资金管理，保留备用金

## 📊 版本演进路径

v1.0 (当前) -> v2.0 (网格) -> v3.0 (斐波那契) -> v4.0 (动态马丁) -> v5.0 (三层网格) -> v6.0 (RSI网格) -> v7.0 (机器学习) -> v8.0 (波动率自适应) -> v9.0 (多时间框架)

"""

    # 保存报告
    report_file = os.path.join(output_dir, "v1_martingale_report.md")
    with open(report_file, 'w') as f:
        f.write(report)

    print(f"  ✅ 报告已保存: {report_file}")

    print()
    print("=" * 60)
    print("✅ v1.0 马丁格尔策略回测完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
