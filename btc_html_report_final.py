#!/usr/bin/env python3
"""
生成 BTC 交易分析的最终版 HTML 报告
统一所有指标的显示方式
"""

import os
import json
from datetime import datetime
import glob

# 路径配置
WORKSPACE = "/root/.openclaw/workspace"
OUTPUT_DIR = os.path.join(WORKSPACE, "reports")
HTML_OUTPUT = os.path.join(WORKSPACE, "btc_report_enhanced.html")
TRADES_FILE = os.path.join(WORKSPACE, "btc_trades.json")

def read_trades_data():
    """读取交易记录数据"""
    try:
        if os.path.exists(TRADES_FILE):
            with open(TRADES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"读取交易数据失败: {e}")
        return []

def calculate_backtest_metrics(trades):
    """计算回测指标 - 使用真实的回测数据"""
    if not trades:
        return {}

    try:
        from btc_tracker import BTCTracker
    except ImportError:
        print("  [警告] 无法导入 BTC Tracker")
        return {}

    tracker = BTCTracker()
    
    # 使用 tracker 的回测方法获取真实数据
    backtest_result = tracker.backtest_improved()
    
    # 提取真实的 capital_history（包含时间）
    capital_history = backtest_result.get('capital_history', [])
    
    # 计算真实指标
    metrics = tracker.calculate_metrics(backtest_result)
    
    # 格式化 capital_history，确保包含时间戳
    # capital_history 格式: [(datetime_obj, capital_value), ...]
    
    return {
        'capital_history': capital_history,
        'initial_capital': metrics.get('initial_capital', 10000),
        'final_capital': metrics.get('final_capital', 10000),
        'total_return': metrics.get('total_return', 0),
        'win_rate': metrics.get('win_rate', 0),
        'total_trades': metrics.get('total_trades', 0),
        'win_count': metrics.get('win_count', 0),
        'max_capital': metrics.get('max_capital', 10000),
        'min_capital': metrics.get('min_capital', 0),
        'max_drawdown': metrics.get('max_drawdown', 0),
        'annualized_return': metrics.get('annualized_return', 0),
        'max_drawdown_duration_hours': metrics.get('max_drawdown_duration_hours', 0),
        'sharpe_ratio': metrics.get('sharpe_ratio', 0),
        'profit_loss_ratio': metrics.get('profit_loss_ratio', 0)
    }

def read_latest_reports():
    """读取最新的报告"""
    reports = {}

    market_report_files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "btc_report_*.txt")))
    if market_report_files:
        with open(market_report_files[-1], 'r', encoding='utf-8') as f:
            reports['market'] = f.read()

    backtest_report_files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "btc_backtest_report_*.txt")))
    if backtest_report_files:
        with open(backtest_report_files[-1], 'r', encoding='utf-8') as f:
            reports['backtest'] = f.read()

    return reports

def generate_enhanced_html(reports, backtest_metrics):
    """生成增强版 HTML 报告"""

    capital_history = backtest_metrics.get('capital_history', [])
    
    # 提取时间和净值
    labels = []
    capital_values = []
    
    for idx, item in enumerate(capital_history):
        time_obj = item[0]  # datetime 对象
        capital_val = item[1]
        
        # 格式化时间为可读格式
        time_str = time_obj.strftime("%m-%d %H:%M")
        labels.append(time_str)
        capital_values.append(capital_val)

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 所有的指标都从 backtest_metrics 读取，确保一致性
    initial_capital = backtest_metrics.get('initial_capital', 0)
    final_capital = backtest_metrics.get('final_capital', 0)
    total_return = backtest_metrics.get('total_return', 0)
    win_rate = backtest_metrics.get('win_rate', 0)
    total_trades = backtest_metrics.get('total_trades', 0)
    win_count = backtest_metrics.get('win_count', 0)
    max_drawdown = backtest_metrics.get('max_drawdown', 0)
    max_capital = backtest_metrics.get('max_capital', 0)
    min_capital = backtest_metrics.get('min_capital', 0)
    annualized_return = backtest_metrics.get('annualized_return', 0)
    max_drawdown_duration_hours = backtest_metrics.get('max_drawdown_duration_hours', 0)
    sharpe_ratio = backtest_metrics.get('sharpe_ratio', 0)
    profit_loss_ratio = backtest_metrics.get('profit_loss_ratio', 0)

    market_content = reports.get('market', '暂无市场分析报告').replace('\n', '<br>\n')
    backtest_content = reports.get('backtest', '暂无回测报告').replace('\n', '<br>\n')

    capital_data_json = json.dumps(capital_values)
    labels_json = json.dumps(labels)

    # 统一所有指标的显示方式
    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTC 交易分析报告 - """ + now_str + """</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
            line-height: 1.6;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: #fff;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }

        .header h1 {
            margin: 0;
            font-size: 36px;
            font-weight: bold;
            margin-bottom: 10px;
        }

        .header .subtitle {
            font-size: 18px;
            opacity: 0.9;
        }

        .header .time {
            font-size: 14px;
            opacity: 0.8;
            margin-top: 15px;
            background: rgba(255,255,255,0.2);
            padding: 8px 16px;
            border-radius: 20px;
            display: inline-block;
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
            display: flex;
            align-items: center;
        }

        .section-title::before {
            content: "";
            width: 6px;
            height: 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin-right: 10px;
            border-radius: 3px;
        }

        .chart-container {
            position: relative;
            height: 400px;
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }

        .content-box {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }

        .pre-formatted {
            font-family: "Courier New", Courier, monospace;
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 13px;
            line-height: 1.8;
            white-space: pre-wrap;
            word-wrap: break-word;
            border: 1px solid #e0e0e0;
        }

        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .metric-card {
            background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            border-left: 4px solid #667eea;
            transition: transform 0.3s, box-shadow 0.3s;
        }

        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.12);
        }

        .metric-label {
            color: #666;
            font-size: 14px;
            margin-bottom: 10px;
            font-weight: 500;
        }

        .metric-value {
            font-size: 28px;
            font-weight: bold;
            color: #333;
        }

        .positive { color: #10b981; }
        .negative { color: #ef4444; }

        .footer {
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            color: #666;
            font-size: 14px;
        }

        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
            margin-right: 8px;
        }

        .badge-success {
            background: #d1fae5;
            color: #065f46;
        }

        .badge-warning {
            background: #fef3c7;
            color: #92400e;
        }

        .badge-danger {
            background: #fee2e2;
            color: #991b1b;
        }

        @media (max-width: 768px) {
            .container {
                margin: 0;
                border-radius: 0;
                box-shadow: none;
            }

            .header {
                padding: 30px 20px;
            }

            .header h1 {
                font-size: 28px;
            }

            .section {
                padding: 20px;
            }

            .metric-grid {
                grid-template-columns: 1fr;
            }

            .metric-card {
                padding: 15px;
            }

            .metric-label {
                font-size: 12px;
            }

            .metric-value {
                font-size: 20px;
            }

            .chart-container {
                height: 300px;
                padding: 15px;
            }
            
            .pre-formatted {
                font-size: 11px;
                padding: 15px;
                line-height: 1.5;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 BTC 交易分析报告</h1>
            <div class="subtitle">实时回测与市场分析</div>
            <div class="time">
                🕐 """ + now_time + """
            </div>
        </div>

        <!-- 回测图表部分 -->
        <div class="section">
            <div class="section-title">
                📈 净值曲线图（交互式）
                <span class="badge badge-success">实时更新</span>
            </div>
            <div class="chart-container">
                <canvas id="capitalChart"></canvas>
            </div>
        </div>

        <!-- 关键指标部分 -->
        <div class="section">
            <div class="section-title">📊 关键指标</div>
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-label">初始资金</div>
                    <div class="metric-value">$""" + f"{initial_capital:,.0f}" + """</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">当前资金</div>
                    <div class="metric-value">$""" + f"{final_capital:,.0f}" + """</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">总收益率</div>
                    <div class="metric-value """ + ("positive" if total_return > 0 else "negative") + """>
                        """ + f"{total_return:.2f}" + """%
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">年化收益率</div>
                    <div class="metric-value """ + ("positive" if annualized_return > 0 else "negative") + """>
                        """ + f"{annualized_return:.2f}" + """%
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">胜率</div>
                    <div class="metric-value """ + ("positive" if win_rate > 50 else "negative") + """>
                        """ + f"{win_rate:.2f}" + """%
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">总交易次数</div>
                    <div class="metric-value">""" + str(total_trades) + """</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">盈利交易</div>
                    <div class="metric-value positive">""" + str(win_count) + """</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">最大回撤</div>
                    <div class="metric-value negative">""" + f"{max_drawdown:.2f}" + """%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">最高净值</div>
                    <div class="metric-value positive">$""" + f"{max_capital:,.0f}" + """</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">最低净值</div>
                    <div class="metric-value negative">$""" + f"{min_capital:,.0f}" + """</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">夏普比率</div>
                    <div class="metric-value">""" + f"{sharpe_ratio:.4f}" + """</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">盈亏比</div>
                    <div class="metric-value """ + ("positive" if profit_loss_ratio > 0 else "negative") + """>
                        """ + f"{profit_loss_ratio:.2f}" + """
                    </div>
                </div>
            </div>
        </div>

        <!-- 市场分析部分 -->
        <div class="section">
            <div class="section-title">💰 市场分析</div>
            <div class="pre-formatted">
""" + market_content + """
            </div>
        </div>

        <!-- 回测报告部分 -->
        <div class="section">
            <div class="section-title">📋 详细回测报告</div>
            <div class="pre-formatted">
""" + backtest_content + """
            </div>
        </div>

        <div class="footer">
            <p>📱 此页面专为手机和电脑浏览器优化</p>
            <p>📈 交互式图表：可缩放、悬停查看详情</p>
            <p>📊 新增：盈亏比指标（盈利/亏损）</p>
            <p>🔧 修复：所有指标显示方式统一</p>
            <p>⚠️ 本报告仅供参考，不构成投资建议</p>
            <p>🔄 自动生成时间：""" + now_time + """</p>
        </div>
    </div>

    <script>
        // 配置 Chart.js
        const ctx = document.getElementById('capitalChart').getContext('2d');

        const capitalData = """ + capital_data_json + """;
        const labels = """ + labels_json + """;

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: '净值曲线',
                    data: capitalData,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 3,
                    pointHoverRadius: 6,
                    pointBackgroundColor: '#667eea',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            font: {
                                size: 14,
                                weight: 'bold'
                            },
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleFont: {
                            size: 14,
                            weight: 'bold'
                        },
                        bodyFont: {
                            size: 13
                        },
                        padding: 12,
                        displayColors: true,
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    label += '$' + context.parsed.y.toFixed(2);
                                }
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: '时间',
                            font: {
                                size: 12,
                                weight: 'bold'
                            }
                        },
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: '净值 ($)',
                            font: {
                                size: 12,
                                weight: 'bold'
                            }
                        },
                        beginAtZero: false,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });

        console.log('BTC 交易分析报告已加载');
        console.log('数据点数:', capitalData.length);
    </script>
</body>
</html>
"""

    return html

def save_html(html_content):
    """保存 HTML 文件"""
    with open(HTML_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(html_content)
    return HTML_OUTPUT

def start_simple_server(port=8081):
    """启动简单的 HTTP 服务器"""
    import http.server
    import threading

    class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header('Content-type', 'text/html; charset=utf-8')
            http.server.SimpleHTTPRequestHandler.end_headers(self)

        def log_message(self, format, *args):
            pass

    try:
        server = http.server.HTTPServer(('0.0.0.0', port), MyHTTPRequestHandler)
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        return True
    except OSError as e:
        if "Address already in use" in str(e):
            return True
        return False

def main():
    """主函数"""
    print(f"[{datetime.now()}] 开始生成增强版 HTML 报告...")

    print("  1. 读取交易数据...")
    trades = read_trades_data()

    print("  2. 计算回测指标...")
    backtest_metrics = calculate_backtest_metrics(trades)

    print("  3. 读取最新报告...")
    reports = read_latest_reports()

    print("  4. 生成 HTML 报告...")
    html_content = generate_enhanced_html(reports, backtest_metrics)

    print("  5. 保存 HTML 文件...")
    html_file = save_html(html_content)
    print(f"  ✅ HTML 报告已生成: {html_file}")

    print("  6. 启动 HTTP 服务器...")
    port = 8081
    server_started = start_simple_server(port)

    if server_started:
        print(f"\n{'='*60}")
        print(f"🚀 HTTP 服务器已启动")
        print(f"{'='*60}")
        print(f"📱 本地访问: http://0.0.0.0:{port}/btc_report_enhanced.html")
        print(f"🌐 外部访问: http://47.90.150.51:{port}/btc_report_enhanced.html")
        print(f"{'='*60}")
        print(f"📋 报告特性:")
        print(f"  • 交互式图表（Chart.js）")
        print(f"  • 响应式设计")
        print(f"  • 无需外部图片文件")
        print(f"  • 支持手机和电脑")
        print(f"  • 修复：所有指标显示方式统一")
        print(f"{'='*60}\n")

    print(f"[{datetime.now()}] 报告生成完成！")

if __name__ == "__main__":
    main()
