"""
เก็บสถิติการใช้หุ่นลงไฟล์ SQLite (มากับ Python ไม่ต้องลงอะไรเพิ่ม)
- คำถามทุกข้อที่มีคนถาม (ไว้ดูว่าคนสนใจเรื่องอะไร)
- ดาว 1–5 ที่คนให้หลังได้คำตอบ (ข้อที่ได้ดาวน้อย = ข้อมูลที่ควรเติม)
ไม่เก็บข้อมูลส่วนตัวของคนถาม เก็บแค่ข้อความคำถาม ภาษา และเวลา
"""
import sqlite3
import threading
from datetime import datetime
from pathlib import Path

MAX_QUESTION_CHARS = 500

_SCHEMA = """
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY, ts TEXT NOT NULL, question TEXT NOT NULL, lang TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS ratings (
    id INTEGER PRIMARY KEY, ts TEXT NOT NULL, stars INTEGER NOT NULL, question TEXT NOT NULL, lang TEXT NOT NULL
);
"""


def _clean(q) -> str:
    return " ".join(str(q or "").split())[:MAX_QUESTION_CHARS]


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class Stats:
    def __init__(self, path):
        self.path = Path(path)
        self._lock = threading.Lock()   # Flask เปิดหลายเธรด — เขียนทีละคน
        self._conn = sqlite3.connect(str(self.path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def _db(self):
        return self._conn

    def log_question(self, question, lang="th"):
        q = _clean(question)
        if not q:
            return
        with self._lock:
            self._conn.execute("INSERT INTO questions(ts, question, lang) VALUES (?, ?, ?)", (_now(), q, lang))
            self._conn.commit()

    def add_rating(self, stars, question, lang="th"):
        if type(stars) is not int or not 1 <= stars <= 5:
            raise ValueError("stars ต้องเป็นจำนวนเต็ม 1–5")
        with self._lock:
            self._conn.execute("INSERT INTO ratings(ts, stars, question, lang) VALUES (?, ?, ?, ?)",
                               (_now(), stars, _clean(question), lang))
            self._conn.commit()

    def summary(self, now=None):
        today = (now or datetime.now()).strftime("%Y-%m-%d")
        one = lambda sql, *a: self._conn.execute(sql, a).fetchone()[0]   # noqa: E731
        with self._lock:
            dist = {n: 0 for n in range(1, 6)}
            for row in self._conn.execute("SELECT stars, COUNT(*) c FROM ratings GROUP BY stars"):
                dist[row["stars"]] = row["c"]
            avg = one("SELECT AVG(stars) FROM ratings")
            top = [{"question": r["question"], "count": r["c"]} for r in self._conn.execute(
                "SELECT question, COUNT(*) c FROM questions GROUP BY question ORDER BY c DESC, MAX(id) DESC LIMIT 10")]
            low = [{"question": r["question"], "stars": r["stars"], "ts": r["ts"]} for r in self._conn.execute(
                "SELECT question, stars, ts FROM ratings WHERE stars <= 2 ORDER BY id DESC LIMIT 20")]
            return {
                "questions_total": one("SELECT COUNT(*) FROM questions"),
                "questions_today": one("SELECT COUNT(*) FROM questions WHERE ts LIKE ?", today + "%"),
                "ratings_total": sum(dist.values()),
                "ratings_today": one("SELECT COUNT(*) FROM ratings WHERE ts LIKE ?", today + "%"),
                "average": round(avg, 2) if avg is not None else None,
                "distribution": dist,
                "top": top,
                "low": low,
            }
