#!/usr/bin/env python3
"""添加测试交易数据"""

import json
import time
from datetime import datetime

TRACKER_FILE = "/root/.openclaw/workspace/btc_trades.json"

def add_trade(action, price):
    """添加一笔交易"""
    trade = {
        "timestamp": datetime.now().isoformat(),
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "price": price,
        "stop_loss": None,
        "take_profit": None,
        "strategy": "测试数据"
    }
    
    # 加载现有交易
    trades = []
    if open(TRACKER_FILE, 'r').read().strip():
        trades = json.loads(open(TRACKER_FILE, 'r').read())
    
    trades.append(trade)
    
    # 保存
    with open(TRACKER_FILE, 'w', encoding='utf-8') as f:
        json.dump(trades, f, indent=2, ensure_ascii=False)
    
    print(f"添加交易: {action} @ ${price}")

# 添加测试交易（模拟真实场景）
# 场景1：开多68000 -> 平多68500（盈利）
add_trade("LONG", 68000)
time.sleep(0.1)

add_trade("SHORT", 68500)  # 平多
time.sleep(0.1)

# 场景2：开空68200 -> 平空68000（盈利）
add_trade("SHORT", 68200)
time.sleep(0.1)

add_trade("LONG", 68000)  # 平空
time.sleep(0.1)

# 场景3：开多68100 -> 平多67900（亏损）
add_trade("LONG", 68100)
time.sleep(0.1)

add_trade("SHORT", 67900)  # 平多
time.sleep(0.1)

print("\n测试交易数据已添加")
print(f"总交易数: {len(json.loads(open(TRACKER_FILE, 'r').read()))}")
