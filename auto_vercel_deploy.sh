#!/bin/bash
"""
完整的自动化部署方案
在服务器上自动将 HTML 部署到 Vercel/Netlify
"""

# 配置
HTML_DIR="/root/.openclaw/workspace"
HTML_FILE="$HTML_DIR/btc_report.html"
LOG_FILE="$HTML_DIR/deployment.log"
URL_CACHE="$HTML_DIR/public_url.txt"

# Vercel 配置
VERCEL_DIR="$HTML_DIR/vercel_project"
VERCEL_CLI="/usr/local/bin/vercel"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
    echo "$1"
}

# 检查并安装 Vercel CLI
check_vercel() {
    if [ ! -f "$VERCEL_CLI" ]; then
        log "📦 安装 Vercel CLI..."
        npm install -g vercel
        log "✅ Vercel CLI 安装完成"
    else
        log "✅ Vercel CLI 已安装"
    fi
}

# 部署到 Vercel
deploy_to_vercel() {
    log "🚀 开始部署到 Vercel..."
    
    # 创建项目目录
    mkdir -p "$VERCEL_DIR"
    cp "$HTML_FILE" "$VERCEL_DIR/index.html"
    
    # 检查是否已登录
    if ! vercel whoami &> /dev/null; then
        log "⚠️  Vercel 未登录，需要手动登录一次"
        log "请运行: vercel login"
        log "登录后，后续部署将完全自动化"
        return 1
    fi
    
    # 部署
    cd "$VERCEL_DIR"
    output=$(vercel deploy --prod --message="BTC Tracker Report - $(date '+%Y-%m-%d %H:%M:%S')" 2>&1)
    
    # 提取 URL
    url=$(echo "$output" | grep -oP '(?<=Production: )[^ ]+' | head -1)
    
    if [ -n "$url" ]; then
        log "✅ 部署成功！"
        log "🌐 公网 URL: $url"
        echo "$url" > "$URL_CACHE"
        log "💡 URL 已保存到: $URL_CACHE"
        return 0
    else
        log "❌ 部署失败"
        log "$output"
        return 1
    fi
}

# 主函数
main() {
    log "========================================"
    log "🚀 BTC 监控 - 自动部署到公网"
    log "========================================"
    
    # 检查 HTML 文件
    if [ ! -f "$HTML_FILE" ]; then
        log "❌ HTML 文件不存在: $HTML_FILE"
        exit 1
    fi
    
    log "✅ HTML 文件就绪: $HTML_FILE"
    
    # 安装 Vercel CLI
    check_vercel
    
    # 部署
    result=$(deploy_to_vercel)
    
    if [ $result -eq 0 ]; then
        # 读取缓存 URL
        if [ -f "$URL_CACHE" ]; then
            cached_url=$(cat "$URL_CACHE")
            log ""
            log "========================================"
            log "✅ 成功！"
            log "========================================"
            log ""
            log "🌐 您的公网 URL:"
            log "$cached_url"
            log ""
            log "💡 说明:"
            log "   • 这是一个永久公网 URL"
            log "   • 可以从任何设备直接访问"
            log "   • 无需登录，无需配置"
            log "   • 每小时自动更新（刷新页面即可）"
            log ""
            log "📱 在手机上访问:"
            log "   • 打开浏览器"
            log "   • 输入上述 URL"
            log "   • 完成！"
            log ""
            log "💻 在电脑上访问:"
            log "   • 打开浏览器"
            log "   • 输入上述 URL"
            log "   • 完成！"
            log ""
            log "========================================"
        fi
    fi
    
    exit $result
}

main
