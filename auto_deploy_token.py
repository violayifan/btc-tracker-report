#!/usr/bin/env python3
"""
完全自动化的 Netlify 部署方案
使用 Netlify API Token，无需任何手动操作
"""

import os
import requests
import base64
import json
from datetime import datetime

# 配置
HTML_FILE = "/root/.openclaw/workspace/btc_report.html"
LOG_FILE = "/root/.openclaw/workspace/deployment.log"
URL_CACHE = "/root/.openclaw/workspace/public_url.txt"

def log(message):
    """记录日志"""
    print(message)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

def deploy_to_netlify_token(token, site_id, html_file):
    """使用 Token 部署到 Netlify"""
    log("=" * 70)
    log("🚀 使用 Netlify Token 部署")
    log("=" * 70)
    
    # 读取 HTML 文件
    if not os.path.exists(html_file):
        log(f"❌ HTML 文件不存在: {html_file}")
        return None, "HTML 文件不存在"
    
    log(f"✅ HTML 文件已准备: {html_file}")
    
    # 读取 HTML 内容
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    log(f"📦 HTML 大小: {len(html_content)} bytes")
    
    # 构建部署请求
    # 注意：Netlify API 不支持直接部署文件，需要先上传到 S3 或使用其他方式
    # 这里我们使用一种变通方法：部署空站点，然后更新文件
    
    # 方法：创建一个新的部署，使用 site ID
    deploy_url = f"https://api.netlify.com/api/v1/sites/{site_id}/deploys"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/zip",
    }
    
    # 将 HTML 压缩为 ZIP（简单方式）
    import zipfile
    import io
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("index.html", html_content)
    
    zip_data = zip_buffer.getvalue()
    log(f"📦 ZIP 大小: {len(zip_data)} bytes")
    
    # 发送部署请求
    try:
        log("📤 发送部署请求到 Netlify...")
        response = requests.post(
            deploy_url,
            data=zip_data,
            headers=headers,
            timeout=60
        )
        
        log(f"✅ 请求已发送！状态码: {response.status_code}")
        
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            
            # 提取 URL
            url = result.get('url', None)
            deploy_id = result.get('id', None)
            state = result.get('state', None)
            
            if url:
                log("✅ 部署成功！")
                log(f"🌐 公网 URL: {url}")
                log(f"📦 部署 ID: {deploy_id}")
                log(f"📊 状态: {state}")
                
                # 保存 URL
                with open(URL_CACHE, 'w', encoding='utf-8') as f:
                    f.write(url)
                
                log(f"💡 URL 已保存到: {URL_CACHE}")
                
                return url, "部署成功"
            else:
                log("❌ 响应中没有 URL")
                log(f"📋 响应内容: {result}")
                return None, "响应中没有 URL"
        else:
            log(f"❌ 部署失败！状态码: {response.status_code}")
            log(f"📋 错误响应: {response.text[:500]}")
            return None, f"部署失败: {response.status_code}"
            
    except Exception as e:
        log(f"❌ 部署过程中发生错误: {str(e)}")
        return None, f"发生错误: {str(e)}"

def deploy_to_vercel_token(token, project_name, html_file):
    """使用 Token 部署到 Vercel"""
    log("=" * 70)
    log("🚀 使用 Vercel Token 部署")
    log("=" * 70)
    
    # 读取 HTML 文件
    if not os.path.exists(html_file):
        log(f"❌ HTML 文件不存在: {html_file}")
        return None, "HTML 文件不存在"
    
    log(f"✅ HTML 文件已准备: {html_file}")
    
    # 读取 HTML 内容
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    log(f"📦 HTML 大小: {len(html_content)} bytes")
    
    # Vercel API 不支持直接部署文件
    # 我们需要使用 Vercel CLI 或 Git
    # 这里提供一个使用 Git 的解决方案
    
    log("⚠️  Vercel API 不支持直接文件部署")
    log("💡 建议：使用 Git + Vercel 自动化")
    log("")
    log("📝 Git + Vercel 自动化步骤：")
    log("   1. 初始化 Git 仓库（一次性）")
    log("   2. 添加远程仓库（一次性）")
    log("   3. 每次提交推送")
    log("   4. Vercel 自动检测并部署")
    log("")
    log("✅ 完全自动化，无需手动操作！")
    
    return None, "Vercel API 不支持直接文件部署"

def main():
    """主函数"""
    log("开始自动化部署...")
    log("=" * 70)
    
    # 检查 Netlify Token（用户需要配置）
    netlify_token = os.environ.get('NETLIFY_TOKEN', '')
    netlify_site_id = os.environ.get('NETLIFY_SITE_ID', '')
    
    if netlify_token and netlify_site_id:
        log("✅ 检测到 Netlify Token 和 Site ID")
        
        url, message = deploy_to_netlify_token(
            netlify_token, 
            netlify_site_id, 
            HTML_FILE
        )
        
        if url:
            log("")
            log("=" * 70)
            log("🎉 部署完成！")
            log("=" * 70)
            log(f"🌐 您的公网 URL: {url}")
            log(f"💡 可以从任何地方直接访问")
            log(f"🔄 每小时自动更新（刷新页面即可）")
            log("=" * 70)
            exit(0)
        else:
            log("")
            log("=" * 70)
            log("❌ 部署失败")
            log("=" * 70)
            log(f"💡 错误: {message}")
            exit(1)
    else:
        log("⚠️  未检测到 Netlify Token")
        log("")
        log("💡 如何配置 Netlify Token：")
        log("   1. 注册 Netlify 账号: https://app.netlify.com/signup")
        log("   2. 创建 Personal Access Token:")
        log("      - User Settings → Applications")
        log("      - New access token")
        log("      - 输入描述：BTC Auto Deploy")
        log("      - 点击 Generate")
        log("      - 只显示一次，请务必复制")
        log("")
        log("   3. 创建站点并获取 Site ID:")
        log("      - 在 Netlify 控制台创建站点")
        log("      - 在 Site settings 中查找 Site ID")
        log("")
        log("   4. 配置环境变量（在服务器上运行）:")
        log("      export NETLIFY_TOKEN='你的_TOKEN'")
        log("      export NETLIFY_SITE_ID='你的_SITE_ID'")
        log("")
        log("   5. 再次运行此脚本")
        log("")
        log("✅ 配置完成后，将实现完全自动化！")
        log("   • 无需手动操作")
        log("   • 无需下载文件")
        log("   • 无需拖拽上传")
        log("   • 完全服务器端自动操作")
        log("   • 直接获得公网 URL")
        log("   • 每小时自动更新")
        log("")
        log("=" * 70)
        exit(1)

if __name__ == "__main__":
    main()
