import argparse
from settle import settle
from add_to_notion import update_notion




# 命令行接口
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Settle Notion pages.")
    parser.add_argument("database_id", help="Notion database ID")
    parser.add_argument("page_id", help="Notion output page ID")
    parser.add_argument("notion_token", help="Notion integration token")
    parser.add_argument("--currency", help="Currency to settle")
    parser.add_argument("--settle_mode", help="Settle mode")
    parser.add_argument("--exchange_rate_mode", help="Exchange rate mode")

    args = parser.parse_args()
    print(args)

    # 转 kwargs 并调用
    kwargs = {
        "currency": args.currency,
        "settle_mode": args.settle_mode,
        "exchange_rate_mode": args.exchange_rate_mode,
    }

    data_to_notion = settle(args.database_id, args.notion_token, **kwargs)
    update_notion(data_to_notion, args.page_id, args.notion_token)