#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全天候策略 v1.0 - 风险平价策略（Risk Parity）
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

class RiskParityStrategy:
    """风险平价策略实现"""

    def __init__(self,
                 initial_capital: float = 10000.0,
                 num_levels: int = 10,            # 价格区间数量
                 rebalance_threshold: float = 0.10,  # 再平衡阈值（10%）
                 rebalance_period: int = 24,      # 再平衡周期（24小时）
                 volatility_period: int = 14):      # 波动率计算周期

        self.initial_capital = initial_capital
        self.num_levels = num_levels
        self.rebalance_threshold = rebalance_threshold
        self.rebalance_period = rebalance_period
        self.volatility_period = volatility_period

        # 策略状态
        self.levels = []
        self.last_rebalance_time = 0
        self.current_volatility = 0.0

    def initialize_levels(self, price: float) -> List[Dict]:
        """
        初始化价格区间和仓位分配

        Args:
            price: 当前价格

        Returns:
            价格区间列表
        """
        levels = []

        # 定义价格区间范围（当前价格 ± 20%）
        min_price = price * 0.8
        max_price = price * 1.2
        range_size = (max_price - min_price) / self.num_levels

        for i in range(self.num_levels):
            lower_bound = min_price + i * range_size
            upper_bound = min_price + (i + 1) * range_size
            mid_price = (lower_bound + upper_bound) / 2

            # 计算该区间分配的资金
            level_capital = self.initial_capital / self.num_levels

            # 计算该区间的 BTC 数量
            btc_amount = level_capital / mid_price

            levels.append({
                "level": i + 1,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "mid_price": mid_price,
                "capital": level_capital,
                "btc_amount": btc_amount,
                "target_value": level_capital  # 目标价值（应该等于 btc_amount * mid_price）
            })

        self.levels = levels
        return levels

    def check_rebalance_needed(self, price: float, timestamp: int) -> bool:
        """
        检查是否需要再平衡

        Args:
            price: 当前价格
            timestamp: 时间戳

        Returns:
            是否需要再平衡
        """
        # 1. 检查时间周期
        if timestamp - self.last_rebalance_time >= self.rebalance_period:
            print(f"  ⏰ 到达再平衡周期 ({self.rebalance_period} 小时)")
            return True

        # 2. 检查偏离度
        total_value = 0.0
        for level in self.levels:
            total_value += level["btc_amount"] * price

        # 计算每个区间的实际价值
        level_values = [level["btc_amount"] * price for level in self.levels]

        # 计算偏离度（标准差 / 平均值）
        avg_value = sum(level_values) / len(level_values)
        std_dev = np.std(level_values)
        deviation = std_dev / avg_value if avg_value > 0 else 0

        print(f"  📊 价值偏离度: {deviation:.2%} (阈值: {self.rebalance_threshold * 100:.1f}%)")

        if deviation > self.rebalance_threshold:
            print(f"  ⚠️ 价值偏离超过阈值，需要再平衡")
            return True

        # 3. 检查单区间偏离
        for level in self.levels:
            actual_value = level["btc_amount"] * price
            target_value = level["target_value"]
            deviation_pct = abs(actual_value - target_value) / target_value

            if deviation_pct > self.rebalance_threshold:
                print(f"  ⚠️ 区间 {level['level']} 偏离: {deviation_pct:.2%}，需要再平衡")
                return True

        return False

    def calculate_volatility(self, price_history: List[float]) -> float:
        """
        计算波动率（简化版）

        Args:
            price_history: 历史价格

        Returns:
            波动率
        """
        if len(price_history) < self.volatility_period:
            return 0.0

        recent_prices = price_history[-self.volatility_period:]
        returns = [(recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1]
                   for i in range(1, len(recent_prices))]

        # 计算波动率（标准差）
        volatility = np.std(returns) if returns else 0.0
        self.current_volatility = volatility

        return volatility

    def generate_rebalance_signal(self, price: float, price_history: List[float]) -> Dict:
        """
        生成再平衡信号

        Args:
            price: 当前价格
            price_history: 历史价格

        Returns:
            信号字典
        """
        # 如果还没有初始化区间，先初始化
        if not self.levels:
            self.initialize_levels(price)

        # 计算当前波动率
        volatility = self.calculate_volatility(price_history)

        # 检查是否需要再平衡
        timestamp = len(price_history)
        needs_rebalance = self.check_rebalance_needed(price, timestamp)

        if needs_rebalance:
            # 执行再平衡：重新初始化所有区间
            print(f"  🔄 执行再平衡...")
            self.initialize_levels(price)
            self.last_rebalance_time = timestamp

            return {
                "action": "REBALANCE",
                "reason": "触发再平衡",
                "volatility": volatility,
                "levels": self.levels
            }

        return {
            "action": "HOLD",
            "reason": f"当前价格区间稳定，波动率: {volatility:.4f}",
            "volatility": volatility
        }

    def get_current_position_summary(self) -> Dict:
        """获取当前持仓摘要"""
        total_btc = sum(level["btc_amount"] for level in self.levels)
        total_value = sum(level["btc_amount"] * level["mid_price"] for level in self.levels)

        return {
            "total_btc": total_btc,
            "total_value": total_value,
            "num_levels": len(self.levels),
            "avg_price": total_value / total_btc if total_btc > 0 else 0,
            "capital_efficiency": (total_value / self.initial_capital * 100) if self.initial_capital > 0 else 0
        }


def run_backtest(price_data: List[float],
                strategy: RiskParityStrategy,
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

    # 初始化区间（使用第一个价格）
    if len(price_data) > 0:
        strategy.initialize_levels(price_data[0])

    # 模拟交易（每24小时检查一次再平衡）
    for i, price in enumerate(price_data[1:], 1):
        # 记录时间戳（小时）
        timestamp = i + 1

        # 获取当前持仓摘要
        position_summary = strategy.get_current_position_summary()

        # 计算当前总价值
        current_total_value = position_summary["total_value"]

        # 计算相对于上一小时的价值变化
        if i > 0:
            prev_summary = strategy.get_current_position_summary()
            prev_total_value = prev_summary["total_value"]
            value_change = current_total_value - prev_total_value

            # 记录收益（如果正数）
            if value_change > 0:
                capital += value_change

                trades.append({
                    "timestamp": timestamp,
                    "action": "VALUE_CHANGE",
                    "price": price,
                    "value_change": value_change,
                    "capital": capital,
                    "total_btc": position_summary["total_btc"]
                })
                print(f"  💰 价格变动收益: +{value_change:.2f}, 资金: ${capital:.2f}")

        # 检查是否需要再平衡（每24小时）
        signal = strategy.generate_rebalance_signal(price, price_data[:i+1])

        if signal["action"] == "REBALANCE":
            # 记录再平衡事件
            trades.append({
                "timestamp": timestamp,
                "action": signal["action"],
                "price": price,
                "reason": signal["reason"],
                "volatility": signal["volatility"],
                "capital": capital
            })
            print(f"  🔄 再平衡完成，资金: ${capital:.2f}")

    # 计算最终统计
    total_value = sum(level["btc_amount"] * price for level in strategy.levels)
    total_return = (total_value - initial_capital) / initial_capital * 100

    # 最大回撤
    capital_curve = []
    running_capital = initial_capital

    for trade in trades:
        if trade["action"] == "VALUE_CHANGE":
            running_capital = trade["capital"]
            capital_curve.append(running_capital)

    max_drawdown = 0
    peak = capital_curve[0] if capital_curve else initial_capital

    for val in capital_curve[1:]:
        if val > peak:
            peak = val
        else:
            drawdown = (peak - val) / peak * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown

    # 夏普比率（简化）
    sharpe_ratio = total_return / 100 / (max_drawdown / 100) if max_drawdown > 0 else 0

    return {
        "initial_capital": initial_capital,
        "final_capital": total_value,
        "total_return": round(total_return, 2),
        "max_drawdown": round(max_drawdown, 2),
        "sharpe_ratio": round(sharpe_ratio, 4),
        "total_events": len(trades),
        "final_position_summary": strategy.get_current_position_summary(),
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
    print("🎯 全天候策略 v1.0 - 风险平价策略（Risk Parity）")
    print("=" * 60)
    print()

    # 1. 生成模拟市场数据
    print("📊 [1/5] 生成模拟市场数据...")

    # 模拟不同的市场环境
    market_scenarios = [
        {"name": "低波动震荡", "volatility": 0.01, "trend": 0.0},
        {"name": "高波动震荡", "volatility": 0.03, "trend": 0.0},
        {"name": "缓慢上涨", "volatility": 0.015, "trend": 0.0003},
        {"name": "缓慢下跌", "volatility": 0.015, "trend": -0.0003},
        {"name": "剧烈波动", "volatility": 0.05, "trend": 0.0},
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
        print(f"  🎯 初始化风险平价策略...")
        strategy = RiskParityStrategy(
            initial_capital=10000.0,
            num_levels=10,           # 10个价格区间
            rebalance_threshold=0.10,  # 10%偏离阈值
            rebalance_period=24,        # 每24小时再平衡
            volatility_period=14
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
            "max_drawdown": backtest_result["max_drawdown"],
            "sharpe_ratio": backtest_result["sharpe_ratio"],
            "total_events": backtest_result["total_events"],
            "final_capital": backtest_result["final_capital"],
            "final_position_summary": backtest_result["final_position_summary"]
        })

        print(f"  ✅ 总收益率: {backtest_result['total_return']}%")
        print(f"  ✅ 最大回撤: {backtest_result['max_drawdown']}%")
        print(f"  ✅ 夏普比率: {backtest_result['sharpe_ratio']}")
        print(f"  ✅ 最终价值: ${backtest_result['final_capital']:.2f}")
        print()

    # 4. 输出总结
    print("=" * 60)
    print("📋 回测总结")
    print("=" * 60)

    for result in results:
        scenario = result["scenario"]
        total_return = result["total_return"]
        max_dd = result["max_drawdown"]
        sharpe = result["sharpe_ratio"]
        final_pos = result["final_position_summary"]

        print(f"\n市场环境: {scenario}")
        print(f"  总收益率: {total_return}%")
        print(f"  最大回撤: {max_dd}%")
        print(f"  夏普比率: {sharpe}")
        print(f"  最终持仓价值: ${final_pos['total_value']:.2f}")
        print(f"  总 BTC 数量: {final_pos['total_btc']:.4f}")
        print(f"  资金效率: {final_pos['capital_efficiency']:.1f}%")

        # 风险评估
        if max_dd > 20:
            risk = "低风险"
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
    results_file = os.path.join(output_dir, "v1.0_risk_parity_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"  ✅ 结果已保存: {results_file}")

    # 保存详细交易记录
    for scenario in market_scenarios:
        trades = [t for t in results if t["scenario"] == scenario["name"]][0]["trades"]]

        if trades:
            df = pd.DataFrame(trades)
            csv_file = os.path.join(output_dir, f"v1.0_risk_parity_{scenario['name']}_trades.csv")
            df.to_csv(csv_file, index=False)

    # 6. 生成策略文档
    report = f"""
# 全天候策略 v1.0 - 风险平价策略（Risk Parity）

## 📅 策略说明

### 核心思想
风险平价是一种投资组合管理策略，通过在不同价格区间分配资金，使每个价格区间的仓位价值相等。

### 基本原理
1. **区间划分**: 将价格范围分成多个区间
2. **等值分配**: 每个区间分配相同的资金价值
3. **动态调整**: 价格变化时自动调整仓位
4. **风险对冲**: 价格波动时自动低买高卖，降低风险

### 优势
1. ✅ 降低整体波动
2. ✅ 减少回撤
3. ✅ 稳定收益
4. ✅ 适合大资金量
5. ✅ 自动化风险管理

### 劣势
1. ❌ 在单边趋势中跑输简单持有
2. ❌ 需要频繁再平衡
3. ❌ 交易成本较高

## 🎯 策略参数
- 初始资金: $10,000
- 价格区间数量: 10 个
- 再平衡阈值: 10%偏离
- 再平衡周期: 24小时
- 波动率计算周期: 14小时

## 📊 回测结果

"""

    for result in results:
        scenario = result["scenario"]
        total_return = result["total_return"]
        max_dd = result["max_drawdown"]
        sharpe = result["sharpe_ratio"]

        report += f"""
### {scenario}
- 总收益率: {total_return}%
- 最大回撤: {max_dd}%
- 夏普比率: {sharpe}

"""

    report += """

## 🔍 策略分析

### 适用场景
- ✅ 横盘震荡市场
- ✅ 波动较大的市场
- ✅ 长期持有策略
- ✅ 大资金量投资

### 不适用场景
- ❌ 单边上涨市场（会跑输）
- ❌ 单边下跌市场（会跑输）
- ❌ 低波动稳定市场（收益低）

### 优化方向
1. 动态区间数量（根据波动率调整）
2. 智能再平衡（根据偏离度触发）
3. 多时间框架（短中长期结合）
4. 机器学习辅助（预测最佳再平衡时机）

## 📁 文件结构
/all_day_strategies/
  /v1.0_risk_parity/
  /v1.0_risk_parity/risk_parity_strategy.py
  /backtest_results/
  /docs/

"""

    report_file = os.path.join(output_dir, "v1.0_risk_parity_report.md")
    with open(report_file, 'w') as f:
        f.write(report)

    print(f"  ✅ 报告已保存: {report_file}")

    print()
    print("=" * 60)
    print("✅ v1.0 风险平价策略回测完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
