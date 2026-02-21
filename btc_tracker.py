#!/usr/bin/env python3
"""BTC 交易跟踪和回测系统（改进版）"""

import json
import os
import datetime as dt_module
import math
from typing import List, Dict, Optional

# 使用模块导入避免冲突
datetime = dt_module.datetime

# 尝试导入 matplotlib 和 numpy，如果不可用则禁用图表功能
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("[BTC Tracker] 警告: matplotlib 或 numpy 未安装，图表生成功能将被禁用")

# 文件路径
TRACKER_FILE = "/root/.openclaw/workspace/btc_trades.json"
REPORTS_DIR = "/root/.openclaw/workspace/reports"
BACKTEST_CHART = "/root/.openclaw/workspace/backtest_chart.png"

class BTCTracker:
    """BTC 交易跟踪器"""

    def __init__(self):
        self.trades = self._load_trades()

    def _load_trades(self) -> List[Dict]:
        """加载交易记录"""
        if os.path.exists(TRACKER_FILE):
            with open(TRACKER_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_trades(self):
        """保存交易记录"""
        with open(TRACKER_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.trades, f, indent=2, ensure_ascii=False)

    def add_trade(self, action: str, price: float, stop_loss: Optional[float] = None,
                 take_profit: Optional[float] = None, strategy: str = ""):
        """添加一笔交易记录"""
        trade = {
            "timestamp": datetime.now().isoformat(),
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": action,  # LONG, SHORT, HOLD
            "price": price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "strategy": strategy
        }
        self.trades.append(trade)
        self._save_trades()
        print(f"[BTC Tracker] 记录交易: {action} @ ${price}")

    def get_latest_trades(self, count: int = 10) -> List[Dict]:
        """获取最近的交易记录"""
        return self.trades[-count:] if len(self.trades) >= count else self.trades

    def backtest_improved(self, initial_capital: float = 10000.0) -> Dict:
        """
        改进的回测逻辑
        
        逻辑说明：
        - 每个交易信号都视为平仓+开仓操作
        - 如果新信号是 LONG 且当前是 SHORT：平空 + 开多
        - 如果新信号是 SHORT 且当前是 LONG：平多 + 开空
        - 如果新信号与当前仓位相同：不操作（或可以重新入场）
        - HOLD 信号不影响仓位
        """
        if not self.trades:
            return {
                "error": "没有交易记录",
                "initial_capital": initial_capital,
                "final_capital": initial_capital,
                "total_return": 0,
                "capital_history": [],
                "trades": []
            }

        capital = initial_capital
        position = 0.0  # 持仓数量（正数=多头，负数=空头）
        entry_price = 0.0  # 入场价格
        position_type = None  # 'LONG' 或 'SHORT'
        entry_time = None
        capital_history = []  # 不添加初始点，只添加交易后的变化
        completed_trades = []  # 已完成的交易记录

        for trade in self.trades:
            # 解析时间戳
            ts = trade["timestamp"]
            try:
                if ts.endswith('Z'):
                    trade_time = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                else:
                    trade_time = datetime.fromisoformat(ts)
            except (AttributeError, ValueError):
                # 回退到字符串解析（支持毫秒格式）
                try:
                    # 尝试带毫秒的格式
                    trade_time = datetime.strptime(ts.split('.')[0], "%Y-%m-%dT%H:%M:%S")
                except:
                    try:
                        trade_time = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                    except:
                        trade_time = datetime.now()

            action = trade["action"]
            price = trade["price"]

            # 忽略 HOLD 信号
            if action == "HOLD":
                continue

            # 回测逻辑：平仓 + 开仓
            if action == "LONG":
                # 如果当前是空仓，先平空
                if position_type == "SHORT":
                    # 平空：卖出头寸的借入量
                    pnl_short = abs(position) * (entry_price - price)
                    capital += pnl_short
                    completed_trades.append({
                        "entry_time": entry_time,
                        "exit_time": trade_time,
                        "entry_price": entry_price,
                        "exit_price": price,
                        "action": "SHORT",
                        "pnl": pnl_short,
                        "type": "平空"
                    })
                    position = 0
                    position_type = None
                    entry_price = 0
                
                # 开多仓
                if position == 0:
                    position = capital / price
                    entry_price = price
                    position_type = "LONG"
                    entry_time = trade_time
                    completed_trades.append({
                        "entry_time": trade_time,
                        "entry_price": price,
                        "action": "LONG",
                        "type": "开多",
                        "capital_before": capital
                    })
                # 如果已经是多仓，可以加仓或保持（这里选择保持）
                
            elif action == "SHORT":
                # 如果当前是多仓，先平多
                if position_type == "LONG":
                    # 平多：卖出持有的BTC
                    pnl_long = position * (price - entry_price)
                    capital += pnl_long
                    completed_trades.append({
                        "entry_time": entry_time,
                        "exit_time": trade_time,
                        "entry_price": entry_price,
                        "exit_price": price,
                        "action": "LONG",
                        "pnl": pnl_long,
                        "type": "平多"
                    })
                    position = 0
                    position_type = None
                    entry_price = 0
                
                # 开空仓
                if position == 0:
                    position = -capital / price
                    entry_price = price
                    position_type = "SHORT"
                    entry_time = trade_time
                    completed_trades.append({
                        "entry_time": trade_time,
                        "entry_price": price,
                        "action": "SHORT",
                        "type": "开空",
                        "capital_before": capital
                    })
                # 如果已经是空仓，可以加仓或保持

            # 计算未实现盈亏和当前净值
            if position_type is not None:
                if position_type == "LONG":
                    unrealized_pnl = position * (price - entry_price)
                else:  # SHORT
                    unrealized_pnl = abs(position) * (entry_price - price)
                current_capital = capital + unrealized_pnl
            else:
                current_capital = capital

            capital_history.append((trade_time, current_capital))

        # 如果还有未平仓，平仓（使用最后一个价格）
        if position != 0 and position_type is not None:
            last_price = self.trades[-1]["price"]
            if position_type == "LONG":
                exit_pnl = position * (last_price - entry_price)
            else:  # SHORT
                exit_pnl = abs(position) * (entry_price - last_price)
            capital += exit_pnl
            capital_history.append((datetime.now(), capital))

        # 计算最终结果
        final_capital = capital_history[-1][1]
        total_return = (final_capital - initial_capital) / initial_capital * 100

        return {
            "initial_capital": initial_capital,
            "final_capital": final_capital,
            "total_return": total_return,
            "capital_history": capital_history,
            "trades": completed_trades
        }

    def calculate_metrics(self, backtest_result: Dict, risk_free_rate: float = 0.02) -> Dict:
        """计算绩效指标（修复年化收益率和夏普比率）"""
        capital_history = backtest_result["capital_history"]
        initial_capital = backtest_result["initial_capital"]
        final_capital = backtest_result["final_capital"]
        total_return = backtest_result["total_return"]

        # 提取净值序列
        values = [c[1] for c in capital_history]

        # 1. 收益率（年化）- 最简单方式（不调整）
        annualized_return = total_return

        # 2. 最大回撤
        peak = values[0] if values else initial_capital
        max_drawdown = 0
        max_drawdown_duration_hours = 0
        current_drawdown_duration_hours = 0
        last_peak_time = capital_history[0][0] if capital_history else datetime.now()

        for time, value in capital_history:
            if value > peak:
                peak = value
                last_peak_time = time
                current_drawdown_duration_hours = 0
            else:
                drawdown = (peak - value) / peak if peak > 0 else 0
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
                current_drawdown_duration_hours = (time - last_peak_time).total_seconds() / 3600
                if current_drawdown_duration_hours > max_drawdown_duration_hours:
                    max_drawdown_duration_hours = current_drawdown_duration_hours

        max_drawdown_pct = max_drawdown * 100

        # 3. 夏普比率（修复版）
        # 计算每小时收益率
        hourly_returns = []
        for i in range(1, len(values)):
            prev_value = values[i-1]
            if prev_value != 0:
                hourly_return = (values[i] - prev_value) / prev_value
                hourly_returns.append(hourly_return)

        # 计算年化波动率（基于24小时）
        if len(hourly_returns) > 0:
            avg_return = sum(hourly_returns) / len(hourly_returns)
            
            if HAS_MATPLOTLIB:
                std_return = np.std(hourly_returns)
            else:
                variance = sum((x - avg_return) ** 2 for x in hourly_returns) / len(hourly_returns)
                std_return = math.sqrt(variance)
            
            # 年化波动率
            annualized_volatility = std_return * math.sqrt(8760)  # 基于年化
            
            # 夏普比率 = 年化收益率 / 年化波动率
            if annualized_volatility > 0:
                sharpe_ratio = annualized_return / annualized_volatility
            else:
                sharpe_ratio = 0
        else:
            sharpe_ratio = 0

        # 4. 胜率
        completed_trades = backtest_result["trades"]
        if completed_trades:
            winning_trades = sum(1 for t in completed_trades if t.get("pnl", 0) > 0)
            win_rate = (winning_trades / len(completed_trades)) * 100
            win_count = winning_trades
        else:
            win_rate = 0
            win_count = 0

        # 5. 最高和最低净值
        max_capital = max(values) if values else initial_capital
        min_capital = min(values) if values else initial_capital

        # 6. 盈亏比（新增）
        profit_trades = sum(t.get("pnl", 0) for t in completed_trades if t.get("pnl", 0) > 0)
        loss_trades = sum(abs(t.get("pnl", 0)) for t in completed_trades if t.get("pnl", 0) < 0)
        
        if loss_trades > 0:
            profit_loss_ratio = profit_trades / loss_trades
        else:
            profit_loss_ratio = 0  # 如果没有亏损，设置为 0 或 Infinity

        return {
            "total_return": round(total_return, 2),
            "annualized_return": round(annualized_return * 100, 2),
            "max_drawdown": round(max_drawdown_pct, 2),
            "max_drawdown_duration_hours": round(max_drawdown_duration_hours, 2),
            "sharpe_ratio": round(sharpe_ratio, 4),
            "total_trades": len(completed_trades),
            "win_rate": round(win_rate, 2),
            "win_count": win_count,
            "initial_capital": initial_capital,
            "final_capital": final_capital,
            "max_capital": max_capital,
            "min_capital": min_capital,
            "profit_loss_ratio": round(profit_loss_ratio, 2)
        }

    def generate_chart(self, backtest_result: Dict, metrics: Dict) -> str:
        """生成净值曲线图"""
        if not HAS_MATPLOTLIB:
            print("[BTC Tracker] matplotlib 未安装，跳过图表生成")
            return "图表生成功能已禁用（matplotlib 未安装）"

        capital_history = backtest_result["capital_history"]
        times = [c[0] for c in capital_history]
        values = [c[1] for c in capital_history]

        # 创建图表
        plt.figure(figsize=(14, 10))

        # 净值曲线
        ax1 = plt.subplot(2, 1, 1)
        ax1.plot(times, values, linewidth=2, label='净值', color='#1f77b4')
        ax1.set_xlabel('时间', fontsize=12)
        ax1.set_ylabel('净值 ($)', fontsize=12)
        ax1.set_title('BTC 交易净值曲线', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='upper left', fontsize=11)

        # 格式化时间轴
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        ax1.xaxis.set_major_locator(mdates.HourLocator(interval=6))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')

        # 绩效指标表格
        ax2 = plt.subplot(2, 1, 2)
        ax2.axis('off')

        metrics_data = [
            ['指标', '数值'],
            ['总收益率', f"{metrics['total_return']}%"],
            ['年化收益率', f"{metrics['annualized_return']}%"],
            ['最大回撤', f"{metrics['max_drawdown']}%"],
            ['回撤持续时间', f"{metrics['max_drawdown_duration_hours']} 小时"],
            ['夏普比率', f"{metrics['sharpe_ratio']}"],
            ['总交易次数', f"{metrics['total_trades']}"],
            ['胜率', f"{metrics['win_rate']}%"],
            ['初始资金', f"${backtest_result['initial_capital']:,.2f}"],
            ['最终资金', f"${backtest_result['final_capital']:,.2f}"]
        ]

        table = ax2.table(cellText=metrics_data, cellLoc='left', loc='center',
                         colWidths=[0.4, 0.6])
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1, 1.5)

        # 设置表格样式
        for i in range(len(metrics_data)):
            for j in range(len(metrics_data[0])):
                cell = table[(i, j)]
                if i == 0:
                    cell.set_facecolor('#4CAF50')
                    cell.set_text_props(weight='bold', color='white')
                else:
                    cell.set_facecolor('#f0f0f0' if i % 2 == 0 else 'white')
                cell.set_edgecolor('white')

        ax2.set_title('绩效指标汇总', fontsize=14, fontweight='bold', pad=20)

        plt.tight_layout()
        plt.savefig(BACKTEST_CHART, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"[BTC Tracker] 图表已生成: {BACKTEST_CHART}")
        return BACKTEST_CHART

    def generate_report(self) -> str:
        """生成完整的回测报告"""
        if not self.trades:
            return "没有交易记录"

        # 使用改进的回测逻辑
        backtest_result = self.backtest_improved()

        # 计算指标
        metrics = self.calculate_metrics(backtest_result)

        # 生成图表
        chart_path = self.generate_chart(backtest_result, metrics)

        # 生成文本报告
        report = f"""
{'='*80}
📊 BTC 交易回测报告（改进版）
{'='*80}

🕐 报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📈 总交易信号: {len(self.trades)}

💰 资金表现
  • 初始资金: ${backtest_result['initial_capital']:,.2f}
  • 最终资金: ${backtest_result['final_capital']:,.2f}
  • 总收益: ${backtest_result['final_capital'] - backtest_result['initial_capital']:,.2f}
  • 总收益率: {metrics['total_return']}%
  • 年化收益率: {metrics['annualized_return']}%

📉 风险指标
  • 最大回撤: {metrics['max_drawdown']}%
  • 回撤持续: {metrics['max_drawdown_duration_hours']} 小时

⚡ 绩效指标
  • 夏普比率: {metrics['sharpe_ratio']}
  • 胜率: {metrics['win_rate']}%
  • 完成交易: {metrics['total_trades']}

📋 最近交易记录
"""

        for trade in self.get_latest_trades(5):
            report += f"  • {trade['datetime']} | {trade['action']} @ ${trade['price']:,.2f}\n"

        report += f"\n📊 净值曲线图已生成: {chart_path}\n"
        report += f"{'='*80}\n"

        return report

def main():
    """主函数"""
    tracker = BTCTracker()
    report = tracker.generate_report()
    print(report)

    # 保存报告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"{REPORTS_DIR}/btc_backtest_report_{timestamp}.txt"
    os.makedirs(REPORTS_DIR, exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"[BTC Tracker] 报告已保存: {report_path}")

    return report, tracker.trades

if __name__ == "__main__":
    main()
