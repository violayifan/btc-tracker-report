#!/usr/bin/env python3
"""
BTC 价格监控与交易策略分析（完全自动化版本）
每小时执行，生成市场情绪分析和交易策略报告
并自动部署到 Netlify/Vercel
"""

import requests
import json
import os
import datetime as dt_module
import subprocess
import time
from typing import Dict, List

# 使用模块导入避免冲突
datetime = dt_module.datetime
timedelta = dt_module.timedelta

# 配置
COINGECKO_API = "https://api.coingecko.com/api/v3"
OUTPUT_DIR = "/root/.openclaw/workspace/reports"
FEAR_GREED_API = "https://api.alternative.me/fng/"

# 自动化配置
AUTO_DEPLOY_ENABLED = True  # 启用自动部署
AUTO_DEPLOY_METHOD = "netlify"  # vercel 或 netlify
AUTO_DEPLOY_SCRIPT = "/root/.openclaw/workspace/auto_deploy_token.py"

def run_auto_deploy():
    """运行自动化部署"""
    if not AUTO_DEPLOY_ENABLED:
        return
    
    try:
        result = subprocess.run(
            ["python3", AUTO_DEPLOY_SCRIPT],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        # 提取 URL
        if result.returncode == 0:
            output = result.stdout
            # 从输出中提取 URL
            lines = output.split('\n')
            for line in lines:
                if 'https://' in line and 'netlify.app' in line:
                    url = line.strip()
                    return url, True
        
        return None, False
    
    except Exception as e:
        return None, False

# 保持原有的所有函数...

# 在 main() 函数的末尾添加自动部署调用

def main():
    """主函数"""
    print(f"[{datetime.now()}] 开始 BTC 市场分析...")
    
    # ... (原有的所有代码) ...
    
    # 在保存报告后添加自动部署
    print(f"  {num + 1}. 保存报告...")
    filepath = save_report(report)
    print(f"  ✅ 报告已保存: {filepath}")
    
    # 自动部署
    num += 1
    print(f"  {num + 1}. 自动部署到 Netlify...")
    
    if AUTO_DEPLOY_ENABLED:
        url, success = run_auto_deploy()
        
        if success and url:
            print(f"  ✅ 部署成功！")
            print(f"  🌐 公网 URL: {url}")
            print(f"  💡 URL 已保存到缓存，后续访问将使用此 URL")
            
            # 保存 URL 到文件
            url_cache = os.path.join(OUTPUT_DIR, "public_url.txt")
            with open(url_cache, 'w', encoding='utf-8') as f:
                f.write(url)
            
            # 将 URL 添加到报告
            report += f"""
{'='*50}
🌐 公网访问
{'='*50}
• 访问地址: {url}
• 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*50}
"""
        else:
            print(f"  ⚠️  部署失败（已保存到本地）")
    
    num += 1
    print(f"  {num + 1}. 生成回测汇总...")
    
    # ... (原有的回测代码) ...
    
    print(f"\n[{datetime.now()}] 分析完成!")
    
    # 返回 URL（如果部署成功）
    if AUTO_DEPLOY_ENABLED and url:
        return url
    return None

if __name__ == "__main__":
    # 运行监控并返回 URL（如果部署成功）
    public_url = main()
