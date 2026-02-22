# BTC 高级监控系统

## 📊 系统概述

这是一个多维度、自主迭代的BTC市场监控系统，每小时自动分析市场情况并更新到GitHub Pages。

## 🚀 核心功能

### 1. **多维度分析**

#### 📈 技术指标
- SMA 6小时/12小时
- RSI (14)
- 波动率
- 价格位置

#### 🔬 量价因子分析
- 价格趋势（多头/空头/中性）
- 成交量趋势
- 量价相关性
- 信号强度

#### ⛓️ 链上资金情况
- 净流入/流出
- 交易所余额
- 鲸鱼活动
- 多空比
- 资金费率

#### 🎭 市场情绪分析
- 恐慌贪婪指数
- 综合情绪评分
- 关键因素

#### 📰 宏观新闻分析
- 美联储政策
- CPI/PCE数据
- 就业数据
- 整体影响评估

#### 🐦 X (Twitter) 舆情分析
- 正面/负面提及
- 情绪比
- 热门关键词
- 影响者情绪

#### 📋 复盘与迭代
- 预测准确率追踪
- 权重自动调整
- 策略持续优化

## 📁 文件结构

```
/root/.openclaw/workspace/
├── btc_monitor.py              # 基础监控系统
├── btc_advanced_monitor.py      # 高级监控系统（新增）
├── btc_tracker.py              # 回测与绩效分析
├── btc_html_report_v2.py      # HTML报告生成
├── auto_update.sh              # 自动更新脚本
├── btc_trades.json            # 交易记录
├── btc_review_history.json     # 复盘历史（新增）
├── reports/                   # 分析报告目录
│   ├── btc_report_*.txt      # 基础报告
│   └── btc_advanced_report_*.txt  # 高级报告（新增）
├── index.html                 # 网页入口
└── .git/                     # Git仓库
```

## ⚙️ 使用方法

### 手动运行高级分析

```bash
python3 /root/.openclaw/workspace/btc_advanced_monitor.py
```

### 自动运行（Cron）

```bash
0 * * * * /root/.openclaw/workspace/auto_update.sh >> /root/.openclaw/workspace/auto_update.log 2>&1
```

### 查看最新报告

```bash
# 查看最新高级报告
cat /root/.openclaw/workspace/reports/btc_advanced_report_*.txt | tail -1

# 查看复盘历史
cat /root/.openclaw/workspace/btc_review_history.json
```

## 🌐 访问方式

- **网页地址**: https://violayifan.github.io/btc-tracker-report
- **GitHub 仓库**: https://github.com/violayifan/btc-tracker-report
- **更新频率**: 每小时自动更新

## 🔬 数据源说明

### 当前状态

| 数据源 | 状态 | 说明 |
|--------|------|------|
| CoingGecko 价格 | ✅ 实时 | BTC价格和历史数据 |
| 恐慌贪婪指数 | ✅ 实时 | Alternative.me API |
| 链上数据 | ⚠️ 模拟 | 需要接入 CryptoQuant/Glassnode |
| 宏观新闻 | ⚠️ 模拟 | 需要接入 NewsAPI/Alpha Vantage |
| X舆情 | ⚠️ 模拟 | 需要接入 Twitter API |

### 接入真实数据源

#### 1. CryptoQuant (链上数据)

```python
# 在 btc_advanced_monitor.py 中
import requests

def get_real_onchain_data():
    headers = {
        "Authorization": "Bearer YOUR_CRYPTQUANT_API_KEY"
    }
    resp = requests.get(
        "https://api.cryptoquant.com/v1/btc/exchange-flows/netflow",
        headers=headers
    )
    return resp.json()
```

#### 2. NewsAPI (宏观新闻)

```python
import requests

def get_real_macro_news():
    api_key = "YOUR_NEWSAPI_KEY"
    url = f"https://newsapi.org/v2/everything?q=btc OR bitcoin OR crypto&apiKey={api_key}"
    resp = requests.get(url)
    return resp.json()
```

#### 3. Twitter API (X舆情)

```python
import tweepy

def get_real_x_sentiment():
    client = tweepy.Client(bearer_token="YOUR_TWITTER_BEARER_TOKEN")
    tweets = client.search_recent_tweets("BTC OR bitcoin", max_results=100)
    # 分析情绪
    return sentiment
```

## 📋 报告示例

```
📊 BTC 多维度市场分析与交易策略报告
============================================================

🕐 报告时间: 2026-02-22 13:55:57

💰 当前价格
  • BTC/USD: $67,894.00
  • BTC/CNY: ¥469,060
  • 24h涨跌: +0.07%

────────────────────────────────────────────────────────────
📈 技术指标
────────────────────────────────────────────────────────────
  • SMA 6小时: $67,901.52
  • SMA 12小时: $67,910.85
  • RSI (14): 37.61
  • 波动率: $50
  • 价格位置: 12.8% (24h)

────────────────────────────────────────────────────────────
🔬 量价因子分析
────────────────────────────────────────────────────────────
  • 价格趋势: bearish
  • 成交量趋势: neutral
  • 量价相关性: 0.00
  • 信号强度: weak

... (更多内容)
```

## 🔄 复盘与迭代机制

### 工作原理

1. **记录预测**: 每次分析后记录预测结果
2. **验证结果**: 后续验证预测准确性
3. **计算准确率**: 统计近期预测准确率
4. **调整权重**: 根据准确率自动调整各因子权重
5. **持续优化**: 不断改进预测模型

### 权重系统

```json
{
  "learned_weights": {
    "volume_price": 0.3,      # 量价因子
    "onchain": 0.2,            # 链上数据
    "sentiment": 0.2,           # 市场情绪
    "macro": 0.15,             # 宏观新闻
    "social": 0.15             # X舆情
  }
}
```

### 迭代规则

- 准确率 < 60%: 降低表现差的因子权重
- 准确率 > 80%: 提高表现好的因子权重
- 自动归一化确保总权重 = 1.0

## 🛠️ 故障排查

### 问题：价格数据获取失败

```bash
# 检查 CoingGecko API
curl "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"

# 查看详细错误日志
tail -f /root/.openclaw/workspace/auto_update.log
```

### 问题：HTML生成失败

```bash
# 手动运行HTML生成
python3 /root/.openclaw/workspace/btc_html_report_v2.py

# 检查生成的HTML
ls -la /root/.openclaw/workspace/btc_report_enhanced.html
```

### 问题：Git推送失败

```bash
# 检查Git配置
cd /root/.openclaw/workspace
git remote -v

# 检查SSH密钥
ssh -T git@github.com
```

## 📊 性能指标

当前回测统计：
- 总收益率: 0.64%
- 年化收益率: 64.01%
- 最大回撤: 2.21%
- 夏普比率: 2.1937
- 胜率: 22.22%

## 🔮 未来计划

- [ ] 接入真实链上数据API（CryptoQuant）
- [ ] 接入真实新闻API（NewsAPI）
- [ ] 接入真实Twitter API
- [ ] 添加机器学习预测模型
- [ ] 实现自动交易信号推送
- [ ] 添加移动端通知功能
- [ ] 优化回测算法

## 📞 支持

如有问题，请检查：
1. `/root/.openclaw/workspace/auto_update.log` - 自动更新日志
2. `/root/.openclaw/workspace/reports/` - 分析报告
3. GitHub Issues - 报告bug和功能请求

---

**最后更新**: 2026-02-22
**版本**: 2.0 (高级监控系统)
