"""หลาย Gemini key: โควตาหมดแล้วสลับไป key ถัดไปเอง"""
import pytest

import ai
import config


class FakeModels:
    def __init__(self, key, log, quota_keys):
        self.key, self.log, self.quota_keys = key, log, quota_keys

    def _check(self):
        self.log.append(self.key)
        if self.key in self.quota_keys:
            raise RuntimeError("429 RESOURCE_EXHAUSTED quota exceeded")

    def generate_content(self, **kw):
        self._check()
        return type("R", (), {"text": f"ตอบจาก {self.key}"})()

    def generate_content_stream(self, **kw):
        self._check()
        yield type("C", (), {"text": f"ตอบจาก {self.key}"})()


@pytest.fixture
def fake(monkeypatch):
    log, quota = [], set()
    monkeypatch.setattr(ai, "GEMINI_API_KEYS", ["k1", "k2", "k3"])
    monkeypatch.setattr(ai, "_gemini_idx", 0)
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
