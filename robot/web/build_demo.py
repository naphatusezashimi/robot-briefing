"""
สร้างเดโมหน้าจอแบบหน้าเว็บนิ่ง ไว้เปิดบน GitHub Pages (ไม่มีเซิร์ฟเวอร์ ไม่มี AI ไม่มี API key)
รัน:  & $py web/build_demo.py <โฟลเดอร์ปลายทาง>
ได้ index.html (= จอเนื้อหา) + demo.js (แทน fetch) + menu.json + static/ ที่ใช้ path แบบ relative
"""
import json
import shutil
import sys
from pathlib import Path

from places import menu_tree

WEB_DIR = Path(__file__).resolve().parent
STATIC = WEB_DIR / "static"
SARABURI_DATA = WEB_DIR.parent / "saraburi_data.json"


def _relative(text: str) -> str:
    # GitHub Pages เปิดใต้ /<ชื่อ repo>/ — path /static/... ต้องเป็น static/...
    for q in ('"', "'", "`", "("):
        text = text.replace(q + "/static/", q + "static/")
    return text


def build(out: Path) -> None:
    out = Path(out)
    (out / "static").mkdir(parents=True, exist_ok=True)
    for f in ("logo.jpg", "map.jpg"):
        shutil.copy2(STATIC / f, out / "static" / f)
    shutil.copytree(STATIC / "places", out / "static" / "places", dirs_exist_ok=True)
    (out / "static" / "screen.js").write_text(_relative((STATIC / "screen.js").read_text(encoding="utf-8")), encoding="utf-8")

    html = _relative((STATIC / "screen.html").read_text(encoding="utf-8"))
    html = html.replace('<script src="static/screen.js"></script>',
                        '<script src="demo.js"></script>\n<script src="static/screen.js"></script>')
    (out / "index.html").write_text(html, encoding="utf-8")
    shutil.copy2(WEB_DIR / "demo" / "demo.js", out / "demo.js")

    data = json.loads(SARABURI_DATA.read_text(encoding="utf-8"))
    menu = _relative(json.dumps(menu_tree(data), ensure_ascii=False))
    (out / "menu.json").write_text(menu, encoding="utf-8")
    (out / ".nojekyll").write_text("", encoding="utf-8")   # ให้ Pages เสิร์ฟไฟล์ตรง ๆ ไม่ผ่าน Jekyll


if __name__ == "__main__":
    build(Path(sys.argv[1] if len(sys.argv) > 1 else "site"))
    print("built demo")
