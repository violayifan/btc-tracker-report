#!/usr/bin/env python3
"""
创建一个简单的 HTTP 服务器并测试访问
"""

import http.server
import socketserver
import threading
import time
import urllib.request
from datetime import datetime

# 配置
HTML_FILE = "/root/.openclaw/workspace/btc_report.html"
PORT = 8082  # 使用 8082 避免冲突
BIND_ADDRESS = "0.0.0.0"

class ReportHandler(http.server.SimpleHTTPRequestHandler):
    """自定义请求处理器"""
    
    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {message}")
    
    def do_GET(self):
        """处理 GET 请求"""
        self.log(f"收到请求: {self.path} from {self.client_address}")
        
        if self.path == '/' or self.path == '/index.html':
            if os.path.exists(HTML_FILE):
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                
                with open(HTML_FILE, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                self.wfile.write(html_content.encode('utf-8'))
                self.log(f"✅ 已发送 HTML 文件 ({len(html_content)} bytes)")
            else:
                self.send_error(404, "File Not Found")
                self.log(f"❌ 文件不存在: {HTML_FILE}")
        else:
            self.send_error(404, "Not Found")
            self.log(f"❌ 未找到路径: {self.path}")

def start_server():
    """启动 HTTP 服务器"""
    
    if not os.path.exists(HTML_FILE):
        print(f"❌ HTML 文件不存在: {HTML_FILE}")
        return False
    
    try:
        # 创建服务器
        server = socketserver.TCPServer((BIND_ADDRESS, PORT), ReportHandler)
        server.allow_reuse_address = True
        
        # 在新线程中运行
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        print("=" * 70)
        print("🌐 HTTP 服务器已启动")
        print("=" * 70)
        print(f"⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📄 HTML 文件: {HTML_FILE}")
        print(f"📍 监听地址: {BIND_ADDRESS}")
        print(f"🚪 监听端口: {PORT}")
        print("=" * 70)
        print(f"📱 本地访问: http://localhost:{PORT}/")
        print(f"🖥 内网访问: http://<内网IP>:{PORT}/")
        print(f"🌐 公网访问: http://47.90.150.51:{PORT}/")
        print("=" * 70)
        print(f"⚠️  请稍等 3-5 秒...")
        print(f"⚠️  如果仍无法访问，请检查防火墙安全组")
        print(f"⚠️  确保云服务商安全组开放 {PORT} 端口")
        print(f"⚠️  需要添加 TCP 入站规则，允许 0.0.0.0/0")
        print("=" * 70)
        print(f"\n🔄 正在测试服务器连接...")
        print()
        
        # 等待服务器启动
        time.sleep(2)
        
        # 测试服务器是否可访问
        try:
            test_url = f"http://{BIND_ADDRESS}:{PORT}/"
            self.log(f"📤 测试 URL: {test_url}")
            response = urllib.request.urlopen(test_url, timeout=10)
            status_code = response.getcode()
            content_length = response.getheader('Content-Length')
            
            print(f"✅ 服务器测试成功！")
            print(f"📊 状态码: {status_code}")
            print(f"📏 内容长度: {content_length} bytes")
            print()
            print("=" * 70)
            print(f"🎉 服务器已就绪！")
            print(f"🌐 公网访问地址: http://47.90.150.51:{PORT}/")
            print(f"🔍 您的公网 IP: http://47.90.150.51:{PORT}/")
            print("=" * 70)
            print(f"💡 提示:")
            print(f"   • 端口: {PORT}")
            print(f"   • 协议: HTTP")
            print(f"   • 防火墙: 需要开放 {PORT} 端口")
            print(f"   • 安全组: 需要添加 TCP 入站规则")
            print(f"   • 源: 0.0.0.0/0 (允许所有 IP)")
            print(f"   • 或指定您的 IP")
            print("=" * 70)
            print(f"\n📱 在浏览器中访问:")
            print(f"   {test_url}")
            print()
            print(f"📱 或在手机浏览器中访问:")
            print(f"   http://47.90.150.51:{PORT}/")
            print("=" * 70)
            print(f"\n按 Ctrl+C 停止服务器\n")
            
            return True, PORT
            
        except Exception as e:
            print(f"\n❌ 服务器测试失败: {str(e)}")
            print(f"\n⚠️  可能的原因:")
            print(f"   1. 防火墙或安全组未开放 {PORT} 端口")
            print(f"   2. 云服务商的防火墙阻止连接")
            print(f"   3. 端口 {PORT} 已被占用")
            print(f"   4. 服务器地址绑定问题")
            print(f"\n💡 解决方案:")
            print(f"   • 检查防火墙: sudo firewall-cmd --list-all")
            print(f"   • 开放端口: sudo firewall-cmd --permanent --add-port={PORT}/tcp")
            print(f"   • 重新加载: sudo firewall-cmd --reload")
            print(f"   • 在云服务商控制台添加安全组规则")
            print(f"   • 允许 TCP 端口 {PORT}，源 0.0.0.0/0")
            print("=" * 70)
            
            return False, 0
    
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n❌ 错误: 端口 {PORT} 已被占用")
            print(f"💡 解决方案:")
            print(f"   1. 查找占用进程: lsof -i:{PORT} -P")
            print(f"   2. 杀掉进程: kill -9 <PID>")
            print(f"   3. 或使用其他端口: 8083, 8084 等")
        else:
            print(f"\n❌ 启动失败: {str(e)}")
        
        print("=" * 70)
        return False, 0

if __name__ == "__main__":
    import os
    import signal
    import sys
    
    start_server()
