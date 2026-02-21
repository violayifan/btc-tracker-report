#!/usr/bin/env python3
"""
测试飞书 Webhook 发送（修复版）
"""

import os
import time
import requests
import json
from datetime import datetime

# 配置
CONFIG_PATH = "/root/.openclaw/openclaw.json"

def load_config():
    """加载配置"""
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def send_text_via_webhook(message, max_retries=3, timeout=30):
    """通过 Webhook 发送纯文本消息"""
    
    # 读取配置
    config = load_config()
    feishu_config = config.get('channels', {}).get('feishu', {})
    
    app_id = feishu_config.get('appId')
    app_secret = feishu_config.get('appSecret')
    
    # 生成 Tenant Access Token
    timestamp = int(time.time() * 1000)
    sign_str = f"{app_id}{app_secret}{timestamp}"
    sign = hashlib.sha256(sign_str.encode('utf-8')).hexdigest()
    tenant_access_token = f"{app_id}.{sign}.{timestamp}"
    
    # Webhook URL
    webhook_url = f"https://open.feishu.cn/open-apis/bot/v2/hook/{tenant_access_token}"
    
    print("=" * 70)
    print("飞书 Webhook 发送测试")
    print("=" * 70)
    print(f"开始时间: {datetime.now().strftime('%H:%M:%S.%f')}")
    print(f"App ID: {app_id}")
    print(f"Token: {tenant_access_token[:30]}...")
    print(f"URL: {webhook_url}")
    print("=" * 70)
    
    # 简化消息体
    msg_body = {
        "msg_type": "text",
        "content": {
            "text": message
        }
    }
    
    # 发送
    for attempt in range(1, max_retries + 1):
        print(f"\n第 {attempt}/{max_retries} 次尝试...")
        print(f"开始时间: {datetime.now().strftime('%H:%M:%S.%f')}")
        
        try:
            print("发送请求...")
            response = requests.post(
                webhook_url,
                json=msg_body,
                timeout=timeout
            )
            
            print(f"\n✅ 成功！")
            print(f"HTTP 状态码: {response.status_code}")
            print(f"响应: {response.text[:200]}")
            print("=" * 70)
            
            return True, "发送成功"
            
        except Exception as e:
            print(f"\n❌ 错误 (尝试 {attempt}/{max_retries})")
            print(f"错误信息: {str(e)}")
            
            if attempt < max_retries:
                continue
            
            return False, f"发送失败: {str(e)}"

def main():
    """主函数"""
    print(f"\n[{datetime.now()}] 开始测试飞书 Webhook 发送...\n")
    
    # 测试消息
    test_message = f"""📊 飞书 Webhook 测试消息

{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✅ 这是纯文本测试消息

⚠️ 用于诊断 Webhook 连接问题"""
    
    success, message = send_text_via_webhook(test_message)
    
    print("\n" + "=" * 70)
    print("最终结果")
    print("=" * 70)
    print(f"状态: {'✅ 成功' if success else '❌ 失败'}")
    print(f"消息: {message}")
    print("=" * 70)

if __name__ == "__main__":
    main()
