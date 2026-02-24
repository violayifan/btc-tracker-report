# HEARTBEAT.md - 定时任务清单

## BTC 高级市场分析（每小时自动运行）

### 自动化流程（Cron 定时任务）

**定时任务设置**：每小时整点自动运行
```bash
0 * * * * /root/.openclaw/workspace/auto_update.sh >> /root/.openclaw/workspace/auto_update.log 2>&1
```

**自动执行内容**：
1. ✅ 运行 BTC 高级市场分析 (`btc_advanced_monitor_v2.py`)
2. ✅ 量价因子分析
3. ✅ 链上资金分析
4. ✅ 市场情绪分析
5. ✅ 宏观新闻分析
6. ✅ X舆情分析
7. ✅ 复盘与迭代
8. ✅ 更新 Git 仓库
9. ✅ 提交更改到 Git
10. ✅ 推送到 GitHub (master 分支)
11. ✅ GitHub Pages 自动部署

**访问网址**：
- 🌐 永久网址：https://violayifan.github.io/btc-tracker-report
- ⏰ 每小时自动更新（刷新页面即可）

**GitHub 仓库**：
- 仓库地址：https://github.com/violayifan/btc-tracker-report
- 分支：master
- 部署方式：GitHub Pages

---

### 手动触发（可选）

当收到包含 "执行 BTC 市场分析与交易策略报告" 的系统事件时：

1. 运行: `python3 /root/.openclaw/workspace/btc_monitor.py`（基础分析）
   或 `python3 /root/.openclaw/workspace/btc_advanced_monitor_v2.py`（高级分析）
2. 读取最新报告: `cat /root/.openclaw/workspace/reports/btc_advanced_report_*.txt | tail -1`
3. 将报告内容发送给用户（**不包含**网址更新，因为手动触发不推送到 GitHub）

### 回测与绩效分析

`btc_advanced_monitor_v2.py` 会自动：
- 记录所有 LONG/SHORT 交易信号（HOLD 不记录）
- 生成回测报告（收益率、最大回撤、夏普比率等）
- 将回测关键指标显示在报告末尾（避免重复）
- 更新 `btc_trades.json` 交易记录文件
- 推送更新到 GitHub，GitHub Pages 自动部署

### 文件位置

- 市场分析报告：`/root/.openclaw/workspace/reports/btc_report_*.txt`
- 回测报告：`/root/.openclaw/workspace/reports/btc_backtest_report_*.txt`
- 交易记录：`/root/.openclaw/workspace/btc_trades.json`
- 净值曲线图：`/root/.openclaw/workspace/backtest_chart.png`
- 自动更新脚本：`/root/.openclaw/workspace/auto_update.sh`
- Git 仓库：`/root/.openclaw/workspace` (已初始化，连接到 GitHub)
- 自动更新日志：`/root/.openclaw/workspace/auto_update.log`

## 其他检查

（可在此添加其他定期任务，如邮件、日历检查等）
