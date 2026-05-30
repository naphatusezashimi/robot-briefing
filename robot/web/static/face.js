// จอใบหน้า: ดึงสถานะจากเซิร์ฟเวอร์มาแสดงอารมณ์ (อ่านอย่างเดียว ไม่ยุ่งเสียง/สมอง)
const LABELS = {
  idle: "พร้อมรับคำถาม", listening: "กำลังฟัง…", thinking: "กำลังคิด…",
  answering: "กำลังตอบ", error: "ขออภัย เกิดข้อผิดพลาด",
};
const txt = document.querySelector(".status-text");
let current = null;

function apply(state) {
  if (state === current) return;
  current = state;
  document.body.className = "page-face state-" + state;
  if (txt) txt.textContent = LABELS[state] || state;
}

async function poll() {
  try {
    const r = await fetch("/state");
    const d = await r.json();
    if (d && d.state) apply(d.state);
  } catch (e) {
    /* เซิร์ฟเวอร์ยังไม่พร้อม ค่อยลองใหม่รอบหน้า */
  }
}

apply("idle");
setInterval(poll, 250);
