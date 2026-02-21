#!/usr/bin/env python3
"""
飞书图片上传脚本（带详细日志和代理检测）
"""

import os
import requests
import base64
from datetime import datetime

# 配置
IMAGE_PATH = "/root/.openclaw/workspace/backtest_chart.png"
FEISHU_WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxxx"  # 需要替换

def check_proxy():
    """检查代理环境"""
    proxy_info = {
        'http_proxy': os.environ.get('HTTP_PROXY', ''),
        'https_proxy': os.environ.get('HTTPS_PROXY', ''),
        'all_proxy': os.environ.get('ALL_PROXY', ''),
        'no_proxy': os.environ.get('NO_PROXY', ''),
        'http_proxy_env': os.environ.get('http_proxy', ''),
        'https_proxy_env': os.environ.get('https_proxy', ''),
        'all_proxy_env': os.environ.get('all_proxy', '')
    }
    
    print("=" * 60)
    print("🔍 代理环境检测")
    print("=" * 60)
    
    for key, value in proxy_info.items():
        status = "✅ 设置" if value else "❌ 未设置"
        print(f"{key:20s}: {status} | {value if value else '(empty)'}")
    
    print("=" * 60)
    return proxy_info

def bypass_proxy_for_feishu():
    """为飞书域名绕过代理"""
    # 飞书域名列表
    feishu_domains = [
        '.feishu.cn',
        '.larksuite.com',
        '.feishuusercontent.com'
    ]
    
    # 检查是否需要添加到 NO_PROXY
    current_no_proxy = os.environ.get('NO_PROXY', '')
    
    # 如果 NO_PROXY 为空，添加飞书域名
    if not current_no_proxy:
        no_proxy = ','.join(feishu_domains)
        os.environ['NO_PROXY'] = no_proxy
        print(f"✅ 已为飞书域名设置绕过代理")
        print(f"   NO_PROXY = {no_proxy}")
        return True
    
    print("ℹ️  NO_PROXY 已设置，检查是否包含飞书域名...")
    if any(domain in current_no_proxy for domain in feishu_domains):
        print("✅ 飞书域名已在绕过列表中")
        return True
    
    print("⚠️  飞书域名不在绕过列表中，可能影响上传")
    return False

def upload_image_with_logging(image_path, max_retries=3, timeout=30):
    """上传图片并记录详细日志"""
    
    print("\n" + "=" * 60)
    print("📤 开始上传图片")
    print("=" * 60)
    print(f"📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📄 文件: {image_path}")
    print(f"📏 文件大小: {os.path.getsize(image_path) / 1024:.2f} KB")
    print(f"🔄 最大重试次数: {max_retries}")
    print(f"⏱️  超时时间: {timeout} 秒")
    print("=" * 60)
    
    # 检查图片文件
    if not os.path.exists(image_path):
        print(f"❌ 图片文件不存在: {image_path}")
        return False, "文件不存在"
    
    # 读取图片
    print("\n📖 读取图片文件...")
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()
        print(f"✅ 图片读取成功，大小: {len(image_data) / 1024:.2f} KB")
    except Exception as e:
        print(f"❌ 图片读取失败: {str(e)}")
        return False, f"读取失败: {str(e)}"
    
    # 编码为 base64
    print("\n🔄 编码为 base64...")
    try:
        image_b64 = base64.b64encode(image_data).decode('utf-8')
        print(f"✅ Base64 编码成功，大小: {len(image_b64)} 字符")
    except Exception as e:
        print(f"❌ Base64 编码失败: {str(e)}")
        return False, f"编码失败: {str(e)}"
    
    # 生成请求 URL
    upload_url = "https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxxx/upload"  # 需要替换
    
    # 准备请求头
    headers = {
        'Content-Type': 'application/octet-stream',
        'Content-Length': str(len(image_data))
    }
    
    # 检查代理设置
    proxy_info = check_proxy()
    
    # 检查是否使用代理
    use_proxy = False
    proxies = None
    
    if proxy_info['http_proxy'] or proxy_info['https_proxy'] or proxy_info['all_proxy']:
        # 检查 NO_PROXY 设置
        bypassed = bypass_proxy_for_feishu()
        if not bypassed:
            print("\n⚠️  检测到代理设置，未设置飞书域名绕过")
            print("   建议: export NO_PROXY=.feishu.cn,.larksuite.com,.feishuusercontent.com")
            
            # 使用代理
            use_proxy = True
            proxies = {
                'http': proxy_info['http_proxy'] or proxy_info['http_proxy_env'] or proxy_info['all_proxy'] or proxy_info['all_proxy_env'],
                'https': proxy_info['https_proxy'] or proxy_info['https_proxy_env'] or proxy_info['all_proxy'] or proxy_info['all_proxy_env']
            }
        else:
            print("\n✅ 已绕过飞书域名的代理")
            use_proxy = False
    else:
        print("\n✅ 未检测到代理设置")
    
    print(f"\n📡 上传配置:")
    print(f"   URL: {upload_url}")
    print(f"   使用代理: {'是' if use_proxy else '否'}")
    if proxies:
        for k, v in proxies.items():
            if v:
                print(f"   {k}: {v}")
    print("=" * 60)
    
    # 重试循环
    for attempt in range(1, max_retries + 1):
        print(f"\n🔄 第 {attempt}/{max_retries} 次尝试...")
        print(f"   开始时间: {datetime.now().strftime('%H:%M:%S.%f')}")
        
        try:
            # 模拟分块上传（减少内存占用）
            print(f"   📊 发送请求...")
            
            response = requests.post(
                upload_url,
                data=image_data,
                headers=headers,
                proxies=proxies if use_proxy else None,
                timeout=timeout,
                stream=True  # 流式上传
            )
            
            # 记录响应信息
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds() if 'start_time' in locals() else 0
            
            print(f"\n✅ 上传成功！")
            print(f"   HTTP 状态码: {response.status_code}")
            print(f"   响应时间: {duration:.2f} 秒")
            print(f"   响应头:")
            for key, value in response.headers.items():
                print(f"     {key}: {value}")
            
            print(f"   响应内容: {response.text[:200]}")
            print("=" * 60)
            
            return True, f"上传成功 (尝试 {attempt}/{max_retries})"
            
        except requests.exceptions.ProxyError as e:
            print(f"\n❌ 代理错误 (尝试 {attempt}/{max_retries})")
            print(f"   错误信息: {str(e)}")
            print(f"   建议: 检查代理配置或尝试绕过代理")
            if attempt < max_retries:
                continue
            return False, f"代理错误: {str(e)}"
            
        except requests.exceptions.ConnectTimeout as e:
            print(f"\n⏰️ 连接超时 (尝试 {attempt}/{max_retries})")
            print(f"   超时时间: {timeout} 秒")
            print(f"   建议: 增加超时时间或检查网络连接")
            if attempt < max_retries:
                continue
            return False, f"连接超时: {str(e)}"
            
        except requests.exceptions.ReadTimeout as e:
            print(f"\n⏱️ 读取超时 (尝试 {attempt}/{max_retries})")
            print(f"   建议: 增加超时时间或减少文件大小")
            if attempt < max_retries:
                continue
            return False, f"读取超时: {str(e)}"
            
        except requests.exceptions.ConnectionError as e:
            error_msg = str(e)
            print(f"\n❌ 连接错误 (尝试 {attempt}/{max_retries})")
            print(f"   错误信息: {error_msg}")
            
            # 分析错误类型
            if 'Connection reset by peer' in error_msg:
                print(f"   错误类型: ECONNRESET (连接被重置）")
                print(f"   可能原因:")
                print(f"     - 代理服务器问题")
                print(f"     - 防火墙阻止")
                print(f"     - 网络不稳定")
                print(f"     - 文件过大")
                print(f"   建议:")
                print(f"     1. 绕小图片文件大小")
                print(f"     2. 绕过代理直连 (export NO_PROXY)")
                print(f"     3. 使用支持大文件的代理")
            elif 'Connection refused' in error_msg:
                print(f"   错误类型: ECONNREFUSED (连接被拒绝）")
                print(f"   可能原因: 服务器未启动或端口被阻止")
            elif 'timeout' in error_msg.lower():
                print(f"   错误类型: 连接超时")
            else:
                print(f"   错误类型: 未知连接错误")
            
            if attempt < max_retries:
                # 指数退避
                wait_time = 2 ** attempt
                print(f"   ⏸️  等待 {wait_time} 秒后重试...")
                import time
                time.sleep(wait_time)
                continue
            
            return False, f"连接错误: {str(e)}"
            
        except requests.exceptions.HTTPError as e:
            print(f"\n🌐 HTTP 错误 (尝试 {attempt}/{max_retries})")
            print(f"   状态码: {e.response.status_code}")
            print(f"   响应: {e.response.text[:200]}")
            
            if e.response.status_code == 413:
                print(f"   错误: Payload too large (文件过大）")
                print(f"   建议: 缩小图片文件大小")
            elif e.response.status_code == 403:
                print(f"   错误: Forbidden (权限被拒绝）")
                print(f"   建议: 检查 API 权限")
            
            if attempt < max_retries:
                continue
            
            return False, f"HTTP 错误 {e.response.status_code}"
            
        except Exception as e:
            print(f"\n❌ 未知错误 (尝试 {attempt}/{max_retries})")
            print(f"   错误类型: {type(e).__name__}")
            print(f"   错误信息: {str(e)}")
            
            if attempt < max_retries:
                continue
            
            return False, f"未知错误: {str(e)}"
        
        finally:
            start_time = datetime.now()

def main():
    """主函数"""
    print(f"\n[{'='*20}] 飞书图片上传诊断工具 [{'='*20}]\n")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 上传图片
    success, message = upload_image_with_logging(
        IMAGE_PATH,
        max_retries=3,
        timeout=30
    )
    
    print("\n" + "=" * 60)
    print("📋 最终结果")
    print("=" * 60)
    print(f"状态: {'✅ 成功' if success else '❌ 失败'}")
    print(f"消息: {message}")
    print("=" * 60)

if __name__ == "__main__":
    main()
