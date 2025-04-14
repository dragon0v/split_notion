import requests
import json
import os

from secret import NOTION_SECRET, NOTION_DATABASE_ID

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
    return date_info.get("start")

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
    for page in pages:
        properties = page['properties']
        participants = extract_participants(properties)
        payer = extract_payer(properties)
        title = extract_title(properties)
        note = extract_note(properties)
        settled = extract_settled(properties)
        date = extract_date(properties)
        currency = extract_currency(properties)
        amount = extract_amount(properties)
        title = extract_title(properties)

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
        
    return data, all_participants, all_currencies


def read_notion_database(database_id, notion_token):
    """
    Reads a Notion database and returns its content.
    
    Args:
        database_id (str): The ID of the Notion database.
        notion_token (str): The Notion integration token.
    
    Returns:
        list: A list of dictionaries representing the rows in the database.
    """

    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    response = requests.post(
        f"https://api.notion.com/v1/databases/{database_id}/query",
        headers=headers,
    )
    # print(response.text)
    has_more = True
    start_cursor = None
    all_pages = []

    while has_more:
        if response.status_code == 200:
            print("获取成功")
            data = response.json()
            all_pages.extend(data["results"])
            has_more = data.get("has_more", False)

        else:
            print("获取失败")
            break
    
    return all_pages

if __name__ == "__main__":
    notion_token = NOTION_SECRET
    database_id = NOTION_DATABASE_ID
    
    database_content = read_notion_database(database_id, notion_token)
    # print(json.dumps(database_content, indent=4, ensure_ascii=False))

    data, all_participants, all_currencies = parse_pages(database_content)
    print(data, all_participants, all_currencies)
