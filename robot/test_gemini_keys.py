"""หลาย Gemini key: โควตาหมดแล้วสลับไป key ถัดไปเอง"""
import pytest

import ai
import config

BUSY, NOT_FOUND = set(), set()


class FakeModels:
    def __init__(self, key, log, quota_keys):
        self.key, self.log, self.quota_keys = key, log, quota_keys

    def _check(self, model):
        self.log.append(self.key)
        if self.key in self.quota_keys:
            raise RuntimeError("429 RESOURCE_EXHAUSTED quota exceeded")
        if model in BUSY:
            raise RuntimeError("503 UNAVAILABLE high demand")
        if (self.key, model) in NOT_FOUND:
            raise RuntimeError("404 NOT_FOUND model not available")

    def generate_content(self, model, **kw):
        self._check(model)
        return type("R", (), {"text": f"ตอบจาก {self.key}"})()

    def generate_content_stream(self, model, **kw):
        self._check(model)
        yield type("C", (), {"text": f"ตอบจาก {self.key}"})()


@pytest.fixture
def fake(monkeypatch):
    log, quota = [], set()
    monkeypatch.setattr(ai, "GEMINI_API_KEYS", ["k1", "k2", "k3"])
    monkeypatch.setattr(ai, "_gemini_idx", 0)
    monkeypatch.setattr(ai, "GEMINI_MODEL", "main")
    monkeypatch.setattr(ai, "_skip_until", {})
    monkeypatch.setattr(ai, "GEMINI_FALLBACK_MODELS", ["backup"])
    BUSY.clear(); NOT_FOUND.clear()
    monkeypatch.setattr(ai, "_gemini_config", lambda *a: None)
    monkeypatch.setattr(ai, "_gemini_client", lambda key: type("Cl", (), {"models": FakeModels(key, log, quota)})())
    return log, quota


def test_key_list_merges_dedupes_and_skips_placeholder():
    assert config._key_list(" a , b,a", "c", "AIzaxxxxxxxx", "") == ["a", "b", "c"]


def test_uses_first_key_when_ok(fake):
    log, _ = fake
    assert ai._ask_gemini("q", {}, {}) == "ตอบจาก k1"
    assert log == ["k1"]


def test_switches_key_on_quota_and_remembers(fake):
    log, quota = fake
    quota.add("k1")
    assert ai._ask_gemini("q", {}, {}) == "ตอบจาก k2"
    assert ai._gemini_idx == 1
    log.clear()
    ai._ask_gemini("q", {}, {})
    assert log == ["k2"]   # ครั้งต่อไปเริ่มที่ key ที่ใช้ได้เลย


def test_stream_switches_key_on_quota(fake):
    _, quota = fake
    quota.update({"k1", "k2"})
    assert list(ai._stream_gemini("q", {}, {})) == ["ตอบจาก k3"]


def test_all_keys_out_raises_quota_error(fake):
    _, quota = fake
    quota.update({"k1", "k2", "k3"})
    with pytest.raises(RuntimeError, match="RESOURCE_EXHAUSTED"):
        ai._ask_gemini("q", {}, {})


def test_other_errors_do_not_switch_key(fake, monkeypatch):
    def boom(key):
        raise ValueError("bad request")
    monkeypatch.setattr(ai, "_gemini_client", boom)
    with pytest.raises(ValueError):
        ai._ask_gemini("q", {}, {})


def test_busy_model_falls_back_to_backup_model(fake):
    log, _ = fake
    BUSY.add("main")
    assert ai._ask_gemini("q", {}, {}) == "ตอบจาก k1"
    assert log == ["k1", "k1"]   # ลอง main ครั้งเดียวแล้วข้ามไป backup ทันที (ไม่ไล่ทุก key)


def test_model_not_for_key_tries_next_key(fake):
    _, _ = fake
    NOT_FOUND.add(("k1", "main"))
    assert list(ai._stream_gemini("q", {}, {})) == ["ตอบจาก k2"]


def test_exhausted_key_is_skipped_next_time(fake, monkeypatch):
    log, quota = fake
    monkeypatch.setattr(ai, "_skip_until", {})
    quota.add("k1")
    ai._ask_gemini("q", {}, {})
    monkeypatch.setattr(ai, "_gemini_idx", 0)   # แม้จะเริ่มที่ k1 อีก
    log.clear()
    ai._ask_gemini("q", {}, {})
    assert log == ["k2"]                        # ข้าม k1 ที่เพิ่งโควตาหมดไปเลย


def test_all_keys_cooling_down_raises_quota(fake, monkeypatch):
    import time
    monkeypatch.setattr(ai, "_skip_until", {(m, k): time.time() + 60 for m in ("main", "backup") for k in ("k1", "k2", "k3")})
    with pytest.raises(RuntimeError, match="RESOURCE_EXHAUSTED"):
        ai._ask_gemini("q", {}, {})
