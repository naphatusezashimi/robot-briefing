"""
โมดูลถาม AI — รองรับ 2 เจ้า เลือกที่ config.AI_PROVIDER
  - "gemini" : Google Gemini (มีโควตาฟรี)
  - "claude" : Anthropic Claude (ต้องเติมเครดิต)
ทั้งสองเจ้าใช้ system prompt กันตอบมั่วตัวเดียวกัน + แนบข้อมูลวิทยาลัยและสระบุรีทุกครั้ง
"""

from config import (
    AI_PROVIDER,
    AI_MAX_TOKENS,
    ANTHROPIC_API_KEY,
    CLAUDE_MODEL,
    GEMINI_API_KEY,
    GEMINI_MODEL,
)
from database import format_all_data

# --- กฎกันตอบมั่ว (ใช้ร่วมกันทุกเจ้า) ---
_SYSTEM_RULES = (
    "คุณเป็นหุ่นยนต์ผู้ช่วยแนะนำข้อมูลของวิทยาลัยเทคนิคท่าหลวงซิเมนต์ไทยอนุสรณ์ "
    "และข้อมูลจังหวัดสระบุรี "
    "ตอบเป็นภาษาไทย สุภาพ สั้น กระชับ เข้าใจง่าย "
    "น้ำเสียงร่าเริง เป็นกันเอง มีชีวิตชีวา "
    "ไม่ต้องขึ้นต้นด้วยคำทักทาย (เช่น สวัสดีค่ะ สวัสดีน้อง ๆ) และไม่ต้องเรียกผู้ถามว่าน้อง "
    "ให้เข้าเรื่องที่ถามทันที "
    "ใส่อีโมจิให้เข้ากับเนื้อหาประปราย เช่น 🏫 🎓 📍 📞 🌊 🛕 🍜 🎉 😊 "
    "(ประมาณหัวข้อละ 1 ตัว หรือต้นรายการ ไม่ต้องใส่ทุกคำ) "
    "ถ้าคำตอบมีหลายรายการ ให้แบ่งหัวข้อเป็น **หัวข้อ:** แล้วตามด้วยรายการขึ้นต้นด้วย * บรรทัดละรายการ "
    "ปิดท้ายด้วยประโยคชวนคุยสั้น ๆ เช่น ถามว่าอยากรู้เรื่องไหนเพิ่มไหมคะ "
    "ตอบโดยอ้างอิงจากข้อมูลวิทยาลัยและข้อมูลจังหวัดสระบุรีที่ให้ไว้เท่านั้น "
    "ห้ามแต่งหรือคาดเดาข้อมูลที่ไม่มีในฐานข้อมูลเด็ดขาด "
    "ถ้าไม่มีข้อมูลในส่วนที่ถาม ให้ตอบว่า 'ขออภัย ยังไม่มีข้อมูลในส่วนนี้' "
    "และแนะนำให้ติดต่อเจ้าหน้าที่วิทยาลัยโดยตรง (โทร 0-3628-1295)"
)

# --- ผู้ใช้เลือกภาษาอังกฤษบนจอ: ข้อมูลยังเป็นภาษาไทย ให้ AI แปลตอนตอบ ---
_LANG_RULES = {
    "en": (
        "\n\nIMPORTANT: The user has chosen English. Reply entirely in natural, friendly English "
        "(translate the Thai data; write Thai place names in English letters). "
        "Keep the same cheerful tone, emojis, **Heading:** and * list format. "
        "If the information is not available, say 'Sorry, I don't have that information yet' "
        "and suggest contacting the college staff (Tel. 0-3628-1295)."
    ),
}


def _rules(lang: str) -> str:
    return _SYSTEM_RULES + _LANG_RULES.get(lang, "")

_NO_QUESTION = "ขออภัยค่ะ ไม่ได้ยินคำถาม กรุณาถามใหม่อีกครั้งนะคะ"

# clients สร้างแบบ lazy — สร้างเฉพาะเจ้าที่ใช้จริง จะได้ไม่ error เพราะ key อีกเจ้าว่าง
_claude_client = None
_gemini_client = None


def _system_text(college_data: dict, saraburi_data: dict, lang: str = "th") -> str:
    return _rules(lang) + "\n\n" + format_all_data(college_data, saraburi_data)


def _gemini(college_data: dict, saraburi_data: dict, lang: str):
    """คืน (client, config) ที่ใช้ร่วมกันทั้งแบบตอบทีเดียวและแบบทยอยตอบ"""
    global _gemini_client
    if _gemini_client is None:
        from google import genai
        _gemini_client = genai.Client(api_key=GEMINI_API_KEY)

    from google.genai import types

    config = types.GenerateContentConfig(
        system_instruction=_system_text(college_data, saraburi_data, lang),
        max_output_tokens=AI_MAX_TOKENS,
        temperature=0.2,
        # ปิดโหมดคิดก่อนตอบ — ไม่งั้นมันกิน token จนคำตอบโดนตัด
        thinking_config=types.ThinkingConfig(thinking_budget=0),
    )
    return _gemini_client, config


def _ask_gemini(question: str, college_data: dict, saraburi_data: dict, lang: str = "th") -> str:
    client, config = _gemini(college_data, saraburi_data, lang)
    response = client.models.generate_content(model=GEMINI_MODEL, contents=question, config=config)
    return (response.text or "").strip()


def _stream_gemini(question: str, college_data: dict, saraburi_data: dict, lang: str = "th"):
    client, config = _gemini(college_data, saraburi_data, lang)
    for chunk in client.models.generate_content_stream(model=GEMINI_MODEL, contents=question, config=config):
        if chunk.text:
            yield chunk.text


def _claude_args(question: str, college_data: dict, saraburi_data: dict, lang: str):
    """คืน (client, args) ที่ใช้ร่วมกันทั้งแบบตอบทีเดียวและแบบทยอยตอบ"""
    global _claude_client
    if _claude_client is None:
        import anthropic
        _claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    return _claude_client, dict(
        model=CLAUDE_MODEL,
        max_tokens=AI_MAX_TOKENS,
        system=[
            {"type": "text", "text": _rules(lang)},
            {
                # ข้อมูลวิทยาลัย+สระบุรี ถูก cache ที่ server — ประหยัด token ในการทดสอบซ้ำ
                "type": "text",
                "text": format_all_data(college_data, saraburi_data),
                "cache_control": {"type": "ephemeral"},
            },
        ],
        messages=[{"role": "user", "content": question}],
    )


def _ask_claude(question: str, college_data: dict, saraburi_data: dict, lang: str = "th") -> str:
    client, args = _claude_args(question, college_data, saraburi_data, lang)
    response = client.messages.create(**args)
    return response.content[0].text


def _stream_claude(question: str, college_data: dict, saraburi_data: dict, lang: str = "th"):
    client, args = _claude_args(question, college_data, saraburi_data, lang)
    with client.messages.stream(**args) as stream:
        yield from stream.text_stream


def ask_ai(question: str, college_data: dict, saraburi_data: dict, lang: str = "th") -> str:
    if not question.strip():
        return _NO_QUESTION

    if AI_PROVIDER == "gemini":
        return _ask_gemini(question, college_data, saraburi_data, lang)
    elif AI_PROVIDER == "claude":
        return _ask_claude(question, college_data, saraburi_data, lang)
    else:
        raise ValueError(f"AI_PROVIDER ไม่รู้จัก: '{AI_PROVIDER}' (ใช้ได้: 'gemini' หรือ 'claude')")


def ask_ai_stream(question: str, college_data: dict, saraburi_data: dict, lang: str = "th"):
    """เหมือน ask_ai แต่ทยอยคืนข้อความทีละท่อนตามที่ AI ส่งมา (ให้จอโชว์คำตอบค่อย ๆ ขึ้น)"""
    if not question.strip():
        yield _NO_QUESTION
        return

    if AI_PROVIDER == "gemini":
        yield from _stream_gemini(question, college_data, saraburi_data, lang)
    elif AI_PROVIDER == "claude":
        yield from _stream_claude(question, college_data, saraburi_data, lang)
    else:
        raise ValueError(f"AI_PROVIDER ไม่รู้จัก: '{AI_PROVIDER}' (ใช้ได้: 'gemini' หรือ 'claude')")
