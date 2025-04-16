import requests
from secret import NOTION_SECRET, NOTION_PAGE_ID




# Step 1: 获取页面下的所有 block
def get_child_blocks(page_id, headers):
    url = f"https://api.notion.com/v1/blocks/{page_id}/children?page_size=100"
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    return res.json()["results"]

# Step 2: 找到 code block
def find_code_block(blocks):
    for block in blocks:
        if block["type"] == "code":
            return block["id"]
    return None

# Step 3: 更新 code block 内容
def update_code_block(block_id, new_code, headers, language="plain text"):
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
            "language": language
        }
    }
    res = requests.patch(url, headers=headers, json=data)
    res.raise_for_status()
    return res.json()

# === 主执行流程 ===
def update_notion(log, page_id, notion_token):
    HEADERS = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    blocks = get_child_blocks(page_id, HEADERS)
    code_block_id = find_code_block(blocks)

    if code_block_id:
        updated = update_code_block(code_block_id, log, HEADERS)
        print("✅ Code block updated successfully.")
    else:
        print("❌ 没有找到 code block。")

if __name__ == "__main__":
    update_notion("test", NOTION_PAGE_ID, NOTION_SECRET)