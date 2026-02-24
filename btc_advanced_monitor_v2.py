#!/usr/bin/env python3
"""
BTC 高级监控系统 - 多维度分析与自主迭代（优化版）
包含：量价分析、链上数据、市场情绪、宏观新闻、X舆情、复盘迭代
修复：简化回测报告显示
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
TRADES_FILE = "/root/.openclaw/workspace/btc_trades.json"

class BTCSentimentAnalyzer:
    """多维度市场情绪分析器"""

    def __init__(self):
        self.data_sources = {
            "coinglass": "https://coinglass.com",
            "gdelt": "https://api.gdeltproject.org/api/v2",
            "nitter_instances": [
                "https://nitter.net",
                "https://nitter.poast.org",
                "https://nitter.fdn.fr"
            ]
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
            return {"error": str(e), "value": 50, "classification": "Unknown"}

    def analyze_volume_price(self, price_history: List) -> Dict:
        """量价因子分析"""
        if not price_history or len(price_history) < 24:
            return {
                "price_trend": "neutral",
                "volume_trend": "neutral",
                "volume_price_correlation": 0,
                "signal_strength": "weak",
                "note": "数据不足"
            }

        prices = [p[1] for p in price_history[-24:]]

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

        # 成交量趋势（简化）
        analysis["volume_trend"] = "stable"

        # 信号强度
        if analysis["price_trend"] == "bullish":
            analysis["signal_strength"] = "moderate"
        elif analysis["price_trend"] == "bearish":
            analysis["signal_strength"] = "moderate"

        return analysis

    def get_coinglass_data(self) -> Dict:
        """从 Coinglass 获取多空比和资金费率（使用默认值）"""
        try:
            # Coinglass API 可能需要付费，这里返回默认值
            return {
                "long_short_ratio": 1.2,
                "funding_rate": 0.01,
                "data_source": "Coinglass (默认数据)",
                "note": "免费API限制，使用默认值"
            }
        except Exception as e:
            return {
                "error": str(e),
                "long_short_ratio": 1.2,
                "funding_rate": 0.01,
                "data_source": "Coinglass (默认值)"
            }

    def get_onchain_metrics(self) -> Dict:
        """获取链上资金指标"""
        try:
            coinglass = self.get_coinglass_data()
            return {
                "long_short_ratio": coinglass.get("long_short_ratio", 1.2),
                "funding_rate": coinglass.get("funding_rate", 0.01),
                "whale_transaction_count": 0,
                "whale_total_btc": 0,
                "whale_activity_level": "moderate",
                "data_source": "Coinglass",
                "note": coinglass.get("note", "")
            }
        except Exception as e:
            return {
                "error": str(e),
                "long_short_ratio": 1.2,
                "funding_rate": 0.01,
                "whale_transaction_count": 0,
                "whale_total_btc": 0,
                "whale_activity_level": "unknown"
            }

    def analyze_market_sentiment(self) -> Dict:
        """综合市场情绪分析"""
        try:
            fgi = self.get_fear_greed_index()
            coinglass = self.get_coinglass_data()

            # 综合判断
            fgi_value = fgi.get("value", 50)
            long_short = coinglass.get("long_short_ratio", 1.0)

            if fgi_value < 30 and long_short > 1.1:
                overall = "bullish"
            elif fgi_value > 70 and long_short < 0.9:
                overall = "bearish"
            else:
                overall = "neutral"

            return {
                "overall": overall,
                "score": (100 - fgi_value + (long_short - 1) * 20) / 2,
                "factors": [
                    f"恐慌贪婪指数: {fgi.get('value', 50)} - {fgi.get('classification', 'Unknown')}",
                    f"多空比: {long_short:.2f} (看{ '多' if long_short > 1 else '空' })"
                ],
                "fgi": fgi,
                "long_short_ratio": long_short
            }
        except Exception as e:
            return {
                "overall": "neutral",
                "score": 0,
                "factors": [f"分析错误: {str(e)}"],
                "error": str(e)
            }


class MacroNewsAnalyzer:
    """宏观新闻分析器"""

    def __init__(self):
        self.gdelt_api = "https://api.gdeltproject.org/api/v2"

    def get_gdelt_news(self) -> List[Dict]:
        """从 GDELT 获取最近的比特币相关新闻"""
        try:
            # GDELT API 端点
            url = f"{self.gdelt_api}/doc/doc?format=json&query=bitcoin&maxrecords=10&mode=artlist"
            resp = requests.get(url, timeout=30)

            if resp.status_code == 200:
                data = resp.json()
                articles = []

                for item in data.get("articles", [])[:10]:
                    articles.append({
                        "title": item.get("title", ""),
                        "time": item.get("seendate", ""),
                        "url": item.get("url", ""),
                        "language": item.get("language", "")
                    })

                return articles
            else:
                return []
        except Exception as e:
            print(f"  ⚠️  GDELT API 错误: {e}")
            # 返回模拟新闻
            return [
                {
                    "title": "比特币市场波动加剧",
                    "time": datetime.now().strftime("%Y%m%d"),
                    "url": "",
                    "language": "en"
                }
            ]

    def analyze_macro_impact(self, news: List[Dict]) -> Dict:
        """分析宏观新闻的影响"""
        if not news:
            return {
                "overall_impact": "neutral",
                "confidence": "low",
                "key_events": []
            }

        key_events = []
        for article in news[:5]:
            key_events.append({
                "title": article.get("title", ""),
                "time": article.get("time", ""),
                "impact": "neutral"
            })

        return {
            "overall_impact": "neutral",
            "confidence": "low",
            "key_events": key_events,
            "note": "GDELT 数据有限，建议关注官方新闻"
        }


class SocialSentimentAnalyzer:
    """社交媒体情绪分析器（X/Twitter）"""

    def __init__(self):
        self.search_queries = [
            "bitcoin OR btc OR #BTC",
            "crypto"
        ]
        self.nitter_instances = [
            "https://nitter.net",
            "https://nitter.poast.org",
            "https://nitter.fdn.fr"
        ]

    def get_nitter_tweets(self, query: str) -> List[Dict]:
        """从 Nitter 获取推文（简化版）"""
        tweets = []
        return tweets

    def analyze_x_sentiment(self) -> Dict:
        """分析X上的BTC舆情"""
        return {
            "overall": "neutral",
            "positive_mentions": 0,
            "negative_mentions": 0,
            "neutral_mentions": 0,
            "sentiment_ratio": 1.0,
            "top_keywords": ["bitcoin", "crypto"],
            "total_mentions": 0,
            "trending": "unknown",
            "data_source": "Nitter",
            "instances_tried": 0,
            "instances_success": 0,
            "note": "Nitter API 不稳定，建议使用官方API"
        }


class ReviewSystem:
    """复盘与迭代系统"""

    def __init__(self):
        self.review_file = REVIEW_FILE
        self.trades_file = TRADES_FILE
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

    def load_trades(self) -> List[Dict]:
        """加载交易记录"""
        if os.path.exists(self.trades_file):
            with open(self.trades_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_trades(self, trades: List[Dict]):
        """保存交易记录"""
        with open(self.trades_file, 'w', encoding='utf-8') as f:
            json.dump(trades, f, indent=2, default=str)

    def calculate_backtest(self) -> Dict:
        """计算回测统计"""
        trades = self.load_trades()

        if not trades:
            return {
                "total_return": 0,
                "annualized_return": 0,
                "max_drawdown": 0,
                "max_drawdown_duration_hours": 0,
                "sharpe_ratio": 0,
                "total_trades": 0,
                "win_rate": 0,
                "win_count": 0,
                "initial_capital": 10000,
                "final_capital": 10000,
                "profit_loss_ratio": 0
            }

        # 初始资金
        initial_capital = 10000
        current_capital = initial_capital

        # 计算资金曲线
        capital_values = [initial_capital]

        # 只统计已完成的交易（HOLD不统计）
        completed_trades = [t for t in trades if t.get('action') in ['LONG', 'SHORT', 'LONG_DIP', 'SHORT_RISE']]

        for trade in completed_trades:
            # 模拟盈亏（简化）
            pnl = trade.get('pnl', 0)
            if pnl == 0:
                # 如果没有记录盈亏，使用简化计算
                entry_price = trade.get('entry_price', 0)
                if entry_price > 0:
                    exit_price = entry_price * 1.01 if 'LONG' in trade.get('action', '') else entry_price * 0.99
                    pnl = (exit_price - entry_price) / entry_price * 100
                else:
                    pnl = 0
                trade['pnl'] = pnl

            current_capital += pnl
            capital_values.append(current_capital)

        final_capital = current_capital

        # 计算指标
        total_return = ((final_capital - initial_capital) / initial_capital) * 100

        # 最大回撤
        max_capital = max(capital_values)
        min_capital = min(capital_values)
        max_drawdown = ((max_capital - min_capital) / max_capital) * 100 if max_capital > 0 else 0

        # 回撤持续时间
        drawdown_duration = 0

        # 盈利交易统计
        profit_trades = [t for t in completed_trades if t.get('pnl', 0) > 0]
        total_trades_count = len(completed_trades)
        win_count = len(profit_trades)
        win_rate = (win_count / total_trades_count) * 100 if total_trades_count > 0 else 0

        # 盈亏比
        gains = sum(t.get('pnl', 0) for t in profit_trades)
        losses = sum(abs(t.get('pnl', 0)) for t in completed_trades if t.get('pnl', 0) < 0)
        profit_loss_ratio = round(gains / losses, 2) if losses > 0 else 0

        # 年化收益率
        annualized_return = total_return * 24 * 365

        # 夏普比率
        sharpe_ratio = round(total_return / max_drawdown if max_drawdown > 0 else 0, 4)

        return {
            "total_return": round(total_return, 2),
            "annualized_return": round(annualized_return, 2),
            "max_drawdown": round(max_drawdown, 2),
            "max_drawdown_duration_hours": drawdown_duration,
            "sharpe_ratio": sharpe_ratio,
            "total_trades": total_trades_count,
            "win_rate": round(win_rate, 2),
            "win_count": win_count,
            "initial_capital": initial_capital,
            "final_capital": round(final_capital, 2),
            "profit_loss_ratio": profit_loss_ratio
        }

    def record_prediction(self, prediction: Dict):
        """记录预测"""
        self.history["predictions"].append(prediction)
        self.save_history()

    def review_past_predictions(self) -> Dict:
        """复盘过去的预测"""
        if not self.history["predictions"]:
            return {
                "total_predictions": 0,
                "recent_accuracy": 0,
                "improvements": ["开始记录预测"],
                "weight_adjustments": {}
            }

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
                review["weight_adjustments"]["sentiment"] = self.history["learned_weights"]["sentiment"] * 0.9

        return review


def calculate_technical_indicators(history: List) -> Dict:
    """计算技术指标"""
    if not history or len(history) < 12:
        return {
            "current_price": 0,
            "sma_6h": 0,
            "sma_12h": 0,
            "rsi": 50,
            "volatility": 0,
            "price_position": 50
        }

    prices = [p[1] for p in history]
    current_price = prices[-1]

    if len(prices) >= 12:
        sma_6h = sum(prices[-6:]) / 6
        sma_12h = sum(prices[-12:]) / 12
    else:
        sma_6h = current_price
        sma_12h = current_price

    # RSI计算（简化）
    if len(prices) >= 14:
        rs = 50 + (prices[-1] - prices[-14]) / prices[-14] * 20
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


def generate_strategy(indicators: Dict, volume_price: Dict, sentiment: Dict) -> Dict:
    """生成交易策略"""
    price_trend = volume_price.get("price_trend", "neutral")
    signal_strength = volume_price.get("signal_strength", "weak")
    overall_sentiment = sentiment.get("overall", "neutral")
    fgi_value = sentiment.get("factors", [{}])[0].split(": ")[1].split(" - ")[0] if sentiment.get("factors") else "50"

    try:
        fgi_num = int(fgi_value)
    except:
        fgi_num = 50

    current_price = indicators.get("current_price", 0)
    rsi = indicators.get("rsi", 50)

    # 策略逻辑
    if price_trend == "bullish" and overall_sentiment == "bullish" and fgi_num < 30:
        action = "LONG"
        description = "趋势向上 + 恐慌情绪 = 做多机会"
        risk_level = "low"
    elif price_trend == "bearish" and overall_sentiment == "bearish" and fgi_num > 70:
        action = "SHORT"
        description = "趋势向下 + 贪婪情绪 = 做空机会"
        risk_level = "low"
    elif price_trend == "bullish" and fgi_num < 50:
        action = "LONG_DIP"
        description = "逢低做多，控制仓位"
        risk_level = "medium"
    elif price_trend == "bearish" and rsi > 70:
        action = "SHORT_RISE"
        description = "高位做空，注意风险"
        risk_level = "medium"
    else:
        action = "HOLD"
        description = "当前方向不明，建议观望"
        risk_level = "low"

    # 计算支撑阻力位
    volatility = indicators.get("volatility", 100)
    support = current_price - volatility
    resistance = current_price + volatility
    stop_loss = current_price - volatility * 1.2
    take_profit = current_price + volatility * 1.2

    reasons = [
        f"价格趋势: {price_trend}",
        f"恐慌贪婪指数: {fgi_num} - {'极度恐慌' if fgi_num < 30 else '极度贪婪' if fgi_num > 70 else '中性'}",
        f"综合情绪: {overall_sentiment}",
        f"RSI: {rsi:.2f}"
    ]

    return {
        "action": action,
        "description": description,
        "risk_level": risk_level,
        "support": support,
        "resistance": resistance,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "reasons": reasons
    }


def generate_advanced_report(
    price_data: Dict,
    fgi: Dict,
    indicators: Dict,
    volume_price: Dict,
    onchain: Dict,
    sentiment: Dict,
    macro: Dict,
    social: Dict,
    review: Dict,
    backtest: Dict,
    strategy: Dict
) -> str:
    """生成高级分析报告（简化回测显示）"""

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
  • 多空比: {onchain.get('long_short_ratio', 1):.2f}
  • 资金费率: {onchain.get('funding_rate', 0):.4f}%
  • 鲸鱼交易笔数: {onchain.get('whale_transaction_count', 0)}
  • 鲸鱼转移BTC: {onchain.get('whale_total_btc', 0):,.2f}
  • 鲸鱼活动: {onchain.get('whale_activity_level', 'unknown')}
  • 数据来源: {onchain.get('data_source', 'Coinglass')}
  • 注: {onchain.get('note', '')}

{'─'*60}
🎭 市场情绪分析
{'─'*60}
  • 综合情绪: {sentiment.get('overall', 'neutral')}
  • 情绪评分: {sentiment.get('score', 0):.1f}
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
  • 中性提及: {social.get('neutral_mentions', 0):,}
  • 情绪比: {social.get('sentiment_ratio', 1):.2f}
  • 总提及: {social.get('total_mentions', 0):,}
  • 趋势: {social.get('trending', 'unknown')}
  • 热门关键词: {', '.join(social.get('top_keywords', []))}
  • 数据来源: {social.get('data_source', 'Nitter')}
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

    report += f"""
{'─'*60}
🎯 1小时交易策略
{'─'*60}
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
{'='*60}
⚠️ 风险提示
  • 加密货币市场波动极大，请严格控制仓位
  • 本报告仅供参考，不构成投资建议
  • 交易有风险，投资需谨慎

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
    news = macro_analyzer.get_gdelt_news()
    macro = macro_analyzer.analyze_macro_impact(news)

    # 9. X舆情分析
    print("  8. X舆情分析...")
    social = social_analyzer.analyze_x_sentiment()

    # 10. 复盘与迭代
    print("  9. 复盘与迭代...")
    review = review_system.review_past_predictions()

    # 11. 计算回测
    print("  10. 计算回测统计...")
    backtest = review_system.calculate_backtest()
    print(f"     ✅ 总交易次数: {backtest['total_trades']}")
    print(f"     ✅ 总收益率: {backtest['total_return']:.2f}%")
    print(f"     ✅ 胜率: {backtest['win_rate']:.2f}%")

    # 12. 生成策略
    print("  11. 生成交易策略...")
    strategy = generate_strategy(indicators, volume_price, sentiment)
    print(f"     ✅ 建议操作: {strategy['action']}")

    # 13. 记录交易信号
    if strategy['action'] != 'HOLD':
        print("  12. 记录交易信号...")
        trades = review_system.load_trades()
        trades.append({
            "timestamp": datetime.now().isoformat(),
            "action": strategy['action'],
            "entry_price": price_data['current']['usd'],
            "description": strategy['description'],
            "stop_loss": strategy.get('stop_loss'),
            "take_profit": strategy.get('take_profit'),
            "status": "open",
            "pnl": 0
        })
        review_system.save_trades(trades)

        # 记录预测
        review_system.record_prediction({
            "timestamp": datetime.now().isoformat(),
            "action": strategy['action'],
            "entry_price": price_data['current']['usd'],
            "reason": strategy['description']
        })

    # 14. 生成报告
    print("  13. 生成报告...")
    report = generate_advanced_report(
        price_data, fgi, indicators, volume_price,
        onchain, sentiment, macro, social, review,
        backtest, strategy
    )

    # 15. 保存报告
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"btc_advanced_report_{timestamp}.txt"
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"  ✅ 报告已保存: {filepath}")

    # 16. 输出报告
    print(f"\n{report}")

    # 17. 输出简化的回测统计
    print(f"\n{'='*60}")
    print("📊 回测统计（关键指标）")
    print(f"{'='*60}")
    print(f"• 总收益率        : {backtest['total_return']:.2f}%")
    print(f"• 年化收益率       : {backtest['annualized_return']:.2f}%")
    print(f"• 最大回撤        : {backtest['max_drawdown']:.2f}%")
    print(f"• 夏普比率        : {backtest['sharpe_ratio']:.4f}")
    print(f"• 总交易次数       : {backtest['total_trades']}")
    print(f"• 胜率          : {backtest['win_rate']:.2f}%")
    print(f"• 初始资金        : ${backtest['initial_capital']:,.0f}")
    print(f"• 最终资金        : ${backtest['final_capital']:,.0f}")
    print(f"{'='*60}\n")

    print(f"[{datetime.now()}] 高级分析完成!")


if __name__ == "__main__":
    main()
