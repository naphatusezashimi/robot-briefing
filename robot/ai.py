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
    "ตอบโดยอ้างอิงจากข้อมูลวิทยาลัยและข้อมูลจังหวัดสระบุรีที่ให้ไว้เท่านั้น "
    "ห้ามแต่งหรือคาดเดาข้อมูลที่ไม่มีในฐานข้อมูลเด็ดขาด "
    "ถ้าไม่มีข้อมูลในส่วนที่ถาม ให้ตอบว่า 'ขออภัย ยังไม่มีข้อมูลในส่วนนี้' "
    "และแนะนำให้ติดต่อเจ้าหน้าที่วิทยาลัยโดยตรง (โทร 0-3628-1295)"
)

_NO_QUESTION = "ขออภัยค่ะ ไม่ได้ยินคำถาม กรุณาถามใหม่อีกครั้งนะคะ"

# clients สร้างแบบ lazy — สร้างเฉพาะเจ้าที่ใช้จริง จะได้ไม่ error เพราะ key อีกเจ้าว่าง
_claude_client = None
_gemini_client = None


def _system_text(college_data: dict, saraburi_data: dict) -> str:
    return _SYSTEM_RULES + "\n\n" + format_all_data(college_data, saraburi_data)


def _ask_gemini(question: str, college_data: dict, saraburi_data: dict) -> str:
    global _gemini_client
    if _gemini_client is None:
        from google import genai
        _gemini_client = genai.Client(api_key=GEMINI_API_KEY)

    from google.genai import types

    response = _gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=question,
        config=types.GenerateContentConfig(
            system_instruction=_system_text(college_data, saraburi_data),
            max_output_tokens=AI_MAX_TOKENS,
            temperature=0.2,
            # ปิดโหมดคิดก่อนตอบ — ไม่งั้นมันกิน token จนคำตอบโดนตัด
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
    )
    return (response.text or "").strip()


def _ask_claude(question: str, college_data: dict, saraburi_data: dict) -> str:
    global _claude_client
    if _claude_client is None:
        import anthropic
        _claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    response = _claude_client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=AI_MAX_TOKENS,
        system=[
            {"type": "text", "text": _SYSTEM_RULES},
            {
                # ข้อมูลวิทยาลัย+สระบุรี ถูก cache ที่ server — ประหยัด token ในการทดสอบซ้ำ
                "type": "text",
                "text": format_all_data(college_data, saraburi_data),
                "cache_control": {"type": "ephemeral"},
            },
        ],
        messages=[{"role": "user", "content": question}],
    )
    return response.content[0].text


def ask_ai(question: str, college_data: dict, saraburi_data: dict) -> str:
    if not question.strip():
        return _NO_QUESTION

    if AI_PROVIDER == "gemini":
        return _ask_gemini(question, college_data, saraburi_data)
    elif AI_PROVIDER == "claude":
        return _ask_claude(question, college_data, saraburi_data)
    else:
        raise ValueError(f"AI_PROVIDER ไม่รู้จัก: '{AI_PROVIDER}' (ใช้ได้: 'gemini' หรือ 'claude')")
