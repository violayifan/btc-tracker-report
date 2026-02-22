#!/usr/bin/env python3
"""
BTC 高级监控系统 - 多维度分析与自主迭代
包含：量价分析、链上数据、市场情绪、宏观新闻、X舆情、复盘迭代
"""

import requests
import json
import os
import datetime as dt_module
from typing import Dict, List
import re

# 使用模块导入避免冲突
datetime = dt_module.datetime
timedelta = dt_module.timedelta

# 配置
COINGECKO_API = "https://api.coingecko.com/api/v3"
OUTPUT_DIR = "/root/.openclaw/workspace/reports"
REVIEW_FILE = "/root/.openclaw/workspace/btc_review_history.json"

class BTCSentimentAnalyzer:
    """多维度市场情绪分析器"""

    def __init__(self):
        self.data_sources = {
            "coinglass": "https://api.coinlass.io/v1/indicator",  # 恐慌贪婪指数
            "cryptoquant": "https://api.cryptoquant.com/v1",  # 链上数据
            # 可以添加更多数据源
        }

    def get_fear_greed_index(self) -> Dict:
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
            return {"error": str(e)}

    def analyze_volume_price(self, price_history: List) -> Dict:
        """量价因子分析"""
        if not price_history or len(price_history) < 24:
            return {"error": "数据不足"}

        prices = [p[1] for p in price_history[-24:]]
        volumes = [p[2] if len(p) > 2 else 0 for p in price_history[-24:]]

        analysis = {
            "price_trend": "neutral",
            "volume_trend": "neutral",
            "volume_price_correlation": 0,
            "signal_strength": "weak"
        }

        # 价格趋势
        if prices[-1] > prices[0]:
            analysis["price_trend"] = "bullish"
        elif prices[-1] < prices[0]:
            analysis["price_trend"] = "bearish"

        # 成交量趋势
        if sum(volumes[-5:]) > sum(volumes[-10:-5]):
            analysis["volume_trend"] = "increasing"

        # 量价配合度
        price_changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        volume_changes = [volumes[i] - volumes[i-1] for i in range(1, len(volumes))]

        if len(price_changes) == len(volume_changes):
            correlation = sum(pc * vc for pc, vc in zip(price_changes, volume_changes))
            analysis["volume_price_correlation"] = round(correlation / max(1, sum(abs(pc) for pc in price_changes)), 2)

        # 信号强度
        if analysis["price_trend"] == "bullish" and analysis["volume_trend"] == "increasing":
            analysis["signal_strength"] = "strong"

        return analysis

    def get_onchain_metrics(self) -> Dict:
        """链上资金情况（模拟数据，实际需要API密钥）"""
        # 实际应用中需要接入 CryptoQuant、Glassnode 等
        return {
            "net_flow": -150.5,  # 净流入（BTC），负数表示流出
            "exchange_balance": 2450000,  # 交易所余额
            "whale_activity": "moderate",  # 鲸鱼活动
            "long_short_ratio": 1.2,  # 多空比
            "funding_rate": 0.01,  # 资金费率
            "note": "数据为模拟，实际需要接入 CryptoQuant API"
        }

    def analyze_market_sentiment(self) -> Dict:
        """综合市场情绪分析"""
        fgi = self.get_fear_greed_index()

        sentiment = {
            "overall": "neutral",
            "score": 0,
            "factors": []
        }

        if "error" not in fgi:
            fgi_value = fgi.get("value", 50)
            if fgi_value <= 20:
                sentiment["score"] += 2
                sentiment["factors"].append(f"恐慌贪婪指数: 极度恐慌 ({fgi_value}) - 反转信号")
            elif fgi_value <= 40:
                sentiment["score"] += 1
                sentiment["factors"].append(f"恐慌贪婪指数: 恐慌 ({fgi_value})")

        return sentiment


class MacroNewsAnalyzer:
    """宏观新闻分析器"""

    def __init__(self):
        # 可以接入新闻 API (NewsAPI, Alpha Vantage 等)
        pass

    def get_macro_news(self) -> List[Dict]:
        """获取宏观新闻（模拟数据）"""
        # 实际应用中需要接入真实新闻 API
        return [
            {
                "title": "美联储暗示维持利率不变",
                "impact": "positive",
                "relevance": "high",
                "time": "2026-02-22 10:00"
            },
            {
                "title": "CPI 数据显示通胀降温",
                "impact": "positive",
                "relevance": "high",
                "time": "2026-02-22 08:30"
            }
        ]

    def analyze_macro_impact(self, news_list: List[Dict]) -> Dict:
        """分析宏观新闻对BTC的影响"""
        positive_count = sum(1 for n in news_list if n.get("impact") == "positive")
        negative_count = sum(1 for n in news_list if n.get("impact") == "negative")

        if positive_count > negative_count:
            impact = "bullish"
        elif negative_count > positive_count:
            impact = "bearish"
        else:
            impact = "neutral"

        return {
            "overall_impact": impact,
            "key_events": news_list[:3],
            "confidence": "medium"
        }


class SocialSentimentAnalyzer:
    """X (Twitter) 舆情分析器"""

    def __init__(self):
        # 可以接入 Twitter API (需要申请密钥)
        pass

    def analyze_x_sentiment(self) -> Dict:
        """分析X上的BTC舆情（模拟数据）"""
        # 实际应用中需要接入 Twitter API
        return {
            "overall": "bullish",
            "positive_mentions": 1250,
            "negative_mentions": 890,
            "sentiment_ratio": 1.4,
            "top_keywords": ["ETF", "halving", "institutional"],
            "influencer_sentiment": "positive",
            "note": "数据为模拟，实际需要接入 Twitter API"
        }


class ReviewSystem:
    """复盘与迭代系统"""

    def __init__(self):
        self.review_file = REVIEW_FILE
        self.load_history()

    def load_history(self):
        """加载历史复盘记录"""
        if os.path.exists(self.review_file):
            with open(self.review_file, 'r', encoding='utf-8') as f:
                self.history = json.load(f)
        else:
            self.history = {
                "predictions": [],
                "accuracy": {
                    "correct": 0,
                    "total": 0,
                    "rate": 0
                },
                "learned_weights": {
                    "volume_price": 0.3,
                    "onchain": 0.2,
                    "sentiment": 0.2,
                    "macro": 0.15,
                    "social": 0.15
                }
            }

    def save_history(self):
        """保存历史复盘记录"""
        with open(self.review_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, default=str)

    def record_prediction(self, prediction: Dict):
        """记录预测"""
        self.history["predictions"].append(prediction)
        self.save_history()

    def review_past_predictions(self) -> Dict:
        """复盘过去的预测"""
        if not self.history["predictions"]:
            return {"status": "no_history"}

        review = {
            "total_predictions": len(self.history["predictions"]),
            "recent_accuracy": self.history["accuracy"]["rate"],
            "improvements": [],
            "weight_adjustments": {}
        }

        # 检查最近5次预测的准确性
        recent = self.history["predictions"][-5:]
        correct = sum(1 for p in recent if p.get("result", "").lower() in ["correct", "profit"])

        if len(recent) > 0:
            recent_rate = correct / len(recent)
            if recent_rate < 0.6:
                review["improvements"].append("预测准确率低于60%，需要调整权重")
                # 调整权重：降低表现差的因子权重
                review["weight_adjustments"]["sentiment"] = self.history["learned_weights"]["sentiment"] * 0.9

        return review

    def update_weights(self, factors: Dict[str, float]):
        """根据复盘结果更新权重"""
        for factor, adjustment in factors.items():
            if factor in self.history["learned_weights"]:
                self.history["learned_weights"][factor] = adjustment

        # 归一化权重
        total = sum(self.history["learned_weights"].values())
        if total > 0:
            for key in self.history["learned_weights"]:
                self.history["learned_weights"][key] /= total

        self.save_history()


def generate_advanced_report(
    price_data: Dict,
    fgi: Dict,
    indicators: Dict,
    volume_price: Dict,
    onchain: Dict,
    sentiment: Dict,
    macro: Dict,
    social: Dict,
    review: Dict
) -> str:
    """生成高级分析报告"""

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    current = price_data.get("current", {})
    price = current.get("usd", 0)
    price_cny = current.get("cny", 0)
    change_24h = current.get("usd_24h_change", 0)

    report = f"""
📊 BTC 多维度市场分析与交易策略报告
{'='*60}

🕐 报告时间: {now}

💰 当前价格
  • BTC/USD: ${price:,.2f}
  • BTC/CNY: ¥{price_cny:,.0f}
  • 24h涨跌: {change_24h:+.2f}%

{'─'*60}
📈 技术指标
{'─'*60}
  • SMA 6小时: ${indicators.get('sma_6h', 0):,.2f}
  • SMA 12小时: ${indicators.get('sma_12h', 0):,.2f}
  • RSI (14): {indicators.get('rsi', 50):.2f}
  • 波动率: ${int(indicators.get('volatility', 0))}
  • 价格位置: {indicators.get('price_position', 50):.1f}% (24h)

{'─'*60}
🔬 量价因子分析
{'─'*60}
  • 价格趋势: {volume_price.get('price_trend', 'neutral')}
  • 成交量趋势: {volume_price.get('volume_trend', 'neutral')}
  • 量价相关性: {volume_price.get('volume_price_correlation', 0):.2f}
  • 信号强度: {volume_price.get('signal_strength', 'weak')}

{'─'*60}
⛓️ 链上资金情况
{'─'*60}
  • 净流入/流出: {onchain.get('net_flow', 0):+.1f} BTC
  • 交易所余额: {onchain.get('exchange_balance', 0):,.0f} BTC
  • 鲸鱼活动: {onchain.get('whale_activity', 'unknown')}
  • 多空比: {onchain.get('long_short_ratio', 1):.2f}
  • 资金费率: {onchain.get('funding_rate', 0):.4f}%
  • 注: {onchain.get('note', '')}

{'─'*60}
🎭 市场情绪分析
{'─'*60}
  • 综合情绪: {sentiment.get('overall', 'neutral')}
  • 情绪评分: {sentiment.get('score', 0)}
  • 恐慌贪婪指数: {fgi.get('value', 0)} - {fgi.get('classification', 'Unknown')}

  关键因素:
"""
    for factor in sentiment.get("factors", []):
        report += f"  • {factor}\n"

    report += f"""
{'─'*60}
📰 宏观新闻分析
{'─'*60}
  • 整体影响: {macro.get('overall_impact', 'neutral')}
  • 置信度: {macro.get('confidence', 'low')}

  关键事件:
"""
    for event in macro.get("key_events", []):
        impact_icon = "📈" if event.get("impact") == "positive" else "📉"
        report += f"  {impact_icon} {event.get('title', '')} ({event.get('time', '')})\n"

    report += f"""
{'─'*60}
🐦 X (Twitter) 市场舆情
{'─'*60}
  • 整体情绪: {social.get('overall', 'neutral')}
  • 正面提及: {social.get('positive_mentions', 0):,}
  • 负面提及: {social.get('negative_mentions', 0):,}
  • 情绪比: {social.get('sentiment_ratio', 1):.2f}
  • 热门关键词: {', '.join(social.get('top_keywords', []))}
  • 影响者情绪: {social.get('influencer_sentiment', 'neutral')}
  • 注: {social.get('note', '')}

{'─'*60}
📋 复盘与迭代
{'─'*60}
  • 总预测次数: {review.get('total_predictions', 0)}
  • 最近准确率: {review.get('recent_accuracy', 0):.1%}
"""

    if review.get("improvements"):
        report += "  • 改进建议:\n"
        for imp in review["improvements"]:
            report += f"    - {imp}\n"

    if review.get("weight_adjustments"):
        report += "  • 权重调整:\n"
        for key, value in review["weight_adjustments"].items():
            report += f"    - {key}: {value:.2f}\n"

    report += f"""
{'='*60}
"""

    return report


def main():
    """主函数"""
    print(f"[{datetime.now()}] 开始 BTC 高级市场分析...")

    # 1. 初始化分析器
    print("  初始化分析器...")
    sentiment_analyzer = BTCSentimentAnalyzer()
    macro_analyzer = MacroNewsAnalyzer()
    social_analyzer = SocialSentimentAnalyzer()
    review_system = ReviewSystem()

    # 2. 获取价格数据
    print("  1. 获取价格数据...")
    try:
        price_resp = requests.get(
            f"{COINGECKO_API}/simple/price?ids=bitcoin&vs_currencies=usd,cny&include_24hr_change=true",
            timeout=30
        )
        price_data = {"current": price_resp.json().get("bitcoin", {})}

        history_resp = requests.get(
            f"{COINGECKO_API}/coins/bitcoin/market_chart?vs_currency=usd&days=1",
            timeout=30
        )
        price_data["history"] = history_resp.json().get("prices", [])
    except Exception as e:
        print(f"  ❌ 价格数据获取失败: {e}")
        return

    # 3. 获取恐慌贪婪指数
    print("  2. 获取恐慌贪婪指数...")
    fgi = sentiment_analyzer.get_fear_greed_index()

    # 4. 计算技术指标
    print("  3. 计算技术指标...")
    indicators = calculate_technical_indicators(price_data.get("history", []))

    # 5. 量价因子分析
    print("  4. 量价因子分析...")
    volume_price = sentiment_analyzer.analyze_volume_price(price_data.get("history", []))

    # 6. 链上资金分析
    print("  5. 链上资金分析...")
    onchain = sentiment_analyzer.get_onchain_metrics()

    # 7. 市场情绪分析
    print("  6. 市场情绪分析...")
    sentiment = sentiment_analyzer.analyze_market_sentiment()

    # 8. 宏观新闻分析
    print("  7. 宏观新闻分析...")
    news = macro_analyzer.get_macro_news()
    macro = macro_analyzer.analyze_macro_impact(news)

    # 9. X舆情分析
    print("  8. X舆情分析...")
    social = social_analyzer.analyze_x_sentiment()

    # 10. 复盘与迭代
    print("  9. 复盘与迭代...")
    review = review_system.review_past_predictions()

    # 11. 生成报告
    print("  10. 生成报告...")
    report = generate_advanced_report(
        price_data, fgi, indicators, volume_price,
        onchain, sentiment, macro, social, review
    )

    # 12. 保存报告
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"btc_advanced_report_{timestamp}.txt"
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"  ✅ 报告已保存: {filepath}")
    print(f"\n{report}")
    print(f"[{datetime.now()}] 高级分析完成!")


def calculate_technical_indicators(history: List) -> Dict:
    """计算技术指标"""
    if not history or len(history) < 12:
        return {
            "current_price": 0,
            "sma_6h": 0,
            "sma_12h": 0,
            "rsi": 50,
            "volatility": 0,
            "price_position": 0
        }

    prices = [p[1] for p in history]
    current_price = prices[-1]

    if len(prices) >= 12:
        sma_6h = sum(prices[-6:]) / 6
        sma_12h = sum(prices[-12:]) / 12
    else:
        sma_6h = current_price
        sma_12h = current_price

    # RSI计算
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

    # 波动率
    volatility = 0
    if len(prices) >= 24:
        mean_price = sum(prices[-24:]) / 24
        variance = sum((p - mean_price) ** 2 for p in prices[-24:]) / 24
        volatility = variance ** 0.5

    # 价格位置
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


if __name__ == "__main__":
    main()
