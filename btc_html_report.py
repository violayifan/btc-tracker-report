#!/usr/bin/env python3
"""
生成 BTC 交易分析的 HTML 报告
"""

import os
import base64
from datetime import datetime
import json
import glob

# 路径配置
WORKSPACE = "/root/.openclaw/workspace"
OUTPUT_DIR = os.path.join(WORKSPACE, "reports")
HTML_OUTPUT = os.path.join(WORKSPACE, "btc_report.html")
PNG_IMAGE = os.path.join(WORKSPACE, "backtest_chart.png")

def image_to_base64(image_path: str) -> str:
    """将图片转为 base64"""
    if os.path.exists(image_path):
        with open(image_path, 'rb') as f:
            encoded = base64.b64encode(f.read())
            return encoded.decode('utf-8')
    return ""

def read_latest_reports():
    """读取最新的报告"""
    reports = {}

    # 读取市场分析报告
    market_report_files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "btc_report_*.txt")))
    if market_report_files:
        with open(market_report_files[-1], 'r', encoding='utf-8') as f:
            reports['market'] = f.read()

    # 读取回测报告
    backtest_report_files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "btc_backtest_report_*.txt")))
    if backtest_report_files:
        with open(backtest_report_files[-1], 'r', encoding='utf-8') as f:
            reports['backtest'] = f.read()

    return reports

def generate_html_report(reports: dict) -> str:
    """生成 HTML 报告"""
    
    # 图片转 base64
    image_base64 = image_to_base64(PNG_IMAGE)

    # 构建 HTML
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTC 交易分析报告 - {datetime.now().strftime("%Y-%m-%d %H:%M")}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: #fff;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}

        .header h1 {{
            margin: 0;
            font-size: 32px;
            font-weight: bold;
        }}

        .header .time {{
            font-size: 16px;
            opacity: 0.9;
            margin-top: 10px;
        }}

        .section {{
            padding: 30px;
            border-bottom: 1px solid #eee;
        }}

        .section:last-child {{
            border-bottom: none;
        }}

        .section-title {{
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
        }}

        .section-title::before {{
            content: "";
            width: 6px;
            height: 24px;
            background: #667eea;
            margin-right: 10px;
            border-radius: 3px;
        }}

        .content-box {{
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }}

        .pre-formatted {{
            font-family: "Courier New", Courier, monospace;
            background: #fff;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 13px;
            line-height: 1.6;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}

        .image-container {{
            text-align: center;
            margin: 20px 0;
            background: #fff;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}

        .chart-image {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}

        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}

        .metric-card {{
            background: #fff;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }}

        .metric-label {{
            color: #666;
            font-size: 14px;
            margin-bottom: 8px;
        }}

        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }}

        .positive {{ color: #10b981; }}
        .negative {{ color: #ef4444; }}

        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 14px;
        }}

        @media (max-width: 768px) {{
            .container {{
                margin: 0;
                border-radius: 0;
                box-shadow: none;
            }}
            
            .section {{
                padding: 20px;
            }}
            
            .header {{
                padding: 20px;
            }}
            
            .header h1 {{
                font-size: 24px;
            }}
            
            .metric-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 BTC 交易分析报告</h1>
            <div class="time">报告时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
        </div>

        <!-- 市场分析部分 -->
        <div class="section">
            <div class="section-title">💰 市场分析</div>
            <div class="pre-formatted">
{reports.get('market', '暂无市场分析报告').replace('\n', '<br>\n')}
            </div>
        </div>

        <!-- 回测图表部分 -->
        <div class="section">
            <div class="section-title">📈 净值曲线图</div>
            <div class="image-container">
"""
    
    # 如果有图片，嵌入 base64
    if image_base64:
        html += f"""                <img src="data:image/png;base64,{image_base64}" alt="BTC 净值曲线图" class="chart-image" />
"""
    else:
        html += """                <p style="color: #999;">图表文件不存在</p>
"""
    
    html += f"""            </div>
        </div>

        <!-- 回测报告部分 -->
        <div class="section">
            <div class="section-title">📋 交易回测报告</div>
            <div class="pre-formatted">
{reports.get('backtest', '暂无回测报告').replace('\n', '<br>\n')}
            </div>
        </div>

        <!-- 统计指标卡片 -->
        <div class="section">
            <div class="section-title">📊 关键指标汇总</div>
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-label">更新时间</div>
                    <div class="metric-value" style="font-size: 16px;">{datetime.now().strftime("%H:%M:%S")}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">报告类型</div>
                    <div class="metric-value" style="font-size: 16px;">HTML 实时报告</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">查看方式</div>
                    <div class="metric-value" style="font-size: 14px;">手机/电脑浏览器</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">自动更新</div>
                    <div class="metric-value" style="font-size: 14px;">每小时</div>
                </div>
            </div>
        </div>

        <div class="footer">
            <p>📱 此页面专为手机和电脑浏览器优化</p>
            <p>⚠️ 本报告仅供参考，不构成投资建议</p>
            <p>🔄 自动生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
    </div>

    <script>
        // 页面加载完成后自动滚动到顶部
        window.onload = function() {{
            console.log('BTC 交易分析报告已加载');
        }};
    </script>
</body>
</html>
"""

    return html

def save_and_serve_html():
    """保存 HTML 并启动简单的 HTTP 服务器"""
    
    # 读取报告
    reports = read_latest_reports()

    # 生成 HTML
    html_content = generate_html_report(reports)

    # 保存 HTML 文件
    with open(HTML_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ HTML 报告已生成: {HTML_OUTPUT}")
    print(f"✅ 图片已嵌入 HTML (base64)")
    
    # 检查 HTTP 服务器是否在运行
    try:
        import http.server
        import socket
        
        # 尝试绑定端口
        PORT = 8080
        
        # 自定义处理器，设置正确的 Content-Type
        class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
            def end_headers(self):
                self.send_header('Content-type', 'text/html; charset=utf-8')
                http.server.SimpleHTTPRequestHandler.end_headers(self)

        try:
            server = http.server.HTTPServer(('0.0.0.0', PORT), MyHTTPRequestHandler)
            
            print(f"\n{'='*60}")
            print(f"🚀 HTTP 服务器已启动")
            print(f"{'='*60}")
            print(f"📱 本地访问: http://0.0.0.0:{PORT}/btc_report.html")
            print(f"🌐 外部访问: http://<服务器IP>:{PORT}/btc_report.html")
            print(f"{'='*60}")
            print(f"按 Ctrl+C 停止服务器")
            print(f"{'='*60}\n")

            # 在后台运行服务器（非阻塞）
            import threading
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.daemon = True
            server_thread.start()

            return PORT, True

        except OSError as e:
            if "Address already in use" in str(e):
                print(f"⚠️ 端口 {PORT} 已被占用，服务器可能已在运行")
                print(f"📱 访问地址: http://<服务器IP>:{PORT}/btc_report.html")
                return PORT, True
            else:
                raise

    except ImportError:
        print("⚠️ http.server 模块不可用")
        return None, False

def main():
    """主函数"""
    print(f"[{datetime.now()}] 开始生成 HTML 报告...")

    port, server_running = save_and_serve_html()

    if server_running:
        print(f"🎉 HTML 报告已就绪！")
        print(f"\n📋 访问链接:")
        print(f"  - http://0.0.0.0:{port}/btc_report.html")
        print(f"  - 在手机/电脑浏览器中打开以上链接")
        print(f"\n💡 提示:")
        print(f"  - 页面包含嵌入了图片（无需额外文件）")
        print(f"  - 响应式设计，支持手机和电脑")
        print(f"  - 每次运行会自动更新")

if __name__ == "__main__":
    main()
