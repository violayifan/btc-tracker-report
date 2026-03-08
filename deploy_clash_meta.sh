#!/bin/bash
# -*- coding: utf-8 -*-
"""
Clash Meta 自动化安装和部署脚本
在 Linux 服务器上下载、安装、配置和启动 Clash Meta
"""

set -e  # 遇到错误立即退出

# 配置
CLASH_VERSION="latest"
CLASH_INSTALL_DIR="/root/.clash-meta"
CLASH_CONFIG_DIR="${CLASH_INSTALL_DIR}/config"
CLASH_LOG_FILE="${CLASH_INSTALL_DIR}/clash-meta.log"
SYSTEMD_SERVICE="/etc/systemd/system/clash-meta.service"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR${NC} $1"
}

# 检查是否为 root 用户
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "请使用 root 权限运行此脚本"
        exit 1
    fi
}

# 检查系统架构
check_architecture() {
    ARCH=$(uname -m)
    log "检测到系统架构: ${ARCH}"

    if [[ $ARCH == "x86_64" ]]; then
        DOWNLOAD_ARCH="amd64"
    elif [[ $ARCH == "aarch64" ]]; then
        DOWNLOAD_ARCH="arm64"
    else
        error "不支持的系统架构: ${ARCH}"
        exit 1
    fi
}

# 下载 Clash Meta
download_clash_meta() {
    log "开始下载 Clash Meta..."

    # 创建安装目录
    mkdir -p "${CLASH_INSTALL_DIR}"

    # 获取最新版本号（通过 GitHub API）
    log "获取 Clash Meta 最新版本信息..."
    LATEST_VERSION=$(curl -s "https://api.github.com/repos/MetaCubeX/meta/releases/latest" | grep '"tag_name":' | sed -n 's/.*"\([^"]*\)".*/\1/p')

    if [[ -z "${LATEST_VERSION}" ]]; then
        error "无法获取最新版本号"
        LATEST_VERSION="v2.12.3"  # 使用默认版本
    fi

    log "最新版本: ${LATEST_VERSION}"

    # 下载对应架构的二进制文件
    DOWNLOAD_URL="https://github.com/MetaCubeX/meta/releases/download/${LATEST_VERSION}/Meta-${DOWNLOAD_ARCH}-host-linux-${LATEST_VERSION}.gz"

    log "下载地址: ${DOWNLOAD_URL}"
    log "开始下载..."

    wget -O "${CLASH_INSTALL_DIR}/clash-meta.gz" "${DOWNLOAD_URL}"

    if [[ $? -eq 0 ]]; then
        log "下载成功"
    else
        error "下载失败"
        exit 1
    fi

    # 解压
    log "正在解压..."
    gunzip "${CLASH_INSTALL_DIR}/clash-meta.gz"

    # 重命名为 meta
    mv "${CLASH_INSTALL_DIR}/Meta-${DOWNLOAD_ARCH}-host-linux-${LATEST_VERSION}/meta" "${CLASH_INSTALL_DIR}/meta"
    rm -rf "${CLASH_INSTALL_DIR}/Meta-${DOWNLOAD_ARCH}-host-linux-${LATEST_VERSION}"

    # 赋予执行权限
    chmod +x "${CLASH_INSTALL_DIR}/meta"

    log "Clash Meta 下载和安装完成"
}

# 创建配置文件
create_config() {
    log "创建 Clash Meta 配置..."

    mkdir -p "${CLASH_CONFIG_DIR}"

    # 创建基础配置文件
    cat > "${CLASH_CONFIG_DIR}/config.yaml" << 'EOF'
port: 7890
socks-port: 7891
allow-lan: true
mode: rule
log-level: info
external-controller: 127.0.0.1:9090
secret: "MetaCubeX"
EOF

    log "基础配置文件已创建: ${CLASH_CONFIG_DIR}/config.yaml"

    # 创建 Country.mmdb（需要的地理数据库）
    log "下载 Country.mmdb..."
    wget -O "${CLASH_CONFIG_DIR}/Country.mmdb" "https://github.com/MetaCubeX/meta-rules/releases/download/latest/GeoSite.dat"

    log "配置文件创建完成"
}

# 创建 systemd 服务
create_systemd_service() {
    log "创建 systemd 服务..."

    cat > "${SYSTEMD_SERVICE}" << 'EOF'
[Unit]
Description=Clash Meta Service
After=network.target

[Service]
Type=simple
User=root
ExecStart=/root/.clash-meta/meta -d /root/.clash-meta/config
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

    # 重新加载 systemd
    systemctl daemon-reload

    log "systemd 服务已创建"
}

# 启动 Clash Meta
start_clash_meta() {
    log "启动 Clash Meta 服务..."

    # 启动服务
    systemctl start clash-meta

    # 检查服务状态
    sleep 3
    systemctl status clash-meta

    if [[ $? -eq 0 ]]; then
        log "Clash Meta 服务启动成功"
    else
        error "Clash Meta 服务启动失败"
        systemctl status clash-meta
        exit 1
    fi
}

# 显示代理配置信息
show_proxy_info() {
    log "========================================"
    log "Clash Meta 代理配置"
    log "========================================"
    log "HTTP 代理: http://服务器IP:7890"
    log "SOCKS5 代理: socks5://服务器IP:7891"
    log "控制面板: http://服务器IP:9090/ui"
    log "========================================"
    log "默认密码: MetaCubeX"
    log "配置文件: ${CLASH_CONFIG_DIR}/config.yaml"
    log "========================================"
}

# 安装依赖
install_dependencies() {
    log "安装必要的依赖..."

    # 检查并安装 wget
    if ! command -v wget &> /dev/null; then
        apt-get update -qq
        apt-get install -y wget
    fi

    # 检查并安装 curl
    if ! command -v curl &> /dev/null; then
        apt-get install -y curl
    fi

    # 检查并安装 gunzip
    if ! command -v gunzip &> /dev/null; then
        apt-get install -y gzip
    fi

    log "依赖安装完成"
}

# 主函数
main() {
    log "========================================"
    log "Clash Meta 自动化部署脚本"
    log "========================================"

    # 检查 root 权限
    check_root

    # 检查系统架构
    check_architecture

    # 安装依赖
    install_dependencies

    # 下载 Clash Meta
    download_clash_meta

    # 创建配置文件
    create_config

    # 创建 systemd 服务
    create_systemd_service

    # 启动 Clash Meta
    start_clash_meta

    # 显示配置信息
    show_proxy_info

    log "========================================"
    log "部署完成！"
    log "========================================"
    log ""
    log "后续操作："
    log "1. 访问控制面板: http://服务器IP:9090/ui"
    log "2. 登录账户并配置订阅链接"
    log "3. 选择节点并启用"
    log "4. 配置客户端代理: http://服务器IP:7890"
    log ""
    log "服务管理："
    log "• 查看状态: systemctl status clash-meta"
    log "• 停止服务: systemctl stop clash-meta"
    log "• 重启服务: systemctl restart clash-meta"
    log "• 开机自启: systemctl enable clash-meta"
    log ""
    log "日志查看:"
    log "• 服务日志: journalctl -u clash-meta -f"
    log "• 直接日志: cat ${CLASH_LOG_FILE}"
}

# 运行主函数
main "$@"