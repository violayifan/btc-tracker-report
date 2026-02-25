# 全天候策略 v1.0 - 经典马丁格尔策略

## 📅 策略说明

### 策略原理
马丁格尔（Martingale）策略是一种经典的资金管理策略，源自 18 世纪的法国赌场。

**基本规则：**
1. 每次下注固定的基础金额
2. 如果输了，下一次下注翻倍（x2）
3. 如果赢了，回到初始基础金额
4. 目标是在单次盈利中覆盖所有之前的亏损

### 数学公式
- 基础下注：B
- 第 n 次下注：B × 2^(n-1)
- 总下注：B × (2^n - 1)

### 优势
- ✅ 理论上，只要有无限资金，最终一定会盈利
- ✅ 适合震荡市场，能快速回本
- ✅ 逻辑简单，易于实现

### 风险
- ❌ 资金要求极高（指数级增长）
- ❌ 遇到长连败时，可能爆仓
- ❌ 在趋势市场容易连续亏损
- ❌ 负期望值策略（长期必亏）

## 🎯 策略参数

```python
# 基础参数
INITIAL_POSITION = 0.001  # 初始仓位（BTC 数量）
MULTIPLIER = 2.0           # 加倍倍数
MAX_POSITIONS = 10         # 最大开仓次数
STOP_LOSS_PERCENTAGE = 0.05 # 止损百分比

# 计算参数
position_count = 0
current_position = INITIAL_POSITION
```

## 📊 交易逻辑

```python
def martingale_strategy(price_history, current_price):
    """
    马丁格尔策略实现

    Args:
        price_history: 历史价格数据
        current_price: 当前价格

    Returns:
        action: 'buy' 或 'sell'
        position_size: 仓位大小
        reason: 交易原因
    """
    global position_count, current_position

    # 如果之前是亏损，增加仓位
    if position_count > 0 and is_last_position_loss():
        position_count += 1
        current_position *= MULTIPLIER

        # 检查是否超过最大开仓次数
        if position_count > MAX_POSITIONS:
            return None, 0, "超过最大开仓次数"

    # 如果是盈利，重置到初始仓位
    elif position_count > 0 and is_last_position_profit():
        position_count = 1
        current_position = INITIAL_POSITION

    else:
        # 第一次开仓
        position_count = 1
        current_position = INITIAL_POSITION

    # 计算止盈和止损价格
    take_profit_price = calculate_take_profit()
    stop_loss_price = calculate_stop_loss()

    return 'buy', current_position, f"马丁格尔第 {position_count} 单"

def calculate_take_profit():
    """计算止盈价格"""
    # 简化：止盈为 1%
    return current_price * 1.01

def calculate_stop_loss():
    """计算止损价格"""
    return current_price * (1 - STOP_LOSS_PERCENTAGE)
```

## 📈 回测评估指标

```python
# 回测参数
INITIAL_CAPITAL = 10000  # 初始资金（USDT）
TRADING_FEE = 0.001       # 交易手续费（0.1%）
```

## 📋 风险管理

1. **最大连败限制**
   - 设置最大开仓次数（如 10 次）
   - 避免指数级资金消耗

2. **硬止损**
   - 每单设置固定止损（如 5%）
   - 防止单笔亏损过大

3. **资金控制**
   - 最大仓位不超过总资金的 20%
   - 避免爆仓风险

## 🔧 参数优化方向

1. **基础仓位**
   - 保守：0.0005 BTC
   - 激进：0.002 BTC

2. **加倍倍数**
   - 保守：1.5 倍
   - 标准：2.0 倍
   - 激进：2.5 倍

3. **最大开仓次数**
   - 保守：5 次
   - 标准：10 次
   - 激进：15 次

## 🚀 实施建议

### 适合市场环境
- ✅ 横盘震荡市场
- ✅ 窄破后回踩
- ✅ 区间震荡（100-500点）

### 不适合市场环境
- ❌ 单边趋势市场（容易连续亏损）
- ❌ 极端波动市场
- ❌ 流动性极低的市场

## 📊 预期表现

### 保守参数
- **年化收益率**：-20% ~ +10%
- **最大回撤**：30% ~ 50%
- **夏普比率**：< 0.5
- **爆仓风险**：低

### 标准参数
- **年化收益率**：-50% ~ +30%
- **最大回撤**：60% ~ 90%
- **夏普比率**：0.5 ~ 1.0
- **爆仓风险**：中

### 激进参数
- **年化收益率**：-100% ~ +100%
- **最大回撤**：90% ~ 100%
- **夏普比率**：< 0.5
- **爆仓风险**：高

## ⚠️ 重要提示

1. **马丁格尔是负期望值策略**
   - 长期来看，大概率会亏损
   - 只适合短期投机

2. **必须有止损**
   - 没有止损的马丁格尔是自杀行为
   - 严格执行止损是生存的关键

3. **资金管理**
   - 不要用全部资金做马丁格尔
   - 预留至少 50% 资金备用

4. **心理建设**
   - 接受可能会爆仓的现实
   - 不要情绪化加仓
   - 严格按照规则执行

## 📚 参考资料

1. **维基百科** - Martingale betting system
2. **Investopedia** - Martingale System Definition
3. **量化交易经典策略** - 马丁格尔策略详解

## 🎓 版本历史
- v1.0 (2026-02-25): 初始版本，经典马丁格尔策略

## 📝 TODO
- [ ] 实现 Python 代码
- [ ] 编写回测函数
- [ ] 参数敏感性分析
- [ ] 不同市场环境测试
- [ ] 风险管理优化
