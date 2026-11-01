"""
เทสต์ที่เก็บสถิติ (คำถาม + ดาว) — ใช้ไฟล์ SQLite ชั่วคราว
รันจากโฟลเดอร์ robot/:  python -m pytest web/test_stats.py -v
"""
from datetime import datetime

import pytest

from stats import Stats


@pytest.fixture
def st(tmp_path):
    return Stats(tmp_path / "stats.db")


def test_empty_summary(st):
    s = st.summary()
    assert s["questions_total"] == 0
    assert s["ratings_total"] == 0
    assert s["average"] is None
    assert s["distribution"] == {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}


def test_rating_summary(st):
    for n in (5, 5, 4, 1):
        st.add_rating(n, "สาขาอะไรบ้าง", "th")
    s = st.summary()
    assert s["ratings_total"] == 4
    assert s["average"] == 3.75
    assert s["distribution"] == {1: 1, 2: 0, 3: 0, 4: 1, 5: 2}


def test_rating_must_be_1_to_5(st):
    for bad in (0, 6, -1, "5", None, 2.5):
        with pytest.raises(ValueError):
            st.add_rating(bad, "q", "th")


def test_low_ratings_listed_newest_first(st):
    st.add_rating(1, "หอพักมีไหม", "th")
    st.add_rating(5, "ดีมาก", "th")
    st.add_rating(2, "ค่าเทอมเท่าไหร่", "th")
    low = [r["question"] for r in st.summary()["low"]]
    assert low == ["ค่าเทอมเท่าไหร่", "หอพักมีไหม"]


def test_top_questions_counted(st):
    for q in ("สาขาอะไรบ้าง", "สาขาอะไรบ้าง", "ติดต่อยังไง", " สาขาอะไรบ้าง "):
        st.log_question(q, "th")
    s = st.summary()
    assert s["questions_total"] == 4
    assert s["top"][0] == {"question": "สาขาอะไรบ้าง", "count": 3}


def test_today_counts(st):
    st.log_question("วันนี้", "th")
    st.add_rating(4, "วันนี้", "th")
    st._db().execute("INSERT INTO questions(ts, question, lang) VALUES ('2020-01-01 10:00:00', 'เก่า', 'th')")
    s = st.summary(now=datetime.now())
    assert s["questions_total"] == 2
    assert s["questions_today"] == 1
    assert s["ratings_today"] == 1


def test_long_question_trimmed(st):
    st.log_question("ก" * 5000, "th")
    assert len(st.summary()["top"][0]["question"]) <= 500
