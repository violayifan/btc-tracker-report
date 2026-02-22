#!/usr/bin/env python3
"""
生成 BTC 高级监控的增强版 HTML 报告
包含：量价分析、链上数据、市场情绪、宏观新闻、X舆情、交易策略
"""

import os
import json
import glob
from datetime import datetime

# 路径配置
WORKSPACE = "/root/.openclaw/workspace"
OUTPUT_DIR = os.path.join(WORKSPACE, "reports")
HTML_OUTPUT = os.path.join(WORKSPACE, "btc_report_enhanced.html")
TRADES_FILE = os.path.join(WORKSPACE, "btc_trades.json")


def read_advanced_reports():
    """读取最新的高级报告"""
    reports = {}

    advanced_report_files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "btc_advanced_report_*.txt")))
    if advanced_report_files:
        with open(advanced_report_files[-1], 'r', encoding='utf-8') as f:
            reports['advanced'] = f.read()

    strategy_report_files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "btc_strategy_*.txt")))
    if strategy_report_files:
        with open(strategy_report_files[-1], 'r', encoding='utf-8') as f:
            reports['strategy'] = f.read()

    return reports


def read_trades_data():
    """读取交易记录数据（读取清理后的数据）"""
    try:
        # 优先读取清理后的数据
        clean_file = os.path.join(WORKSPACE, "btc_trades_clean.json")
        if os.path.exists(clean_file):
            with open(clean_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 如果清理后的数据不存在，读取原始数据
        with open(TRADES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[警告] 读取交易数据失败: {e}")
        return []


def calculate_backtest_metrics(trades):
    """计算回测指标"""
    if not trades:
        return {}

    try:
        # 简化计算
        completed_trades = [t for t in trades if t.get("status") == "completed"]

        if not completed_trades:
            return {
                "total_return": 0,
                "annualized_return": 0,
                "max_drawdown": 0,
                "sharpe_ratio": 0,
                "total_trades": 0,
                "win_rate": 0,
                "initial_capital": 10000,
                "final_capital": 10000,
                "win_count": 0,
                "max_capital": 10000,
                "min_capital": 10000,
                "max_drawdown_duration_hours": 0,
                "profit_loss_ratio": 0,
                "capital_history": []
            }

        initial_capital = 10000
        current_capital = initial_capital
        capital_history = []

        for trade in completed_trades:
            pnl = trade.get("pnl", 0)
            current_capital += pnl
            capital_history.append([datetime.now(), current_capital])

        total_return = ((current_capital - initial_capital) / initial_capital) * 100

        # 计算其他指标
        win_trades = [t for t in completed_trades if t.get("pnl", 0) > 0]
        win_count = len(win_trades)
        total_trades_count = len(completed_trades)
        win_rate = (win_count / total_trades_count) * 100 if total_trades_count > 0 else 0

        # 盈亏比
        profit = sum(t.get("pnl", 0) for t in win_trades)
        loss = sum(abs(t.get("pnl", 0)) for t in completed_trades if t.get("pnl", 0) < 0)
        profit_loss_ratio = round(profit / loss, 2) if loss > 0 else 0

        # 最大净值和最小净值
        values = [c[1] for c in capital_history]
        max_capital = max(values) if values else initial_capital
        min_capital = min(values) if values else initial_capital

        # 最大回撤
        max_drawdown_pct = 0
        for i, val in enumerate(values):
            if i == 0:
                peak = val
            else:
                if val > peak:
                    peak = val
                drawdown = (peak - val) / peak * 100
                if drawdown > max_drawdown_pct:
                    max_drawdown_pct = drawdown

        return {
            "total_return": round(total_return, 2),
            "annualized_return": round(total_return * 365 * 24, 2),  # 简化年化
            "max_drawdown": round(max_drawdown_pct, 2),
            "sharpe_ratio": round(profit_loss_ratio * 2, 4),  # 简化夏普比率
            "total_trades": total_trades_count,
            "win_rate": round(win_rate, 2),
            "win_count": win_count,
            "initial_capital": initial_capital,
            "final_capital": round(current_capital, 2),
            "max_capital": max_capital,
            "min_capital": min_capital,
            "max_drawdown_duration_hours": 0,
            "profit_loss_ratio": profit_loss_ratio,
            "capital_history": capital_history[-100:]  # 最近100个数据点
        }

    except Exception as e:
        print(f"[警告] 计算回测指标失败: {e}")
        return {}


def generate_enhanced_html(reports, backtest_metrics):
    """生成增强版 HTML 报告"""

    capital_history = backtest_metrics.get('capital_history', [])

    # 提取时间和净值
    labels = []
    capital_values = []

    for idx, item in enumerate(capital_history):
        time_obj = item[0]
        capital_val = item[1]

        time_str = time_obj.strftime("%m-%d %H:%M")
        labels.append(time_str)
        capital_values.append(capital_val)

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 所有的指标都从 backtest_metrics 读取，确保一致性
    initial_capital = backtest_metrics.get('initial_capital', 10000)
    final_capital = backtest_metrics.get('final_capital', 10000)
    total_return = backtest_metrics.get('total_return', 0)
    win_rate = backtest_metrics.get('win_rate', 0)
    total_trades = backtest_metrics.get('total_trades', 0)
    win_count = backtest_metrics.get('win_count', 0)
    max_drawdown = backtest_metrics.get('max_drawdown', 0)
    max_capital = backtest_metrics.get('max_capital', 10000)
    min_capital = backtest_metrics.get('min_capital', 10000)

    # 额外指标
    annualized_return = backtest_metrics.get('annualized_return', 0)
    max_drawdown_duration_hours = backtest_metrics.get('max_drawdown_duration_hours', 0)
    sharpe_ratio = backtest_metrics.get('sharpe_ratio', 0)
    profit_loss_ratio = backtest_metrics.get('profit_loss_ratio', 0)

    # 格式化报告内容
    advanced_content = reports.get('advanced', '暂无高级分析报告').replace('\n', '<br>\n')
    strategy_content = reports.get('strategy', '暂无策略报告').replace('\n', '<br>\n')

    capital_data_json = json.dumps(capital_values)
    labels_json = json.dumps(labels)

    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTC 高级监控报告 - """ + now_str + """</title>
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
            max-width: 1600px;
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

        .pre-formatted {
            font-family: "Courier New", Courier, monospace;
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            font-size: 14px;
            line-height: 1.8;
            white-space: pre-wrap;
            word-wrap: break-word;
            border: 1px solid #e9ecef;
        }

        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .metric-card {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            transition: transform 0.3s ease;
        }

        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        }

        .metric-label {
            font-size: 14px;
            color: #6c757d;
            margin-bottom: 10px;
            font-weight: 500;
        }

        .metric-value {
            font-size: 28px;
            font-weight: bold;
            color: #333;
        }

        .metric-value.positive {
            color: #28a745;
        }

        .metric-value.negative {
            color: #dc3545;
        }

        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
            margin-left: 10px;
        }

        .badge-success {
            background: #28a745;
            color: white;
        }

        .badge-warning {
            background: #ffc107;
            color: #333;
        }

        .badge-danger {
            background: #dc3545;
            color: white;
        }

        .data-source {
            font-size: 12px;
            color: #6c757d;
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #dee2e6;
        }

        .footer {
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            border-top: 1px solid #e9ecef;
        }

        .footer p {
            margin: 5px 0;
            color: #6c757d;
            font-size: 14px;
        }

        @media (max-width: 768px) {
            .header h1 {
                font-size: 28px;
            }

            .section-title {
                font-size: 20px;
            }

            .metric-grid {
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 10px;
            }

            .metric-value {
                font-size: 22px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 BTC 高级监控报告</h1>
            <div class="subtitle">多维度市场分析与交易策略</div>
            <div class="time">
                🕐 """ + now_time + """
            </div>
        </div>

        <!-- 净值曲线图部分 -->
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
                    <div class="metric-value """ + ("positive" if total_return > 0 else "negative") + """">
                        """ + f"{total_return:.2f}" + """%
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">胜率</div>
                    <div class="metric-value """ + ("positive" if win_rate > 50 else "negative") + """">
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
                    <div class="metric-label">盈亏比</div>
                    <div class="metric-value """ + ("positive" if profit_loss_ratio >= 1 else "negative") + """">
                        """ + f"{profit_loss_ratio:.2f}" + """
                    </div>
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
            </div>
        </div>

        <!-- 高级市场分析部分 -->
        <div class="section">
            <div class="section-title">
                🔬 高级市场分析
                <span class="badge badge-success">多维度</span>
            </div>
            <div class="pre-formatted">
""" + advanced_content + """
            </div>
            <div class="data-source">
                📊 数据来源: CoingGecko + Coinglass + Whale Alert + GDELT + Nitter (全免费)
            </div>
        </div>

        <!-- 交易策略部分 -->
        <div class="section">
            <div class="section-title">
                🎯 综合交易策略
                <span class="badge badge-warning">动态优化</span>
            </div>
            <div class="pre-formatted">
""" + strategy_content + """
            </div>
        </div>

        <div class="footer">
            <p>📱 此页面专为手机和电脑浏览器优化</p>
            <p>📈 交互式图表：可缩放、悬停查看详情</p>
            <p>🔬 多维度分析：技术面 + 链上数据 + 市场情绪 + 宏观新闻 + 社交舆情</p>
            <p>💰 数据成本: $0/月（完全免费的数据源）</p>
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
                    label: '净值',
                    data: capitalData,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 2,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function(context) {
                                return '$' + context.parsed.y.toLocaleString();
                            }
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 0,
                        autoSkip: true,
                        maxTicksLimit: 10
                    }
                },
                y: {
                    beginAtZero: false,
                    grid: {
                        color: 'rgba(0,0,0,0.05)'
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

        console.log('BTC 高级监控报告已加载');
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


def main():
    """主函数"""
    print(f"[{datetime.now()}] 开始生成高级 HTML 报告...")

    # 1. 读取交易数据
    print("  1. 读取交易数据...")
    trades = read_trades_data()

    # 2. 计算回测指标
    print("  2. 计算回测指标...")
    backtest_metrics = calculate_backtest_metrics(trades)

    # 3. 读取高级报告
    print("  3. 读取高级市场分析报告...")
    reports = read_advanced_reports()

    # 4. 生成 HTML
    print("  4. 生成 HTML 报告...")
    html = generate_enhanced_html(reports, backtest_metrics)

    # 5. 保存 HTML
    print("  5. 保存 HTML 文件...")
    filepath = save_html(html)
    print(f"  ✅ HTML 报告已生成: {filepath}")

    # 6. 启动 HTTP 服务器（可选）
    print("  6. 启动 HTTP 服务器...")
    import http.server
    import threading

    PORT = 8081

    def start_server():
        server = http.server.HTTPServer(('0.0.0.0', PORT), http.server.SimpleHTTPRequestHandler)
        print(f"\n{'='*60}")
        print("🚀 HTTP 服务器已启动")
        print(f"{'='*60}")
        print(f"📱 本地访问: http://0.0.0.0:{PORT}")
        print(f"🌐 外部访问: http://47.90.150.51:{PORT}")
        print(f"{'='*60}")
        print(f"📋 报告特性:")
        print(f"  • 多维度市场分析（量价 + 链上 + 情绪 + 宏观 + 社交）")
        print(f"  • 综合交易策略")
        print(f"  • 交互式图表（Chart.js）")
        print(f"  • 响应式设计")
        print(f"  • 支持手机和电脑")
        print(f"{'='*60}\n")
        server.serve_forever()

    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    print(f"\n[{datetime.now()}] 报告生成完成！")


if __name__ == "__main__":
    main()
