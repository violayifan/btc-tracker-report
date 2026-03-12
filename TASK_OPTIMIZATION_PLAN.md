# 定时任务优化方案

## 📅 创建日期
2026-03-12 09:50

---

## 🎯 优化目标

### 问题诊断
当前定时任务系统存在以下问题：

1. **任务分散**: 多个独立的脚本，缺乏统一管理
2. **重复执行**: BTC 相关任务有 2 个每小时任务，资源浪费
3. **缺乏监控**: 没有任务执行统计和健康检查
4. **日志分散**: 日志文件分散在不同位置，难以查看
5. **错误处理**: 缺乏失败重试和错误告警机制

### 优化目标

1. **统一管理**: 所有任务通过单一管理器调度
2. **消除重复**: 合并重复的 BTC 任务
3. **智能监控**: 自动统计和健康检查
4. **集中日志**: 统一的日志目录结构
5. **容错机制**: 自动重试和错误处理

---

## 🚀 优化方案

### 1. 统一任务管理器

**文件**: `task_manager.sh`

**功能**:
- ✅ 统一的任务调度接口
- ✅ 自动重试机制（可配置重试次数）
- ✅ 任务执行统计（JSON 格式）
- ✅ 完整的日志记录
- ✅ 健康检查功能
- ✅ 日志清理功能

**核心特性**:
```bash
# 查看统计
./task_manager.sh stats

# 健康检查
./task_manager.sh health

# 清理日志
./task_manager.sh cleanup

# 执行 BTC 流水线
./task_manager.sh btc

# 执行 Arxiv 日报
./task_manager.sh arxiv
```

---

### 2. 优化的定时任务配置

**新配置** (NEW_CRONTAB.txt):

```bash
# BTC 完整流水线（每小时）
0 * * * * /root/.openclaw/workspace/task_manager.sh btc >> logs/btc_pipeline.log 2>&1

# Arxiv 论文日报（每天 8:00）
0 8 * * * /root/.openclaw/workspace/task_manager.sh arxiv >> logs/arxiv_daily.log 2>&1

# 任务健康检查（每天 9:00）
0 9 * * * /root/.openclaw/workspace/task_manager.sh health >> logs/health_check.log 2>&1

# 日志清理（每周日 3:00）
0 3 * * 0 /root/.openclaw/workspace/task_manager.sh cleanup >> logs/cleanup.log 2>&1
```

**对比旧配置**:

| 任务 | 旧配置 | 新配置 | 改进 |
|------|--------|--------|------|
| BTC 每小时 | 2 个独立脚本 | 1 个统一管理器 | 消除重复，节省资源 |
| Arxiv 日报 | 1 个脚本 + 依赖主会话 | 1 个统一管理器 | 可靠性提升 |
| 健康检查 | 无 | 每天 9:00 | 新增监控 |
| 日志清理 | 无 | 每周日 | 新增维护 |

---

### 3. 任务执行统计

**文件**: `task_stats.json`

**示例数据**:
```json
{
  "tasks": {
    "btc_analysis": {
      "last_run": "2026-03-12T09:00:00Z",
      "status": "success",
      "duration": 15,
      "history": [
        {"time": "2026-03-12T09:00:00Z", "status": "success", "duration": 15},
        {"time": "2026-03-12T08:00:00Z", "status": "success", "duration": 14}
      ]
    },
    "arxiv_analysis": {
      "last_run": "2026-03-12T08:00:00Z",
      "status": "success",
      "duration": 8,
      "history": [...]
    }
  }
}
```

**查看统计**:
```bash
./task_manager.sh stats
```

---

### 4. 健康检查机制

**检查项**:
- ✅ Git 仓库状态
- ✅ 关键文件完整性
- ✅ Python 依赖包
- ✅ 磁盘空间
- ✅ 日志文件大小

**执行频率**: 每天 9:00

**查看健康状态**:
```bash
./task_manager.sh health
```

---

### 5. 日志管理

**目录结构**:
```
/root/.openclaw/workspace/logs/
├── task_manager.log    # 管理器日志
├── btc_pipeline.log    # BTC 流水线日志
├── arxiv_daily.log     # Arxiv 日报日志
├── health_check.log    # 健康检查日志
└── cleanup.log         # 日志清理日志
```

**自动清理**: 每周日 3:00 清理 7 天前的旧日志

**查看所有日志**:
```bash
ls -lh /root/.openclaw/workspace/logs/
tail -f /root/.openclaw/workspace/logs/task_manager.log
```

---

## 📋 实施步骤

### 步骤 1: 备份当前配置（自动）
```bash
crontab -l > /root/.openclaw/workspace/crontab_backup_$(date +%Y%m%d_%H%M%S).txt
```

### 步骤 2: 应用新配置
```bash
chmod +x /root/.openclaw/workspace/migrate_crontab.sh
./migrate_crontab.sh
```

### 步骤 3: 验证配置
```bash
crontab -l  # 查看新配置
./task_manager.sh health  # 健康检查
./task_manager.sh stats  # 查看统计
```

### 步骤 4: 回滚（如需要）
```bash
crontab /root/.openclaw/workspace/crontab_backup_YYYYMMDD_HHMMSS.txt
```

---

## 🔧 故障排查

### 问题 1: 任务没有执行

**检查**:
```bash
# 查看 cron 服务状态
systemctl status cron

# 查看任务日志
tail -100 /root/.openclaw/workspace/logs/btc_pipeline.log

# 查看任务统计
./task_manager.sh stats
```

### 问题 2: Git push 失败

**检查**:
```bash
cd /root/.openclaw/workspace
git status
git remote -v
git push origin master --dry-run  # 测试推送
```

### 问题 3: 飞书消息没有发送

**检查**:
```bash
# 查看飞书报告是否生成
ls -lh /root/.openclaw/workspace/temp_feishu_report.md

# 查看任务日志
tail -100 /root/.openclaw/workspace/logs/arxiv_daily.log
```

### 问题 4: 磁盘空间不足

**检查**:
```bash
# 查看磁盘使用
df -h

# 手动清理旧日志
./task_manager.sh cleanup

# 查看日志文件大小
du -sh /root/.openclaw/workspace/logs/*
```

---

## 📊 监控面板

### 快速状态查看

```bash
# 一键查看所有任务状态
/root/.openclaw/workspace/task_manager.sh stats

# 健康检查
/root/.openclaw/workspace/task_manager.sh health

# 查看最新日志
tail -50 /root/.openclaw/workspace/logs/task_manager.log
```

### 关键指标

- **任务成功率**: 从统计数据中计算
- **平均执行时间**: 从统计数据中分析
- **磁盘使用情况**: 健康检查自动报告
- **最近失败任务**: 检查统计数据中的 failed 状态

---

## 🎯 优化效果

### 资源使用

| 指标 | 优化前 | 优化后 | 改进 |
|------|--------|--------|------|
| BTC 每小时任务 | 2 个 | 1 个 | -50% |
| 定时任务数 | 3 个 | 4 个 | +33% (新增监控) |
| 日志文件数 | 分散 | 集中 | 统一管理 |
| 健康检查 | 无 | 每天 1 次 | 新增 |

### 可靠性

| 指标 | 优化前 | 优化后 |
|------|--------|--------|
| 任务监控 | ❌ 无 | ✅ 统计 + 日志 |
| 失败重试 | ❌ 无 | ✅ 可配置 |
| 健康检查 | ❌ 无 | ✅ 每天 |
| 日志清理 | ❌ 无 | ✅ 每周 |

### 可维护性

- ✅ 统一的配置文件
- ✅ 集中的日志管理
- ✅ 清晰的命令接口
- ✅ 完整的文档说明

---

## 📝 最佳实践

1. **定期检查统计**: 每周运行一次 `./task_manager.sh stats`
2. **监控磁盘空间**: 每周检查健康检查日志
3. **备份重要数据**: 定期备份 task_stats.json
4. **测试变更**: 修改脚本前先手动测试
5. **查看日志**: 遇到问题时首先查看相关日志

---

## 🔄 升级路径

### 未来改进

1. **添加告警通知**: 任务失败时发送飞书消息
2. **Web 监控面板**: 可视化任务状态
3. **依赖管理**: 自动检查和更新 Python 包
4. **性能优化**: 并行执行独立任务
5. **配置文件**: 支持外部配置文件

---

## ✅ 总结

**优化完成后的优势**:

- ✅ **统一管理**: 所有任务通过单一入口
- ✅ **消除重复**: BTC 任务从 2 个减少到 1 个
- ✅ **智能监控**: 自动统计和健康检查
- ✅ **容错机制**: 自动重试和错误处理
- ✅ **集中日志**: 统一的日志目录和清理机制
- ✅ **易于维护**: 清晰的命令接口和文档

**预期效果**:

- 🚀 任务执行更可靠
- 📊 问题诊断更快速
- 🔧 系统维护更简单
- 💾 资源使用更高效

---

*文档创建时间: 2026-03-12 09:50*
*版本: 1.0*
