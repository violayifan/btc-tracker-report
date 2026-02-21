# HEARTBEAT.md - 定时任务清单

## BTC 市场分析（每小时自动运行）

### 自动化流程（Cron 定时任务）

**定时任务设置**：每小时整点自动运行
```bash
0 * * * * /root/.openclaw/workspace/update_btc_report.sh >> /root/.openclaw/workspace/update_btc_report.log 2>&1
```

**自动执行内容**：
1. ✅ 运行 BTC 市场分析
2. ✅ 生成增强版 HTML 报告
3. ✅ 部署到 Netlify（网址不变，内容自动更新）

**访问网址**：
- 永久网址：https://btc-tracker-report.netlify.app
- 每小时自动更新

---

### 手动触发（可选）

当收到包含 "执行 BTC 市场分析与交易策略报告" 的系统事件时：

1. 运行: `python3 /root/.openclaw/workspace/btc_monitor.py`
2. 读取最新报告: `cat /root/.openclaw/workspace/reports/btc_report_*.txt | tail -1`
3. 将报告内容发送给用户

### 回测与绩效分析

`btc_monitor.py` 会自动：
- 记录所有 LONG/SHORT 交易信号（HOLD 不记录）
- 生成回测报告（收益率、最大回撤、夏普比率等）
- 生成净值曲线图并保存到 `/root/.openclaw/workspace/backtest_chart.png`
- 将回测汇总附加到市场分析报告末尾

### 文件位置

- 市场分析报告：`/root/.openclaw/workspace/reports/btc_report_*.txt`
- 回测报告：`/root/.openclaw/workspace/reports/btc_backtest_report_*.txt`
- 交易记录：`/root/.openclaw/workspace/btc_trades.json`
- 净值曲线图：`/root/.openclaw/workspace/backtest_chart.png`

## 其他检查

（可在此添加其他定期任务，如邮件、日历检查等）
