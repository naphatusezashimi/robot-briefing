import json
from config import DISTRICT_DATA_PATH


def load_district_data() -> dict:
    with open(DISTRICT_DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def format_for_prompt(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)
