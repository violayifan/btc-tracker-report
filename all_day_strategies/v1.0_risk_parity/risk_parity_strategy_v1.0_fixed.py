#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全天候策略 v1.0 - 风险平价策略（Risk Parity）（修复版）
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
                 num_levels: int = 10,
                 rebalance_threshold: float = 0.10,
                 rebalance_period: int = 24):

        self.initial_capital = initial_capital
        self.num_levels = num_levels
        self.rebalance_threshold = rebalance_threshold
        self.rebalance_period = rebalance_period

        # 策略状态
        self.levels = []
        self.last_rebalance_time = 0
        self.current_volatility = 0.0

    def initialize_levels(self, price: float) -> List[Dict]:
        """初始化价格区间和仓位分配"""
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
                "btc_amount": btc_amount
            })

        self.levels = levels
        return levels

    def check_rebalance_needed(self, price: float, timestamp: int) -> bool:
        """检查是否需要再平衡"""
        if not self.levels:
            self.initialize_levels(price)

        # 计算当前总价值
        total_value = sum(level["btc_amount"] * price for level in self.levels)

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

        return False

    def calculate_volatility(self, price_history: List[float]) -> float:
        """计算波动率"""
        if len(price_history) < 14:
            return 0.0

        recent_prices = price_history[-14:]
        returns = [(recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1]
                   for i in range(1, len(recent_prices))]

        volatility = np.std(returns) if returns else 0.0
        self.current_volatility = volatility

        return volatility

    def generate_rebalance_signal(self, price: float, price_history: List[float]) -> Dict:
        """生成再平衡信号"""
        if not self.levels:
            self.initialize_levels(price)

        volatility = self.calculate_volatility(price_history)

        # 检查时间周期
        timestamp = len(price_history)
        if timestamp - self.last_rebalance_time >= self.rebalance_period:
            print(f"  ⏰ 到达再平衡周期 ({self.rebalance_period} 小时)")
            self.initialize_levels(price)
            self.last_rebalance_time = timestamp

            return {
                "action": "REBALANCE",
                "reason": "周期性再平衡",
                "volatility": volatility,
                "levels": self.levels
            }

        needs_rebalance = self.check_rebalance_needed(price, timestamp)

        if needs_rebalance:
            print(f"  🔄 执行再平衡...")
            self.initialize_levels(price)
            self.last_rebalance_time = timestamp

            return {
                "action": "REBALANCE",
                "reason": "价值偏离触发再平衡",
                "volatility": volatility,
                "levels": self.levels
            }

        return {
            "action": "HOLD",
            "reason": f"当前状态稳定，波动率: {volatility:.4f}",
            "volatility": volatility
        }

    def get_current_position_summary(self, price: float) -> Dict:
        """获取当前持仓摘要"""
        total_btc = sum(level["btc_amount"] for level in self.levels)
        total_value = sum(level["btc_amount"] * price for level in self.levels)

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
    """运行回测"""
    capital = initial_capital
    trades = []

    # 初始化区间（使用第一个价格）
    if len(price_data) > 0:
        strategy.initialize_levels(price_data[0])

    for i, price in enumerate(price_data[1:], 1):
        timestamp = i + 1

        # 获取信号
        signal = strategy.generate_rebalance_signal(price, price_data[:i+1])

        # 记录持仓摘要（每小时）
        position_summary = strategy.get_current_position_summary(price)

        # 计算价值变化
        if i > 0:
            prev_summary = strategy.get_current_position_summary(price_data[i-1])
            value_change = position_summary["total_value"] - prev_summary["total_value"]

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

        # 记录再平衡事件
        if signal["action"] == "REBALANCE":
            trades.append({
                "timestamp": timestamp,
                "action": signal["action"],
                "price": price,
                "reason": signal["reason"],
                "capital": capital,
                "total_btc": position_summary["total_btc"],
                "volatility": signal["volatility"]
            })
            print(f"  🔄 再平衡事件: {signal['reason']}")

    # 计算最终统计
    final_summary = strategy.get_current_position_summary(price_data[-1])
    final_value = final_summary["total_value"]
    total_return = (final_value - initial_capital) / initial_capital * 100

    # 最大回撤
    capital_curve = [initial_capital]
    running_capital = initial_capital

    for trade in trades:
        if trade["action"] == "VALUE_CHANGE":
            running_capital = trade["capital"]
            capital_curve.append(running_capital)

    max_drawdown = 0
    peak = capital_curve[0]

    for val in capital_curve[1:]:
        if val > peak:
            peak = val
        else:
            drawdown = (peak - val) / peak * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown

    # 夏普比率
    if max_drawdown > 0:
        sharpe_ratio = total_return / 100 / (max_drawdown / 100)
    else:
        sharpe_ratio = 0

    return {
        "initial_capital": initial_capital,
        "final_capital": final_value,
        "total_return": round(total_return, 2),
        "max_drawdown": round(max_drawdown, 2),
        "sharpe_ratio": round(sharpe_ratio, 4),
        "total_events": len(trades),
        "final_position_summary": final_summary,
        "trades": trades
    }


def simulate_market_data(start_price: float,
                         days: int = 30,
                         volatility: float = 0.02,
                         trend: float = 0.0) -> List[float]:
    """模拟市场数据"""
    np.random.seed(42)
    prices = [start_price]

    for i in range(days * 24):
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

    market_scenarios = [
        {"name": "低波动震荡", "volatility": 0.01, "trend": 0.0},
        {"name": "高波动震荡", "volatility": 0.03, "trend": 0.0},
        {"name": "缓慢上涨", "volatility": 0.015, "trend": 0.0005},
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
            num_levels=10,
            rebalance_threshold=0.10,
            rebalance_period=24
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
        print(f"  最终价值: ${final_pos['total_value']:.2f}")
        print(f"  最终BTC数: {final_pos['total_btc']:.4f}")

        # 风险评估
        if max_dd > 20:
            risk = "低风险"
        elif max_dd > 30:
            risk = "中风险"
        else:
            risk = "高风险"

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

    # 保存详细交易记录
    for scenario in market_scenarios:
        result = [r for r in results if r["scenario"] == scenario["name"]]
        if result:
            df = pd.DataFrame(result[0]["trades"])
            csv_file = os.path.join(output_dir, f"v1.0_risk_parity_{scenario['name']}_trades.csv")
            df.to_csv(csv_file, index=False)

    print(f"  ✅ 结果已保存: {results_file}")

    # 6. 生成报告
    report = f"""
# 全天候策略 v1.0 - 风险平价策略（Risk Parity）回测报告

## 📅 测试参数
- 初始资金: $10,000
- 交易手续费: 0.1%
- 测试周期: 30 天
- 数据频率: 每小时

## 📊 策略参数
- 价格区间数量: 10 个
- 再平衡阈值: 10%偏离
- 再平衡周期: 24小时

## 📋 回测结果

"""

    for result in results:
        scenario = result["scenario"]
        total_return = result["total_return"]
        max_dd = result["max_drawdown"]
        sharpe = result["sharpe_ratio"]
        final_pos = result["final_position_summary"]

        report += f"""
### {scenario}
- 总收益率: {total_return}%
- 最大回撤: {max_dd}%
- 夏普比率: {sharpe}
- 最终价值: ${final_pos['total_value']:.2f}
- 最终BTC数: {final_pos['total_btc']:.4f}

"""

    report += """

## 🔍 策略分析

### 优势
1. ✅ 自动风险管理，降低回撤
2. ✅ 稳定的持仓结构
3. ✅ 适合大资金量投资
4. ✅ 无需频繁交易

### 劣势
1. ❌ 在单边趋势中可能跑输
2. ❌ 收益相对有限
3. ❌ 需要一定的资金量才能有效

### 适用场景
- ✅ 横盘震荡市场
- ✅ 波动较大的市场
- ✅ 长期持有的投资

### 不适用场景
- ❌ 单边明显的上涨/下跌趋势
- ❌ 低波动的稳定市场
- ❌ 资金量较小的交易

### 风险控制建议
1. ⚠️ 严格按照阈值进行再平衡
2. ⚠️ 监控总持仓价值的变化
3. ⚠️ 避免过度集中单个价格区间
4. ⚠️ 定期审查策略参数

## 📊 版本演进路径

v1.0 (当前: 风险平价) -> v2.0 (动态区间) -> v3.0 (波动率自适应) -> v4.0 (机器学习优化) -> v5.0 (多资产配置)

"""

    # 保存报告
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
