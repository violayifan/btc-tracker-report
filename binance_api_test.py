#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
币安API测试脚本 - 通过代理访问
测试多个币安公开API接口
"""

import requests
import json
import time
from datetime import datetime

# ==================== 配置 ====================
PROXY = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890',
}

# 超时设置
TIMEOUT = 10
# ===========================================

def print_section(title):
    """打印分隔线"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_api(url, name, params=None):
    """测试API接口"""
    try:
        print(f"\n📡 测试: {name}")
        print(f"🔗 URL: {url}")

        response = requests.get(url, params=params, proxies=PROXY, timeout=TIMEOUT)

        print(f"✅ 状态码: {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()
                print(f"📊 数据类型: {type(data).__name__}")

                # 显示部分数据
                if isinstance(data, dict):
                    if 'success' in data:
                        print(f"✨ 成功: {data.get('success')}")
                    if 'code' in data:
                        print(f"🔑 Code: {data.get('code')}")
                    if 'data' in data:
                        data_content = data.get('data')
                        print(f"📦 数据预览: {json.dumps(data_content, ensure_ascii=False)[:200]}...")
                elif isinstance(data, list) and len(data) > 0:
                    print(f"📦 数据预览: {json.dumps(data[0], ensure_ascii=False)[:200]}...")

                return data
            except json.JSONDecodeError:
                print(f"❌ JSON解析失败")
                print(f"📝 响应内容: {response.text[:200]}")
                return None
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"📝 响应内容: {response.text[:200]}")
            return None

    except requests.exceptions.ProxyError as e:
        print(f"❌ 代理错误: {str(e)}")
        return None
    except requests.exceptions.Timeout:
        print(f"⏰ 请求超时")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"❌ 连接错误: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ 未知错误: {str(e)}")
        return None

def main():
    """主函数"""
    print_section("币安API测试脚本 - 通过代理访问")
    print(f"🕐 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 代理: {PROXY['http']}")

    # 测试统计
    total_tests = 0
    success_tests = 0
    failed_tests = 0

    # ==================== 1. 公告相关API ====================
    print_section("1️⃣ 公告相关API")

    # 1.1 新币上架公告
    total_tests += 1
    result = test_api(
        "https://www.binance.com/bapi/composite/v1/public/cms/article/list/query",
        "新币上架公告列表",
        params={
            "type": "1",
            "catalogId": "48",
            "pageNo": "1",
            "pageSize": "3"
        }
    )
    if result:
        success_tests += 1
        if result.get('success') and result.get('data', {}).get('catalogs'):
            articles = result['data']['catalogs'][0].get('articles', [])
            print(f"\n📰 最新3条公告:")
            for i, article in enumerate(articles, 1):
                print(f"   {i}. {article.get('title', 'N/A')}")
    else:
        failed_tests += 1

    time.sleep(1)

    # ==================== 2. 行情数据API ====================
    print_section("2️⃣ 行情数据API")

    # 2.1 获取所有交易对价格
    total_tests += 1
    result = test_api(
        "https://api.binance.com/api/v3/ticker/price",
        "所有交易对价格"
    )
    if result:
        success_tests += 1
        if isinstance(result, list) and len(result) > 0:
            print(f"\n💰 示例价格数据 (前5个):")
            for i, item in enumerate(result[:5], 1):
                print(f"   {i}. {item.get('symbol', 'N/A')}: ${item.get('price', 'N/A')}")
    else:
        failed_tests += 1

    time.sleep(1)

    # 2.2 BTC交易对详情
    total_tests += 1
    result = test_api(
        "https://api.binance.com/api/v3/ticker/24hr",
        "BTC/USDT 24小时行情",
        params={"symbol": "BTCUSDT"}
    )
    if result:
        success_tests += 1
        if isinstance(result, dict):
            print(f"\n📊 BTC/USDT 24小时数据:")
            print(f"   最新价: ${result.get('lastPrice', 'N/A')}")
            print(f"   24h涨跌: {result.get('priceChangePercent', 'N/A')}%")
            print(f"   24h成交量: {result.get('volume', 'N/A')} BTC")
            print(f"   24h成交额: ${result.get('quoteVolume', 'N/A')} USDT")
    else:
        failed_tests += 1

    time.sleep(1)

    # 2.3 深度数据
    total_tests += 1
    result = test_api(
        "https://api.binance.com/api/v3/depth",
        "BTC/USDT 深度数据",
        params={"symbol": "BTCUSDT", "limit": "5"}
    )
    if result:
        success_tests += 1
        if isinstance(result, dict):
            bids = result.get('bids', [])[:3]
            asks = result.get('asks', [])[:3]
            print(f"\n📈 BTC/USDT 深度数据:")
            print(f"   买单 (前3档):")
            for i, bid in enumerate(bids, 1):
                print(f"      {i}. ${bid[0]} - {bid[1]} BTC")
            print(f"   卖单 (前3档):")
            for i, ask in enumerate(asks, 1):
                print(f"      {i}. ${ask[0]} - {ask[1]} BTC")
    else:
        failed_tests += 1

    time.sleep(1)

    # 2.4 K线数据
    total_tests += 1
    result = test_api(
        "https://api.binance.com/api/v3/klines",
        "BTC/USDT 1小时K线数据",
        params={"symbol": "BTCUSDT", "interval": "1h", "limit": "3"}
    )
    if result:
        success_tests += 1
        if isinstance(result, list) and len(result) > 0:
            print(f"\n📊 BTC/USDT 1小时K线 (最近3根):")
            for i, kline in enumerate(result, 1):
                open_time = datetime.fromtimestamp(kline[0] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                print(f"   {i}. {open_time} | 开: ${kline[1]} | 高: ${kline[2]} | 低: ${kline[3]} | 收: ${kline[4]}")
    else:
        failed_tests += 1

    time.sleep(1)

    # ==================== 3. 复制交易API ====================
    print_section("3️⃣ 复制交易API")

    # 3.1 带单交易员ROI数据
    total_tests += 1
    result = test_api(
        "https://www.binance.com/bapi/futures/v1/public/future/copy-trade/lead-portfolio/chart-data",
        "复制交易带单ROI数据",
        params={
            "dataType": "ROI",
            "portfolioId": "4894637394886608641",
            "timeRange": "30D"
        }
    )
    if result:
        success_tests += 1
        if result.get('success') and result.get('data'):
            data = result['data']
            if len(data) > 0:
                print(f"\n📈 复制交易ROI数据:")
                print(f"   数据点数量: {len(data)}")
                print(f"   最新ROI: {data[-1].get('value', 'N/A')}%")
                print(f"   最高ROI: {max([d.get('value', 0) for d in data]):.2f}%")
                print(f"   最低ROI: {min([d.get('value', 0) for d in data]):.2f}%")
    else:
        failed_tests += 1

    time.sleep(1)

    # ==================== 4. 交易所信息API ====================
    print_section("4️⃣ 交易所信息API")

    # 4.1 服务器时间
    total_tests += 1
    result = test_api(
        "https://api.binance.com/api/v3/time",
        "服务器时间"
    )
    if result:
        success_tests += 1
        if isinstance(result, dict) and 'serverTime' in result:
            server_time = datetime.fromtimestamp(result['serverTime'] / 1000)
            print(f"\n⏰ 币安服务器时间: {server_time.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        failed_tests += 1

    time.sleep(1)

    # 4.2 交易规则
    total_tests += 1
    result = test_api(
        "https://api.binance.com/api/v3/exchangeInfo",
        "交易所规则",
        params={"symbol": "BTCUSDT"}
    )
    if result:
        success_tests += 1
        if isinstance(result, dict) and 'symbols' in result:
            symbol_info = result['symbols'][0] if result['symbols'] else {}
            print(f"\n📋 BTC/USDT 交易规则:")
            print(f"   交易对状态: {symbol_info.get('status', 'N/A')}")
            print(f"   基础资产: {symbol_info.get('baseAsset', 'N/A')}")
            print(f"   报价资产: {symbol_info.get('quoteAsset', 'N/A')}")
            print(f"   最小订单量: {symbol_info.get('filters', [{}])[0].get('minQty', 'N/A') if symbol_info.get('filters') else 'N/A'}")
    else:
        failed_tests += 1

    # ==================== 测试总结 ====================
    print_section("📊 测试总结")
    print(f"\n总测试数: {total_tests}")
    print(f"✅ 成功: {success_tests}")
    print(f"❌ 失败: {failed_tests}")
    print(f"📈 成功率: {(success_tests/total_tests*100):.1f}%")

    print(f"\n🕐 结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if success_tests == total_tests:
        print("\n🎉 所有API测试通过！代理配置正常。")
    elif success_tests > total_tests / 2:
        print("\n⚠️ 部分API测试失败，请检查网络连接或代理配置。")
    else:
        print("\n❌ 大部分API测试失败，代理可能配置有误。")

    return success_tests, failed_tests

if __name__ == "__main__":
    success, failed = main()
    exit(0 if failed == 0 else 1)
