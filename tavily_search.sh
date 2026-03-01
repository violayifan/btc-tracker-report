#!/bin/bash

# Tavily API 搜索脚本
API_KEY="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"

if [ -z "$1" ]; then
    echo "使用方法: $0 <搜索查询> [结果数量] [天数]"
    echo "示例: $0 \"今日新闻 加密货币\" 10 1"
    exit 1
fi

QUERY="$1"
MAX_RESULTS="${2:-10}"
DAYS="${3:-1}"

curl -s "https://api.tavily.com/search" \
  -H "Content-Type: application/json" \
  -d "{
    \"api_key\": \"$API_KEY\",
    \"query\": \"$QUERY\",
    \"max_results\": $MAX_RESULTS,
    \"days\": $DAYS
  }" | python3 -m json.tool
