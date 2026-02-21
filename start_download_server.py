#!/usr/bin/env python3
"""
简单的下载服务器 - 使用 80 端口
"""

import http.server
import socket
import threading
import os
from datetime import datetime

PORT = 80
HTML_FILE = "/root/.openclaw/workspace/btc_report_enhanced.html"

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            # 重定向到报告文件
            self.path = '/btc_report_enhanced.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def end_headers(self):
        self.send_header('Content-type', 'text/html; charset=utf-8')
        http.server.SimpleHTTPRequestHandler.end_headers(self)

    def log_message(self, format, *args):
        # 不输出日志
        pass

def start_server():
    try:
        # 切换到工作目录
        os.chdir('/root/.openclaw/workspace')

        server = http.server.HTTPServer(('0.0.0.0', PORT), MyHTTPRequestHandler)
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        return True, None
    except PermissionError:
        return False, "需要 root 权限绑定 80 端口"
    except OSError as e:
        if "Address already in use" in str(e):
            return False, "80 端口已被占用"
        elif "Permission denied" in str(e):
            return False, "需要 root 权限绑定 80 端口"
        else:
            return False, str(e)

def main():
    print("=" * 60)
    print("🚀 启动下载服务器")
    print("=" * 60)

    success, error = start_server()

    if success:
        print(f"✅ 服务器启动成功！")
        print(f"\n📋 访问信息:")
        print(f"  • 外网访问: http://47.90.150.51/btc_report_enhanced.html")
        print(f"  • 本地访问: http://0.0.0.0/btc_report_enhanced.html")
        print(f"\n💡 提示:")
        print(f"  • 80 端口通常已经开放")
        print(f"  • 如果仍无法访问，可能是云服务商安全组限制")
        print(f"\n按 Ctrl+C 停止服务器")
        print("=" * 60)

        try:
            while True:
                pass
        except KeyboardInterrupt:
            print("\n\n🛑 服务器已停止")
    else:
        print(f"❌ 服务器启动失败: {error}")
        print(f"\n📋 尝试其他方案:")

if __name__ == "__main__":
    main()
