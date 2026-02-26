#!/usr/bin/env python3
"""
Tavily Search Tool - Fixed Version
修复 API 端点和请求格式
"""
import os
import requests
from dotenv import load_dotenv
from datetime import datetime

# 加载环境变量
load_dotenv('/root/.openclaw/workspace/.tavily.env')

# Tavily API 配置
API_KEY = os.environ.get('TAVILY_API_KEY', '')
# 尝试不同的端点
API_ENDPOINTS = [
    'https://api.tavily.com/search',
    'https://tavily.com/api/search',
    'https://api.tavily.com/v1/search'
]

def tavily_search(query, max_results=5):
    """
    使用 Tavily API 执行搜索
    """
    if not API_KEY:
        print("❌ Tavily API Key 未设置")
        print("请检查 /root/.openclaw/workspace/.tavily.env 文件")
        return None
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # 尝试不同的 payload 格式
    payloads = [
        # 格式 1
        {
            'api_key': API_KEY,
            'query': query,
            'search_depth': 'basic',
            'max_results': max_results,
            'include_answer': 'true',
            'include_images': 'false',
            'include_raw_content': 'false'
        },
        # 格式 2 - 更简单的字段
        {
            'api_key': API_KEY,
            'query': query,
            'limit': max_results
        }
    ]
    
    for endpoint in API_ENDPOINTS:
        for i, payload in enumerate(payloads):
            try:
                print(f"🔍 尝试端点: {endpoint}")
                print(f"📝 Payload 格式: {i + 1}")
                
                response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
                response.raise_for_status()
                
                result = response.json()
                print(f"✅ 成功！端点: {endpoint}")
                return result
                
            except requests.exceptions.HTTPError as e:
                print(f"❌ HTTP 错误 {e.response.status_code}: {e}")
                print(f"   响应: {e.response.text[:200]}")
            except requests.exceptions.RequestException as e:
                print(f"❌ 请求错误: {e}")
            except Exception as e:
                print(f"❌ 未知错误: {e}")
    
    print("❌ 所有尝试都失败了")
    return None

def format_search_results(result):
    """
    格式化搜索结果用于显示
    """
    if not result:
        return "❌ 无搜索结果"
    
    output = []
    output.append("=" * 60)
    output.append(f"📌 Tavily 搜索结果")
    output.append("=" * 60)
    output.append(f"🕐 搜索时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append(f"🔍 查询: {result.get('query', 'N/A')}")
    output.append("")
    
    # 显示答案
    if result.get('answer'):
        output.append("💡 AI 答案:")
        output.append(f"   {result['answer']}")
        output.append("")
    
    # 显示搜索结果
    results = result.get('results', [])
    if results:
        output.append(f"📊 找到 {len(results)} 个结果:")
        output.append("-" * 60)
        
        for i, item in enumerate(results, 1):
            output.append(f"\n{i}. {item.get('title', 'N/A')}")
            output.append(f"   🔗 {item.get('url', 'N/A')}")
            
            # 显示内容预览（截取前 150 字符）
            content = item.get('content', '')
            if content:
                preview = (content[:150] + "...") if len(content) > 150 else content
                output.append(f"   📝 {preview}")
            output.append("-" * 60)
    else:
        output.append("📭 未找到相关结果")
    
    output.append("=" * 60)
    return "\n".join(output)

def main():
    """主函数"""
    import sys
    
    # 如果提供了查询参数
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
        result = tavily_search(query)
        if result:
            print(format_search_results(result))
            return
    
    # 交互式模式
    print("🔍 Tavily 搜索工具")
    print("=" * 60)
    
    # 默认搜索 BTC 相关信息
    default_query = "BTC 比特币 最新行情 2026年2月26日"
    
    # 询问用户查询
    query = input(f"\n请输入搜索查询 (直接回车使用默认: {default_query}): ").strip()
    
    if not query:
        query = default_query
    
    result = tavily_search(query)
    if result:
        print("\n")
        print(format_search_results(result))

if __name__ == "__main__":
    main()
