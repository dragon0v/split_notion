from collections import defaultdict
import time
import read_notion
from add_to_notion import update_notion
from secret import NOTION_SECRET, NOTION_DATABASE_ID, NOTION_PAGE_ID
from constants import EXCHANGE_RATE_LOCAL



def settle(database_id, notion_token, **kwargs):
    """
    结算函数
    :param database_id: Notion 数据库 ID
    :param notion_token: Notion 集成令牌
    :param args: 其他参数
    :param kwargs: 关键字参数
    :return: log: str
    """

    log = ""

    for key, value in kwargs.items():
        match key:
            case "currency":
                settle_currency = value
            case "settle_mode":
                settle_mode = value
            case "exchange_rate_mode":
                exchange_rate_mode = value
            case _:
                raise ValueError(f"Unknown argument: {key}")

    
        

    # 读取 Notion 数据库
    pages = read_notion.read_notion_database(database_id, notion_token)
    
    # 解析页面数据
    data, all_participants, all_currencies = read_notion.parse_pages(pages)

    # print(data)
    # print(all_participants)
    # print(all_currencies)
    print("更新于：", time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime()))
    log += "更新于：" + time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime()) + "\n"
    
    has_paid = defaultdict(lambda: defaultdict(int)) # who has paid how much in different currencies
    gets = defaultdict(lambda: defaultdict(int)) # who gets how much in different currencies
    total_amount = defaultdict(int) # currency: amount
    for payment in data:
        participants = payment["participants"]
        payer = payment["payer"]
        amount = payment["amount"]
        currency = payment["currency"]
        settled = payment["settled"]

        if settled:
            continue
        
        has_paid[payer][currency] += amount
        gets[payer][currency] += amount
        total_amount[currency] += amount
        
        # 计算每个人的份额
        share = amount / len(participants)
        
        # 更新每个人的份额
        for participant in participants:
            gets[participant][currency] -= share
    
    # print everyone's total amount paid
    for participant, currencies in has_paid.items():
        for currency, amount in currencies.items():
            if amount > 0:
                print(f"{participant} 累计已支付 {amount} {currency}")
                log += f"{participant} 累计已支付 {amount} {currency}\n"
    for currency, amount in total_amount.items():
        print(f"总计已支付 {amount} {currency}")
        log += f"总计已支付 {amount} {currency}\n"
    print('------------------------------')
    log += '------------------------------\n'

    # print everyone's total amount to get
    for participant, currencies in gets.items():
        for currency, amount in currencies.items():
            if amount > 0:
                print(f"{participant} 应收 {amount} {currency}")
                log += f"{participant} 应收 {amount} {currency}\n"
            elif amount < 0:
                print(f"{participant} 应付 {-amount} {currency}")
                log += f"{participant} 应付 {-amount} {currency}\n"
            # else:
            #     print(f"{participant} is settled up in {currency}")
    print('------------------------------')
    log += '------------------------------\n'

    # settle
    if settle_mode == 'bank':
        new_gets = defaultdict(int) # who gets how much in settle_currency
        print(f'正在以 {settle_currency} 结算')
        log += f'正在以 {settle_currency} 结算\n'

        if exchange_rate_mode == 'local':
            print('使用本地汇率', EXCHANGE_RATE_LOCAL)
            log += '使用本地汇率' + str(EXCHANGE_RATE_LOCAL) + '\n'
            exchange_rate_dict = EXCHANGE_RATE_LOCAL

        for participant, currencies in gets.items():
            for currency, amount in currencies.items():
                if currency == settle_currency:
                    new_gets[participant] += amount
                else:
                    new_gets[participant] += amount * exchange_rate_dict[currency][settle_currency]
        # find who is bank
        _max_amount = 0
        bank = None
        for participant, amount in new_gets.items():
            if amount > _max_amount:
                _max_amount = amount
                bank = participant

        for participant, amount in new_gets.items():
            if participant == bank:
                continue
            if amount > 0:
                print(f"{bank} 应向 {participant} 支付 {amount} {settle_currency}")
                log += f"{bank} 应向 {participant} 支付 {amount} {settle_currency}\n"
            elif amount <= 0:
                print(f"{bank} 应从 {participant} 得到 {-amount} {settle_currency}")
                log += f"{bank} 应从 {participant} 得到 {-amount} {settle_currency}\n"
        print(f"({bank} 总计得到 {new_gets[bank]} {settle_currency})")
        log += f"({bank} 总计得到 {new_gets[bank]} {settle_currency})\n"
        print('------------------------------')
        log += '------------------------------\n'

        return log


if __name__ == "__main__":
    log = settle(NOTION_DATABASE_ID, NOTION_SECRET, settle_mode='bank', currency='SEK', exchange_rate_mode='local')
    # update_notion(log, NOTION_PAGE_ID, NOTION_SECRET)