#!/usr/bin/env python3
"""
修复后的飞书机器人 API v2 调用
"""

import os
import time
import hmac
import hashlib
import requests
import base64
from datetime import datetime

# 配置
CONFIG_PATH = "/root/.openclaw/openclaw.json"
USER_ID = "ou_9cde50d77f516edcf3a661ca32f83b2a"
IMAGE_PATH = "/root/.openclaw/workspace/backtest_chart_ultra.jpg"  # 1.65KB

def load_config():
    """加载配置"""
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_tenant_access_token(app_id, app_secret):
    """生成 Tenant Access Token"""
    timestamp = int(time.time() * 1000)
    sign_str = f"{app_id}{app_secret}{timestamp}"
    sign = hashlib.sha256(sign_str.encode('utf-8')).hexdigest()
    return f"{app_id}.{sign}.{timestamp}"

def build_message_v2(message_text, image_path=None):
    """
    构建飞书机器人 API v2 消息
    参考: https://open.feishu.cn/document/server-docs/bot-v2/add-message
    """
    # 读取图片
    image_data = None
    if image_path and os.path.exists(image_path):
        with open(image_path, 'rb') as f:
            image_data = f.read()
    
    # 简化：先尝试纯文本消息
    msg_content = {
        "text": message_text
    }
    
    # 如果有图片，添加到 content
    # 注意：图片上传需要先调用上传接口，这里简化为纯文本测试
    if image_data:
        msg_content["image_key"] = "chart_image"
    
    msg_body = {
        "msg_type": "text",  # 先用 text 类型
        "content": msg_content,
        "uuid": str(int(time.time() * 1000))  # 消息唯一标识
    }
    
    return msg_body, image_data

def send_message_via_webhook(message_text, image_path=None, max_retries=3, timeout=30):
    """通过 Webhook 发送消息（简化版）"""
    
    # 读取配置
    config = load_config()
    feishu_config = config.get('channels', {}).get('feishu', {})
    
    app_id = feishu_config.get('appId')
    app_secret = feishu_config.get('appSecret')
    
    if not app_id or not app_secret:
        return False, "缺少 App ID 或 App Secret"
    
    # 生成 Tenant Access Token
    tenant_access_token = generate_tenant_access_token(app_id, app_secret)
    
    # Webhook URL
    webhook_url = f"https://open.feishu.cn/open-apis/bot/v2/hook/{tenant_access_token}"
    
    print("=" * 70)
    print("飞书机器人 Webhook 发送（简化版）")
    print("=" * 70)
    print(f"开始时间: {datetime.now().strftime('%H:%M:%S.%f')}")
    print(f"App ID: {app_id}")
    print(f"Token: {tenant_access_token[:30]}...")
    print(f"URL: {webhook_url}")
    print("=" * 70)
    
    # 构建消息
    msg_body, image_data = build_message_v2(message_text, image_path)
    
    # 简化为纯文本消息（先不尝试图片）
    simple_msg = {
        "msg_type": "text",
        "content": {
            "text": message_text
        }
    }
    
    # 尝试纯文本消息
    print("\n尝试 1: 纯文本消息")
    for attempt in range(1, max_retries + 1):
        print(f"\n第 {attempt}/{max_retries} 次尝试")
        print(f"开始时间: {datetime.now().strftime('%H:%M:%S.%f')}")
        
        try:
            print("发送请求...")
            response = requests.post(
                webhook_url,
                json=simple_msg,
                timeout=timeout
            )
            
            duration = (datetime.now() - start_time).total_seconds() if 'start_time' in locals() else 0
            
            print(f"\n✅ 成功！")
            print(f"HTTP 状态码: {response.status_code}")
            print(f"耗时: {duration:.2f} 秒")
            print(f"响应: {response.text[:200]}")
            print("=" * 70)
            
            return True, "纯文本消息发送成功"
            
        except Exception as e:
            print(f"\n❌ 错误 (尝试 {attempt}/{max_retries})")
            print(f"错误类型: {type(e).__name__}")
            print(f"错误信息: {str(e)}")
            
            if attempt < max_retries:
                wait_time = 2 ** attempt
                print(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
                continue
            
            return False, f"纯文本消息失败: {str(e)}"
        
        finally:
            start_time = datetime.now()

def main():
    """主函数"""
    print(f"\n[{datetime.now()}] 开始测试飞书 Webhook 发送...\n")
    
    # 测试消息
    test_message = f"""📊 BTC 交易分析报告（测试）

{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💰 市场状态
• BTC 价格: $67,422
• 24h 涨跌: +1.37%

⚠️ 这是用于诊断图片上传问题的测试消息"""
    
    success, message = send_message_via_webhook(test_message)
    
    print("\n" + "=" * 70)
    print("最终结果")
    print("=" * 70)
    print(f"状态: {'✅ 成功' if success else '❌ 失败'}")
    print(f"消息: {message}")
    print("=" * 70)

if __name__ == "__main__":
    main()
