# Fetch exchange rate from Frankfurter Exchange Rates API
# https://frankfurter.dev/

import json
import os

import requests
from datetime import datetime

def build_exchange_rate_dict(base="SEK", date=None):
    """
    获取指定日期指定基准货币对所有可用币种的汇率字典
    date默认为今日，格式YYYY-MM-DD
    返回格式: {"CNY": 7.24, "EUR": 0.92, ...}
    """
    base = base.upper()
    params = {"base": base}

    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
        url = f"https://api.frankfurter.dev/v1/latest"
        cache_name = f"temp/frankfurter_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{base}.json"
    else:
        validate_date(date)
        url = f"https://api.frankfurter.dev/v1/{date}"
        # 如果temp文件夹内已有本地缓存的汇率，直接读取本地汇率并返回
        cache_name = f"temp/frankfurter_{date.replace('-', '')}_{base}.json"
        if os.path.exists(cache_name):
            with open(cache_name, "r") as f:
                print("Using cached exchange rates from", cache_name)
                return json.load(f)

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

        format_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 保存到本地 temp/frankfurter_YYYYMMDD_base.json
        if not os.path.exists("temp"):
            os.makedirs("temp")
        with open(cache_name, "w") as f:
            json.dump({"description": f"frankfurter rate on {date}, fetched at {format_time}", base: exchange_rates}, f)

        return {"description": f"frankfurter rate on {date}, fetched at {format_time}", base: exchange_rates}

    except requests.exceptions.RequestException as e:
        print(f"🚀 网络连接失败: {e}")
        return {}

def validate_date(date):
    """
    验证日期字符串是否符合 YYYY-MM-DD 格式，并且是一个有效的日期
    """
    try:
        # 尝试解析日期，确保格式正确且是一个真实的日期
        valid_date = datetime.strptime(date, "%Y-%m-%d")
        
        # 判断是否是未来日期
        if valid_date > datetime.now():
            raise ValueError(f"日期 {date} 不能是未来日期。")

    except ValueError as e:
        print(e)


# 使用示例
if __name__ == "__main__":
    # print(build_exchange_rate_dict())
    # print(build_exchange_rate_dict(base="CNY"))
    print(build_exchange_rate_dict(base="SEK", date="2026-01-01"))