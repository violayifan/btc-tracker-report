#!/usr/bin/env python3
"""
BTC 市场分析自动报告 + 服务器启动
整合市场分析、HTML 生成、服务器启动
"""

import subprocess
import time
import sys
import os
from datetime import datetime

def run_btc_monitor():
    """运行 BTC 市场分析"""
    print("=" * 60)
    print("步骤 1: 运行 BTC 市场分析")
    print("=" * 60)

    script_path = "/root/.openclaw/workspace/btc_monitor.py"
    if os.path.exists(script_path):
        subprocess.run([sys.executable, script_path], check=True)
        print("✅ BTC 市场分析完成\n")
    else:
        print(f"❌ 脚本不存在: {script_path}")
        return False
    return True

def run_html_report():
    """运行 HTML 报告生成"""
    print("=" * 60)
    print("步骤 2: 生成增强版 HTML 报告")
    print("=" * 60)

    script_path = "/root/.openclaw/workspace/btc_html_report_v2.py"
    if os.path.exists(script_path):
        subprocess.run([sys.executable, script_path], check=True)
        print("✅ HTML 报告生成完成\n")
    else:
        print(f"❌ 脚本不存在: {script_path}")
        return False
    return True

def display_access_info():
    """显示访问信息"""
    port = 8081
    html_file = "/root/.openclaw/workspace/btc_report_enhanced.html"

    print("=" * 60)
    print("📊 BTC 交易分析报告 - 访问信息")
    print("=" * 60)
    print(f"\n🌐 访问网址:")
    print(f"  • 本地: http://0.0.0.0:{port}/btc_report_enhanced.html")
    print(f"  • 外网: http://47.90.150.51:{port}/btc_report_enhanced.html")
    print(f"\n📄 文件位置:")
    print(f"  • {html_file}")
    print(f"\n📱 访问方式:")
    print(f"  • 在手机/电脑浏览器中打开上述网址")
    print(f"  • 直接拖拽 HTML 文件到浏览器也可以打开")
    print(f"\n📊 报告特性:")
    print(f"  • 交互式图表（Chart.js）")
    print(f"  • 实时回测数据")
    print(f"  • 响应式设计")
    print(f"  • 无需服务器环境（可本地打开）")
    print(f"\n⏰ 更新频率:")
    print(f"  • 每小时自动更新一次")
    print(f"  • 手动运行此脚本立即更新")
    print(f"\n" + "=" * 60)
    print(f"⚠️  外网访问说明:")
    print(f"  • 如果外网无法访问，请检查防火墙设置")
    print(f"  • 确保云服务商安全组开放 {port} 端口")
    print(f"  • 或者使用 ngrok 等内网穿透工具")
    print(f"=" * 60)

def main():
    """主函数"""
    print(f"\n{'='*60}")
    print(f"🚀 BTC 市场分析自动报告系统")
    print(f"{'='*60}")
    print(f"🕐 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    try:
        # 步骤 1: 运行 BTC 市场分析
        if not run_btc_monitor():
            print("❌ BTC 市场分析失败")
            return

        # 步骤 2: 生成 HTML 报告
        if not run_html_report():
            print("❌ HTML 报告生成失败")
            return

        # 显示访问信息
        display_access_info()

        print(f"\n🕐 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\n✅ 所有步骤完成！服务器正在运行中...")
        print(f"\n💡 提示:")
        print(f"  • 服务器会在后台持续运行")
        print(f"  • 按 Ctrl+C 可停止服务器")
        print(f"  • 下次运行此脚本会自动更新报告")

        # 保持服务器运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 服务器已停止")

    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
