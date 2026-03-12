#!/bin/bash
# ============================================
# 定时任务迁移脚本
# ============================================
# 功能：安全地更新定时任务配置
# ============================================

WORKSPACE="/root/.openclaw/workspace"
CURRENT_CRONTAB="/tmp/current_crontab_$$"
NEW_CRONTAB="$WORKSPACE/NEW_CRONTAB.txt"

echo "=========================================="
echo "🔄 定时任务优化迁移"
echo "=========================================="
echo ""

# 1. 显示当前定时任务
echo "📋 当前定时任务:"
echo "=========================================="
crontab -l
echo "=========================================="
echo ""

# 2. 分析当前任务
echo "🔍 分析当前任务:"
echo "=========================================="
crontab -l | while read line; do
    if [[ ! "$line" =~ ^# ]]; then
        if [[ "$line" =~ auto_update|update_btc_report|arxiv_daily ]]; then
            echo "📌 $line"
            echo "   ⚠️  将被新的统一管理器替代"
        fi
    fi
done
echo "=========================================="
echo ""

# 3. 显示新任务
echo "✨ 新定时任务配置:"
echo "=========================================="
cat "$NEW_CRONTAB"
echo "=========================================="
echo ""

# 4. 询问用户确认
echo "⚠️  即将应用新的定时任务配置"
echo ""
echo "变更内容:"
echo "  • BTC 每小时任务: auto_update.sh + update_btc_report.sh → task_manager.sh btc"
echo "  • Arxiv 每日任务: arxiv_daily_with_notification.sh → task_manager.sh arxiv"
echo "  • 新增: 每日健康检查 (9:00)"
echo "  • 新增: 每周日日志清理 (周日 3:00)"
echo ""
echo "旧任务将被禁用（注释掉），新任务将立即生效"
echo ""
echo "是否继续? (yes/no)"
read -r confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ 迁移已取消"
    exit 0
fi

# 5. 备份当前配置
BACKUP_FILE="$WORKSPACE/crontab_backup_$(date +%Y%m%d_%H%M%S).txt"
crontab -l > "$BACKUP_FILE"
echo "✅ 当前配置已备份到: $BACKUP_FILE"
echo ""

# 6. 应用新配置
echo "🚀 应用新配置..."
cat "$NEW_CRONTAB" | crontab -
echo "✅ 新配置已应用"
echo ""

# 7. 验证新配置
echo "📋 新定时任务 (已生效):"
echo "=========================================="
crontab -l
echo "=========================================="
echo ""

# 8. 快速测试
echo "🧪 快速测试任务管理器..."
if /root/.openclaw/workspace/task_manager.sh stats > /dev/null 2>&1; then
    echo "✅ 任务管理器运行正常"
else
    echo "❌ 任务管理器运行异常，请检查"
fi
echo ""

echo "=========================================="
echo "✅ 定时任务优化完成！"
echo "=========================================="
echo ""
echo "📊 任务统计:"
/root/.openclaw/workspace/task_manager.sh stats 2>/dev/null || echo "暂无统计数据"
echo ""
echo "📝 日志文件位置:"
echo "  • BTC 流水线: $WORKSPACE/logs/btc_pipeline.log"
echo "  • Arxiv 日报: $WORKSPACE/logs/arxiv_daily.log"
echo "  • 健康检查: $WORKSPACE/logs/health_check.log"
echo "  • 日志清理: $WORKSPACE/logs/cleanup.log"
echo "  • 管理器日志: $WORKSPACE/logs/task_manager.log"
echo ""
echo "💡 如需回滚，请使用:"
echo "  crontab $BACKUP_FILE"
echo ""
