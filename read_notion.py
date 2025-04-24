import requests
import json
import os

from secret import NOTION_SECRET, NOTION_PAGE_ID

def get_ids(page_id, notion_token):
    HEADERS = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    # Step 1: fetch all blocks in the page
    url = f"https://api.notion.com/v1/blocks/{page_id}/children?page_size=100"
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    blocks =  res.json()["results"]
    # Step 2: find the first inline database block and the first code block
    database_id = None
    code_block_id = None
    for block in blocks:
        if database_id is None and block["type"] == "child_database":
            database_id = block["id"]
        elif code_block_id is None and block["type"] == "code":
            code_block_id = block["id"]
    # Step 3: check if both blocks are found
    if database_id is None or code_block_id is None:
        raise ValueError("inline database block or code block not found")
    return database_id, code_block_id

def extract_participants(properties):
    participants = properties.get("参与人", {}).get("multi_select", [])
    names = [p["name"] for p in participants]
    return names

def extract_payer(properties):
    payer = properties.get("支付人", {}).get("select")
    return payer["name"] if payer else None

# 提取标题（Name）
def extract_title(properties):
    title_info = properties.get("Name", {}).get("title", [])
    return title_info[0]["plain_text"] if title_info else None

# 提取参与人（multi_select）
def extract_participants(properties):
    participants = properties.get("参与人", {}).get("multi_select", [])
    return [p["name"] for p in participants]

# 提取支付人（select）
def extract_payer(properties):
    payer = properties.get("支付人", {}).get("select")
    return payer["name"] if payer else None

# 提取备注（rich_text）
def extract_note(properties):
    notes = properties.get("备注", {}).get("rich_text", [])
    return notes[0]["plain_text"] if notes else None

# 提取是否已结算（checkbox）
def extract_settled(properties):
    return properties.get("已结算", {}).get("checkbox", False)

# 提取日期（date）
def extract_date(properties):
    date_info = properties.get("Date", {}).get("date", {})
    return date_info.get("start", None)

# 提取币种（select）
def extract_currency(properties):
    currency = properties.get("币种", {}).get("select")
    return currency["name"] if currency else None

# 提取金额（number）
def extract_amount(properties):
    return properties.get("金额", {}).get("number")


def parse_pages(pages):
    data = []
    all_participants = set()
    all_currencies = set()
    skipped = 0
    for page in pages:
        properties = page['properties']
        if "参与人" not in properties or "支付人" not in properties or "币种" not in properties or "金额" not in properties:
            print("有缺失的字段,跳过")
            skipped += 1
            continue
        participants = extract_participants(properties)
        payer = extract_payer(properties)
        title = extract_title(properties)
        note = extract_note(properties)
        settled = extract_settled(properties)
        date = extract_date(properties)
        currency = extract_currency(properties)
        amount = extract_amount(properties)
        title = extract_title(properties)

        if not participants or not payer or not currency or not amount:
            # amount = 0 is also considered as missing value
            print("有缺失的值,跳过")
            skipped += 1
            continue

        all_participants.update(participants)
        all_participants.add(payer)
        all_currencies.add(currency)

        data.append({
            "title": title,
            "participants": participants,
            "payer": payer,
            "note": note,
            "settled": settled,
            "date": date,
            "currency": currency,
            "amount": amount
        })

    return data, all_participants, all_currencies, skipped


def read_notion_database(database_id, notion_token):
    """
    Reads a Notion database and returns its content.
    
    Args:
        database_id (str): The ID of the Notion database.
        notion_token (str): The Notion integration token.
    
    Returns:
        list: A list of dictionaries representing the rows in the database.
    """

    HEADERS = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    response = requests.post(
        f"https://api.notion.com/v1/databases/{database_id}/query",
        headers=HEADERS,
    )
    # print(response.text)
    has_more = True
    start_cursor = None # TODO query only returns 100 results, so we need to paginate in the future version
    all_pages = []

    while has_more:
        if response.status_code == 200:
            print("获取成功")
            data = response.json()
            all_pages.extend(data["results"])
            has_more = data.get("has_more", False)

        else:
            print("获取失败")
            print(response.text)
            break
    
    return all_pages

if __name__ == "__main__":
    notion_token = NOTION_SECRET
    database_id, _ = get_ids(NOTION_PAGE_ID, notion_token)
    
    database_content = read_notion_database(database_id, notion_token)
    # print(json.dumps(database_content, indent=4, ensure_ascii=False))

    data, all_participants, all_currencies, skipped = parse_pages(database_content)
    print(data, all_participants, all_currencies, skipped)
