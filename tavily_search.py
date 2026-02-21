#!/usr/bin/env python3
"""使用 Tavily API 进行网络搜索"""

import json
import sys
import requests
from typing import List, Dict

# Tavily API Key
TAVILY_API_KEY = "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"
TAVILY_API_URL = "https://api.tavily.com/search"

def tavily_search(query: str, max_results: int = 5) -> Dict:
    """
    使用 Tavily API 进行搜索

    Args:
        query: 搜索查询
        max_results: 最大结果数（默认5）

    Returns:
        搜索结果字典
    """
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "max_results": max_results,
        "search_depth": "basic",
        "include_answer": True,
        "include_raw_content": False
    }

    try:
        response = requests.post(TAVILY_API_URL, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def format_results(results: Dict) -> str:
    """
    格式化搜索结果

    Args:
        results: Tavily API 返回的结果

    Returns:
        格式化后的字符串
    """
    if "error" in results:
        return f"搜索错误: {results['error']}"

    output = []
    output.append(f"查询: {results.get('query', '')}\n")

    # 如果有直接答案
    answer = results.get("answer")
    if answer:
        output.append(f"📝 答案:\n{answer}\n")

    # 搜索结果
    output.append("🔍 搜索结果:")
    for idx, result in enumerate(results.get("results", []), 1):
        title = result.get("title", "")
        url = result.get("url", "")
        content = result.get("content", "")
        score = result.get("score", 0)

        output.append(f"\n{idx}. {title}")
        output.append(f"   URL: {url}")
        output.append(f"   相关度: {score:.2f}")
        if content:
            # 只显示前200个字符
            preview = content[:200] + "..." if len(content) > 200 else content
            output.append(f"   摘要: {preview}")

    return "\n".join(output)

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 tavily_search.py <查询内容> [最大结果数]")
        print("示例: python3 tavily_search.py 上海天气 3")
        sys.exit(1)

    query = " ".join(sys.argv[1:-1]) if len(sys.argv) > 2 else sys.argv[1]
    max_results = int(sys.argv[-1]) if len(sys.argv) > 2 and sys.argv[-1].isdigit() else 5

    print(f"正在搜索: {query}")
    print("-" * 80)

    results = tavily_search(query, max_results)
    formatted = format_results(results)

    print(formatted)

if __name__ == "__main__":
    main()
