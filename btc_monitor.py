#!/usr/bin/env python3
"""BTC 价格监控与交易策略分析（修复版）"""

import requests
import json
import os
import datetime as dt_module
from typing import Dict, List

# 使用模块导入避免冲突
datetime = dt_module.datetime
timedelta = dt_module.timedelta

# 配置
COINGECKO_API = "https://api.coingecko.com/api/v3"
OUTPUT_DIR = "/root/.openclaw/workspace/reports"
FEAR_GREED_API = "https://api.alternative.me/fng/"

def get_btc_price() -> Dict:
    """获取 BTC 当前价格和历史数据"""
    try:
        # 当前价格
        price_resp = requests.get(
            f"{COINGECKO_API}/simple/price?ids=bitcoin&vs_currencies=usd,cny&include_24hr_change=true&include_24hr_vol=true",
            timeout=10
        )
        price_data = price_resp.json()

        # 获取过去24小时的价格数据用于技术分析（每小时一个点）
        history_resp = requests.get(
            f"{COINGECKO_API}/coins/bitcoin/market_chart?vs_currency=usd&days=1",
            timeout=10
        )
        history_data = history_resp.json()

        return {
            "current": price_data.get("bitcoin", {}),
            "history": history_data.get("prices", [])
        }
    except Exception as e:
        return {"error": str(e)}

def get_fear_greed_index() -> Dict:
    """获取加密货币恐慌贪婪指数"""
    try:
        resp = requests.get(FEAR_GREED_API, timeout=10)
        data = resp.json()
        return {
            "value": int(data["data"][0]["value"]),
            "classification": data["data"][0]["value_classification"],
            "timestamp": data["data"][0]["timestamp"]
        }
    except Exception as e:
        return {"error": str(e)}

def calculate_technical_indicators(history: List) -> Dict:
    """计算技术指标"""
    if not history or len(history) < 12:
        return {
            "error": "数据不足",
            "current_price": 0,
            "sma_6h": 0,
            "sma_12h": 0,
            "rsi": 50,
            "volatility": 0,
            "price_position": 0
        }

    prices = [p[1] for p in history]
    current_price = prices[-1]
    
    # 计算6小时和12小时SMA（过去6小时和12小时，每小时一个点）
    if len(prices) >= 12:
        sma_6h = sum(prices[-6:]) / 6
        sma_12h = sum(prices[-12:]) / 12
    else:
        sma_6h = current_price
        sma_12h = current_price
    
    # 计算RSI（14周期）
    if len(prices) >= 14:
        gains = []
        losses = []
        for i in range(1, 15):
            change = prices[-i] - prices[-i-1]
            if change >= 0:
                gains.append(change)
            else:
                losses.append(abs(change))
        
        avg_gain = sum(gains) / len(gains) if gains else 0
        avg_loss = sum(losses) / len(losses) if losses else 0
        
        if avg_loss == 0:
            rs = 70
        else:
            rs = 100 - (100 / (1 + (avg_gain / avg_loss)))
    else:
        rs = 50
    
    # 计算波动率（24小时价格标准差）
    volatility = 0
    if len(prices) >= 24:
        mean_price = sum(prices[-24:]) / 24
        variance = sum((p - mean_price) ** 2 for p in prices[-24:]) / 24
        volatility = variance ** 0.5
    
    # 计算价格在24小时中的位置（百分比）
    if len(prices) >= 24:
        min_price = min(prices[-24:])
        max_price = max(prices[-24:])
        if max_price > min_price:
            price_position = ((current_price - min_price) / (max_price - min_price)) * 100
        else:
            price_position = 50
    else:
        price_position = 50

    return {
        "current_price": current_price,
        "sma_6h": sma_6h,
        "sma_12h": sma_12h,
        "rsi": rs,
        "volatility": volatility,
        "price_position": price_position
    }

def analyze_market_sentiment(price_data: Dict, fgi: Dict, indicators: Dict) -> Dict:
    """分析市场情绪"""
    sentiment_score = 0
    sentiment_factors = []
    
    # 恐慌贪婪指数
    if "value" in fgi:
        fgi_value = fgi["value"]
        if fgi_value <= 20:
            sentiment_score += 2
            sentiment_factors.append(f"极度恐慌: Extreme Fear ({fgi_value}) - 可能是买入机会")
        elif fgi_value <= 40:
            sentiment_score += 1
            sentiment_factors.append(f"恐慌: Fear ({fgi_value})")
        elif fgi_value >= 80:
            sentiment_score -= 1
            sentiment_factors.append(f"贪婪: Greed ({fgi_value}) - 注意回调")
    
    # 24小时涨跌
    if "current" in price_data:
        change_24h = price_data["current"].get("usd_24h_change", 0)
        if change_24h > 5:
            sentiment_score += 1
            sentiment_factors.append(f"24h变化 {change_24h:.2f}% - 强势上涨")
        elif change_24h < -5:
            sentiment_score -= 1
            sentiment_factors.append(f"24h变化 {change_24h:.2f}% - 大幅下跌")
        else:
            sentiment_factors.append(f"24h变化 {change_24h:.2f}% - 震荡整理")
    
    # RSI
    rsi = indicators.get("rsi", 50)
    if rsi >= 70:
        sentiment_factors.append(f"RSI {rsi:.2f} - 超买区域，注意回调")
    elif rsi <= 30:
        sentiment_factors.append(f"RSI {rsi:.2f} - 超卖区域，可能反弹")
    elif rsi >= 55:
        sentiment_factors.append(f"RSI {rsi:.2f} - 偏强")
    else:
        sentiment_factors.append(f"RSI {rsi:.2f} - 偏弱")
    
    # 价格位置
    price_position = indicators.get("price_position", 50)
    if price_position >= 90:
        sentiment_factors.append(f"价格位置 {price_position:.1f}% - 接近24h高位")
    elif price_position <= 10:
        sentiment_factors.append(f"价格位置 {price_position:.1f}% - 接近24h低位")
    else:
        sentiment_factors.append(f"价格位置 {price_position:.1f}%")
    
    # 波动率
    volatility = indicators.get("volatility", 0)
    if volatility < 100:
        sentiment_factors.append(f"低波动率 ({int(volatility)}) - 可能突破")
    elif volatility > 500:
        sentiment_factors.append(f"高波动率 ({int(volatility)}) - 注意风险")
    
    # 综合情绪
    if sentiment_score >= 2:
        overall = "bullish"
        overall_text = "偏多"
    elif sentiment_score >= 1:
        overall = "slightly_bullish"
        overall_text = "轻度偏多"
    elif sentiment_score <= -1:
        overall = "bearish"
        overall_text = "轻度偏空"
    elif sentiment_score <= -2:
        overall = "strongly_bearish"
        overall_text = "偏空"
    else:
        overall = "neutral"
        overall_text = "中性"

    return {
        "overall": overall,
        "overall_text": overall_text,
        "score": sentiment_score,
        "factors": sentiment_factors
    }

def generate_1h_strategy(current_price: float, indicators: Dict, sentiment: Dict) -> Dict:
    """生成1小时交易策略"""
    strategy = {
        "action": "HOLD",
        "description": "",
        "reasoning": [],
        "risk_level": "medium",
        "price_levels": {}
    }
    
    if not indicators:
        return strategy
    
    sma_6h = indicators.get("sma_6h", 0)
    sma_12h = indicators.get("sma_12h", 0)
    rsi = indicators.get("rsi", 50)
    volatility = indicators.get("volatility", 0)
    
    # 判断趋势
    if current_price > sma_6h > sma_12h:
        trend = "uptrend"
        strategy["reasoning"].append("价格站上短期均线，上升趋势")
    elif current_price < sma_6h < sma_12h:
        trend = "downtrend"
        strategy["reasoning"].append("价格跌破均线，下降趋势")
    else:
        trend = "sideways"
        strategy["reasoning"].append("价格在均线附近震荡")
    
    # 结合情绪判断
    sentiment_overall = sentiment.get("overall", "neutral")
    
    # 生成策略
    if trend == "uptrend" and sentiment_overall in ["bullish", "slightly_bullish"]:
        if rsi < 70:
            strategy["action"] = "LONG"
            strategy["reasoning"].append("上升趋势 + 多头情绪 + RSI未超买 = 适当做多机会")
        else:
            strategy["action"] = "WAIT_PULLBACK"
            strategy["reasoning"].append("RSI超买，等待回调后再入场")
    elif trend == "downtrend" and sentiment_overall in ["bearish", "slightly_bearish"]:
        if rsi > 30:
            strategy["action"] = "SHORT"
            strategy["reasoning"].append("下降趋势 + 空头情绪 + RSI未超卖 = 适当做空机会")
        else:
            strategy["action"] = "WAIT_REBOUND"
            strategy["reasoning"].append("RSI超卖，等待反弹后再做空")
    elif sentiment_overall == "bullish" and rsi <= 40:
        strategy["action"] = "LONG_DIP"
        strategy["reasoning"].append("多头情绪 + 价格回调 = 低吸机会")
    elif sentiment_overall == "bearish" and rsi >= 60:
        strategy["action"] = "SHORT_RALLY"
        strategy["reasoning"].append("空头情绪 + 价格反弹 = 高抛机会")
    else:
        strategy["action"] = "HOLD"
        strategy["reasoning"].append("信号模糊，建议观望")
    
    # 设置关键价格位
    volatility_premium = volatility * 0.5
    
    if strategy["action"] in ["LONG", "LONG_DIP"]:
        strategy["price_levels"]["stop_loss"] = round(current_price - volatility_premium, 2)
        strategy["price_levels"]["take_profit"] = round(current_price + volatility_premium * 2, 2)
        strategy["price_levels"]["support"] = round(current_price - volatility_premium * 0.5, 2)
    elif strategy["action"] in ["SHORT", "SHORT_RALLY"]:
        strategy["price_levels"]["stop_loss"] = round(current_price + volatility_premium, 2)
        strategy["price_levels"]["take_profit"] = round(current_price - volatility_premium * 2, 2)
        strategy["price_levels"]["resistance"] = round(current_price + volatility_premium * 0.5, 2)
    else:
        strategy["price_levels"]["support"] = round(current_price - volatility_premium * 0.5, 2)
        strategy["price_levels"]["resistance"] = round(current_price + volatility_premium * 0.5, 2)
    
    # 风险等级（确保所有策略都有风险等级）
    if volatility > 800:
        strategy["risk_level"] = "high"
    elif volatility < 200:
        strategy["risk_level"] = "low"
    else:
        strategy["risk_level"] = "medium"
    
    # 策略说明（确保所有策略都有描述）
    if strategy["action"] == "LONG":
        strategy["description"] = "建议做多，关注上方阻力位突破"
    elif strategy["action"] == "SHORT":
        strategy["description"] = "建议做空，关注下方支撑位跌破"
    elif strategy["action"] == "LONG_DIP":
        strategy["description"] = "逢低做多，控制仓位"
    elif strategy["action"] == "SHORT_RALLY":
        strategy["description"] = "逢高做空，控制仓位"
    elif strategy["action"] == "WAIT_PULLBACK":
        strategy["description"] = "等待回调后再考虑做多"
    elif strategy["action"] == "WAIT_REBOUND":
        strategy["description"] = "等待反弹后再考虑做空"
    else:  # HOLD 或其他
        strategy["description"] = "当前方向不明，建议观望等待明确信号"

    return strategy

def record_trade(strategy: Dict, price: float):
    """记录交易信号到跟踪文件"""
    try:
        from btc_tracker import BTCTracker
    except ImportError:
        print("  [警告] 无法导入 BTC Tracker，交易将不会记录")
        return
    
    tracker = BTCTracker()
    
    # 如果策略是 HOLD，不记录交易
    action = strategy['action']
    if action == "HOLD":
        print(f"  [交易记录] 当前策略: {action} - 不记录交易")
        return
    
    # 记录交易
    stop_loss = strategy['price_levels'].get('stop_loss')
    take_profit = strategy['price_levels'].get('take_profit')
    
    tracker.add_trade(
        action=action,
        price=price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        strategy=strategy['description']
    )

def generate_backtest_summary():
    """生成回测汇总（仅统计数据）"""
    try:
        from btc_tracker import BTCTracker
        import traceback

        tracker = BTCTracker()
        if not tracker.trades:
            return "\n📝 暂无交易记录"

        # 使用改进的回测逻辑
        backtest_result = tracker.backtest_improved()

        # 计算指标
        metrics = tracker.calculate_metrics(backtest_result)

        # 生成统计数据（不包含图表）
        full_report = "\n📊 回测统计\n" + "-" * 40 + "\n"

        metrics_list = [
            ("总收益率", f"{metrics.get('total_return', 0)}%"),
            ("年化收益率", f"{metrics.get('annualized_return', 0)}%"),
            ("最大回撤", f"{metrics.get('max_drawdown', 0)}%"),
            ("回撤持续时间", f"{metrics.get('max_drawdown_duration_hours', 0)} 小时"),
            ("夏普比率", f"{metrics.get('sharpe_ratio', 0)}"),
            ("总交易次数", f"{metrics.get('total_trades', 0)}"),
            ("胜率", f"{metrics.get('win_rate', 0)}%"),
            ("初始资金", f"${metrics.get('initial_capital', 0):,.0f}"),
            ("最终资金", f"${metrics.get('final_capital', 0):,.0f}")
        ]

        for key, value in metrics_list:
            full_report += f"• {key:<12s}: {value}\n"

        full_report += "\n" + "=" * 80 + "\n"

        # 保存回测报告
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(OUTPUT_DIR, f"btc_backtest_report_{timestamp}.txt")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(full_report)

        return f"\n{full_report}"
    except Exception as e:
        traceback.print_exc()
        return f"\n⚠️ 回测生成失败: {str(e)}"

def generate_simple_chart(backtest_result: Dict, metrics: Dict) -> str:
    """生成简化的文本图表（备用方案）"""
    if not backtest_result.get("capital_history"):
        return "没有数据生成图表"
    
    capital_history = backtest_result["capital_history"]
    values = [c[1] for c in capital_history]
    
    # 简化：只显示最近10个数据点
    recent_values = values[-10:] if len(values) >= 10 else values
    
    # 找到最大和最小值用于归一化
    min_val = min(recent_values)
    max_val = max(recent_values)
    val_range = max_val - min_val if max_val > min_val else 1
    
    # 图表宽度
    width = 50
    
    chart = f"\n{'='*80}\n📊 BTC 交易净值走势（文本版）\n{'='*80}\n"
    
    # 生成净值走势
    for i, value in enumerate(recent_values):
        # 归一化到 0-100
        normalized = int((value - min_val) / val_range * 100) if val_range > 0 else 50
        bar_length = int(normalized / 100 * width)
        bar = "█" * bar_length + "░" * (width - bar_length)
        chart += f"{i:2d} | ${value:,.0f} | {bar}\n"
    
    # 统计数据
    chart += f"\n📊 统计数据\n{'-'*40}\n"
    
    metrics_list = [
        ("总收益率", f"{metrics.get('total_return', 0)}%"),
        ("年化收益率", f"{metrics.get('annualized_return', 0)}%"),
        ("最大回撤", f"{metrics.get('max_drawdown', 0)}%"),
        ("回撤持续时间", f"{metrics.get('max_drawdown_duration_hours', 0)} 小时"),
        ("夏普比率", f"{metrics.get('sharpe_ratio', 0)}"),
        ("总交易次数", f"{metrics.get('total_trades', 0)}"),
        ("胜率", f"{metrics.get('win_rate', 0)}%"),
        ("初始资金", f"${metrics.get('initial_capital', 0):,.0f}"),
        ("最终资金", f"${metrics.get('final_capital', 0):,.0f}")
    ]
    
    for key, value in metrics_list:
        chart += f"• {key:<12s}: {value}\n"
    
    chart += f"\n{'='*80}\n"
    
    return chart

def generate_report(price_data: Dict, fgi: Dict, indicators: Dict, sentiment: Dict, strategy: Dict) -> str:
    """生成交易报告"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    current = price_data.get("current", {})
    price = current.get("usd", 0)
    price_cny = current.get("cny", 0)
    change_24h = current.get("usd_24h_change", 0)
    
    report = f"""
📊 BTC 市场分析与交易策略报告
{'='*50}

🕐 报告时间: {now}

💰 当前价格
  • BTC/USD: ${price:,.2f}
  • BTC/CNY: ¥{price_cny:,.0f}
  • 24h涨跌: {change_24h:+.2f}%

📈 技术指标
  • SMA 6小时: ${indicators.get('sma_6h', 0):,.2f}
  • SMA 12小时: ${indicators.get('sma_12h', 0):,.2f}
  • RSI (14): {indicators.get('rsi', 50):.2f}
  • 波动率: ${int(indicators.get('volatility', 0))}
  • 价格位置: {indicators.get('price_position', 50):.1f}% (24h)

🎭 市场情绪: {sentiment.get('overall_text', 'neutral')}
  • 恐慌贪婪指数: {fgi.get('value', 0)} - {fgi.get('classification', 'Unknown')}
  • 情绪评分: {sentiment.get('score', 0)}

  分析因素:
"""
    
    for factor in sentiment.get("factors", []):
        report += f"  • {factor}\n"
    
    report += f"""
🎯 1小时交易策略
  • 建议操作: {strategy['action']}
  • 策略描述: {strategy['description']}
  • 风险等级: {strategy['risk_level']}

  价格点位:
"""
    
    support = strategy['price_levels'].get('support')
    resistance = strategy['price_levels'].get('resistance')
    
    support_str = f"${support:,.2f}" if support else "N/A"
    resistance_str = f"${resistance:,.2f}" if resistance else "N/A"
    
    report += f"  • 支撑位: {support_str}\n"
    report += f"  • 阻力位: {resistance_str}\n"
    
    if strategy['price_levels'].get('stop_loss'):
        report += f"  • 止损位: ${strategy['price_levels']['stop_loss']:,.2f}\n"
    if strategy['price_levels'].get('take_profit'):
        report += f"  • 止盈位: ${strategy['price_levels']['take_profit']:,.2f}\n"
    
    report += "\n  策略理由:\n"
    for reason in strategy.get("reasoning", []):
        report += f"  • {reason}\n"
    
    report += f"""
⚠️ 风险提示
  • 加密货币市场波动极大，请严格控制仓位
  • 本报告仅供参考，不构成投资建议
  • 交易有风险，投资需谨慎

{'='*50}
"""
    
    return report

def save_report(report: str):
    """保存报告到文件"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"btc_report_{timestamp}.txt"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return filepath

def main():
    """主函数"""
    print(f"[{datetime.now()}] 开始 BTC 市场分析...")
    
    # 获取数据
    print("  1. 获取价格数据...")
    price_data = get_btc_price()
    if "error" in price_data:
        print(f"  ❌ 价格数据获取失败: {price_data['error']}")
        return
    
    print("  2. 获取恐慌贪婪指数...")
    fgi = get_fear_greed_index()
    if "error" in fgi:
        print(f"  ❌ FGI 获取失败: {fgi['error']}")
        fgi = {}
    
    print("  3. 计算技术指标...")
    indicators = calculate_technical_indicators(price_data.get("history", []))
    
    print("  4. 分析市场情绪...")
    sentiment = analyze_market_sentiment(price_data, fgi, indicators)
    
    print("  5. 生成交易策略...")
    current_price = price_data["current"].get("usd", 0)
    strategy = generate_1h_strategy(
        current_price,
        indicators,
        sentiment
    )
    
    # 记录交易信号
    print("  6. 记录交易信号...")
    record_trade(strategy, current_price)
    
    print("  7. 生成报告...")
    report = generate_report(price_data, fgi, indicators, sentiment, strategy)
    
    print("  8. 保存报告...")
    filepath = save_report(report)
    print(f"  ✅ 报告已保存: {filepath}")
    
    # 生成回测汇总（包含文本图表）
    print("  9. 生成回测汇总...")
    backtest_summary = generate_backtest_summary()
    report += backtest_summary
    
    print("\n" + report)
    
    print(f"[{datetime.now()}] 分析完成!")

if __name__ == "__main__":
    main()
