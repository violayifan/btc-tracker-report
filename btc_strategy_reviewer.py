#!/usr/bin/env python3
"""
BTC 策略复盘与自动迭代系统
每次信号更新后自动复盘，记录策略运行情况，生成改进建议
"""

import json
import os
import datetime as dt_module
from typing import Dict, List
from collections import defaultdict

# 使用模块导入避免冲突
datetime = dt_module.datetime

# 文件路径
WORKSPACE = "/root/.openclaw/workspace"
TRACKER_FILE = os.path.join(WORKSPACE, "btc_trades.json")
STRATEGY_LOG_FILE = os.path.join(WORKSPACE, "strategy_history.json")
STRATEGY_REPORT_FILE = os.path.join(WORKSPACE, "strategy_report.txt")

class StrategyReviewer:
    """策略复盘和迭代系统"""
    
    def __init__(self):
        self.strategy_history = self._load_strategy_history()
        self.performance_metrics = self._calculate_performance_metrics()
    
    def _load_strategy_history(self) -> List[Dict]:
        """加载策略历史记录"""
        if os.path.exists(STRATEGY_LOG_FILE):
            with open(STRATEGY_LOG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_strategy_history(self):
        """保存策略历史记录"""
        with open(STRATEGY_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.strategy_history, f, indent=2, ensure_ascii=False)
    
    def _load_trades(self) -> List[Dict]:
        """加载交易记录"""
        if os.path.exists(TRACKER_FILE):
            with open(TRACKER_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _calculate_performance_metrics(self) -> Dict:
        """计算当前策略的绩效指标"""
        if not self.strategy_history:
            return {}
        
        # 计算胜率
        total_signals = len(self.strategy_history)
        if total_signals == 0:
            return {}
        
        long_signals = sum(1 for s in self.strategy_history if s['action'] == 'LONG')
        short_signals = sum(1 for s in self.strategy_history if s['action'] == 'SHORT')
        
        # 获取交易绩效
        try:
            from btc_tracker import BTCTracker
            tracker = BTCTracker()
            backtest_result = tracker.backtest_improved()
            metrics = tracker.calculate_metrics(backtest_result)
            
            return {
                'total_signals': total_signals,
                'long_signals': long_signals,
                'short_signals': short_signals,
                'win_rate': metrics.get('win_rate', 0),
                'total_return': metrics.get('total_return', 0),
                'sharpe_ratio': metrics.get('sharpe_ratio', 0),
                'max_drawdown': metrics.get('max_drawdown', 0),
                'total_trades': metrics.get('total_trades', 0),
                'win_count': metrics.get('win_count', 0),
                'profit_loss_ratio': metrics.get('profit_loss_ratio', 0)
            }
        except Exception as e:
            print(f"  [警告] 计算绩效指标失败: {e}")
            return {}
    
    def record_strategy_signal(self, signal: Dict, market_data: Dict):
        """记录策略信号"""
        timestamp = datetime.now().isoformat()
        
        record = {
            "timestamp": timestamp,
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": signal['action'],
            "strategy_description": signal.get('description', ''),
            "reasoning": signal.get('reasoning', []),
            "risk_level": signal.get('risk_level', ''),
            "price_levels": signal.get('price_levels', {}),
            "market_conditions": {
                "price": market_data.get('price', 0),
                "rsi": market_data.get('rsi', 50),
                "sma_6h": market_data.get('sma_6h', 0),
                "sma_12h": market_data.get('sma_12h', 0),
                "price_position": market_data.get('price_position', 50),
                "fear_greed": market_data.get('fear_greed', 50),
                "volatility": market_data.get('volatility', 0)
            },
            "expected_outcome": self._predict_outcome(signal, market_data)
        }
        
        self.strategy_history.append(record)
        self._save_strategy_history()
        
        return record
    
    def _predict_outcome(self, signal: Dict, market_data: Dict) -> str:
        """预测信号结果"""
        action = signal['action']
        risk_level = signal.get('risk_level', 'medium')
        
        # 基于历史绩效预测
        if self.performance_metrics.get('win_rate', 0) < 30:
            return "高风险：胜率较低"
        elif self.performance_metrics.get('win_rate', 0) > 50:
            return "预期良好：胜率较高"
        
        # 基于市场条件预测
        if market_data.get('volatility', 0) < 50:
            return "低波动环境：收益可能有限"
        elif market_data.get('volatility', 0) > 200:
            return "高波动环境：注意风险"
        
        return "正常波动环境"
    
    def analyze_strategy_performance(self) -> Dict:
        """分析策略绩效"""
        if not self.strategy_history:
            return {"status": "no_data"}
        
        metrics = self._calculate_performance_metrics()
        if not metrics:
            return {"status": "no_metrics"}
        
        analysis = {
            "overall_status": self._evaluate_status(metrics),
            "strengths": [],
            "weaknesses": [],
            "improvements": []
        }
        
        # 分析优势
        if metrics.get('win_rate', 0) > 50:
            analysis['strengths'].append(f"胜率良好：{metrics['win_rate']:.2f}%")
        
        if metrics.get('profit_loss_ratio', 0) > 2:
            analysis['strengths'].append(f"盈亏比优秀：{metrics['profit_loss_ratio']:.2f}")
        
        if metrics.get('sharpe_ratio', 0) > 1:
            analysis['strengths'].append(f"夏普比率良好：{metrics['sharpe_ratio']:.2f}")
        
        if metrics.get('max_drawdown', 0) < 5:
            analysis['strengths'].append(f"风险控制良好：最大回撤 {metrics['max_drawdown']:.2f}%")
        
        # 分析劣势
        if metrics.get('win_rate', 0) < 30:
            analysis['weaknesses'].append(f"胜率偏低：{metrics['win_rate']:.2f}% - 需要改进信号质量")
        
        if metrics.get('max_drawdown', 0) > 10:
            analysis['weaknesses'].append(f"风险控制不足：最大回撤 {metrics['max_drawdown']:.2f}% - 需要优化止损")
        
        if metrics.get('profit_loss_ratio', 0) < 1:
            analysis['weaknesses'].append(f"盈亏比偏低：{metrics['profit_loss_ratio']:.2f} - 需要优化止盈策略")
        
        # 生成改进建议
        if metrics.get('win_rate', 0) < 30:
            analysis['improvements'].append("建议：提高信号筛选标准，只在多重指标共振时开仓")
            analysis['improvements'].append("建议：增加趋势确认指标，避免逆势交易")
        
        if metrics.get('max_drawdown', 0) > 10:
            analysis['improvements'].append("建议：收紧止损，降低单笔交易风险")
            analysis['improvements'].append("建议：使用分批建仓，不要一次性满仓")
        
        if abs(metrics.get('total_return', 0)) < 1:
            analysis['improvements'].append("建议：在高确定性机会时才交易")
            analysis['improvements'].append("建议：考虑增加持仓时间，让利润充分释放")
        
        return analysis
    
    def _evaluate_status(self, metrics: Dict) -> str:
        """评估策略状态"""
        win_rate = metrics.get('win_rate', 0)
        sharpe_ratio = metrics.get('sharpe_ratio', 0)
        max_drawdown = metrics.get('max_drawdown', 100)
        
        if win_rate > 50 and sharpe_ratio > 1 and max_drawdown < 10:
            return "excellent"
        elif win_rate > 40 and sharpe_ratio > 0.5 and max_drawdown < 15:
            return "good"
        elif win_rate > 30 and sharpe_ratio > 0 and max_drawdown < 20:
            return "acceptable"
        else:
            return "needs_improvement"
    
    def generate_strategy_report(self) -> str:
        """生成策略复盘报告"""
        if not self.strategy_history:
            return "暂无策略数据"
        
        metrics = self._calculate_performance_metrics()
        analysis = self.analyze_strategy_performance()
        
        # 统计信号类型
        recent_signals = self.strategy_history[-20:]  # 最近20个信号
        long_count = sum(1 for s in recent_signals if s['action'] == 'LONG')
        short_count = sum(1 for s in recent_signals if s['action'] == 'SHORT')
        
        report = f"""
{'='*80}
📊 BTC 策略复盘与改进报告
{'='*80}

🕐 报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📈 策略信号总数: {len(self.strategy_history)}
📋 近期信号数（最近20次）: {len(recent_signals)}

💰 策略绩效
------------------------------------------------
"""
        
        report += f"  • 总收益率: {metrics.get('total_return', 0):.2f}%\n"
        report += f"  • 胜率: {metrics.get('win_rate', 0):.2f}%\n"
        report += f"  • 盈亏比: {metrics.get('profit_loss_ratio', 0):.2f}\n"
        report += f"  • 夏普比率: {metrics.get('sharpe_ratio', 0):.4f}\n"
        report += f"  • 最大回撤: {metrics.get('max_drawdown', 0):.2f}%\n"
        report += f"  • 总交易次数: {metrics.get('total_trades', 0)}\n"
        report += f"  • 盈利交易: {metrics.get('win_count', 0)}\n"
        
        report += f"""
📈 信号类型分布
------------------------------------------------
  • 做多信号: {long_count} ({long_count/len(recent_signals)*100:.1f}%)
  • 做空信号: {short_count} ({short_count/len(recent_signals)*100:.1f}%)
  • 观望信号: {len(recent_signals)-long_count-short_count} ({(len(recent_signals)-long_count-short_count)/len(recent_signals)*100:.1f}%)

📊 策略评估
------------------------------------------------
  • 整体状态: {self._get_status_label(analysis.get('overall_status', 'unknown'))}
"""
        
        # 显示优势
        if analysis['strengths']:
            report += "\n  ✅ 策略优势:\n"
            for strength in analysis['strengths']:
                report += f"    • {strength}\n"
        
        # 显示劣势
        if analysis['weaknesses']:
            report += "\n  ❌ 策略劣势:\n"
            for weakness in analysis['weaknesses']:
                report += f"    • {weakness}\n"
        
        # 显示改进建议
        if analysis['improvements']:
            report += "\n  💡 改进建议:\n"
            for i, improvement in enumerate(analysis['improvements'], 1):
                report += f"    {i}. {improvement}\n"
        
        # 显示最近信号
        report += f"""
📋 最近5个信号记录
------------------------------------------------
"""
        
        for signal in self.strategy_history[-5:]:
            action_icon = "🟢" if signal['action'] == 'LONG' else "🔴" if signal['action'] == 'SHORT' else "⏸️"
            report += f"  {action_icon} {signal['datetime']} | {signal['action']} @ ${signal['market_conditions']['price']:,.2f}\n"
            report += f"      {signal['strategy_description']}\n"
            report += f"      预期: {signal['expected_outcome']}\n"
        
        report += f"\n{'='*80}\n"
        
        return report
    
    def _get_status_label(self, status: str) -> str:
        """获取状态标签"""
        labels = {
            "excellent": "🌟 优秀",
            "good": "✅ 良好",
            "acceptable": "⚠️  可接受",
            "needs_improvement": "❌ 需要改进"
        }
        return labels.get(status, status)
    
    def save_report(self, report: str):
        """保存策略复盘报告"""
        with open(STRATEGY_REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write(report)
        return STRATEGY_REPORT_FILE

def main():
    """主函数"""
    print(f"[{datetime.now()}] 开始策略复盘...")
    
    reviewer = StrategyReviewer()
    
    # 分析策略绩效
    print("  1. 分析策略绩效...")
    analysis = reviewer.analyze_strategy_performance()
    
    # 生成复盘报告
    print("  2. 生成复盘报告...")
    report = reviewer.generate_strategy_report()
    
    # 保存报告
    print("  3. 保存复盘报告...")
    report_file = reviewer.save_report(report)
    print(f"  ✅ 报告已保存: {report_file}")
    
    # 显示报告
    print("\n" + report)
    
    print(f"[{datetime.now()}] 策略复盘完成!")

if __name__ == "__main__":
    main()
