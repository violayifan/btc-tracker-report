#!/usr/bin/env python3
import json
import os
from datetime import datetime

TRACKER_FILE = "/root/.openclaw/workspace/btc_trades.json"

try:
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, 'r', encoding='utf-8') as f:
            trades = json.load(f)
        print(f"当前交易记录数: {len(trades)}")
        if trades:
            for t in trades:
                print(f"  {t['datetime']} | {t['action']} @ ${t['price']}")
    else:
        print("没有交易记录")
        trades = []
except Exception as e:
    print(f"读取错误: {e}")
    trades = []
