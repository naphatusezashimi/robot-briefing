"""
จำคำตอบของคำถามที่เคยตอบแล้ว — คำถามยอดนิยมบนจอถูกกดซ้ำบ่อย ตอบจากที่จำไว้ได้ทันที ไม่ต้องรอ AI และไม่กินโควตา

- คำถามที่ต่างกันแค่ช่องว่าง/เครื่องหมาย/คำลงท้าย (ครับ ค่ะ คะ นะ) นับเป็นคำถามเดียวกัน
- แก้ไฟล์ข้อมูล (college_data.json, sar_2568.md, saraburi_data.json) เมื่อไหร่ คำตอบที่จำไว้ใช้ไม่ได้ทันที
- จำไว้ในหน่วยความจำ ปิดเซิร์ฟเวอร์แล้วล้างเอง
"""
import os
import re
import threading
import time

_TAIL = re.compile(r"(ครับ|คับ|ค่ะ|คะ|ค่า|จ้า|นะ|หน่อย)+$")


def normalize(question: str) -> str:
    q = re.sub(r"[\s?!.,'\"“”‘’()]+", "", (question or "").lower())
    return _TAIL.sub("", q)


class AnswerCache:
    def __init__(self, ttl_seconds: float, data_files=(), max_items: int = 300):
        self.ttl = ttl_seconds
        self.files = list(data_files)
        self.max_items = max_items
        self._items = {}                      # key -> (เวลาที่จำ, คำตอบ)
        self._lock = threading.Lock()

    def _version(self) -> tuple:
        out = []
        for f in self.files:
            try:
                out.append(os.path.getmtime(f))
            except OSError:
                out.append(0)
        return tuple(out)

    def _key(self, question: str, lang: str):
        return (lang, normalize(question), self._version())

    def get(self, question: str, lang: str):
        if self.ttl <= 0:
            return None
        key = self._key(question, lang)
        with self._lock:
            hit = self._items.get(key)
            if not hit:
                return None
            if time.time() - hit[0] > self.ttl:
                del self._items[key]
                return None
            return hit[1]

    def put(self, question: str, lang: str, answer: str) -> None:
        if self.ttl <= 0 or not normalize(question) or not (answer or "").strip():
            return
        with self._lock:
            if len(self._items) >= self.max_items:
                oldest = min(self._items, key=lambda k: self._items[k][0])
                del self._items[oldest]
            self._items[self._key(question, lang)] = (time.time(), answer)

    def clear(self) -> None:
        with self._lock:
            self._items.clear()


def replay_pieces(answer: str, size: int = 40):
    """แบ่งคำตอบที่จำไว้เป็นท่อน ๆ ให้จอพิมพ์ตามแบบเดียวกับตอนตอบสด"""
    return [answer[i:i + size] for i in range(0, len(answer), size)]
