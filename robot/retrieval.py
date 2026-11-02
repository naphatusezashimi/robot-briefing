"""
เลือกเฉพาะส่วนของข้อมูล SAR ที่เกี่ยวกับคำถาม (RAG แบบง่าย ไม่ต้องใช้ฐานข้อมูลเวกเตอร์)

ทำไม: ข้อมูล SAR + คำถาม-คำตอบ 266 ข้อ ยาวราว 64,000 ตัวอักษร ถ้าส่งให้ AI ทุกครั้ง AI อ่านนาน ตอบช้า
และกินโควตา — เลยหั่นเป็นชิ้น (ทีละหัวข้อย่อย / ทีละคำถาม-คำตอบ) แล้วส่งเฉพาะชิ้นที่ตรงกับคำถาม

วิธีให้คะแนน: ภาษาไทยไม่เว้นวรรคระหว่างคำ เลยเทียบกันเป็น "ตัวอักษรติดกัน 3 ตัว" (trigram)
ชิ้นที่มี trigram ตรงกับคำถามเยอะ และเป็นคำที่ไม่ได้มีอยู่ทุกชิ้น (เช่น "วิทยาลัย") จะได้คะแนนสูง
"""
import math
import re
from functools import lru_cache

# ชิ้นที่แนบทุกครั้ง: ข้อมูลภาพรวม ใช้ตอบคำถามกว้าง ๆ ได้ (เช่น "แนะนำวิทยาลัยหน่อย")
ALWAYS = ("ข้อมูลสำคัญฉบับย่อ (Fact Sheet)",)
# คำถามที่ไม่ตรงกับชิ้นไหนเลย (เช่น ถามเป็นภาษาอังกฤษ) → แนบหัวข้อหลักเหล่านี้แทน
FALLBACK = ("Key Messages สำหรับประชาสัมพันธ์", "หลักสูตรและสาขาที่เปิดสอน (ปีการศึกษา 2568)")

_QA = re.compile(r"^\d{1,3}\.\s")
# คำถาม/คำลงท้ายที่มีแทบทุกคำถาม ตัดออกก่อนเทียบ ไม่งั้น "อะไรบ้าง" จะไปตรงกับคำถาม-คำตอบทุกข้อ
_FILLER = re.compile(
    "อะไรบ้าง|อะไร|บ้าง|หรือไม่|หรือเปล่า|ไหม|มั้ย|เท่าไหร่|เท่าไร|เท่าใด|อย่างไร|ยังไง|"
    "เมื่อไหร่|เมื่อใด|ที่ไหน|ตรงไหน|ไหน|ใคร|กี่|ครับ|คะ|ค่ะ|นะ|หน่อย|ช่วย|อยากรู้|อยากทราบ|บอก"
)
_THAI = re.compile(r"[฀-๿]")


def _grams(text: str) -> set:
    s = re.sub(r"[\s\W_]+", "", text.lower())
    return {s[i:i + 3] for i in range(len(s) - 2)}


def split_chunks(md: str) -> list:
    """หั่นข้อความ markdown เป็นชิ้น: หัวข้อย่อยละชิ้น, ในคลังคำถาม-คำตอบ ข้อละชิ้น
    คืน [{"title": หัวข้อ, "text": เนื้อหา (มีหัวข้อนำ)}] เรียงตามลำดับในเอกสาร"""
    chunks, cur = [], None
    h3 = h4 = ""
    in_qa = False

    def close():
        if cur and cur["lines"]:
            body = "\n".join(cur["lines"]).strip()
            if body:
                chunks.append({"title": cur["title"], "text": body})

    for line in md.splitlines():
        if line.startswith("# "):
            continue                                   # หัวเรื่องของไฟล์
        if line.startswith("### "):
            close()
            h3, h4 = line[4:].strip(), ""
            in_qa = h3.startswith("คลังคำถาม-คำตอบ")
            cur = {"title": h3, "lines": [line]}
            continue
        if line.startswith("#### "):
            close()
            h4 = line[5:].strip()
            cur = {"title": f"{h3} / {h4}", "lines": [f"### {h3}", line]}
            continue
        if in_qa and _QA.match(line):
            close()
            cur = {"title": f"{h3} / {h4}", "lines": [f"({h4})", line]}
            continue
        if cur is None:
            cur = {"title": "", "lines": []}
        cur["lines"].append(line)
    close()
    return chunks


@lru_cache(maxsize=4)
def _index(md: str):
    chunks = split_chunks(md)
    grams = [_grams(c["text"]) for c in chunks]
    df = {}
    for g in grams:
        for t in g:
            df[t] = df.get(t, 0) + 1
    n = len(chunks)
    idf = {t: math.log((n + 1) / (d + 0.5)) for t, d in df.items()}
    return chunks, grams, idf


def select(md: str, question: str, budget: int = 9000) -> str:
    """คืนเฉพาะชิ้นที่เกี่ยวกับคำถาม รวมแล้วไม่เกิน budget ตัวอักษร (เรียงตามลำดับในเอกสาร)"""
    if not md.strip():
        return ""
    chunks, grams, idf = _index(md)
    q = _grams(_FILLER.sub(" ", question))
    scored = []
    for i, g in enumerate(grams):
        hit = q & g
        if not hit:
            continue
        score = sum(idf[t] for t in hit) / (len(g) ** 0.25)   # ชิ้นยาวได้เปรียบนิดหน่อย ไม่ให้ชนะเพราะยาวอย่างเดียว
        scored.append((score, i))
    scored.sort(reverse=True)

    picked, used = set(), 0

    def take(i):
        nonlocal used
        if i in picked or used + len(chunks[i]["text"]) > budget:
            return
        picked.add(i)
        used += len(chunks[i]["text"])

    for i, c in enumerate(chunks):
        if c["title"] in ALWAYS:
            take(i)
    best = scored[0][0] if scored else 0
    if best < 3 or not _THAI.search(question):     # ไม่ตรงอะไรเลย / ถามเป็นภาษาอังกฤษ → แนบหัวข้อหลักแทน
        for i, c in enumerate(chunks):
            if c["title"].split(" / ")[0] in FALLBACK:
                take(i)
    for score, i in scored:
        if score < best * 0.25:                     # ตัดชิ้นที่ตรงแค่นิดเดียวทิ้ง
            break
        take(i)
    return "\n\n".join(chunks[i]["text"] for i in sorted(picked))
