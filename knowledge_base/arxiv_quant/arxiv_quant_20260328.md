# Arxiv 量化投资论文日报 - 2026-03-28

## 📄 论文基本信息

**标题**: Portfolio Optimization under Recursive Utility via Reinforcement Learning

**作者**: Minkey Chang


**发布时间**: 2026-03-24T07:25:30Z

**论文类别**: q-fin.GN

**论文链接**: https://arxiv.org/abs/2603.22880v1

**PDF链接**: https://arxiv.org/pdf/2603.22880v1.pdf

**分析时间**: 2026-03-28 08:30:03

---

## 📝 论文摘要

We study whether a risk-sensitive objective from asset-pricing theory -- recursive utility -- improves reinforcement learning for portfolio allocation. The Bellman equation under recursive utility involves a certainty equivalent (CE) of future value that has no closed form under observed returns; we approximate it by $K$-sample Monte Carlo and train actor-critic (PPO, A2C) on the resulting value target and an approximate advantage estimate (AAE) that generalizes the Bellman residual to multi-step with state-dependent weights. This formulation applies only to critic-based algorithms. On 10 chronological train/test splits of South Korean ETF data, the recursive-utility agent improves on the discounted (naive) baseline in Sharpe ratio, max drawdown, and cumulative return. Derivations, world model and metrics, and full result tables are in the appendices.

---

## 🎯 关键贡献

1. We study whether a risk-sensitive objective from asset-pricing theory -- recursive utility -- improves reinforcement learning for portfolio allocation
2. The Bellman equation under recursive utility involves a certainty equivalent (CE) of future value that has no closed form under observed returns; we approximate it by $K$-sample Monte Carlo and train actor-critic (PPO, A2C) on the resulting value target and an approximate advantage estimate (AAE) that generalizes the Bellman residual to multi-step with state-dependent weights
3. This formulation applies only to critic-based algorithms

---

## 🔬 研究方法

- 强化学习
- 投资组合优化
- 夏普比率优化


---

## 💡 潜在应用

- 投资组合优化


---

## 📊 详细总结

### 研究目标

We study whether a risk-sensitive objective from asset-pricing theory -- recursive utility -- improves reinforcement learning for portfolio allocation.

### 研究方法/方法学

This formulation applies only to critic-based algorithms

Derivations, world model and metrics, and full result tables are in the appendices

### 关键发现

- 见论文详细内容


### 数据和研究范围

The Bellman equation under recursive utility involves a certainty equivalent (CE) of future value that has no closed form under observed returns; we approximate it by $K$-sample Monte Carlo and train actor-critic (PPO, A2C) on the resulting value target and an approximate advantage estimate (AAE) that generalizes the Bellman residual to multi-step with state-dependent weights

On 10 chronological train/test splits of South Korean ETF data, the recursive-utility agent improves on the discounted (naive) baseline in Sharpe ratio, max drawdown, and cumulative return

### 研究局限性

- 基于论文摘要无法判断


---

## 🏆 论文评价

### 创新性
**评价**: 一般 - 主要是对现有方法的应用或比较

### 实用价值
**评价**: 中 - 有一定的实用价值

### 理论贡献
**评价**: 中 - 有一定的理论贡献

### 数据质量
**评价**: 无法判断 - 摘要中未详细描述数据

### 适用性
**评价**: 中 - 模型有一定的适用性

### 综合评分
**⭐⭐ 较低 - 按需阅读**

---

## 📖 阅读建议

**适合人群**:
- 投资组合优化从业者

- 量化金融研究人员
- 金融科技工程师

**阅读重点**:
- 论文摘要和引言（了解研究背景）
- 方法论部分（理解核心创新）
- 实验结果（评估实际效果）
- 结论部分（了解未来研究方向）

**预期收获**:
- 了解最新的量化金融研究进展
- 学习新的方法和技术
- 获取实践应用的灵感
- 发现新的研究机会

---

## ⚠️ 注意事项

1. 本报告主要基于论文摘要进行分析，完整理解需要阅读全文
2. 论文的实际效果需要在实际场景中验证
3. 不同市场环境下，模型的适用性可能有所不同
4. 建议结合自身需求，评估论文的实用价值

---

*本报告由自动化系统生成，仅供参考。*
