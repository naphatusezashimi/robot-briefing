"""
เทสต์ตัวสร้างเดโมหน้าจอสำหรับ GitHub Pages (หน้าเว็บนิ่ง ไม่มีเซิร์ฟเวอร์/AI)
รันจากโฟลเดอร์ robot/:  & $py -m pytest web/test_demo.py -v
"""
import json
import re

from build_demo import build


def test_demo_has_all_files(tmp_path):
    build(tmp_path)
    for f in ("index.html", "demo.js", "menu.json", ".nojekyll",
              "static/screen.js", "static/logo.jpg", "static/map.jpg", "static/places/CREDITS.md"):
        assert (tmp_path / f).is_file(), f


def test_demo_uses_relative_paths(tmp_path):
    # GitHub Pages เปิดที่ /robot-briefing/ — path ที่ขึ้นต้นด้วย /static/ จะหาไฟล์ไม่เจอ
    build(tmp_path)
    for f in ("index.html", "static/screen.js", "menu.json"):
        assert not re.search(r"[\"'`(]/static/", (tmp_path / f).read_text(encoding="utf-8")), f


def test_demo_shim_loads_before_screen_js(tmp_path):
    build(tmp_path)
    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert html.index('src="demo.js"') < html.index('src="static/screen.js"')


def test_demo_menu_photos_exist(tmp_path):
    build(tmp_path)
    menu = json.loads((tmp_path / "menu.json").read_text(encoding="utf-8"))
    photos = [it["photo"] for sec in menu.values() for c in sec["categories"] for it in c["items"] if it["photo"]]
    assert photos
    for p in photos:
        assert p.startswith("static/places/") and (tmp_path / p).is_file(), p


def test_demo_never_contains_api_key(tmp_path):
    build(tmp_path)
    for p in tmp_path.rglob("*"):
        if p.is_file() and p.suffix in (".html", ".js", ".json", ".md"):
            text = p.read_text(encoding="utf-8")
            assert "GEMINI_API_KEY" not in text and not re.search(r"AIza[0-9A-Za-z_-]{20,}", text), p.name
