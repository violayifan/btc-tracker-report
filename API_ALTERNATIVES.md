# API 替代方案指南

## 📊 三大API的免费情况

### 1. CryptoQuant (链上数据）

**❌ 不是完全免费的**

- **免费层级**: 每天20次API调用
- **付费计划**:
  - Basic: $99/月
  - Pro: $499/月
  - Enterprise: 定制

**限制**:
- 免费层级调用次数太少，不适合每小时监控
- 大部分高级指标需要付费

---

### 2. NewsAPI (宏观新闻)

**✅ 有免费层级**

- **免费层级**: 每天100次请求
- **付费计划**:
  - Developer: $449/月 (10,000请求/天)
  - Business: $549/月 (25,000请求/天)

**限制**:
- 每小时1次分析，每天24次，完全在免费范围内
- 需要注册获取API密钥

---

### 3. Twitter/X API

**❌ 基本没有免费层级**

- **免费层级**: 已取消（2024年起）
- **付费计划**:
  - Basic: $100/月 (10,000 tweets/月)
  - Pro: $5,000/月 (1,000,000 tweets/月)
  - Enterprise: 定制

**限制**:
- 即使是Basic计划，也仅支持只读访问
- 价格昂贵，不适合个人项目

---

## 🔄 替代方案

### 🔬 CryptoQuant 替代方案（链上数据）

#### 方案1: Coinglass ⭐ 推荐
**✅ 完全免费**
- 提供多空比、资金费率等数据
- 官方网站: https://coinglass.com
- 可直接爬取数据，无需API

**可用指标**:
- 多空比
- 资金费率
- 大户持仓
- 持仓量
- 期权数据

#### 方案2: Glassnode
**⚠️ 有免费但限制多**
- 免费层级: 每天25次API调用
- 网站地址: https://glassnode.com
- 需要注册账户

#### 方案3: Whale Alert
**✅ 完全免费**
- 专门追踪大额交易
- 网站地址: https://whale-alert.io
- 提供WebSocket实时数据
- 可监控鲸鱼活动

#### 方案4: CoinMarketCap
**✅ 基础数据免费**
- 网站地址: https://coinmarketcap.com
- 免费提供一些基础链上指标
- 需要注册获取API密钥

#### 方案5: 自建爬虫
**✅ 完全免费但需注意法律**
- 爬取交易所公开数据
- 注意: 需要遵守网站的robots.txt和使用条款
- 推荐使用: Binance、OKX等交易所的公开数据

---

### 📰 NewsAPI 替代方案（宏观新闻）

#### 方案1: GDELT ⭐ 推荐
**✅ 完全免费**
- 全球事件数据库
- 网站: https://www.gdeltproject.org/
- 无需API密钥
- 可以查询加密货币相关的新闻事件

**优势**:
- 完全免费，无限调用
- 实时更新
- 可以通过关键词搜索

#### 方案2: NewsData.io
**✅ 有免费层级**
- 免费层级: 每天200次请求
- 网站: https://newsdata.io/
- 注册后即可使用

#### 方案3: TheNewsAPI
**✅ 有免费层级**
- 免费层级: 每天10次请求（较少）
- 网站: https://www.thenewsapi.com/

#### 方案4: RSS订阅
**✅ 完全免费**
- 使用各大新闻网站的RSS源
- 比较可靠
- 无需API密钥

**推荐RSS源**:
- CoinDesk: https://www.coindesk.com/arc/outboundfeeds/rss/
- Cointelegraph: https://cointelegraph.com/rss
- CoinDesk: https://www.coindesk.com/arc/outboundfeeds/rss/

#### 方案5: 爬取财经新闻网站
**✅ 完全免费但需注意法律**
- 爬取 Bloomberg、Reuters、CNBC 等财经新闻
- 注意版权和使用条款
- 推荐使用: 公开的新闻聚合网站

---

### 🐦 Twitter/X API 替代方案（社交媒体舆情）

#### 方案1: Reddit API ⭐ 推荐
**✅ 完全免费**
- Reddit有活跃的加密货币社区
- 官方API完全免费
- 无需付费

**相关subreddit**:
- r/Bitcoin
- r/CryptoCurrency
- r/CryptoMarkets

#### 方案2: Telegram Bot API
**✅ 完全免费**
- 大量加密货币相关的Telegram频道
- Bot API完全免费
- 可以抓取频道消息

**推荐频道**:
- Whale Alert
- CoinDesk
- Cointelegraph
- 各种加密货币分析频道

#### 方案3: Discord Bot
**✅ 完全免费**
- Discord上有加密货币社区
- Bot API完全免费
- 需要申请开发者权限

#### 方案4: Nitter
**✅ 完全免费**
- Twitter的开源前端
- 可以通过Nitter实例访问Twitter
- 无需API密钥
- 注意: 实例可能不稳定

**公共Nitter实例**:
- https://nitter.net
- https://nitter.poast.org
- https://nitter.fdn.fr

#### 方案5: 自建爬虫（注意法律）
**⚠️ 完全免费但有风险**
- 直接爬取Twitter网页
- 注意: 违反Twitter服务条款
- 可能被封IP
- 不推荐

---

## 🎯 推荐的组合方案

### 方案A: 完全免费组合 ⭐⭐⭐
```
链上数据: Coinglass (免费爬取)
宏观新闻: GDELT (完全免费)
社交舆情: Reddit API (完全免费)
```

**优势**:
- 完全免费，无限调用
- 数据来源可靠
- 实时更新

### 方案B: 部分免费组合 ⭐⭐
```
链上数据: Glassnode (免费层级，25次/天)
宏观新闻: NewsAPI (免费层级，100次/天)
社交舆情: Reddit API (完全免费)
```

**优势**:
- 专业性更强
- 每小时分析完全够用
- 成本为零

### 方案C: 爬虫组合 ⭐
```
链上数据: 自建爬虫（交易所数据）
宏观新闻: RSS订阅
社交舆情: Telegram频道
```

**优势**:
- 完全自主
- 无限调用
- 可自定义数据源

**注意**:
- 需要注意法律和使用条款
- 维护成本较高
- 可能不稳定

---

## 📋 API密钥申请指南

### NewsAPI (推荐申请)
1. 访问: https://newsapi.org/register
2. 填写邮箱、密码、公司信息
3. 验证邮箱
4. 获取API密钥
5. 开始使用（每天100次免费）

### Glassnode (可选申请)
1. 访问: https://glassnode.com/
2. 点击 Sign Up
3. 选择免费计划
4. 验证邮箱
5. 获取API密钥
6. 开始使用（每天25次免费）

### Reddit API (推荐申请)
1. 访问: https://www.reddit.com/
2. 注册账户
3. 前往: https://www.reddit.com/prefs/apps
4. 创建应用
5. 获取client_id和client_secret
6. 开始使用（完全免费）

---

## 💡 实施建议

### 阶段1: 快速实现（1-2天）
使用完全免费的方案:
- 链上数据: Coinglass爬取
- 宏观新闻: GDELT API
- 社交舆情: Reddit API

### 阶段2: 优化提升（1周）
优化数据质量和分析:
- 申请NewsAPI (宏观新闻）
- 优化Coinglass爬虫
- 增加更多subreddit监控

### 阶段3: 全面升级（1-2周）
接入更专业数据源:
- 申请Glassnode API (链上）
- 优化GDELT查询
- 增加Telegram频道监控

---

## ⚠️ 注意事项

### 法律和道德
1. 遵守网站的服务条款
2. 尊重robots.txt
3. 不要频繁请求（避免被封IP）
4. 数据仅供个人使用，不商用

### 技术考虑
1. 添加请求间隔（避免被封）
2. 实现错误处理
3. 缓存数据（减少请求）
4. 监控API使用量

### 成本控制
1. 优先使用完全免费的方案
2. 监控API调用次数
3. 合理设置请求频率
4. 避免意外超支

---

## 📞 需要帮助？

如果您需要我帮助实现某个替代方案，请告诉我：
1. 您想使用哪个方案？
2. 您希望监控哪些具体指标？

我可以帮您：
- 编写API调用代码
- 实现爬虫
- 优化数据获取
- 集成到现有系统

---

**最后更新**: 2026-02-22
**版本**: 1.0
