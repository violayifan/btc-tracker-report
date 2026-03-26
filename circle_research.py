#!/usr/bin/env python3
"""
Circle 盈利模式深度研究脚本（使用新版 SerpAPI）
"""

import json
import concurrent.futures
from pathlib import Path
from datetime import datetime
import serpapi


def search_serpapi(query, engine="google"):
    """执行单次 SerpAPI 搜索"""
    SERPAPI_KEY = "8cd77245b0a692e1f1b0c31fca9e26b805af658ce627cde8b5f3f694d53250d4"

    params = {
        "q": query,
        "num": 10,
        "engine": engine,
        "api_key": SERPAPI_KEY
    }

    results = serpapi.search(params)

    organic_results = results.get("organic_results", [])

    formatted_results = []
    for item in organic_results:
        formatted_results.append({
            "title": item.get("title", ""),
            "url": item.get("link", ""),
            "snippet": item.get("snippet", ""),
            "date": item.get("date", ""),
            "source": item.get("source", "")
        })

    return formatted_results


def main():
    query = "Circle profit model business model USDC revenue sources"

    print(f"\n{'='*70}")
    print(f"🔍 Circle 盈利模式深度研究")
    print(f"{'='*70}\n")

    results = {}

    # 定义多路搜索
    search_tasks = [
        ("Google 全网", query, "google"),
        ("Google News", f"{query} news", "google"),
        ("Twitter", f'{query} site:x.com OR site:twitter.com', "google"),
        ("Reddit", f'{query} site:reddit.com', "google"),
        ("LinkedIn", f'{query} site:linkedin.com', "google"),
    ]

    # 并发执行搜索
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_name = {
            executor.submit(search_serpapi, q, e): name
            for name, q, e in search_tasks
        }

        for future in concurrent.futures.as_completed(future_to_name):
            name = future_to_name[future]
            try:
                search_results = future.result()
                results[name] = search_results
                print(f"✓ {name} 搜索完成，找到 {len(search_results)} 条结果")
            except Exception as e:
                print(f"✗ {name} 搜索失败: {e}")
                results[name] = []

    # 生成 Markdown 报告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = Path(f"/root/.openclaw/workspace/circle_business_model_{timestamp}.md")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Circle 盈利模式深度研究报告\n\n")
        f.write(f"**搜索时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (北京时间)\n\n")
        f.write(f"**搜索关键词**: {query}\n\n")
        f.write(f"{'-'*70}\n\n")

        # 按渠道输出结果
        for channel in ["Google 全网", "Google News", "Twitter", "Reddit", "LinkedIn"]:
            if channel in results and results[channel]:
                f.write(f"## {channel}搜索结果\n\n")
                for i, item in enumerate(results[channel], 1):
                    f.write(f"### {i}. {item.get('title', '无标题')}\n\n")
                    f.write(f"**摘要**: {item.get('snippet', '无摘要')}\n\n")
                    f.write(f"**来源**: {item.get('url', '无链接')}\n\n")
                    if item.get('date'):
                        f.write(f"**日期**: {item.get('date')}\n\n")
                    f.write(f"{'-'*50}\n\n")

        # 搜索统计
        f.write(f"## 搜索统计\n\n")
        f.write(f"| 渠道 | 结果数 | 状态 |\n")
        f.write(f"|------|--------|------|\n")
        for channel in ["Google 全网", "Google News", "Twitter", "Reddit", "LinkedIn"]:
            count = len(results.get(channel, []))
            status = "✅" if count > 0 else "⚠️"
            f.write(f"| {channel} | {count} | {status} |\n")

        f.write(f"\n**总计**: {sum(len(v) for v in results.values())} 条结果\n")

    print(f"\n{'='*70}")
    print(f"✅ 研究完成!")
    print(f"📄 报告已保存: {output_file}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
