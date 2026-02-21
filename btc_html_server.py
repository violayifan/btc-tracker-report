#!/usr/bin/env python3
"""
生成 BTC 交易分析的 HTML 报告（简化版）
"""

import os
import base64
from datetime import datetime
import glob
import http.server
import socket
import threading

# 路径配置
WORKSPACE = "/root/.openclaw/workspace"
OUTPUT_DIR = os.path.join(WORKSPACE, "reports")
HTML_OUTPUT = os.path.join(WORKSPACE, "btc_report.html")
PNG_IMAGE = os.path.join(WORKSPACE, "backtest_chart.png")

def read_file_content(filepath):
    """读取文件内容"""
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def image_to_base64(image_path):
    """将图片转为 base64"""
    if os.path.exists(image_path):
        with open(image_path, 'rb') as f:
            encoded = base64.b64encode(f.read())
            return encoded.decode('utf-8')
    return ""

def get_latest_report():
    """获取最新的报告内容"""
    content = {
        'market': '暂无市场分析报告',
        'backtest': '暂无回测报告'
    }
    
    # 读取市场分析报告
    market_files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "btc_report_*.txt")))
    if market_files:
        content['market'] = read_file_content(market_files[-1])
    
    # 读取回测报告
    backtest_files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "btc_backtest_report_*.txt")))
    if backtest_files:
        content['backtest'] = read_file_content(backtest_files[-1])
    
    return content

def format_text_for_html(text):
    """将纯文本格式化为 HTML（简单转义）"""
    if not text:
        return ""
    
    # 简单的转义
    html_text = text.replace('&', '&amp;')
    html_text = html_text.replace('<', '&lt;')
    html_text = html_text.replace('>', '&gt;')
    
    # 保留换行
    html_text = html_text.replace('\n', '<br>\n')
    
    return html_text

def generate_html():
    """生成完整的 HTML 页面"""
    
    # 获取报告内容
    reports = get_latest_report()
    image_base64 = image_to_base64(PNG_IMAGE)
    report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 构建 HTML
    html_parts = []
    
    # HTML 头部
    html_parts.append("""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTC 交易分析报告 - """ + report_time + """</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: #fff;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }

        .header h1 {
            margin: 0;
            font-size: 36px;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }

        .header .time {
            font-size: 16px;
            opacity: 0.9;
            margin-top: 10px;
        }

        .section {
            padding: 30px;
            border-bottom: 1px solid #eee;
        }

        .section:last-child {
            border-bottom: none;
        }

        .section-title {
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }

        .content-box {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }

        .pre-formatted {
            font-family: "Courier New", "Monaco", "Consolas", monospace;
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            font-size: 14px;
            line-height: 1.6;
            white-space: pre-wrap;
            word-wrap: break-word;
            border: 1px solid #e0e0e0;
        }

        .image-container {
            text-align: center;
            margin: 30px 0;
            background: #fff;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }

        .chart-image {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }

        .no-image {
            color: #999;
            padding: 20px;
            text-align: center;
        }

        .footer {
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            color: #666;
            font-size: 14px;
            margin-top: 20px;
        }

        .metrics {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-top: 20px;
        }

        .metric-card {
            flex: 1;
            min-width: 150px;
            background: #fff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }

        .metric-label {
            color: #666;
            font-size: 13px;
            margin-bottom: 8px;
        }

        .metric-value {
            font-size: 18px;
            font-weight: bold;
            color: #333;
        }

        .positive {
            color: #10b981;
        }

        .negative {
            color: #ef4444;
        }

        @media (max-width: 768px) {
            .container {
                margin: 0;
                border-radius: 0;
                box-shadow: none;
            }
            
            .section {
                padding: 20px;
            }
            
            .header {
                padding: 20px;
            }
            
            .header h1 {
                font-size: 24px;
            }
            
            .metrics {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>BTC 交易分析报告</h1>
            <div class="time">报告时间：""" + report_time + """</div>
        </div>

        <!-- 市场分析部分 -->
        <div class="section">
            <div class="section-title">💰 市场分析</div>
            <div class="content-box">
                <div class="pre-formatted">""" + format_text_for_html(reports['market']) + """</div>
            </div>
        </div>

        <!-- 净值曲线图部分 -->
        <div class="section">
            <div class="section-title">📈 净值曲线图</div>
            <div class="image-container">""")
    
    # 如果有图片，嵌入 base64
    if image_base64:
        html_parts.append("""                <img src="data:image/png;base64,"""") + image_base64 + """" alt="BTC 净值曲线图" class="chart-image" />""")
    else:
        html_parts.append("""                <div class="no-image">图表文件不存在</div>""")
    
    html_parts.append("""
            </div>
        </div>

        <!-- 回测报告部分 -->
        <div class="section">
            <div class="section-title">📊 交易回测报告</div>
            <div class="content-box">
                <div class="pre-formatted">""" + format_text_for_html(reports['backtest']) + """</div>
            </div>
        </div>

        <!-- 关键指标卡片 -->
        <div class="section">
            <div class="section-title">🎯 关键指标</div>
            <div class="metrics">
                <div class="metric-card">
                    <div class="metric-label">报告类型</div>
                    <div class="metric-value">HTML 实时报告</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">查看方式</div>
                    <div class="metric-value">手机/电脑浏览器</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">更新频率</div>
                    <div class="metric-value">每小时自动</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">最后更新</div>
                    <div class="metric-value">""" + report_time + """</div>
                </div>
            </div>
        </div>

        <div class="footer">
            <p>📱 此页面专为手机和电脑浏览器优化</p>
            <p>⚠️ 本报告仅供参考，不构成投资建议</p>
            <p>🔄 自动生成时间：""" + report_time + """</p>
        </div>
    </div>

    <script>
        window.onload = function() {
            console.log('BTC 交易分析报告已加载');
            console.log('最后更新：""" + report_time + """');
        };
    </script>
</body>
</html>""")
    
    return "".join(html_parts)

def save_html():
    """保存 HTML 文件"""
    html_content = generate_html()
    
    with open(HTML_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("HTML 报告已生成")
    return HTML_OUTPUT

def start_server():
    """启动 HTTP 服务器"""
    PORT = 8080
    
    # 自定义处理器
    class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header('Content-type', 'text/html; charset=utf-8')
            http.server.SimpleHTTPRequestHandler.end_headers(self)

    try:
        server = http.server.HTTPServer(('0.0.0.0', PORT), MyHTTPRequestHandler)
        
        print("=" * 60)
        print("HTTP 服务器已启动")
        print("=" * 60)
        print("访问地址：")
        print(f"  本地: http://localhost:{PORT}/btc_report.html")
        print(f"  外部: http://<服务器IP>:{PORT}/btc_report.html")
        print("=" * 60)
        print("按 Ctrl+C 停止服务器")
        print("=" * 60)
        print()

        # 在后台运行
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()

        return PORT, True

    except OSError as e:
        if "Address already in use" in str(e):
            print(f"端口 {PORT} 已被占用，服务器可能已在运行")
            print(f"访问地址: http://<服务器IP>:{PORT}/btc_report.html")
            return PORT, True
        else:
            print(f"启动服务器失败: {e}")
            return PORT, False
    except Exception as e:
        print(f"发生错误: {e}")
        return PORT, False

def main():
    """主函数"""
    print(f"[{datetime.now()}] 开始生成 HTML 报告...")
    
    # 保存 HTML
    html_path = save_html()
    print(f"文件路径: {html_path}")
    
    # 启动服务器
    port, success = start_server()
    
    if success:
        print(f"✅ HTML 报告已就绪！")
        print(f"📱 请在手机或电脑浏览器中打开：")
        print(f"   http://<服务器IP>:{port}/btc_report.html")
        print(f"✨ 页面特点：")
        print(f"   - 包含嵌入了图片（无需额外下载）")
        print(f"   - 响应式设计，支持手机和电脑")
        print(f"   - 美观的界面和样式")

if __name__ == "__main__":
    main()
