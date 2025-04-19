# !/usr/bin/python
# -*- coding: utf-8 -*-
import json
import os
import aiofiles


# Đường dẫn các file cấu hình
CONFIG_FILE = "config.json"
SKILL_FILE = "skill.json"
ACTION_FILE = "action.json"
OBJECT_FILE = "object.json"
ADVERB_FILE = "adverb.json"

# Hàm load dữ liệu từ file JSON
def load_config(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

# Hàm lưu dữ liệu vào file JSON
async def save_config():
    async with aiofiles.open("config.json", "w", encoding="utf-8") as f:
        await f.write(json.dumps(config, indent=2, ensure_ascii=False))

# Các biến toàn cục dùng cho toàn hệ thống
config = load_config(CONFIG_FILE)
skill = load_config(SKILL_FILE)
action = load_config(ACTION_FILE)
objectt = load_config(OBJECT_FILE)
adverb = load_config(ADVERB_FILE)
