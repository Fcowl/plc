import os
import json
SAVE_FILE = r'C:\Users\Fcowl\PycharmProject\Playtime_Counter_git\123.json'

def load_user_data(encoding:str = "UTF-8",filename:str= SAVE_FILE) -> dict:
    if not os.path.exists(filename):
        return {}
    with open(filename, "r", encoding=encoding) as f:
        return json.load(f)

print(load_user_data())