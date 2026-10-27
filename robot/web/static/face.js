// จอใบหน้า: ดึงสถานะจากเซิร์ฟเวอร์มาแสดงอารมณ์ (อ่านอย่างเดียว ไม่ยุ่งเสียง/สมอง)
// ภาษาของป้ายสถานะตามที่จอเนื้อหาเลือก (เซิร์ฟเวอร์ส่ง lang มากับ /state)
const LABELS = {
  th: {
    idle: "พร้อมรับคำถาม", listening: "กำลังฟัง…", thinking: "กำลังคิด…",
    answering: "กำลังตอบ", error: "ขออภัย เกิดข้อผิดพลาด",
  },
  en: {
    idle: "Ready for your question", listening: "Listening…", thinking: "Thinking…",
    answering: "Answering", error: "Sorry, something went wrong",
  },
};
const txt = document.querySelector(".status-text");
let current = null, currentLang = null;

function apply(state, lang) {
  lang = LABELS[lang] ? lang : "th";
  if (state === current && lang === currentLang) return;
  current = state; currentLang = lang;
  document.body.className = "page-face state-" + state;
  document.documentElement.lang = lang;
  if (txt) txt.textContent = LABELS[lang][state] || state;
}

async function poll() {
  try {
    const r = await fetch("/state");
    const d = await r.json();
    if (d && d.state) apply(d.state, d.lang);
  } catch (e) {
    /* เซิร์ฟเวอร์ยังไม่พร้อม ค่อยลองใหม่รอบหน้า */
  }
}

apply("idle", "th");
setInterval(poll, 250);
