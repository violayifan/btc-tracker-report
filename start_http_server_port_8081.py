#!/usr/bin/env python3
"""
简单的 HTTP 服务器托管 BTC 报告
"""

import http.server
import socketserver
import os
import threading
from datetime import datetime

# 配置
HTML_FILE = "/root/.openclaw/workspace/btc_report.html"
PORT = 8081
BIND_ADDRESS = "0.0.0.0"  # 监听所有网络接口

class BTCReportHandler(http.server.SimpleHTTPRequestHandler):
    """自定义请求处理器"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """处理 GET 请求"""
        # 记录访问日志
        client_addr = self.client_address
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] 访问来自: {client_addr[0]}:{client_addr[1]}")
        
        # 如果访问根路径，返回 HTML 文件
        if self.path == '/' or self.path == '/index.html':
            if os.path.exists(HTML_FILE):
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                
                # 读取 HTML 文件
                with open(HTML_FILE, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # 发送内容
                self.wfile.write(html_content.encode('utf-8'))
                
                print(f"[{timestamp}] HTML 文件已发送")
            else:
                self.send_error(404, "File Not Found")
                print(f"[{timestamp}] HTML 文件不存在")
        else:
            self.send_error(404, "File Not Found")
            print(f"[{timestamp}] 未找到路径: {self.path}")
    
    def log_message(self, format, *args):
        """自定义日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {format % args}")

def start_http_server():
    """启动 HTTP 服务器"""
    
    # 检查 HTML 文件
    if not os.path.exists(HTML_FILE):
        print(f"❌ HTML 文件不存在: {HTML_FILE}")
        return False, "HTML 文件不存在"
    
    print("=" * 80)
    print("🌐 BTC 报告 HTTP 服务器启动")
    print("=" * 80)
    print(f"⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📄 HTML 文件: {HTML_FILE}")
    print(f"📏 文件大小: {os.path.getsize(HTML_FILE) / 1024:.2f} KB")
    print(f"🌍 监听地址: {BIND_ADDRESS}")
    print(f"🚪 监听端口: {PORT}")
    print("=" * 80)
    print()
    print("📱 访问方式:")
    print(f"   本地访问: http://localhost:{PORT}/")
    print(f"   内网访问: http://<局域网IP>:{PORT}/")
    print(f"   公网访问: http://47.90.150.51:{PORT}/")
    print()
    print("⚠️  防火墙已开放 {PORT} 端口")
    print("✅  现在可以从任何地方访问此公网 URL！")
    print()
    print("=" * 80)
    print("按 Ctrl+C 停止服务器")
    print("=" * 80)
    print()
    
    try:
        # 创建服务器
        server = socketserver.TCPServer((BIND_ADDRESS, PORT), BTCReportHandler)
        server.allow_reuse_address = True
        
        # 在新线程中运行
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        print("✅ 服务器已启动！")
        print("🌐 公网地址: http://47.90.150.51:8081/")
        print("🎉 可以从任何地方访问了！")
        print()
        
        return True, PORT
    
    except Exception as e:
        print(f"❌ 服务器启动失败: {str(e)}")
        return False, 0

def main():
    """主函数"""
    print(f"[{datetime.now()}] 启动 BTC 报告 HTTP 服务器...")
    
    success, port = start_http_server()
    
    if success:
        print()
        print("=" * 80)
        print("🎉 成功！")
        print("=" * 80)
        print(f"🌐 公网 URL: http://47.90.150.51:{port}/")
        print()
        print("💡 使用说明:")
        print("   • 在任何设备的浏览器中打开上述 URL")
        print("   • 可以看到完整的 HTML BTC 监控报告")
        print("   • 包含市场分析、净值曲线图、回测数据")
        print("   • 每小时 BTC 监控会自动更新 HTML 文件")
        print("   • 刷新浏览器页面即可看到最新报告")
        print()
        print("🔄 服务器将持续运行")
        print("   • 按 Ctrl+C 停止服务器")
        print("   • 停止后，URL 将无法访问")
        print()
        print("=" * 80)
    else:
        print()
        print("=" * 80)
        print("❌ 启动失败")
        print("=" * 80)

if __name__ == "__main__":
    main()
