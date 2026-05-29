import json
from config import COLLEGE_DATA_PATH


def load_college_data() -> dict:
    with open(COLLEGE_DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def format_for_prompt(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)
