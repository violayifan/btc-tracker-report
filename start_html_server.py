#!/usr/bin/env python3
"""
简单的 HTML 报告服务器（通过 SSH 隧道转发访问）
"""

import http.server
import socketserver
import threading
import os
import time
from datetime import datetime

# 配置
HTML_FILE = "/root/.openclaw/workspace/btc_report.html"
PORT = 8081
BIND_ADDRESS = "0.0.0.0"

class HTMLRequestHandler(http.server.SimpleHTTPRequestHandler):
    """自定义请求处理器"""
    def end_headers(self):
        """设置正确的 Content-Type"""
        self.send_header('Content-type', 'text/html; charset=utf-8')
        http.server.SimpleHTTPRequestHandler.end_headers(self)

    def do_GET(self):
        """处理 GET 请求"""
        if self.path == '/':
            self.send_response(200)
            self.end_headers()
            
            # 读取 HTML 文件
            if os.path.exists(HTML_FILE):
                with open(HTML_FILE, 'r', encoding='utf-8') as f:
                    html_content = f.read()
            else:
                html_content = f"<html><body><h1>文件不存在：{HTML_FILE}</h1></body></html>"
            
            # 发送内容
            self.wfile.write(html_content.encode('utf-8'))
        elif self.path == '/health':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

def start_html_server():
    """启动 HTML 服务器"""
    
    # 检查 HTML 文件是否存在
    if not os.path.exists(HTML_FILE):
        print(f"❌ HTML 文件不存在: {HTML_FILE}")
        return False
    
    print("=" * 80)
    print("🌐 HTML 报告服务器启动")
    print("=" * 80)
    print(f"⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📄 HTML 文件: {HTML_FILE}")
    print(f"🌍 监听地址: {BIND_ADDRESS}:{PORT}")
    print(f"📱 本地访问: http://localhost:{PORT}/")
    print("=" * 80)
    print("\n" + "=" * 80)
    print("📝 SSH 隧道转发配置（外部访问）")
    print("=" * 80)
    print("\n在您的本地电脑上，运行以下命令建立 SSH 隧道：")
    print(f"\n  ssh -N -L 8080:localhost:{PORT} root@47.90.150.51")
    print(f"\n参数说明：")
    print(f"  -N           : 不执行远程命令（只转发端口）")
    print(f"  -L 8080:localhost:{PORT} : 隧道配置")
    print(f"    8080      : 本地监听端口")
    print(f"    localhost  : 远程目标")
    print(f"    {PORT}     : 服务器端口")
    print(f"  root@...   : SSH 连接（使用您的 SSH 端口）")
    print("\n建立连接后，在浏览器访问：")
    print(f"  http://localhost:8080/")
    print("\n" + "=" * 80)
    print("💡 提示：")
    print("  1. 保留 SSH 终端窗口以维持连接")
    print("  2. 连接断开后重新运行上述命令")
    print("  3. 可以在 .ssh/config 中配置永久隧道")
    print("=" * 80)
    print("\n按 Ctrl+C 停止服务器\n")
    
    try:
        # 创建服务器
        server = socketserver.TCPServer((BIND_ADDRESS, PORT), HTMLRequestHandler)
        server.allow_reuse_address = True
        
        # 在新线程中运行
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        return True, PORT
    
    except Exception as e:
        print(f"❌ 服务器启动失败: {str(e)}")
        return False, 0

def main():
    """主函数"""
    success, port = start_html_server()
    
    if success:
        print(f"\n✅ 服务器已启动！")
        print(f"🌐 服务器地址: {BIND_ADDRESS}:{port}")
        print(f"📄 文件路径: {HTML_FILE}")
        print(f"\n📋 SSH 隧道转发命令：")
        print(f"   ssh -N -L 8080:localhost:{port} root@47.90.150.51")
        print(f"\n📱 本地访问链接:")
        print(f"   http://localhost:8080/")
        print(f"\n⚠️  服务器将在后台运行")
        print(f"   按 Ctrl+C 终止")
        
        # 保持运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 服务器已停止")
    else:
        print(f"\n❌ 服务器启动失败")

if __name__ == "__main__":
    main()
