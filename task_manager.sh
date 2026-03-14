#!/bin/bash
# ============================================
# 定时任务统一管理器
# ============================================
# 功能：
# 1. 统一管理所有定时任务
# 2. 任务健康检查
# 3. 执行统计和监控
# 4. 统一日志管理
# 5. 失败重试机制
# ============================================

WORKSPACE="/root/.openclaw/workspace"
LOG_DIR="$WORKSPACE/logs"
TASK_STATS="$WORKSPACE/task_stats.json"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 日志函数
log() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_DIR/task_manager.log"
}

# 记录任务统计
record_task_stat() {
    local task_name=$1
    local status=$2
    local duration=$3
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    # 如果统计文件不存在，创建默认结构
    if [ ! -f "$TASK_STATS" ]; then
        echo '{"tasks":{}}' > "$TASK_STATS"
    fi

    # 使用临时文件来更新 JSON（避免并发问题）
    local temp_file=$(mktemp)
    jq --arg task "$task_name" \
       --arg status "$status" \
       --arg ts "$timestamp" \
       --argjson dur "$duration" \
       '.tasks[$task] = {
           last_run: $ts,
           status: $status,
           duration: $dur,
           history: (.tasks[$task].history // [] | [{time: $ts, status: $status, duration: $dur}] + . | .[0:10])
       }' "$TASK_STATS" > "$temp_file" && mv "$temp_file" "$TASK_STATS"
}

# 任务执行包装器
run_task() {
    local task_name=$1
    local task_command=$2
    local max_retries=${3:-1}
    local retry_count=0
    local start_time=$(date +%s)
    local exit_code=1

    log "INFO" "=========================================="
    log "INFO" "🚀 开始执行任务: $task_name"
    log "INFO" "📝 命令: $task_command"
    log "INFO" "🔄 最大重试次数: $max_retries"
    log "INFO" "=========================================="

    while [ $retry_count -lt $max_retries ]; do
        if [ $retry_count -gt 0 ]; then
            log "WARN" "🔄 第 $((retry_count + 1)) 次尝试..."
        fi

        # 执行任务
        eval "$task_command"
        exit_code=$?

        if [ $exit_code -eq 0 ]; then
            log "INFO" "✅ 任务执行成功"
            break
        else
            log "ERROR" "❌ 任务执行失败 (退出码: $exit_code)"
            retry_count=$((retry_count + 1))

            if [ $retry_count -lt $max_retries ]; then
                log "WARN" "⏳ 等待 10 秒后重试..."
                sleep 10
            fi
        fi
    done

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    # 记录统计
    if [ $exit_code -eq 0 ]; then
        record_task_stat "$task_name" "success" "$duration"
        log "INFO" "⏱️  执行时间: ${duration}秒"
    else
        record_task_stat "$task_name" "failed" "$duration"
        log "ERROR" "⚠️  任务最终失败，耗时: ${duration}秒"
    fi

    log "INFO" "=========================================="
    echo ""

    return $exit_code
}

# BTC 高级市场分析任务
task_btc_advanced_analysis() {
    log "INFO" "📊 BTC 高级市场分析任务"

    # 进入工作目录
    cd "$WORKSPACE"

    # 运行高级分析
    python3 btc_advanced_monitor_v2.py
    if [ $? -ne 0 ]; then
        log "ERROR" "BTC 高级分析失败"
        return 1
    fi

    log "INFO" "✅ BTC 高级分析完成"
    return 0
}

# 生成 HTML 报告任务
task_generate_html() {
    log "INFO" "📄 生成 HTML 报告任务"

    cd "$WORKSPACE"

    # 生成 HTML 报告（后台运行，限时 10 秒）
    python3 btc_html_report_v3.py > /dev/null 2>&1 &
    local HTML_PID=$!
    sleep 10

    # 检查进程状态
    if ps -p $HTML_PID > /dev/null; then
        log "WARN" "HTML 生成超时，终止进程"
        kill $HTML_PID 2>/dev/null
    fi

    # 检查文件是否生成
    if [ ! -f "$WORKSPACE/btc_report_enhanced.html" ]; then
        log "ERROR" "HTML 报告生成失败"
        return 1
    fi

    # 复制到 index.html
    cp "$WORKSPACE/btc_report_enhanced.html" "$WORKSPACE/index.html"

    log "INFO" "✅ HTML 报告生成完成"
    return 0
}

# 推送到 GitHub Pages 任务
task_push_github() {
    log "INFO" "🚀 推送到 GitHub Pages 任务"

    cd "$WORKSPACE"

    # 检查是否有更改
    if git diff --quiet && git diff --quiet --cached; then
        log "INFO" "⚠️  没有需要推送的更改"
        return 0
    fi

    # 添加所有更改
    git add -A
    if [ $? -ne 0 ]; then
        log "ERROR" "Git add 失败"
        return 1
    fi

    # 提交
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    git commit -m "Update BTC 市场分析报告 - $timestamp"
    if [ $? -ne 0 ]; then
        log "ERROR" "Git commit 失败"
        return 1
    fi

    # 推送
    git push origin master
    if [ $? -ne 0 ]; then
        log "ERROR" "Git push 失败"
        return 1
    fi

    # 验证推送
    local local_commit=$(git rev-parse master)
    local remote_commit=$(git rev-parse origin/master)

    if [ "$local_commit" = "$remote_commit" ]; then
        log "INFO" "✅ 推送验证成功"
    else
        log "WARN" "⚠️  本地和远程提交不一致"
    fi

    log "INFO" "✅ GitHub Pages 推送完成"
    return 0
}

# 发送飞书消息
send_feishu_message() {
    local message=$1
    log "INFO" "📤 发送飞书消息..."

    # 创建临时 Python 脚本发送消息
    local temp_script=$(mktemp)
    cat > "$temp_script" << 'PYTHON_SCRIPT'
#!/usr/bin/env python3
import sys
import subprocess
import json

# 读取消息内容
message = sys.stdin.read()

# 调用 OpenClaw 发送飞书消息
# 使用 openclaw CLI 发送
try:
    result = subprocess.run(
        ['openclaw', 'message', 'send', '--channel', 'feishu', '--message', message],
        capture_output=True,
        text=True,
        timeout=30
    )
    if result.returncode == 0:
        print(json.dumps({"status": "success"}))
        sys.exit(0)
    else:
        print(json.dumps({"status": "error", "message": result.stderr}), file=sys.stderr)
        sys.exit(1)
except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}), file=sys.stderr)
    sys.exit(1)
PYTHON_SCRIPT

    # 执行脚本
    echo "$message" | python3 "$temp_script" 2>/dev/null
    local exit_code=$?

    # 清理临时文件
    rm -f "$temp_script"

    if [ $exit_code -eq 0 ]; then
        log "INFO" "✅ 飞书消息发送成功"
        return 0
    else
        log "WARN" "⚠️  飞书消息发送失败（可能由主会话处理）"
        return 0  # 不影响任务执行
    fi
}

# 读取最新 BTC 报告
read_latest_btc_report() {
    local latest_report=$(ls -t "$WORKSPACE/reports/btc_report_"*.txt 2>/dev/null | head -1)

    if [ -z "$latest_report" ]; then
        log "WARN" "⚠️  未找到 BTC 报告文件"
        return 1
    fi

    cat "$latest_report"
    return 0
}

# BTC 完整流水线（每小时）
run_btc_full_pipeline() {
    log "INFO" "=========================================="
    log "INFO" "🔄 BTC 完整更新流水线"
    log "INFO" "=========================================="

    # 1. 运行市场分析
    run_task "btc_analysis" "task_btc_advanced_analysis" 2 || return 1

    # 2. 生成 HTML 报告
    run_task "html_generation" "task_generate_html" 2 || return 1

    # 3. 推送到 GitHub
    run_task "github_push" "task_push_github" 2 || return 1

    log "INFO" "🌐 网址: https://violayifan.github.io/btc-tracker-report"
    log "INFO" "✅ BTC 完整流水线执行成功"

    # 4. 发送飞书消息
    log "INFO" "📤 准备发送飞书消息..."
    local report_content=$(read_latest_btc_report)

    if [ $? -eq 0 ]; then
        # 添加访问链接前缀
        local message="[自动任务 - BTC 市场分析]

🌐 查看完整报告: https://violayifan.github.io/btc-tracker-report

─────────────────────────────────────

$report_content"

        send_feishu_message "$message"
    else
        log "WARN" "⚠️  无法读取报告，跳过飞书消息"
    fi

    log "INFO" "✅ BTC 完整流水线执行完成（含飞书消息）"

    return 0
}

# Arxiv 论文日报任务
run_arxiv_daily() {
    log "INFO" "=========================================="
    log "INFO" "📚 Arxiv 论文日报任务"
    log "INFO" "=========================================="

    cd "$WORKSPACE"

    # 运行 Arxiv 分析
    run_task "arxiv_analysis" "python3 arxiv_quant_daily.py" 2 || return 1

    # 检查飞书报告是否生成
    if [ ! -f "$WORKSPACE/temp_feishu_report.md" ]; then
        log "ERROR" "飞书报告未生成"
        return 1
    fi

    # 读取报告内容
    local report_content=$(cat "$WORKSPACE/temp_feishu_report.md")

    # 发送飞书消息
    log "INFO" "📤 发送飞书消息..."

    # 添加标题前缀
    local message="[自动任务 - Arxiv 量化金融论文日报]

─────────────────────────────────────

$report_content"

    send_feishu_message "$message"

    # 清理待处理标记
    rm -f "$WORKSPACE/.arxiv_pending"

    log "INFO" "✅ Arxiv 论文日报任务完成（含飞书消息）"
    return 0
}

# 健康检查
health_check() {
    log "INFO" "=========================================="
    log "INFO" "🏥 任务健康检查"
    log "INFO" "=========================================="

    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local issues_found=0

    # 检查 1: Git 仓库状态
    cd "$WORKSPACE"
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log "ERROR" "❌ Git 仓库未初始化"
        issues_found=$((issues_found + 1))
    else
        log "INFO" "✅ Git 仓库状态正常"
    fi

    # 检查 2: 关键文件是否存在
    local required_files=(
        "btc_advanced_monitor_v2.py"
        "arxiv_quant_daily.py"
        "task_manager.sh"
    )

    for file in "${required_files[@]}"; do
        if [ ! -f "$WORKSPACE/$file" ]; then
            log "ERROR" "❌ 缺少关键文件: $file"
            issues_found=$((issues_found + 1))
        else
            log "INFO" "✅ 文件存在: $file"
        fi
    done

    # 检查 3: 日志文件大小
    local log_files=(
        "$LOG_DIR/task_manager.log"
        "$WORKSPACE/arxiv_quant_daily.log"
        "$WORKSPACE/auto_update.log"
    )

    for log_file in "${log_files[@]}"; do
        if [ -f "$log_file" ]; then
            local size=$(du -h "$log_file" | cut -f1)
            log "INFO" "📄 $log_file: $size"
        fi
    done

    # 检查 4: Python 依赖
    if python3 -c "import requests" 2>/dev/null; then
        log "INFO" "✅ Python 依赖正常"
    else
        log "WARN" "⚠️  Python requests 模块未安装"
        issues_found=$((issues_found + 1))
    fi

    # 检查 5: 磁盘空间
    local disk_usage=$(df -h "$WORKSPACE" | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt 90 ]; then
        log "WARN" "⚠️  磁盘空间不足: ${disk_usage}%"
        issues_found=$((issues_found + 1))
    else
        log "INFO" "✅ 磁盘空间充足: ${disk_usage}%"
    fi

    log "INFO" "=========================================="
    if [ $issues_found -eq 0 ]; then
        log "INFO" "✅ 健康检查通过，无问题"
    else
        log "WARN" "⚠️  发现 $issues_found 个问题"
    fi
    log "INFO" "=========================================="

    return $issues_found
}

# 显示任务统计
show_stats() {
    log "INFO" "=========================================="
    log "INFO" "📊 任务执行统计"
    log "INFO" "=========================================="

    if [ ! -f "$TASK_STATS" ]; then
        log "WARN" "⚠️  暂无统计数据"
        return 1
    fi

    jq '.' "$TASK_STATS"
    log "INFO" "=========================================="
}

# 清理旧日志
cleanup_logs() {
    log "INFO" "=========================================="
    log "INFO" "🧹 清理旧日志"
    log "INFO" "=========================================="

    # 保留最近 7 天的日志
    find "$LOG_DIR" -name "*.log" -mtime +7 -delete 2>/dev/null
    log "INFO" "✅ 旧日志已清理"

    # 显示当前日志文件
    log "INFO" "📄 当前日志文件:"
    ls -lh "$LOG_DIR"/*.log 2>/dev/null || log "INFO" "无日志文件"

    log "INFO" "=========================================="
}

# 主函数
main() {
    local action=${1:-help}

    case "$action" in
        btc)
            run_btc_full_pipeline
            ;;
        arxiv)
            run_arxiv_daily
            ;;
        health)
            health_check
            ;;
        stats)
            show_stats
            ;;
        cleanup)
            cleanup_logs
            ;;
        *)
            echo "=========================================="
            echo "🔧 定时任务管理器"
            echo "=========================================="
            echo ""
            echo "用法: $0 <command>"
            echo ""
            echo "命令:"
            echo "  btc     - 执行 BTC 完整流水线"
            echo "  arxiv   - 执行 Arxiv 论文日报"
            echo "  health  - 健康检查"
            echo "  stats   - 显示任务统计"
            echo "  cleanup - 清理旧日志"
            echo ""
            echo "示例:"
            echo "  $0 btc          # 每小时执行"
            echo "  $0 arxiv        # 每天 8:00 执行"
            echo "  $0 health       # 每周执行一次"
            echo ""
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
