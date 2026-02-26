# Fetch exchange rate from Frankfurter Exchange Rates API
# https://frankfurter.dev/

import requests
from datetime import datetime

def build_exchange_rate_dict(base="SEK"):
    """
    获取指定基准货币对所有可用币种的今日汇率字典
    返回格式: {"CNY": 7.24, "EUR": 0.92, ...}
    """
    base = base.upper()
    # 不带 symbols 参数，API 会返回所有支持的货币
    url = f"https://api.frankfurter.dev/v1/latest"
    params = {"base": base}

    try:
        response = requests.get(url, params=params)
        
        # 如果基准货币不支持（例如输入了 'XYZ'），API 会返回 400/404
        if response.status_code != 200:
            print(f"❌ 无法获取基准货币 {base} 的数据。")
            return {}

        data = response.json()
        
        # 提取 rates 部分，它本身就是一个字典
        exchange_rates = data.get("rates", {})
        
        # 补充基准货币自身 (1:1)，方便后续计算
        exchange_rates[base] = 1.0
        
        print(f"✅ 成功构建汇率表，基准: {base}，共包含 {len(exchange_rates)} 个币种。")
        """
        # return format
        EXCHANGE_RATE_LOCAL = {
            "description": "4-12到4-18的xe平均汇率",
            "SEK": {
                "NOK": 1 / 0.922346,
            },
            "NOK": {
                "SEK": 0.922346,
            },
        }
        """
        format_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return {"description":f"{format_time} 的frankfurter汇率", base:exchange_rates}

    except requests.exceptions.RequestException as e:
        print(f"🚀 网络连接失败: {e}")
        return {}
    

def get_exchange_rate(base="USD", target="SEK", date=None):
    """
    获取指定日期的汇率：1单位base货币 = x单位target货币
    date 默认为 None (即最新汇率)，格式应为 'YYYY-MM-DD'
    """
    
    # 1. 校验日期格式与合法性
    request_date = "latest"
    if date:
        try:
            # 尝试解析日期，确保格式正确且是一个真实的日期
            valid_date = datetime.strptime(date, "%Y-%m-%d")
            
            # 判断是否是未来日期（API 不支持预测未来）
            if valid_date > datetime.now():
                print(f"⚠️ 错误: 日期 {date} 不能是未来日期。")
                return None
            
            request_date = date

        except ValueError:
            print(f"⚠️ 错误: 日期格式 '{date}' 无效，请使用 'YYYY-MM-DD' 格式。")
            return None

    # 2. 构建 API URL
    # Frankfurter API 路径格式: /YYYY-MM-DD 或 /latest
    url = f"https://api.frankfurter.dev/v1/{request_date}"
    params = {
        "base": base.upper(),
        "symbols": target.upper()
    }

    # 3. 发送请求
    try:
        response = requests.get(url, params=params)
        
        # 处理 API 报错（如货币代码不支持）
        if response.status_code != 200:
            error_info = response.json()
            print(f"❌ API 错误: {error_info.get('message', '未知错误')}")
            return None
            
        data = response.json()
        
        # 提取汇率
        rate = data.get('rates', {}).get(target.upper())
        if rate:
            return rate
        else:
            print(f"⚠️ 未能获取 {base} 到 {target} 的汇率。")
            return None

    except requests.exceptions.RequestException as e:
        print(f"🚀 网络请求异常: {e}")
        return None

# 使用示例
if __name__ == "__main__":
    rate = get_exchange_rate(base="SEK", target="CNY")
    print(f"当前 SEK/CNY 汇率: {rate}")

    rate = get_exchange_rate(base="SEK", target="CNY", date='2026-01-01')
    print(f"20260101 SEK/CNY 汇率: {rate}")

    print(build_exchange_rate_dict())