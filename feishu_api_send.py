#!/usr/bin/env python3
"""
使用飞书机器人 API 直接发送消息（带详细日志）
"""

import os
import json
import time
import hmac
import hashlib
import requests
from datetime import datetime

# 配置
CONFIG_PATH = "/root/.openclaw/openclaw.json"
IMAGE_PATH = "/root/.openclaw/workspace/backtest_chart_ultra.jpg"  # 1.65KB

def load_config():
    """加载飞书配置"""
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_tenant_token(app_id, app_secret):
    """生成 Tenant Access Token"""
    timestamp = int(time.time() * 1000)
    sign_str = f"{app_id}{app_secret}{timestamp}"
    sign = hashlib.sha256(sign_str.encode('utf-8')).hexdigest()
    tenant_access_token = f"{app_id}.{sign}.{timestamp}"
    return tenant_access_token

def send_feishu_message_v2(message, image_path=None, max_retries=3, timeout=30):
    """使用飞书机器人 API v2 发送消息"""
    
    # 加载配置
    config = load_config()
    feishu_config = config.get('channels', {}).get('feishu', {})
    
    app_id = feishu_config.get('appId')
    app_secret = feishu_config.get('appSecret')
    user_id = "ou_9cde50d77f516edcf3a661ca32f83b2a"  # 你的用户 ID
    
    if not app_id or not app_secret:
        return False, "飞书配置缺失 App ID 或 App Secret"
    
    # 生成 Tenant Access Token
    tenant_access_token = generate_tenant_token(app_id, app_secret)
    
    # API 端点
    api_url = f"https://open.feishu.cn/open-apis/bot/v2/hook/{tenant_access_token}"
    
    print("=" * 70)
    print("📤 飞书机器人 API v2 消息发送")
    print("=" * 70)
    print(f"⏰ 开始时间: {datetime.now().strftime('%H:%M:%S.%f')}")
    print(f"📱 用户 ID: {user_id}")
    print(f"🔑 App ID: {app_id}")
    print(f"🔒 App Secret: {app_secret[:10]}...{app_secret[-5:]}")
    print(f"🎫 Token: {tenant_access_token[:30]}...")
    print(f"🌐 API URL: {api_url}")
    print(f"📊 文件路径: {image_path}")
    print(f"📏 文件大小: {os.path.getsize(image_path) / 1024:.2f} KB")
    print("=" * 70)
    
    # 检查图片
    if image_path and not os.path.exists(image_path):
        return False, f"图片文件不存在: {image_path}"
    
    # 读取图片
    image_data = None
    if image_path:
        with open(image_path, 'rb') as f:
            image_data = f.read()
        print(f"✅ 图片已读取: {len(image_data)} bytes")
    
    # 构建 JSON 消息体
    msg_body = {
        "msg_type": "interactive",
        "receive_id": f"ou_{user_id.replace('ou_', '')}",  # 模拟 receive_id
        "content": {
            "text": message
        }
    }
    
    # 如果有图片，添加图片消息
    if image_data:
        msg_body["content"]["image_key"] = "chart_image"
        msg_body["content"]["image_base64"] = ""
    
    # 构建 JSON
    msg_json = json.dumps(msg_body, ensure_ascii=False)
    
    # 检查代理设置
    proxy_info = {
        'http_proxy': os.environ.get('HTTP_PROXY', ''),
        'https_proxy': os.environ.get('HTTPS_PROXY', ''),
        'all_proxy': os.environ.get('ALL_PROXY', ''),
        'http_proxy_env': os.environ.get('http_proxy', ''),
        'https_proxy_env': os.environ.get('https_proxy', ''),
        'all_proxy_env': os.environ.get('all_proxy', '')
    }
    
    print("\n" + "-" * 70)
    print("🔍 代理设置")
    print("-" * 70)
    for key, value in proxy_info.items():
        status = "✅ 已设置" if value else "❌ 未设置"
        print(f"{key:20s}: {status}")
    print("-" * 70)
    
    # 确定是否使用代理
    proxies = None
    use_proxy = False
    if proxy_info['http_proxy'] or proxy_info['https_proxy'] or proxy_info['all_proxy']:
        use_proxy = True
        proxies = {
            'http': proxy_info['http_proxy'] or proxy_info['http_proxy_env'] or proxy_info['all_proxy_env'] or proxy_info['all_proxy_env'],
            'https': proxy_info['https_proxy'] or proxy_info['https_proxy_env'] or proxy_info['all_proxy_env'] or proxy_info['all_proxy_env']
        }
        print(f"✅ 将使用代理")
    else:
        print("❌ 不使用代理")
    
    # 添加图片到 multipart
    files = None
    data = None
    if image_data:
        files = {
            'image': ('chart.jpg', image_data, 'image/jpeg')
        }
        data = msg_body
        print(f"✅ 将上传图片: {len(image_data)} bytes")
    else:
        data = {'msg_body': msg_json}
        headers = {'Content-Type': 'application/json'}
        print(f"✅ 将发送纯文本消息")
    
    # 重试循环
    for attempt in range(1, max_retries + 1):
        print(f"\n{'='*70}")
        print(f"🔄 第 {attempt}/{max_retries} 次尝试")
        print(f"{'='*70}")
        print(f"⏱️  开始时间: {datetime.now().strftime('%H:%M:%S.%f')}")
        
        try:
            print("📡 发送请求...")
            start_time = datetime.now()
            
            if image_data:
                # 上传图片
                response = requests.post(
                    api_url,
                    data=data,
                    files=files,
                    proxies=proxies if use_proxy else None,
                    timeout=timeout
                )
            else:
                # 发送纯文本
                response = requests.post(
                    api_url,
                    data=json.dumps(msg_body),
                    headers=headers,
                    proxies=proxies if use_proxy else None,
                    timeout=timeout
                )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # 记录响应
            print(f"\n✅ 请求成功！")
            print(f"⏱️  耗时: {duration:.2f} 秒")
            print(f"📊 HTTP 状态码: {response.status_code}")
            print(f"📋 响应头:")
            for key, value in response.headers.items():
                print(f"     {key}: {value}")
            print(f"📄 响应内容 (前500字节):")
            try:
                response_text = response.text
                print(response_text[:500])
            except:
                # 如果是图片上传，没有 text
                print(f"     Content-Type: {response.headers.get('Content-Type', 'N/A')}")
                print(f"     Content-Length: {response.headers.get('Content-Length', 'N/A')}")
            
            print(f"\n{'='*70}")
            print(f"🎉 成功！")
            print(f"{'='*70}")
            
            return True, f"发送成功 (尝试 {attempt}/{max_retries})"
            
        except requests.exceptions.ProxyError as e:
            print(f"\n❌ 代理错误 (尝试 {attempt}/{max_retries})")
            print(f"   错误: {str(e)}")
            print(f"   建议: 检查代理设置或尝试不使用代理")
            if attempt < max_retries:
                wait_time = 2 ** attempt
                print(f"   ⏳ 等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
                continue
            return False, f"代理错误: {str(e)}"
        
        except requests.exceptions.ConnectTimeout as e:
            print(f"\n⏰️ 连接超时 (尝试 {attempt}/{max_retries})")
            print(f"   超时时间: {timeout} 秒")
            print(f"   建议: 增加超时时间或检查网络连接")
            if attempt < max_retries:
                wait_time = 2 ** attempt
                print(f"   ⏳ 等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
                continue
            return False, f"连接超时: {str(e)}"
        
        except requests.exceptions.ReadTimeout as e:
            print(f"\n📖 读取超时 (尝试 {attempt}/{max_retries})")
            print(f"   建议: 减小文件大小或增加超时时间")
            if attempt < max_retries:
                wait_time = 2 ** attempt
                print(f"   ⏳ 等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
                continue
            return False, f"读取超时: {str(e)}"
        
        except requests.exceptions.ConnectionError as e:
            error_msg = str(e)
            print(f"\n❌ 连接错误 (尝试 {attempt}/{max_retries})")
            print(f"   错误: {error_msg}")
            
            # 分析错误类型
            if 'Connection reset by peer' in error_msg:
                print(f"   错误类型: ECONNRESET (连接被对端重置）")
                print(f"   可能原因:")
                print(f"     - 代理服务器问题")
                print(f"     - 防火墙阻止")
                print(f"     - 网络不稳定")
                print(f"     - 文件过大")
                print(f"   建议:")
                print(f"     1. 绕小图片文件大小")
                print(f"     2. 设置 NO_PROXY 环境变量绕过代理")
                print(f"     3. 使用支持大文件上传的代理")
            elif 'Connection refused' in error_msg:
                print(f"   错误类型: ECONNREFUSED (连接被拒绝）")
                print(f"   可能原因: 服务器未启动或端口被阻止")
            elif 'timeout' in error_msg.lower():
                print(f"   错误类型: 连接超时")
            else:
                print(f"   错误类型: 未知连接错误")
            
            if attempt < max_retries:
                wait_time = 2 ** attempt
                print(f"   ⏳ 等待 {wait_time} 秒后重试（指数退避）...")
                time.sleep(wait_time)
                continue
            
            return False, f"连接错误: {str(e)}"
        
        except requests.exceptions.HTTPError as e:
            print(f"\n🌐 HTTP 错误 (尝试 {attempt}/{max_retries})")
            print(f"   HTTP 状态码: {e.response.status_code}")
            
            if e.response.status_code == 413:
                print(f"   错误: Payload too large (文件过大）")
                print(f"   建议: 缩小图片文件大小")
            elif e.response.status_code == 403:
                print(f"   错误: Forbidden (权限被拒绝）")
                print(f"   建议: 检查 App ID 和 App Secret 配置")
            elif e.response.status_code == 404:
                print(f"   错误: Not Found (机器人不存在）")
            elif e.response.status_code == 400:
                print(f"   错误: Bad Request (请求无效）")
                print(f"   建议: 检查 API 调用格式和参数")
            else:
                print(f"   错误: HTTP {e.response.status_code}")
            
            try:
                error_response = e.response.json()
                print(f"   错误响应: {json.dumps(error_response, indent=2, ensure_ascii=False)}")
            except:
                if e.response.text:
                    print(f"   错误响应: {e.response.text[:200]}")
            
            if attempt < max_retries:
                wait_time = 2 ** attempt
                print(f"   ⏳ 等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
                continue
            
            return False, f"HTTP 错误 {e.response.status_code}"
        
        except Exception as e:
            print(f"\n❌ 未知错误 (尝试 {attempt}/{max_retries})")
            print(f"   错误类型: {type(e).__name__}")
            print(f"   错误: {str(e)}")
            
            if attempt < max_retries:
                wait_time = 2 ** attempt
                print(f"   ⏳ 等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
                continue
            
            return False, f"未知错误: {str(e)}"

def main():
    """主函数"""
    print(f"\n[{'='*20}] 飞书图片上传诊断工具 [{'='*20}]\n")
    
    # 测试消息
    test_message = f"""📊 BTC 交易净值曲线图（超小版 - 1.65KB）

报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💰 资金表现
  • 初始资金: $10,000
  • 最终资金: $9,962
  • 收益率: -0.38%

📉 风险指标
  • 最大回撤: 1.96%
  • 夏普比率: -2.15

⚠️ 这是测试消息，用于诊断图片上传问题"""
    
    # 发送消息（带图片）
    success, message = send_feishu_message_v2(
        test_message,
        image_path=IMAGE_PATH,
        max_retries=3,
        timeout=30
    )
    
    print(f"\n{'='*70}")
    print("📋 最终结果")
    print(f"{'='*70}")
    print(f"状态: {'✅ 成功' if success else '❌ 失败'}")
    print(f"消息: {message}")

if __name__ == "__main__":
    main()
