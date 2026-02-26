import requests
import os
from dotenv import load_dotenv

# 加载 .env 文件中的变量
load_dotenv()

# 从环境变量中读取
NOTION_SECRET = os.getenv("NOTION_SECRET")
NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID")

def update_code_block(block_id, notion_token, new_code):
    HEADERS = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    url = f"https://api.notion.com/v1/blocks/{block_id}"
    data = {
        "code": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": new_code
                    }
                }
            ],
            "language": "plain text"
        }
    }
    res = requests.patch(url, headers=HEADERS, json=data)
    res.raise_for_status()
    return res.json()


def update_notion(log, code_block_id, notion_token):
    update_code_block(code_block_id, notion_token, log)
    print("✅ Code block updated successfully.")

