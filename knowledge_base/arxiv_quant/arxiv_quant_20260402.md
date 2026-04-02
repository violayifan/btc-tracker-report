# Arxiv 量化投资论文日报 - 2026-04-02

## 📄 论文基本信息

**标题**: Model Predictive Control For Trade Execution

**作者**: Thomas P. McAuliffe, Samuel Liew, Yuchao Li, Andrey Ushenin, Chihang Wang
Alexandros Tasos, Jack Pearce, Dimitris Tasoulis, Dimitri P. Bertsekas, Theodoros Tsagaris

**发布时间**: 2026-03-30T18:25:52Z

**论文类别**: q-fin.TR

**论文链接**: https://arxiv.org/abs/2603.28898v1

**PDF链接**: https://arxiv.org/pdf/2603.28898v1.pdf

**分析时间**: 2026-04-02 08:30:02

---

## 📝 论文摘要

We address the problem of executing large client orders in continuous double-auction markets under time and liquidity constraints. We propose a model predictive control (MPC) framework that balances three competing objectives: order completion, market impact, and opportunity cost. Our algorithm is guided by a trading schedule (such as time-weighted average price or volume-weighted average price) but allows for deviations to reduce the expected execution cost, with due regard to risk.
  Our MPC algorithm executes the order progressively, and at each decision step it solves a fast quadratic program that trades off expected transaction cost against schedule deviation, while incorporating a residual cost term derived from a simple base policy. Approximate schedule adherence is maintained through explicit bounds, while variance constraints on deviation provide direct risk control. The resulting system is modular, data-driven, and suitable for deployment in production trading infrastructure.
  Using six months of NASDAQ 'level 3' data and simulated orders, we show that our MPC approach reduces schedule shortfall by approximately 40-50% relative to spread-crossing benchmarks and achieves significant reductions in slippage. Moreover, augmenting the base policy with predictive price information further enhances performance, highlighting the framework's flexibility for integration with forecasting components.

---

## 🎯 关键贡献

1. We propose a model predictive control (MPC) framework that balances three competing objectives: order completion, market impact, and opportunity cost.
2. we show that our MPC approach reduces schedule shortfall by approximately 40-50% relative to spread-crossing benchmarks and achieves significant reductions in slippage.
3. We address the problem of executing large client orders in continuous double-auction markets under time and liquidity constraints

---

## 🔬 研究方法

- 基准测试
- 预测模型


---

## 💡 潜在应用

- 量化交易
- 风险控制
- 交易执行


---

## 📊 详细总结

### 研究目标

研究量化投资相关的理论和方法问题

### 研究方法/方法学

We propose a model predictive control (MPC) framework that balances three competing objectives: order completion, market impact, and opportunity cost

Our algorithm is guided by a trading schedule (such as time-weighted average price or volume-weighted average price) but allows for deviations to reduce the expected execution cost, with due regard to risk

### 关键发现

- we show that our MPC approach reduces schedule shortfall by approximately 40-50% relative to spread-crossing benchmarks and achieves significant reductions in slippage.


### 数据和研究范围

The resulting system is modular, data-driven, and suitable for deployment in production trading infrastructure

Using six months of NASDAQ 'level 3' data and simulated orders, we show that our MPC approach reduces schedule shortfall by approximately 40-50% relative to spread-crossing benchmarks and achieves significant reductions in slippage

### 研究局限性

- We address the problem of executing large client orders in continuous double-auction markets under time and liquidity constraints
- Approximate schedule adherence is maintained through explicit bounds, while variance constraints on deviation provide direct risk control


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
**评价**: 一般 - 需要进一步验证泛化能力

### 综合评分
**⭐⭐⭐ 一般 - 可以了解**

---

## 📖 阅读建议

**适合人群**:
- 量化交易从业者
- 风险控制从业者
- 交易执行从业者

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
