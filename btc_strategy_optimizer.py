#!/usr/bin/env python3
"""
BTC 策略参数优化器
基于复盘结果自动调整策略参数
"""

import json
import os
import datetime as dt_module
from typing import Dict, List

# 使用模块导入避免冲突
datetime = dt_module.datetime

# 文件路径
WORKSPACE = "/root/.openclaw/workspace"
STRATEGY_CONFIG_FILE = os.path.join(WORKSPACE, "strategy_config.json")
STRATEGY_REPORT_FILE = os.path.join(WORKSPACE, "strategy_report.txt")

class StrategyOptimizer:
    """策略参数优化器"""
    
    def __init__(self):
        self.config = self._load_config()
        self.iteration_history = []
    
    def _load_config(self) -> Dict:
        """加载策略配置"""
        if os.path.exists(STRATEGY_CONFIG_FILE):
            with open(STRATEGY_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 默认配置
        return {
            "version": 1,
            "last_updated": datetime.now().isoformat(),
            "parameters": {
                "rsi_threshold_long": {
                    "value": 30,
                    "min": 20,
                    "max": 40,
                    "step": 1,
                    "description": "做多信号 RSI 下限"
                },
                "rsi_threshold_short": {
                    "value": 70,
                    "min": 60,
                    "max": 80,
                    "step": 1,
                    "description": "做空信号 RSI 上限"
                },
                "trend_confirmation": {
                    "value": True,
                    "description": "是否需要趋势确认"
                },
                "sma_alignment": {
                    "value": True,
                    "description": "是否要求均线对齐"
                },
                "volatility_filter": {
                    "value": True,
                    "min_volatility": 50,
                    "max_volatility": 200,
                    "description": "波动率过滤"
                },
                "risk_level": {
                    "value": "medium",
                    "description": "默认风险等级"
                }
            },
            "performance_tracking": {
                "win_rate_target": 40,
                "max_drawdown_limit": 15,
                "min_sharpe_ratio": 0.5
            }
        }
    
    def _save_config(self):
        """保存策略配置"""
        self.config['last_updated'] = datetime.now().isoformat()
        with open(STRATEGY_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def optimize_based_on_performance(self, performance_metrics: Dict) -> Dict:
        """基于绩效优化策略参数"""
        
        changes = []
        current_params = self.config['parameters']
        win_rate = performance_metrics.get('win_rate', 0)
        max_drawdown = performance_metrics.get('max_drawdown', 100)
        sharpe_ratio = performance_metrics.get('sharpe_ratio', 0)
        
        print(f"  [优化] 当前绩效: 胜率={win_rate:.2f}%, 最大回撤={max_drawdown:.2f}%, 夏普={sharpe_ratio:.2f}")
        
        # 1. 如果胜率过低，调整 RSI 阈值
        if win_rate < 30:
            print("  [优化] 检测到胜率过低，调整 RSI 阈值...")
            rsi_long = current_params['rsi_threshold_long']['value']
            rsi_short = current_params['rsi_threshold_short']['value']
            
            # 收紧做多信号（只在极端超卖时做多）
            new_rsi_long = max(rsi_long - 2, current_params['rsi_threshold_long']['min'])
            
            # 放宽做空信号（在更早的超买时做空）
            new_rsi_short = min(rsi_short + 2, current_params['rsi_threshold_short']['max'])
            
            current_params['rsi_threshold_long']['value'] = new_rsi_long
            current_params['rsi_threshold_short']['value'] = new_rsi_short
            
            changes.append({
                "parameter": "rsi_threshold",
                "old_value": f"{rsi_long} / {rsi_short}",
                "new_value": f"{new_rsi_long} / {new_rsi_short}",
                "reason": "胜率过低，收紧做多信号，放宽做空信号"
            })
            
            print(f"    • RSI 多: {rsi_long} -> {new_rsi_long}")
            print(f"    • RSI 空: {rsi_short} -> {new_rsi_short}")
        
        # 2. 如果最大回撤过大，调整风险管理
        elif max_drawdown > 15:
            print("  [优化] 检测到风险控制不足，调整风险管理参数...")
            volatility_filter = current_params['volatility_filter']['value']
            
            # 如果波动率过滤未启用，启用它
            if not volatility_filter:
                current_params['volatility_filter']['value'] = True
                changes.append({
                    "parameter": "volatility_filter",
                    "old_value": "Disabled",
                    "new_value": "Enabled",
                    "reason": "最大回撤过大，启用波动率过滤"
                })
                print(f"    • 启用波动率过滤")
            else:
                # 提高波动率过滤的下限
                min_vol = current_params['volatility_filter']['min_volatility']
                new_min_vol = min_vol + 20
                current_params['volatility_filter']['min_volatility'] = new_min_vol
                
                changes.append({
                    "parameter": "volatility_filter_min",
                    "old_value": min_vol,
                    "new_value": new_min_vol,
                    "reason": "最大回撤过大，提高波动率过滤"
                })
                print(f"    • 波动率下限: {min_vol} -> {new_min_vol}")
        
        # 3. 如果夏普比率过低，增加趋势确认要求
        if sharpe_ratio < 0.5:
            print("  [优化] 检测到夏普比率过低，增加趋势确认要求...")
            
            # 启用趋势确认
            if not current_params['trend_confirmation']['value']:
                current_params['trend_confirmation']['value'] = True
                changes.append({
                    "parameter": "trend_confirmation",
                    "old_value": "Disabled",
                    "new_value": "Enabled",
                    "reason": "夏普比率过低，增加趋势确认"
                })
                print(f"    • 启用趋势确认")
            
            # 启用均线对齐
            if not current_params['sma_alignment']['value']:
                current_params['sma_alignment']['value'] = True
                changes.append({
                    "parameter": "sma_alignment",
                    "old_value": "Disabled",
                    "new_value": "Enabled",
                    "reason": "夏普比率过低，启用均线对齐"
                })
                print(f"    • 启用均线对齐")
        
        # 4. 调整风险等级
        current_risk = current_params['risk_level']['value']
        if win_rate < 35:
            new_risk = "low"
            if current_risk != new_risk:
                current_params['risk_level']['value'] = new_risk
                changes.append({
                    "parameter": "risk_level",
                    "old_value": current_risk,
                    "new_value": new_risk,
                    "reason": "胜率偏低，降低风险等级"
                })
                print(f"    • 风险等级: {current_risk} -> {new_risk}")
        elif win_rate > 50:
            new_risk = "medium"
            if current_risk != new_risk:
                current_params['risk_level']['value'] = new_risk
                changes.append({
                    "parameter": "risk_level",
                    "old_value": current_risk,
                    "new_value": new_risk,
                    "reason": "胜率较高，恢复中等风险"
                })
                print(f"    • 风险等级: {current_risk} -> {new_risk}")
        
        # 保存优化记录
        optimization_record = {
            "timestamp": datetime.now().isoformat(),
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "performance_at_optimization": performance_metrics,
            "changes_made": changes,
            "new_parameters": current_params
        }
        
        self.iteration_history.append(optimization_record)
        self._save_config()
        
        return optimization_record
    
    def generate_optimization_report(self, performance_metrics: Dict, optimization_record: Dict) -> str:
        """生成优化报告"""
        
        report = f"""
{'='*80}
🤖 BTC 策略参数优化报告
{'='*80}

🕐 优化时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📊 优化时的绩效数据
------------------------------------------------
  • 胜率: {performance_metrics.get('win_rate', 0):.2f}%
  • 总收益率: {performance_metrics.get('total_return', 0):.2f}%
  • 最大回撤: {performance_metrics.get('max_drawdown', 0):.2f}%
  • 夏普比率: {performance_metrics.get('sharpe_ratio', 0):.2f}
  • 盈亏比: {performance_metrics.get('profit_loss_ratio', 0):.2f}
  • 总交易次数: {performance_metrics.get('total_trades', 0)}

📈 参数优化结果
------------------------------------------------
"""
        
        if optimization_record['changes_made']:
            report += "  本次优化调整了以下参数:\n\n"
            for i, change in enumerate(optimization_record['changes_made'], 1):
                report += f"  {i}. {change['parameter']}\n"
                report += f"     旧值: {change['old_value']}\n"
                report += f"     新值: {change['new_value']}\n"
                report += f"     理由: {change['reason']}\n\n"
        else:
            report += "  ⚠️ 本次无需调整参数\n\n"
        
        report += f"""
🎯 优化后的策略参数
------------------------------------------------
"""
        
        for param_name, param_info in optimization_record['new_parameters'].items():
            if isinstance(param_info, dict) and 'value' in param_info:
                report += f"  • {param_info['description']}: {param_info['value']}\n"
        
        report += f"""
📊 策略迭代历史
------------------------------------------------
  • 总优化次数: {len(self.iteration_history)}
  • 上次优化: {self.config.get('last_updated', 'N/A')}
"""
        
        if len(self.iteration_history) > 1:
            report += "  • 优化趋势:\n"
            for i, record in enumerate(self.iteration_history[-3:], 1):
                perf = record['performance_at_optimization']
                report += f"    {i}. {record['datetime']} | 胜率 {perf.get('win_rate', 0):.2f}%\n"
        
        report += f"""
💡 使用建议
------------------------------------------------
  • 新参数将在下次信号生成时生效
  • 建议监控接下来几次交易的表现
  • 如果绩效没有改善，系统会再次自动优化

{'='*80}
"""
        
        return report

def main():
    """主函数"""
    print(f"[{datetime.now()}] 开始策略参数优化...")
    
    optimizer = StrategyOptimizer()
    
    # 模拟从复盘系统获取绩效数据
    # 实际使用时应该从 btc_strategy_reviewer.py 获取
    performance_metrics = {
        "total_return": 0.67,
        "annualized_return": 0.67,
        "max_drawdown": 2.21,
        "max_drawdown_duration_hours": 24.06,
        "sharpe_ratio": 1.70,
        "total_trades": 9,
        "win_rate": 22.22,
        "win_count": 2,
        "initial_capital": 10000,
        "final_capital": 10067,
        "max_capital": 10162,
        "min_capital": 9937,
        "profit_loss_ratio": 2.55
    }
    
    print("  1. 基于绩效优化参数...")
    optimization_record = optimizer.optimize_based_on_performance(performance_metrics)
    
    print("  2. 生成优化报告...")
    report = optimizer.generate_optimization_report(performance_metrics, optimization_record)
    
    # 保存报告
    with open(STRATEGY_REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"  ✅ 报告已保存: {STRATEGY_REPORT_FILE}")
    
    # 显示报告
    print("\n" + report)
    
    print(f"[{datetime.now()}] 策略参数优化完成!")

if __name__ == "__main__":
    main()
