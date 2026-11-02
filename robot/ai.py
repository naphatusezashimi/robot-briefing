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
    GEMINI_API_KEYS,
    GEMINI_FALLBACK_MODELS,
    GEMINI_TTS_MODELS,
    GEMINI_TTS_VOICE,
    GEMINI_MODEL,
)
from database import format_all_data

# --- กฎกันตอบมั่ว (ใช้ร่วมกันทุกเจ้า) ---
_SYSTEM_RULES = (
    "คุณเป็นหุ่นยนต์ผู้ช่วยแนะนำข้อมูลของวิทยาลัยเทคนิคท่าหลวงซิเมนต์ไทยอนุสรณ์ "
    "และข้อมูลจังหวัดสระบุรี "
    "คุณเป็นหุ่นยนต์ผู้ชาย ชื่อทีแอลบอท แทนตัวเองว่า ผม และลงท้ายประโยคด้วย ครับ เสมอ (ห้ามใช้ ค่ะ คะ หนู ดิฉัน) "
    "ตอบเป็นภาษาไทย สุภาพ สั้น กระชับ เข้าใจง่าย "
    "น้ำเสียงร่าเริง เป็นกันเอง มีชีวิตชีวา "
    "ไม่ต้องขึ้นต้นด้วยคำทักทาย (เช่น สวัสดีครับ สวัสดีน้อง ๆ) และไม่ต้องเรียกผู้ถามว่าน้อง "
    "ให้เข้าเรื่องที่ถามทันที "
    "ใส่อีโมจิให้เข้ากับเนื้อหาประปราย เช่น 🏫 🎓 📍 📞 🌊 🛕 🍜 🎉 😊 "
    "(ประมาณหัวข้อละ 1 ตัว หรือต้นรายการ ไม่ต้องใส่ทุกคำ) "
    "ถ้าคำตอบมีหลายรายการ ให้แบ่งหัวข้อเป็น **หัวข้อ:** แล้วตามด้วยรายการขึ้นต้นด้วย * บรรทัดละรายการ "
    "ปิดท้ายด้วยประโยคชวนคุยสั้น ๆ เช่น ถามว่าอยากรู้เรื่องไหนเพิ่มไหมครับ "
    "ตอบโดยอ้างอิงจากข้อมูลวิทยาลัยและข้อมูลจังหวัดสระบุรีที่ให้ไว้เท่านั้น "
    "ห้ามแต่งหรือคาดเดาข้อมูลที่ไม่มีในฐานข้อมูลเด็ดขาด "
    "ข้อมูลวิทยาลัยมี 2 แหล่ง: ฐานข้อมูลจากเว็บไซต์ (ช่องทางติดต่อ การรับสมัคร) และรายงาน SAR ปีการศึกษา 2568 (สถิติ ผลงาน รางวัล ประวัติ) "
    "ถ้าตอบด้วยตัวเลขจาก SAR ให้บอกว่าเป็นข้อมูลปีการศึกษา 2568 "
    "ถ้าสองแหล่งขัดกัน ให้ใช้ข้อมูลเว็บไซต์เรื่องการติดต่อ/รับสมัคร และใช้ SAR เรื่องชื่อสาขา สถิติ และผลงาน "
    "เวลาตอบเรื่องสาขาที่เปิดสอน ให้ใช้รายชื่อ 26 สาขาตาม SAR 2568 (ปวช. 13 / ปวส. 13) เท่านั้น "
    "ถ้าไม่มีข้อมูลในส่วนที่ถาม ให้ตอบว่า 'ขออภัย ยังไม่มีข้อมูลในส่วนนี้' "
    "และแนะนำให้ติดต่อเจ้าหน้าที่วิทยาลัยโดยตรง (โทร 0-3628-1295)"
)

# --- ผู้ใช้เลือกภาษาอังกฤษบนจอ: ข้อมูลยังเป็นภาษาไทย ให้ AI แปลตอนตอบ ---
_LANG_RULES = {
    "en": (
        "\n\nIMPORTANT: The user has chosen English. Reply entirely in natural, friendly English "
        "(translate the Thai data; write Thai place names in English letters). "
        "You are TL-Bot, a male robot. Keep the same cheerful tone, emojis, **Heading:** and * list format. "
        "If the information is not available, say 'Sorry, I don't have that information yet' "
        "and suggest contacting the college staff (Tel. 0-3628-1295)."
    ),
}


def _rules(lang: str) -> str:
    return _SYSTEM_RULES + _LANG_RULES.get(lang, "")

_NO_QUESTION = "ขออภัยครับ ไม่ได้ยินคำถาม กรุณาถามใหม่อีกครั้งนะครับ"

# clients สร้างแบบ lazy — สร้างเฉพาะเจ้าที่ใช้จริง จะได้ไม่ error เพราะ key อีกเจ้าว่าง
_claude_client = None
_gemini_clients = {}   # key -> client
_gemini_idx = 0        # key ที่ใช้อยู่ตอนนี้ (โควตาหมดแล้วเลื่อนไปตัวถัดไป)


def _system_text(college_data: dict, saraburi_data: dict, lang: str = "th") -> str:
    return _rules(lang) + "\n\n" + format_all_data(college_data, saraburi_data)


def is_quota_error(e: Exception) -> bool:
    msg = str(e)
    return "RESOURCE_EXHAUSTED" in msg or "429" in msg or "rate_limit" in msg


def _gemini_client(key: str):
    if key not in _gemini_clients:
        from google import genai
        _gemini_clients[key] = genai.Client(api_key=key)
    return _gemini_clients[key]


def _gemini_config(college_data: dict, saraburi_data: dict, lang: str):
    from google.genai import types

    return types.GenerateContentConfig(
        system_instruction=_system_text(college_data, saraburi_data, lang),
        max_output_tokens=AI_MAX_TOKENS,
        temperature=0.2,
        # ปิดโหมดคิดก่อนตอบ — ไม่งั้นมันกิน token จนคำตอบโดนตัด
        thinking_config=types.ThinkingConfig(thinking_budget=0),
    )


def is_busy_error(e: Exception) -> bool:
    msg = str(e)
    return any(s in msg for s in ("UNAVAILABLE", "503", "DEADLINE_EXCEEDED", "504")) or "overloaded" in msg.lower()


def _model_not_for_key(e: Exception) -> bool:
    # เช่น key ใหม่ใช้ gemini-2.5-flash ไม่ได้แล้ว (404 NOT_FOUND)
    return "NOT_FOUND" in str(e) or "404" in str(e)


def _keys_in_order():
    """ไล่ key เริ่มจากตัวที่ใช้อยู่ วนครบทุกตัว 1 รอบ: คืน (index, key)"""
    keys = GEMINI_API_KEYS or [""]
    for i in range(len(keys)):
        idx = (_gemini_idx + i) % len(keys)
        yield idx, keys[idx]


def _try_gemini(call, models=None):
    """ลองถาม Gemini แบบไม่ยอมแพ้ง่าย ๆ:
    - โควตา key หมด / key ใช้โมเดลนี้ไม่ได้ → ลอง key ถัดไป
    - โมเดลล่มหรือคนใช้เยอะ (ทุก key เจอเหมือนกัน) → ข้ามไปโมเดลสำรอง
    call(client, model, idx) ต้อง yield ข้อความ; ถ้าตอบไปแล้วบางส่วนแล้วพัง จะส่ง error ตามจริง"""
    errors = []
    for model in models or [GEMINI_MODEL, *GEMINI_FALLBACK_MODELS]:
        for idx, key in _keys_in_order():
            started = False
            try:
                for piece in call(_gemini_client(key), model, idx):
                    started = True
                    yield piece
                return
            except Exception as e:
                if started:
                    raise
                errors.append(e)
                if is_busy_error(e):
                    break          # โมเดลนี้ล่มทั้งระบบ → โมเดลถัดไป
                if not (is_quota_error(e) or _model_not_for_key(e)):
                    raise
    # ล้มหมดทุกทาง: ถ้ามีเรื่องโควตาให้แจ้งโควตา ไม่งั้นแจ้ง error ล่าสุด
    raise next((e for e in errors if is_quota_error(e)), errors[-1])


def _ask_gemini(question: str, college_data: dict, saraburi_data: dict, lang: str = "th") -> str:
    config = _gemini_config(college_data, saraburi_data, lang)

    def call(client, model, idx):
        global _gemini_idx
        response = client.models.generate_content(model=model, contents=question, config=config)
        _gemini_idx = idx
        yield (response.text or "").strip()

    return "".join(_try_gemini(call))


def _stream_gemini(question: str, college_data: dict, saraburi_data: dict, lang: str = "th"):
    config = _gemini_config(college_data, saraburi_data, lang)

    def call(client, model, idx):
        global _gemini_idx
        for chunk in client.models.generate_content_stream(model=model, contents=question, config=config):
            if chunk.text:
                _gemini_idx = idx
                yield chunk.text
        _gemini_idx = idx

    yield from _try_gemini(call)


# ---- เสียงพูด: Gemini TTS ----
# ส่งเฉพาะข้อความที่จะพูด — ห้ามใส่คำสั่งนำหน้า (เช่น "พูดด้วยน้ำเสียง…") เพราะโมเดลจะอ่านคำสั่งออกเสียงด้วย
# ความร่าเริงมาจากตัวเสียง (GEMINI_TTS_VOICE) อยู่แล้ว
TTS_SAMPLE_RATE = 24000   # เสียงที่ได้: PCM 16-bit โมโน 24kHz


def _tts_config():
    from google.genai import types
    return types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=GEMINI_TTS_VOICE))),
    )


def speak_pcm_stream(text: str, lang: str = "th"):
    """ข้อความ → เสียง PCM ทยอยส่งเป็นท่อน ๆ (ได้ท่อนแรกเร็ว เริ่มเล่นได้ก่อนสร้างเสร็จทั้งประโยค)"""
    config = _tts_config()

    def call(client, model, idx):
        for chunk in client.models.generate_content_stream(model=model, contents=text, config=config):
            try:
                data = chunk.candidates[0].content.parts[0].inline_data.data
            except (AttributeError, IndexError, TypeError):
                data = None
            if data:
                yield data

    yield from _try_gemini(call, models=GEMINI_TTS_MODELS)


def pcm_to_wav(pcm: bytes) -> bytes:
    import io
    import wave
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(TTS_SAMPLE_RATE)
        w.writeframes(pcm)
    return buf.getvalue()


def speak_wav(text: str, lang: str = "th") -> bytes:
    return pcm_to_wav(b"".join(speak_pcm_stream(text, lang)))


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
