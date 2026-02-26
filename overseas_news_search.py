#!/usr/bin/env python3
"""
海外财经新闻搜索工具
专门搜索雅虎财经、CNBC、Financial Times、Bloomberg 等权威海外财经来源
"""
import os
import sys
from tavily_search_fixed import tavily_search, format_search_results

def search_overseas_financial_news(keyword, max_results=10):
    """
    搜索海外财经新闻
    
    Args:
        keyword (str): 搜索关键词
        max_results (int): 最大结果数量
    """
    # 构建搜索查询，指定权威海外财经来源
    query = f"{keyword} site:finance.yahoo.com OR site:cnbc.com OR site:ft.com OR site:bloomberg.com OR site:wsj.com 2026"
    
    result = tavily_search(query, max_results=max_results)
    return result

def search_nvidia_earnings(max_results=10):
    """专门搜索 NVIDIA 财报"""
    keywords = [
        "NVIDIA earnings 2026 Q4",
        "NVDA earnings report",
        "Jensen Huang earnings call",
        "英伟达 财报 2026"
        "英伟达 财报 雅虎财经"
    ]
    
    all_results = []
    
    for keyword in keywords:
        result = search_overseas_financial_news(keyword, max_results=5)
        if result:
            all_results.append(result)
    
    return all_results

def format_earnings_report(results):
    """格式化财报报告"""
    if not results:
        return "❌ 无财报信息"
    
    output = []
    output.append("=" * 70)
    output.append("📊 英伟达（NVIDIA）财报报告 - 海外权威来源")
    output.append("=" * 70)
    output.append("")
    
    for i, result in enumerate(results, 1):
        if result and result.get('results'):
            output.append(f"\n📰 搜索 {i}: {result.get('query', 'N/A')}")
            output.append("-" * 70)
            
            # 显示前3个结果
            for item in result.get('results', [])[:3]:
                title = item.get('title', 'N/A')
                url = item.get('url', 'N/A')
                content = item.get('content', '')
                
                output.append(f"\n   📌 {title}")
                output.append(f"   🔗 {url}")
                
                # 提取关键信息（营收、EPS 等）
                if 'earnings' in title.lower() or '财报' in title:
                    if '$' in content:
                        output.append(f"   💰 检测到金额信息")
                    if 'billion' in content or '亿' in content:
                        output.append(f"   💰 可能是营收数据")
                    if 'eps' in content.lower() or '每股收益' in content:
                        output.append(f"   💰 可能是 EPS 数据")
                
                output.append("")
    
    output.append("=" * 70)
    return "\n".join(output)

def main():
    import sys
    
    if len(sys.argv) > 1:
        keyword = ' '.join(sys.argv[1:])
        print(f"\n🔍 搜索海外财经新闻: {keyword}")
        result = search_overseas_financial_news(keyword)
        if result:
            print(format_search_results(result))
        return
    
    # 默认模式：搜索 NVIDIA 财报
    print("\n📊 搜索 NVIDIA 财报...")
    results = search_nvidia_earnings(max_results=5)
    
    if results:
        print(format_earnings_report(results))
    else:
        print("❌ 搜索失败，请检查 API Key 或网络连接")

if __name__ == "__main__":
    main()
