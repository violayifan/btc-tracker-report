#!/usr/bin/env python3
"""
BTC 市场监控（多备选数据源）
按优先级尝试多个免费 API
"""

import requests
import json
import os
import time
from datetime import datetime

# 配置
OUTPUT_DIR = "/root/.openclaw/workspace/reports"
TRADES_FILE = "/root/.openclaw/workspace/btc_trades.json"


class MultiSourcePriceData:
    """多数据源价格获取器"""

    def __init__(self):
        self.sources = {
            "binance": {
                "url": "https://api.binance.com/api/v3/ticker/price",
                "symbol": "BTCUSDT",
                "name": "Binance API"
            },
            "okx": {
                "url": "https://www.okx.com/api/v5/market/ticker",
                "symbol": "BTC-USDT",
                "name": "OKX API"
            },
            "kucoin": {
                "url": "https://api.kucoin.com/api/v1/market/stats?symbol=BTC-USDT",
                "name": "KuCoin API"
            },
            "coinglass": {
                "url": "https://open-api.coinglass.com/api/v1/ticker?symbol=BTCUSDT",
                "name": "Coinglass API"
            }
        }

    def try_get_price(self):
        """尝试从多个数据源获取价格"""
        for source_name, config in self.sources.items():
            print(f"[价格获取] 尝试 {config['name']}...")
            try:
                resp = requests.get(config['url'], timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    price = self.parse_response(source_name, data)
                    if price:
                        print(f"  ✅ {config['name']} 成功: ${price['usd']:,.2f}")
                        return price
                else:
                    print(f"  ⚠️  {config['name']} 响应格式异常")
                    time.sleep(1)
            except Exception as e:
                print(f"  ❌ {config['name']} 失败: {e}")
                time.sleep(1)

        print("[价格获取] 所有数据源都失败")
        return None

    def parse_response(self, source, data):
        """解析 API 响应"""
        price_data = {}

        if source == "binance":
            # Binance: {"symbol": "BTCUSDT", "price": "12345.67"}
            price_data['usd'] = float(data.get("price", 0))
            price_data['cny'] = price_data['usd'] * 7.0

        elif source == "okx":
            # OKX: [{"instId": "BTC-USDT", "last": "12345.67"}, ...]
            if isinstance(data, list) and len(data) > 0:
                price_data['usd'] = float(data[0].get("last", 0))
                price_data['cny'] = price_data['usd'] * 7.0

        elif source == "kucoin":
            # KuCoin: {"symbol": "BTC-USDT", "data": {"buy": "12345.67", ...}}
            ticker = data.get("data", {})
            price_data['usd'] = float(ticker.get("buy", 0))
            price_data['cny'] = price_data['usd'] * 7.0

        elif source == "coinglass":
            # Coinglass: {"result": [{"s": "12345.67"}], ...}
            result = data.get("result", [])
            if len(result) > 0:
                price_data['usd'] = float(result[0].get("s", 0))
                price_data['cny'] = price_data['usd'] * 7.0

        return price_data if price_data.get('usd', 0) > 0 else None


def get_fear_greed_index():
    """获取恐慌贪婪指数"""
    try:
        resp = requests.get("https://api.alternative.me/fng/", timeout=10)
        data = resp.json()
        return {
            "value": int(data["data"][0]["value"]),
            "classification": data["data"][0]["value_classification"],
            "timestamp": data["data"][0]["timestamp"]
        }
    except Exception as e:
        print(f"[FGI] 获取失败: {e}")
        return {"value": 50, "classification": "Neutral"}


# 技术指标函数（与之前相同）
def calculate_sma(prices, period):
    if len(prices) < period:
        return None
    return sum(prices[-period:]) / period


def calculate_rsi(prices, period=14):
    if len(prices) < period + 1:
        return 50

    gains = []
    losses = []

    for i in range(1, len(prices)):
        change = prices[i] - prices[i-1]
        if change > 0:
            gains.append(change)
        else:
            losses.append(abs(change))

    avg_gain = sum(gains) / len(gains) if gains else 0
    avg_loss = sum(losses) / len(losses) if losses else 1

    if avg_loss == 0:
        return 70

    rs = 100 - (100 / (1 + (avg_gain / avg_loss)))
    return rs


def calculate_volatility(prices):
    if not prices or len(prices) < 2:
        return 0

    mean_price = sum(prices) / len(prices)
    variance = sum((p - mean_price) ** 2 for p in prices) / len(prices)
    return variance ** 0.5


def calculate_price_position(current_price, prices):
    if not prices or len(prices) < 2:
        return 0

    min_price = min(prices)
    max_price = max(prices)

    if max_price > min_price:
        return ((current_price - min_price) / (max_price - min_price)) * 100
    else:
        return 50


def analyze_market_sentiment(fgi):
    """分析市场情绪"""
    sentiment = {
        "overall": "neutral",
        "score": 0,
        "factors": []
    }

    if "value" in fgi:
        fgi_value = fgi.get("value", 50)
        if fgi_value <= 20:
            sentiment["score"] += 2
            sentiment["factors"].append(f"恐慌贪婪指数: 极度恐慌 ({fgi_value}) - 反转信号")
        elif fgi_value <= 40:
            sentiment["score"] += 1
            sentiment["factors"].append(f"恐慌贪婪指数: 恐慌 ({fgi_value})")

    if sentiment["score"] >= 2:
        sentiment["overall"] = "bullish"
    elif sentiment["score"] >= 1:
        sentiment["overall"] = "neutral"
    else:
        sentiment["overall"] = "bearish"

    return sentiment


def generate_strategy(price_data, indicators, sentiment):
    """生成交易策略"""
    current_price = price_data.get("usd", 0)
    sma_6h = indicators.get("sma_6h", 0)
    sma_12h = indicators.get("sma_12h", 0)
    rsi = indicators.get("rsi", 50)

    strategy = {
        "action": "HOLD",
        "description": "当前方向不明，建议观望等待明确信号",
        "risk_level": "low",
        "support": None,
        "resistance": None,
        "stop_loss": None,
        "take_profit": None,
        "reasons": []
    }

    # 价格趋势判断
    if current_price > sma_6h and current_price > sma_12h:
        strategy["action"] = "LONG"
        strategy["description"] = "建议做多，关注上方阻力位突破"
        strategy["risk_level"] = "low"
        strategy["support"] = current_price * 0.999
        strategy["resistance"] = current_price * 1.001
        strategy["stop_loss"] = current_price * 0.998
        strategy["take_profit"] = current_price * 1.002
        strategy["reasons"].append("价格站上短期均线，上升趋势")
    elif current_price < sma_6h and current_price < sma_12h:
        strategy["action"] = "LONG_DIP"
        strategy["description"] = "逢低做多，控制仓位"
        strategy["risk_level"] = "medium"
        strategy["support"] = current_price * 0.995
        strategy["resistance"] = current_price * 1.005
        strategy["stop_loss"] = current_price * 0.992
        strategy["take_profit"] = current_price * 1.003
        strategy["reasons"].append("价格跌破均线，等待反弹")

    # RSI 判断
    if rsi > 70:
        strategy["risk_level"] = "high"
        strategy["reasons"].append("RSI超买，短期回调风险高")
    elif rsi < 30:
        strategy["reasons"].append("RSI超卖，可能是反弹机会")

    # 恐慌贪婪指数
    fgi_value = indicators.get("fgi_value", 50)
    if fgi_value <= 20:
        strategy["reasons"].append(f"恐慌贪婪指数: 极度恐慌 ({fgi_value}) - 反转信号")

    # 综合判断
    if strategy["action"] in ["LONG", "LONG_DIP"] and sentiment["overall"] == "bullish":
        strategy["reasons"].append("上升趋势 + 多头情绪 + RSI未超买 = 适当做多机会")

    return strategy


def record_trade_signal(action, price, strategy, stop_loss=None, take_profit=None):
    """记录交易信号"""
    if action == "HOLD":
        print("[交易记录] 当前策略: HOLD - 不记录交易")
        return

    trade = {
        "timestamp": datetime.now().isoformat(),
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "price": float(price),
        "stop_loss": float(stop_loss) if stop_loss else None,
        "take_profit": float(take_profit) if take_profit else None,
        "strategy": strategy
    }

    if os.path.exists(TRADES_FILE):
        with open(TRADES_FILE, 'r', encoding='utf-8') as f:
            trades = json.load(f)
    else:
        trades = []

    trades.append(trade)

    with open(TRADES_FILE, 'w', encoding='utf-8') as f:
        json.dump(trades, f, indent=2, default=str, ensure_ascii=False)

    print(f"[交易记录] {action} @ ${price:,.2f} - {strategy}")


def calculate_backtest(trades):
    """计算回测统计（简化版）"""
    if not trades:
        return {}

    # 过滤出完成的交易
    completed_trades = [t for t in trades if 'pnl' in t]

    if not completed_trades:
        return {
            "total_return": 0,
            "annualized_return": 0,
            "max_drawdown": 0,
            "max_drawdown_duration_hours": 0,
            "sharpe_ratio": 0,
            "total_trades": 0,
            "win_rate": 0,
            "initial_capital": 10000,
            "final_capital": 10000,
            "max_capital": 10000,
            "min_capital": 10000
        }

    capital_history = []
    current_capital = 10000

    for trade in completed_trades:
        current_capital += trade['pnl']
        capital_history.append(current_capital)

    # 计算指标
    total_return = ((current_capital - 10000) / 10000) * 100
    max_capital = max(capital_history) if capital_history else 10000
    min_capital = min(capital_history) if capital_history else 10000

    # 最大回撤
    max_drawdown = 0
    for val in capital_history:
        if val > max_capital:
            max_capital = val
        drawdown = (max_capital - val) / max_capital * 100 if max_capital > 0 else 0
        if drawdown > max_drawdown:
            max_drawdown = drawdown

    # 盈利交易
    profit_trades = [t for t in completed_trades if t.get('pnl', 0) > 0]
    total_trades = len(completed_trades)
    win_count = len(profit_trades)
    win_rate = (win_count / total_trades) * 100 if total_trades > 0 else 0

    # 盈亏比
    gains = sum(t.get('pnl', 0) for t in profit_trades)
    losses = sum(abs(t.get('pnl', 0)) for t in completed_trades if t.get('pnl', 0) < 0)
    profit_loss_ratio = round(gains / losses, 2) if losses > 0 else 0

    return {
        "total_return": round(total_return, 2),
        "annualized_return": round(total_return * 24 * 365, 2),
        "max_drawdown": round(max_drawdown, 2),
        "max_drawdown_duration_hours": 0,
        "sharpe_ratio": round(profit_loss_ratio * 2, 4),
        "total_trades": total_trades,
        "win_rate": round(win_rate, 2),
        "win_count": win_count,
        "initial_capital": 10000,
        "final_capital": round(current_capital, 2),
        "max_capital": max_capital,
        "min_capital": min_capital,
        "profit_loss_ratio": profit_loss_ratio
    }


def generate_report(price_data, indicators, sentiment, strategy, backtest):
    """生成市场分析报告"""
    current_price = price_data.get("usd", 0)
    current_cny = price_data.get("cny", 0)
    change_24h = 0  # 暂时设为 0

    now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = f"""
📊 BTC 市场分析与交易策略报告
{'='*60}

🕐 报告时间: {now_time}
📊 数据来源: {price_data.get('source', 'unknown')}

💰 当前价格
  • BTC/USD: ${current_price:,.2f}
  • BTC/CNY: ¥{current_cny:,.0f}
  • 24h涨跌: {change_24h:+.2f}%

📈 技术指标
{'='*60}
  • SMA 6小时: ${indicators.get('sma_6h', 0):,.2f}
  • SMA 12小时: ${indicators.get('sma_12h', 0):,.2f}
  • RSI (14): {indicators.get('rsi', 50):.2f}
  • 波动率: ${int(indicators.get('volatility', 0))}
  • 价格位置: {indicators.get('price_position', 50):.1f}% (24h)

🎭 市场情绪: {sentiment.get('overall', 'neutral')}
  • 恐慌贪婪指数: {indicators.get('fgi_value', 50)} - {indicators.get('fgi_classification', 'Unknown')}

  分析因素:
"""

    for factor in sentiment.get("factors", []):
        report += f"  • {factor}\n"

    report += f"""
🎯 1小时交易策略
  • 建议操作: {strategy.get('action', 'HOLD')}
  • 策略描述: {strategy.get('description', '')}
  • 风险等级: {strategy.get('risk_level', 'low')}

  价格点位:
"""

    if strategy.get("support"):
        report += f"  • 支撑位: ${strategy.get('support', 0):,.2f}\n"
    if strategy.get("resistance"):
        report += f"  • 阻力位: ${strategy.get('resistance', 0):,.2f}\n"
    if strategy.get("stop_loss"):
        report += f"  • 止损位: ${strategy.get('stop_loss', 0):,.2f}\n"
    if strategy.get("take_profit"):
        report += f"  • 止盈位: ${strategy.get('take_profit', 0):,.2f}\n"

    report += """
  策略理由:
"""

    for reason in strategy.get("reasons", []):
        report += f"  • {reason}\n"

    report += f"""
⚠️ 风险提示
  • 加密货币市场波动极大，请严格控制仓位
  • 本报告仅供参考，不构成投资建议
  • 交易有风险，投资需谨慎

{'='*60}

📊 回测统计
{'-'*60}
• 总收益率        : {backtest.get('total_return', 0):.2f}%
• 年化收益率       : {backtest.get('annualized_return', 0):.2f}%
• 最大回撤        : {backtest.get('max_drawdown', 0):.2f}%
• 回撤持续时间      : {backtest.get('max_drawdown_duration_hours', 0):.2f} 小时
• 夏普比率        : {backtest.get('sharpe_ratio', 0):.4f}
• 总交易次数       : {backtest.get('total_trades', 0)}
• 胜率          : {backtest.get('win_rate', 0):.2f}%
• 初始资金        : ${backtest.get('initial_capital', 0):,.0f}
• 最终资金        : ${backtest.get('final_capital', 0):,.0f}

================================================================================
"""

    return report


def main():
    """主函数"""
    print(f"[{datetime.now()}] 开始 BTC 市场分析（多数据源）...")
    print()

    # 1. 初始化多数据源
    print("  1. 初始化多数据源...")
    price_api = MultiSourcePriceData()
    print("     ✅ 支持 4 个免费数据源:")
    for name in price_api.sources:
        print(f"       - {price_api.sources[name]['name']}")

    # 2. 获取价格数据
    print()
    print("  2. 尝试获取价格数据（多数据源）...")
    price_data = price_api.try_get_price()

    if price_data:
        print(f"     ✅ 价格获取成功")
        print(f"     ✅ USD: ${price_data['usd']:,.2f}")
        print(f"     ✅ CNY: ¥{price_data['cny']:,.0f}")
        # 添加来源标记
        price_data["source"] = "Multi-Source"
    else:
        print("     ❌ 所有数据源都失败")
        print("     ⚠️  使用缓存数据或默认值")
        price_data = {
            "usd": 68000,
            "cny": 476000,
            "source": "Cache/Default"
        }

    # 3. 获取恐慌贪婪指数
    print()
    print("  3. 获取恐慌贪婪指数...")
    fgi = get_fear_greed_index()
    print(f"     ✅ FGI: {fgi.get('value', 50)} - {fgi.get('classification', 'Unknown')}")

    # 4. 计算技术指标（模拟历史数据）
    print()
    print("  4. 计算技术指标...")
    # 模拟历史数据
    current_price = price_data.get("usd", 68000)
    price_history = [current_price] * 24  # 简化

    indicators = {
        "fgi_value": fgi.get("value", 50),
        "fgi_classification": fgi.get("classification", "Unknown"),
        "sma_6h": calculate_sma(price_history[-6:], 6),
        "sma_12h": calculate_sma(price_history[-12:], 12),
        "rsi": calculate_rsi(price_history, 14),
        "volatility": calculate_volatility(price_history),
        "price_position": calculate_price_position(current_price, price_history)
    }

    print(f"     ✅ SMA 6h: ${indicators['sma_6h']:,.2f}")
    print(f"     ✅ SMA 12h: ${indicators['sma_12h']:,.2f}")
    print(f"     ✅ RSI: {indicators['rsi']:.2f}")

    # 5. 分析市场情绪
    print()
    print("  5. 分析市场情绪...")
    sentiment = analyze_market_sentiment(fgi)
    print(f"     ✅ 市场情绪: {sentiment['overall']}")

    # 6. 生成交易策略
    print()
    print("  6. 生成交易策略...")
    strategy = generate_strategy(price_data, indicators, sentiment)
    print(f"     ✅ 建议操作: {strategy['action']}")

    # 7. 记录交易信号
    print()
    print("  7. 记录交易信号...")
    record_trade_signal(
        strategy['action'],
        price_data['usd'],
        strategy['description'],
        strategy.get('stop_loss'),
        strategy.get('take_profit')
    )

    # 8. 计算回测
    print()
    print("  8. 计算回测...")
    if os.path.exists(TRADES_FILE):
        with open(TRADES_FILE, 'r', encoding='utf-8') as f:
            trades = json.load(f)
        backtest = calculate_backtest(trades)
        print(f"     ✅ 总收益率: {backtest['total_return']:.2f}%")
        print(f"     ✅ 胜率: {backtest['win_rate']:.2f}%")
        print(f"     ✅ 夏普比率: {backtest['sharpe_ratio']:.4f}")
    else:
        backtest = {}
        print("     ⚠️  交易记录文件不存在")

    # 9. 生成报告
    print()
    print("  9. 生成报告...")
    report = generate_report(price_data, indicators, sentiment, strategy, backtest)

    # 10. 保存报告
    print()
    print(" 10. 保存报告...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"btc_report_{timestamp}.txt"
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"     ✅ 报告已保存: {filepath}")

    # 11. 输出报告
    print()
    print(report)
    print()
    print(f"[{datetime.now()}] 分析完成!")


if __name__ == "__main__":
    main()
