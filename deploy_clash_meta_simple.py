#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clash Meta 下载和部署脚本 - 简化版本
专注于当前服务器环境，解决网络和API问题
"""

import subprocess
import os
import sys
import json
from pathlib import Path
from datetime import datetime

class ClashMetaDeployer:
    def __init__(self):
        self.workspace = Path("/root/.openclaw/workspace")
        self.install_dir = self.workspace / "clash-meta"
        self.config_dir = self.install_dir / "config"
        self.log_file = self.install_dir / "deploy.log"

        # 创建目录
        self.install_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        print(log_message.strip())
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message)

    def check_server_info(self):
        """检查服务器信息"""
        self.log("检查服务器环境...")

        info = {
            'arch': subprocess.run(['uname', '-m'], capture_output=True, text=True).stdout.strip(),
            'ip': subprocess.run(['hostname', '-I'], capture_output=True, text=True).stdout.strip(),
            'disk': subprocess.run(['df', '-h', '/root'], capture_output=True, text=True).stdout.split()[4],
            'memory': subprocess.run(['free', '-h'], capture_output=True, text=True).stdout.split()[6],
        }

        self.log(f"架构: {info['arch']}")
        self.log(f"IP地址: {info['ip']}")
        self.log(f"磁盘空间: {info['disk']}")
        self.log(f"内存: {info['memory']}")

        return info

    def run_command(self, cmd, description, timeout=120):
        """运行命令"""
        try:
            self.log(f"执行: {description}")
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            stdout, stderr = proc.communicate(timeout=timeout)

            if proc.returncode == 0:
                self.log(f"✅ {description} 成功")
                return True, stdout, stderr
            else:
                self.log(f"❌ {description} 失败: returncode={proc.returncode}")
                return False, stdout, stderr

        except subprocess.TimeoutExpired:
            self.log(f"⏱ {description} 超时")
            return False, None, "命令执行超时"
        except Exception as e:
            self.log(f"❌ {description} 异常: {str(e)}")
            return False, None, str(e)

    def download_clash_meta(self):
        """下载 Clash Meta"""
        self.log("开始下载 Clash Meta...")

        # 多个下载源的优先级
        download_sources = [
            {
                'name': '官方CDN',
                'url': 'https://download.metaprd.com/Meta-linux-amd64-v2.12.3.zip',
                'priority': 1
            },
            {
                'name': 'GitHub Release',
                'url': 'https://github.com/MetaCubeX/Meta/releases/download/v2.12.3/Meta-linux-amd64-v2.12.3.zip',
                'priority': 2
            },
            {
                'name': '备用镜像',
                'url': 'https://github.com/MetaCubeX/Meta/releases/download/v2.12.2/Meta-linux-amd64-v2.12.2.zip',
                'priority': 3
            }
        ]

        # 尝试从每个源下载
        for source in download_sources:
            self.log(f"尝试从 {source['name']} 下载...")

            download_file = self.install_dir / "clash-meta.zip"

            cmd = ['wget', '-O', download_file, source['url']]
            success, stdout, stderr = self.run_command(
                cmd,
                f"从 {source['name']} 下载",
                timeout=300
            )

            if success and download_file.exists():
                file_size = download_file.stat().st_size / (1024 * 1024)  # MB
                self.log(f"✅ 下载成功: {source['name']} ({file_size:.2f} MB)")
                return download_file

            self.log(f"❌ 从 {source['name']} 下载失败")

        return None

    def extract_clash_meta(self, zip_file):
        """解压 Clash Meta"""
        self.log("解压 Clash Meta...")

        cmd = ['unzip', '-o', str(self.install_dir), str(zip_file)]
        success, stdout, stderr = self.run_command(
            cmd,
            "解压 zip 文件",
            timeout=120
        )

        if success:
            self.log("✅ 解压成功")

            # 查找解压后的可执行文件
            meta_binary = None
            for root, dirs, files in os.walk(self.install_dir):
                for file in files:
                    if file == 'meta' or file == 'Meta':
                        meta_binary = os.path.join(root, file)
                        break
                    if file == 'meta-gh':
                        meta_binary = os.path.join(root, file)
                        break
                    if file.endswith('.AppImage'):
                        # AppImage 格式
                        meta_binary = os.path.join(root, file)
                        break

            if meta_binary:
                self.log(f"✅ 找到可执行文件: {meta_binary}")
                return meta_binary
            else:
                self.log("❌ 未找到可执行文件")
                return None

        return None

    def create_simple_config(self):
        """创建简单配置"""
        self.log("创建基础配置...")

        # 创建配置目录
        config_file = self.config_dir / "config.yaml"

        # 基础配置
        config_content = """port: 7890
socks-port: 7891
allow-lan: true
mode: rule
log-level: info
external-controller: 127.0.0.1:9090
mixed-port: 7892
ipv6: true
"""

        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(config_content)
            self.log(f"✅ 配置文件创建成功: {config_file}")
            return config_file
        except Exception as e:
            self.log(f"❌ 配置文件创建失败: {str(e)}")
            return None

    def create_systemd_service(self, meta_binary, config_file):
        """创建 systemd 服务"""
        self.log("创建 systemd 服务...")

        service_file = "/etc/systemd/system/clash-meta.service"

        service_content = f"""[Unit]
Description=Clash Meta Service
After=network.target

[Service]
Type=simple
User=root
ExecStart={meta_binary} -d {config_file}
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
"""

        try:
            with open(service_file, 'w', encoding='utf-8') as f:
                f.write(service_content)
            self.log(f"✅ 服务文件创建成功: {service_file}")
            return service_file
        except Exception as e:
            self.log(f"❌ 服务文件创建失败: {str(e)}")
            return None

    def start_service(self):
        """启动服务"""
        self.log("启动 Clash Meta 服务...")

        # 重新加载 systemd
        cmd = ['systemctl', 'daemon-reload']
        self.run_command(cmd, "重新加载 systemd", timeout=30)

        # 启用服务
        cmd = ['systemctl', 'enable', 'clash-meta']
        success, _, _ = self.run_command(cmd, "启用服务", timeout=30)

        if success:
            # 启动服务
            cmd = ['systemctl', 'start', 'clash-meta']
            success, stdout, stderr = self.run_command(cmd, "启动服务", timeout=30)

            if success:
                self.log("✅ 服务启动成功")
                return True
            else:
                self.log("❌ 服务启动失败")
                return False
        else:
            self.log("❌ 服务启用失败")
            return False

    def check_service_status(self):
        """检查服务状态"""
        self.log("检查服务状态...")

        cmd = ['systemctl', 'status', 'clash-meta']
        success, stdout, stderr = self.run_command(cmd, "检查状态", timeout=30)

        if success:
            # 检查服务是否活跃
            cmd = ['systemctl', 'is-active', 'clash-meta']
            success, stdout, stderr = self.run_command(cmd, "检查活跃状态", timeout=10)

            is_active = success and "active" in stdout

            if is_active:
                self.log("✅ 服务运行中")

                # 检查端口
                cmd = ['netstat', '-tulpn', ':7890']
                success, stdout, stderr = self.run_command(cmd, "检查端口", timeout=10)
                port_active = success and len(stdout.strip()) > 0

                self.log(f"端口状态: {'✅ 端口 7890 监听中' if port_active else '❌ 端口未监听'}")

                return {
                    'service_running': True,
                    'port_active': port_active,
                    'status_output': stdout
                }
            else:
                self.log("❌ 服务未运行")
                return {
                    'service_running': False,
                    'port_active': False,
                    'status_output': stdout
                }
        else:
            self.log("❌ 无法检查服务状态")
            return {
                'service_running': False,
                'status_output': stderr
            }

    def show_proxy_info(self, status):
        """显示代理信息"""
        self.log("========================================")
        self.log("Clash Meta 代理配置")
        self.log("========================================")

        if status.get('service_running'):
            self.log("HTTP 代理: http://服务器IP:7890")
            self.log("SOCKS5 代理: socks5://服务器IP:7891")
            self.log("配置文件: /root/.clash-meta/config/config.yaml")
            self.log("========================================")

            if status.get('port_active'):
                self.log("✅ 代理服务运行正常")
            else:
                self.log("⚠️ 端口未正常监听")
                self.log("请检查: systemctl status clash-meta")
        else:
            self.log("❌ 代理服务未运行")
            self.log("启动服务: systemctl start clash-meta")
            self.log("查看日志: journalctl -u clash-meta -f")
            self.log("========================================")

    def deploy(self):
        """完整部署流程"""
        self.log("开始 Clash Meta 完整部署...")
        self.log("=" * 60)

        # 1. 检查服务器信息
        server_info = self.check_server_info()

        # 2. 下载 Clash Meta
        zip_file = self.download_clash_meta()

        if not zip_file:
            self.log("❌ 下载失败，部署终止")
            return False

        # 3. 解压
        meta_binary = self.extract_clash_meta(zip_file)

        if not meta_binary:
            self.log("❌ 解压失败，部署终止")
            return False

        # 4. 创建配置
        config_file = self.create_simple_config()

        if not config_file:
            self.log("❌ 配置创建失败，部署终止")
            return False

        # 5. 创建 systemd 服务
        service_file = self.create_systemd_service(meta_binary, config_file)

        if not service_file:
            self.log("❌ 服务创建失败，部署终止")
            return False

        # 6. 启动服务
        start_success = self.start_service()

        if not start_success:
            self.log("❌ 服务启动失败，部署终止")
            return False

        # 7. 检查服务状态
        status = self.check_service_status()

        # 8. 显示代理信息
        self.show_proxy_info(status)

        # 9. 保存部署信息
        deploy_info = {
            'timestamp': datetime.now().isoformat(),
            'server_info': server_info,
            'meta_binary': meta_binary,
            'config_file': str(config_file),
            'service_file': str(service_file),
            'status': status,
            'install_dir': str(self.install_dir)
        }

        deploy_info_file = self.install_dir / "deploy_info.json"
        with open(deploy_info_file, 'w', encoding='utf-8') as f:
            json.dump(deploy_info, f, ensure_ascii=False, indent=2)

        self.log(f"✅ 部署信息已保存: {deploy_info_file}")

        # 总结
        self.log("=" * 60)
        self.log("✅ 部署完成！")
        self.log("=" * 60)
        self.log("")
        self.log("后续操作:")
        self.log("1. 访问控制面板: http://服务器IP:9090")
        self.log("2. 查看服务状态: systemctl status clash-meta")
        self.log("3. 查看日志: journalctl -u clash-meta -f")
        self.log("4. 配置订阅链接（如需要）")
        self.log("5. 添加分流规则（如需要）")
        self.log("=" * 60)

        return True

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python3 deploy_clash_meta_simple.py --deploy     # 完整部署")
        print("  python3 deploy_clash_meta_simple.py --status      # 检查状态")
        print("  python3 deploy_clash_meta_simple.py --start      # 启动服务")
        print("  python3 deploy_clash_meta_simple.py --stop       # 停止服务")
        print("  python3 deploy_clash_meta_simple.py --restart    # 重启服务")
        return

    command = sys.argv[1]

    deployer = ClashMetaDeployer()

    if command == '--deploy':
        deployer.deploy()
    elif command == '--status':
        deployer.show_proxy_info(deployer.check_service_status())
    elif command == '--start':
        deployer.start_service()
    elif command == '--stop':
        deployer.run_command(['systemctl', 'stop', 'clash-meta'], "停止服务", 60)
    elif command == '--restart':
        deployer.run_command(['systemctl', 'restart', 'clash-meta'], "重启服务", 60)
    else:
        print("❌ 未知命令")
        sys.exit(1)

if __name__ == "__main__":
    main()