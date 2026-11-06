// จอเนื้อหา: คุมไมค์ (STT) + พิมพ์ → เรียก /ask → แสดงคำตอบ + พูด (TTS) + แจ้ง /state
// รองรับ 2 ภาษา (th/en) และโหมดมืด/สว่าง — ภาษาที่เลือกส่งไปเซิร์ฟเวอร์ด้วย ให้จอใบหน้าและ AI ใช้ตาม

// ---- ข้อความทุกภาษา ----
const T = {
  th: {
    brand: "ผู้ช่วยท่าหลวงฯ", college: "วิทยาลัยเทคนิคท่าหลวงซิเมนต์ไทยอนุสรณ์",
    newChat: "เริ่มคุยใหม่", newShort: "คุยใหม่",
    popular: "คำถามยอดนิยม", popularHint: "คำถามยอดนิยม — แตะถามได้เลย",
    phone: "โทร 0-3628-1295", phoneNote: "ข้อมูลไม่ครบ ติดต่อเจ้าหน้าที่ได้เลยครับ",
    hello: "อยากรู้อะไรเกี่ยวกับ<em>ท่าหลวงฯ</em>ดี?",
    sub: "แตะไมค์เพื่อพูด หรือพิมพ์ถามได้เลยครับ 😊", subNoMic: "พิมพ์คำถามด้านล่างได้เลยครับ 😊",
    placeholder: "ถามอะไรก็ได้เกี่ยวกับวิทยาลัย…", listening: "กำลังฟัง… พูดได้เลยครับ (แตะไมค์เพื่อหยุด)",
    send: "ส่ง", mic: "กดเพื่อพูด", replay: "ฟังอีกครั้ง", theme: "สลับโหมดมืด/สว่าง",
    cMap: "แผนผังวิทยาลัย", cPrograms: "สาขาที่เปิดสอน", cApply: "คุณสมบัติผู้สมัคร",
    cContact: "ช่องทางติดต่อ", cTrips: "ที่เที่ยวสระบุรี", cSouvenir: "ของฝากสระบุรี",
    cTour: "แนะนำสถานที่วิทยาลัย", openLink: "แตะเพื่อเปิด", closeTour: "ปิด กลับหน้าถามตอบ",
    hint: "หุ่นยนต์ตอบจากข้อมูลของวิทยาลัย ถ้าไม่แน่ใจ สอบถามเจ้าหน้าที่ได้นะครับ",
    spoken: "🎤 พูด", mapAlt: "แผนผังวิทยาลัย",
    mapMsg: "นี่คือแผนผังวิทยาลัยครับ 🗺️ แตะที่รูปเพื่อขยายดูได้เลย",
    sysErr: "ขออภัยครับ ระบบขัดข้อง ลองใหม่อีกครั้งนะครับ",
    noHear: "ไม่ได้ยินครับ ลองพูดใหม่ หรือพิมพ์คำถามดูนะครับ 🙏",
    menuPick: "เลือกหมวดได้เลยครับ 👇", menuItems: "แตะดูรายละเอียดได้เลยครับ 👇",
    back: "ย้อนกลับ", home: "หน้าแรก", districtPre: "อ.",
    greet: "สวัสดีครับ ผมชื่อทีแอลบอท มีอะไรให้ช่วยไหมครับ",
    rateAsk: "คำตอบนี้ช่วยได้ไหมครับ?", rateThanks: "ขอบคุณที่ให้คะแนนครับ 🙏", starUnit: "ดาว",
    attractSub: "สวัสดีครับ ผมชื่อทีแอลบอท ผู้ช่วยตอบคำถามของวิทยาลัย", attractTap: "👆 แตะจอเพื่อถามหุ่นยนต์",
    announceTag: "ประกาศ",
    scanned: "📷 สแกน QR", qrUnknown: "ยังไม่รู้จัก QR นี้ครับ 🙏 ลองถามด้วยเสียงหรือพิมพ์ดูนะครับ",
    stopTalk: "⏹ หยุดพูด", seeScreen: "รายละเอียดเพิ่มเติมดูบนจอได้เลยครับ",
    states: { idle: "พร้อมรับคำถาม", greeting: "สวัสดีครับ 👋", listening: "กำลังฟัง…", thinking: "กำลังคิด…", answering: "กำลังตอบ", error: "เกิดข้อผิดพลาด" },
    speech: "th-TH",
  },
  en: {
    brand: "Tha Luang Assistant", college: "Tha Luang Cement Thai Anusorn Technical College",
    newChat: "New chat", newShort: "New chat",
    popular: "Popular questions", popularHint: "Popular questions — tap to ask",
    phone: "Tel. 0-3628-1295", phoneNote: "Need more info? Our staff are happy to help.",
    hello: "What would you like to know about <em>Tha Luang</em>?",
    sub: "Tap the mic to speak, or type your question 😊", subNoMic: "Type your question below 😊",
    placeholder: "Ask anything about the college…", listening: "Listening… go ahead (tap the mic to stop)",
    send: "Send", mic: "Tap to speak", replay: "Play again", theme: "Switch dark/light mode",
    cMap: "Campus map", cPrograms: "Programs offered", cApply: "Admission requirements",
    cContact: "Contact us", cTrips: "Places to visit", cSouvenir: "Local souvenirs",
    cTour: "Campus tour (3D)", openLink: "Tap to open", closeTour: "Close",
    hint: "Answers come from the college's own information. When in doubt, please ask our staff.",
    spoken: "🎤 Spoken", mapAlt: "Campus map",
    mapMsg: "Here's the campus map 🗺️ Tap the image to zoom in.",
    sysErr: "Sorry, something went wrong. Please try again.",
    noHear: "Sorry, I didn't catch that. Try speaking again or type your question 🙏",
    menuPick: "Pick a category 👇", menuItems: "Tap one to see more 👇",
    back: "Back", home: "Home", districtPre: "",
    greet: "Hi! I'm TL-Bot. How can I help you today?",
    rateAsk: "Was this answer helpful?", rateThanks: "Thanks for rating! 🙏", starUnit: "stars",
    attractSub: "Hi! I'm TL-Bot, the college's question assistant.", attractTap: "👆 Tap the screen to ask the robot",
    announceTag: "Announcement",
    scanned: "📷 QR scan", qrUnknown: "Sorry, I don't recognise this QR code 🙏 Try asking by voice or typing.",
    stopTalk: "⏹ Stop", seeScreen: "More details are on the screen.",
    states: { idle: "Ready", greeting: "Hello! 👋", listening: "Listening…", thinking: "Thinking…", answering: "Answering", error: "Error" },
    speech: "en-US",
  },
};

const $ = (id) => document.getElementById(id);
const body = document.body, root = document.documentElement;
const chat = $("chat"), scroller = $("scroll"), composer = $("composer"), input = $("q"), mic = $("mic");
const ledText = document.querySelector(".led-text");
const store = {
  get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} },
};

let lang = T[store.get("lang")] ? store.get("lang") : "th";
let convo = 0;   // เพิ่มทุกครั้งที่กด "คุยใหม่" — คำตอบของบทสนทนาเก่าที่ยังไหลอยู่จะหยุดเอง
let state = "idle";
const t = () => T[lang];

// ---- สถานะ: อัปเดต UI ตัวเอง + แจ้งเซิร์ฟเวอร์ (ให้จอใบหน้า sync) ----
let idleSince = Date.now();   // เวลาที่มีความเคลื่อนไหวล่าสุด (แตะจอ/เปลี่ยนสถานะ) — ใช้นับเข้าโหมดรอ
function setState(s) {
  state = s; idleSince = Date.now();
  body.className = body.className.replace(/\bstate-\S+/, "state-" + s);
  if (ledText) ledText.textContent = t().states[s] || s;
  fetch("/state", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ state: s, lang }),
  }).catch(() => {});
}
// กำลังอ่านคำตอบออกเสียง (ไม่ใช่กำลังพิมพ์คำตอบ) ไม่นับว่ายุ่ง — ถามข้อใหม่/กดไมค์แล้วเสียงเก่าหยุดเอง
const busy = () => state === "thinking" || (state === "answering" && !answerTalking);

// ---- หน้าแรก ↔ หน้าคุย: ย้ายช่องถามจากกลางจอลงล่าง ----
function setView(v) {
  body.classList.toggle("v-welcome", v === "welcome");
  body.classList.toggle("v-thread", v === "thread");
  (v === "welcome" ? $("welcomeSlot") : $("dockSlot")).appendChild(composer);
}

// ---- ภาษา ----
function applyLang(l) {
  lang = l; store.set("lang", l);
  root.lang = l;
  document.querySelectorAll("[data-t]").forEach((e) => { if (t()[e.dataset.t]) e.innerHTML = t()[e.dataset.t]; });
  document.querySelectorAll("[data-ph]").forEach((e) => { e.placeholder = t()[e.dataset.ph]; });
  document.querySelectorAll("[data-title]").forEach((e) => { e.title = t()[e.dataset.title]; });
  document.querySelectorAll("#langSeg button").forEach((b) => b.classList.toggle("on", b.dataset.lang === l));
  $("themeBtn").title = t().theme;
  if (!SR) $("welcomeSub").textContent = t().subNoMic;
  if (recog) recog.lang = t().speech;
  setState(state);   // อัปเดตป้ายสถานะ + บอกเซิร์ฟเวอร์ว่าเปลี่ยนภาษา
}

// ---- โหมดมืด/สว่าง ----
$("themeBtn").addEventListener("click", () => {
  const next = root.dataset.theme === "light" ? "dark" : "light";
  root.dataset.theme = next; store.set("theme", next);
});

// ---- ข้อความ ----
function escapeHtml(s) { const d = document.createElement("div"); d.textContent = s; return d.innerHTML; }

// AI ตอบเป็น markdown (**หัวข้อ**, * รายการ) — แปลงเป็นหัวข้อ/รายการสวย ๆ แทนการโชว์ดอกจัน
// ลิงก์: [ข้อความ](https://...) → ปุ่มข้อความให้แตะ (ไม่โชว์ URL) / URL เปล่า ๆ → ปุ่ม "แตะเพื่อเปิด"
// แตะแล้วเปิดเต็มจอในหน้าหุ่นเอง (openTour(url)) ไม่ออกจากหน้าถามตอบ
const MD_LINK_RE = /\[([^\]\n]+)\]\((https?:\/\/[^\s<>"')]+)\)/g;
const BARE_URL_RE = /(^|\s)(https?:\/\/[^\s<>"')]+?)([.,]?)(?=\s|$)/g;
function linkHtml(url, label) { return '<a class="md-link" href="' + url + '" data-open-url="' + url + '">🔗 ' + label + "</a>"; }
function inlineMd(s) {
  return s
    .replace(MD_LINK_RE, (_, label, url) => linkHtml(url, label))
    .replace(BARE_URL_RE, (_, pre, url, dot) => pre + linkHtml(url, t().openLink) + dot)
    .replace(/\*\*(.+?)\*\*/g, "<b>$1</b>")
    .replace(/(^|[^*])\*(?!\s)([^*]+?)\*(?!\*)/g, "$1$2")   // *ตัวเอียง* → ข้อความธรรมดา
    .replace(/\*/g, "");
}
function formatAnswer(text) {
  let s = escapeHtml(text).replace(/\r/g, "");
  // บางทีมาเป็นบรรทัดเดียวยาว ๆ — แยกบรรทัดก่อนรายการ " * " และก่อนหัวข้อ "**...:**"
  // (ไม่แยกหัวข้อที่อยู่หลัง "* " เพราะนั่นคือชื่อในรายการ เช่น "* **น้ำตก:** ...")
  if (!s.includes("\n")) {
    s = s.replace(/\s+\*\s+(?=\S)/g, "\n* ").replace(/(?<=[^\s*])\s+(\*\*[^*\n]+?:\s*\*\*)/g, "\n$1");
  }
  let html = "", inList = false;
  for (let line of s.split("\n")) {
    line = line.trim();
    const li = line.match(/^(?:[*\-•]|\d+[.)])\s+(.*)$/);
    if (li) {
      if (!inList) { html += '<ul class="md-list">'; inList = true; }
      html += "<li>" + inlineMd(li[1]) + "</li>";
      continue;
    }
    if (inList) { html += "</ul>"; inList = false; }
    if (!line) continue;
    const h = line.match(/^#{1,6}\s+(.*)$/) || line.match(/^\*\*([^*]+?)\*\*:?$/);
    html += h ? '<div class="md-h">' + inlineMd(h[1]) + "</div>" : '<p class="md-p">' + inlineMd(line) + "</p>";
  }
  if (inList) html += "</ul>";
  return html;
}
// เวลาพูด ไม่ต้องอ่านเครื่องหมาย markdown และอีโมจิ
function plainForSpeech(text) {
  return text.replace(/[\p{Extended_Pictographic}\u{1F1E6}-\u{1F1FF}\u{1F3FB}-\u{1F3FF}\u{FE0F}\u{200D}\u{20E3}]/gu, "")
    .replace(MD_LINK_RE, "$1").replace(/https?:\/\/\S+/g, "")   // ไม่อ่าน URL ออกเสียง
    .replace(/^#{1,6}\s+/gm, "").replace(/\s\*\s+/g, " ").replace(/[*#•]/g, "").replace(/\s+/g, " ").trim();
}

// ---- เสียงอ่านแบบย่อ: จอโชว์คำตอบเต็ม แต่เสียงอ่านแค่ช่วงต้น (ไม่เกิน SPEAK_MAX_CHARS ตัวอักษร) ----
const SPEAK_MAX_CHARS = 200;   // ภาษาไทยราว 12–15 วินาที — อยากให้อ่านยาวขึ้น/สั้นลงแก้ตรงนี้
function speechSummary(text, lng) {
  const lines = text.split("\n").map((l) => l.trim()).filter(Boolean);
  const structural = (l) => /^(#{1,6}\s|[*•-]\s|\d+\.\s)/.test(l) || /^\*\*[^*]+\*\*:?[\s\p{Extended_Pictographic}️]*$/u.test(l);
  const out = []; let len = 0, cut = false, listMode = false;
  for (const line of lines) {
    const st = structural(line);
    if (out.length && st && !listMode) { cut = true; break; }    // อ่านบทนำจบแล้ว เจอหัวข้อ/รายการ → พอ
    if (!out.length && st) listMode = true;                      // คำตอบเริ่มด้วยรายการเลย → อ่านรายการต้น ๆ
    const p = plainForSpeech(line);
    if (!p) continue;
    if (out.length && len + p.length > SPEAK_MAX_CHARS) { cut = true; break; }
    out.push(p); len += p.length;
  }
  let say = out.join(" ");
  if (say.length > SPEAK_MAX_CHARS * 1.5) {                      // ย่อหน้าแรกยาวมาก → ตัดที่ช่องว่างก่อนถึงขีดจำกัด
    const sp = say.lastIndexOf(" ", SPEAK_MAX_CHARS);
    say = say.slice(0, sp > 40 ? sp : SPEAK_MAX_CHARS); cut = true;
  }
  return cut ? say + " " + T[lng].seeScreen : say;
}

const AVA = '<div class="ava"><div class="face"><i></i><i></i></div></div>';
const REPLAY_ICON = '<svg viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3A4.5 4.5 0 0 0 14 8v8a4.5 4.5 0 0 0 2.5-4zM14 3.2v2.1a7 7 0 0 1 0 13.4v2.1a9 9 0 0 0 0-17.6z"/></svg>';

function scrollDown() { requestAnimationFrame(() => { scroller.scrollTop = scroller.scrollHeight; }); }
// ตอนคำตอบกำลังไหล เลื่อนตามเฉพาะถ้าผู้ใช้ยังอยู่ท้ายแชท (ถ้าเลื่อนขึ้นไปอ่านอยู่ ไม่ดึงกลับ)
function nearBottom() { return scroller.scrollHeight - scroller.scrollTop - scroller.clientHeight < 80; }

function addMsg(role, text, opts = {}) {
  setView("thread");
  const m = document.createElement("div");
  m.className = "msg " + role;
  if (role === "user") {
    const tag = opts.qr ? t().scanned : opts.voice ? t().spoken : "";
    m.innerHTML = (tag ? '<span class="mic-tag">' + tag + "</span>" : "") + escapeHtml(text);
  } else {
    m.innerHTML = AVA + '<div class="a-body"></div>';
    renderBot(m, text, { ...opts, done: true });
  }
  chat.appendChild(m); scrollDown();
  return m;
}
// วาดเนื้อหาคำตอบ — ระหว่างไหลมีจุดกะพริบท้ายข้อความ, จบแล้วค่อยใส่รูป + ปุ่มฟังซ้ำ
function renderBot(m, text, opts = {}) {
  const box = m.querySelector(".a-body");
  box.classList.toggle("warn", !!opts.warn);
  let html = formatAnswer(text);
  if (!opts.done) {
    const caret = '<span class="caret"></span>';
    html = /<\/(p|li|div)>(<\/ul>)?$/.test(html) ? html.replace(/(<\/(?:p|li|div)>)(<\/ul>)?$/, caret + "$1$2") : html + caret;
    box.innerHTML = html;
    return;
  }
  const img = opts.image ? `<img class="map-thumb" src="${opts.image}" alt="${t().mapAlt}">` : "";
  const tools = opts.warn ? "" :
    `<div class="tools"><button type="button" class="replay" title="${t().replay}">${REPLAY_ICON}</button></div>`;
  const follow = nearBottom();
  box.innerHTML = html + img + photosHtml(opts.photos) + tools + (opts.rateQ ? rateHtml(opts.rateQ) : "");
  // รูปโหลดเสร็จทีหลัง ความสูงเพิ่ม — เลื่อนตามถ้าผู้ใช้อยู่ท้ายแชท ไม่งั้นรูปโดนตัดขอบล่าง
  if (follow) box.querySelectorAll("img").forEach((i) => i.addEventListener("load", scrollDown, { once: true }));
  const r = box.querySelector(".replay");
  if (r) {
    const sayLang = lang;
    r.addEventListener("click", () => { if (busy()) return; setState("answering"); speakAnswer(text, sayLang); });
  }
}

// ---- ให้ดาว 1–5 ใต้คำตอบจาก AI (เก็บที่เซิร์ฟเวอร์ไว้ดูหน้า /stats) ----
function rateHtml(question) {
  const stars = [5, 4, 3, 2, 1].map((n) =>   // เรียงกลับ เพราะ CSS ใช้ row-reverse
    `<button type="button" data-stars="${n}" title="${n} ${t().starUnit}" aria-label="${n} ${t().starUnit}">★</button>`).join("");
  return `<div class="rate" data-question="${escapeHtml(question).replace(/"/g, "&quot;")}" data-lang="${lang}">` +
    `<span>${t().rateAsk}</span><div class="stars">${stars}</div></div>`;
}
function sendRating(btn) {
  const row = btn.closest(".rate");
  if (!row || row.classList.contains("done")) return;
  row.classList.add("done");
  btn.classList.add("on");
  fetch("/rate", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ stars: Number(btn.dataset.stars), question: row.dataset.question, lang: row.dataset.lang }),
  }).catch(() => {});
  row.querySelector("span").outerHTML = `<span class="thanks">${t().rateThanks}</span>`;
}

// รูปสถานที่ใต้คำตอบ: รูปเดียวโชว์ใหญ่, หลายรูปเรียงเป็นแถวรูปเล็ก (แตะขยายได้)
function photosHtml(photos) {
  if (!photos || !photos.length) return "";
  const fig = (p) => `<figure><img class="place-photo" src="${p.src}" alt="${escapeHtml(p.name)}">` +
    `<figcaption>${escapeHtml(p.name)}${p.caption ? " · " + t().districtPre + escapeHtml(p.caption) : ""}</figcaption></figure>`;
  return photos.length === 1 ? `<div class="photo-one">${fig(photos[0])}</div>`
    : `<div class="photo-row">${photos.map(fig).join("")}</div>`;
}

// ---- พิมพ์คำตอบแบบค่อย ๆ ไหล: รับข้อความเข้ามาเป็นก้อน แต่โชว์ไล่ตามทีละนิดให้ลื่น ----
function typewriter(m) {
  let full = "", shown = 0, finished = false, finalOpts = null, onDone = null, raf = 0;
  function frame() {
    const follow = nearBottom();
    const backlog = full.length - shown;
    if (backlog > 0) {
      shown += Math.max(1, Math.ceil(backlog / 14));   // ค้างเยอะ = เร่ง, ค้างน้อย = ช้าลง
      renderBot(m, full.slice(0, shown));
    }
    if (follow) scroller.scrollTop = scroller.scrollHeight;
    if (finished && shown >= full.length) {
      renderBot(m, full, { ...finalOpts, done: true });
      if (follow) scrollDown();
      raf = 0; if (onDone) onDone();
      return;
    }
    raf = requestAnimationFrame(frame);
  }
  return {
    push(piece) { full += piece; if (!raf) raf = requestAnimationFrame(frame); },
    finish(opts, cb) { finished = true; finalOpts = opts; onDone = cb; if (!raf) raf = requestAnimationFrame(frame); },
    get text() { return full; },
  };
}
// ---- โชว์แผนผังทันที (ไม่เรียก /ask) ----
function showMap() {
  addMsg("bot", t().mapMsg, { image: "/static/map.jpg" });
}

function typing(on) {
  let el = $("typing");
  if (on && !el) {
    el = document.createElement("div"); el.id = "typing"; el.className = "msg bot typing";
    el.innerHTML = AVA + '<div class="shimmer"><i></i><i></i><i></i></div>';
    chat.appendChild(el); scrollDown();
  } else if (!on && el) { el.remove(); }
}

// ---- พูดออกเสียง ----
// หลัก: เสียง AI จากเซิร์ฟเวอร์ (/tts — Gemini เสียงผู้ชายเป็นธรรมชาติ)
// สำรอง: เสียงในเครื่อง (Web Speech) — ใช้เมื่อสร้างเสียงไม่ทัน / โควตาหมด / ไม่มีเน็ต
const SPEECH_RATE = 1.15;      // ความเร็วพูดของเสียงในเครื่อง (1 = ปกติ) — เสียง AI ตั้งที่ EDGE_TTS_RATE ใน config.py
const TTS_TIMEOUT_MS = 6000;   // รอเสียง AI เริ่มดังนานสุดเท่านี้ ไม่ทันก็ใช้เสียงในเครื่อง
let ttsJob = null;             // เสียงที่กำลังพูดอยู่ (มีได้ทีละอัน)

const ttsUrl = (text, lng) => "/tts?lang=" + lng + "&text=" + encodeURIComponent(text);
// ให้เซิร์ฟเวอร์สร้างเสียงเก็บไว้ล่วงหน้า (คำทักทาย/ประกาศ) ตอนพูดจริงจะได้ทันที
const warmed = new Set();
function warmTts(text, lng) {
  const url = ttsUrl(text, lng);
  if (warmed.has(url) || !window.fetch) return;
  warmed.add(url);
  fetch(url).then((r) => r.blob()).catch(() => warmed.delete(url));
}

// รายชื่อเสียงในเครื่องโหลดช้า — จำไว้ตั้งแต่โหลดเสร็จ จะได้ไม่พลาดเสียงผู้ชายตอนพูดครั้งแรก
let localVoices = [];
function loadVoices() { if ("speechSynthesis" in window) localVoices = window.speechSynthesis.getVoices(); }
loadVoices();
if ("speechSynthesis" in window) window.speechSynthesis.addEventListener("voiceschanged", loadVoices);

function speak(text, speakLang, onEnd) {
  stopSpeech();   // พูดได้ทีละอัน — อันเก่าจบ (เรียก onEnd ของมัน) ก่อนเริ่มอันใหม่
  const job = { ended: false, audio: null };
  job.finish = () => {
    if (job.ended) return;
    job.ended = true;
    if (ttsJob === job) ttsJob = null;
    if (onEnd) onEnd();
  };
  ttsJob = job;
  const local = () => {
    if (job.ended || job.local) return;   // กันเรียกซ้ำ (ถอดเสียง AI ออกแล้วอาจมี error ตามมาอีกรอบ)
    job.local = true;
    if (job.audio) { job.audio.pause(); job.audio.removeAttribute("src"); job.audio = null; }
    localSpeak(text, speakLang, job);
  };
  if (!window.Audio) { local(); return; }
  // เบราว์เซอร์เล่น MP3 ได้ตั้งแต่ท่อนแรกมาถึง ไม่ต้องรอเซิร์ฟเวอร์สร้างเสร็จทั้งประโยค
  const a = new Audio(ttsUrl(text, speakLang));
  job.audio = a;
  let started = false;
  const timer = setTimeout(() => { if (!started) local(); }, TTS_TIMEOUT_MS);
  a.addEventListener("playing", () => { started = true; clearTimeout(timer); });
  a.addEventListener("ended", () => { clearTimeout(timer); job.finish(); });
  a.addEventListener("error", () => { clearTimeout(timer); if (!started) local(); else job.finish(); });
  a.play().catch(() => { clearTimeout(timer); if (!started) local(); });   // บล็อกเสียงอัตโนมัติ → เสียงในเครื่อง
}

function localSpeak(text, speakLang, job) {
  if (!("speechSynthesis" in window)) { job.finish(); return; }
  const code = T[speakLang].speech;
  const u = new SpeechSynthesisUtterance(text);
  u.lang = code;
  const voices = (localVoices.length ? localVoices : window.speechSynthesis.getVoices())
    .filter((v) => v.lang && v.lang.toLowerCase().startsWith(code.slice(0, 2)));
  // หุ่นเป็นผู้ชาย: หาเสียงผู้ชายก่อน (Windows: Pattara / Edge: Niwat) — \bmale ไม่ติดคำว่า female
  const male = voices.find((v) => /ชาย|\bmale|\bman\b|pattara|niwat|david|guy|mark|ryan|christopher/i.test(v.name));
  if (male || voices[0]) u.voice = male || voices[0];
  u.rate = SPEECH_RATE;
  u.onend = job.finish;
  u.onerror = job.finish;
  window.speechSynthesis.speak(u);
}

// หยุดเสียงที่กำลังพูด/กำลังรอสร้าง ทันที (onEnd ของเสียงนั้นถูกเรียกตามปกติ)
function stopSpeech() {
  const job = ttsJob;
  ttsJob = null;
  if (job && job.audio) { job.audio.pause(); job.audio.removeAttribute("src"); job.audio.load(); }
  if ("speechSynthesis" in window) window.speechSynthesis.cancel();
  if (job) job.finish();
}

// อ่านคำตอบ (แบบย่อ) + โชว์ปุ่มหยุดพูด — ถามข้อใหม่/กดไมค์/กดหยุด แล้วเสียงหยุดทันที
let answerTalking = false, answerGen = 0;
function speakAnswer(text, lng) {
  const g = ++answerGen;
  answerTalking = true; body.classList.add("speaking");
  speak(speechSummary(text, lng), lng, () => {
    if (g !== answerGen) return;   // เสียงนี้ถูกเสียงใหม่แทนที่ไปแล้ว
    answerTalking = false; body.classList.remove("speaking");
    lastActive = Date.now();
    if (state === "answering") setState("idle");
  });
}
function stopAnswer() {
  if (answerTalking) stopSpeech();
}
$("stopTalk").addEventListener("click", stopAnswer);

// ---- ถาม-ตอบหลัก ----
async function ask(question, opts = {}) {
  question = (question || "").trim();
  if (!question) { setState("idle"); return; }
  stopAnswer();   // ยังอ่านคำตอบเก่าอยู่ → หยุดก่อนถามข้อใหม่
  const askLang = lang, myConvo = convo;
  const stale = () => myConvo !== convo;
  addMsg("user", question, { voice: !!opts.voice, qr: !!opts.qr });
  setState("thinking"); typing(true);
  const fail = (msg) => {
    if (stale()) return;
    typing(false);
    addMsg("bot", msg || t().sysErr, { warn: true });
    setState("error");
    setTimeout(() => setState("idle"), 2500);
  };
  try {
    const r = await fetch("/ask/stream", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, lang: askLang }),
    });
    if (!r.ok) {
      // โชว์สาเหตุจริงจากเซิร์ฟเวอร์ (เช่น ยังไม่ได้ตั้งค่า API key) จะได้แก้ถูกจุด
      const d = await r.json().catch(() => ({}));
      fail(d.error);
      return;
    }
    // อ่านคำตอบทีละบรรทัด JSON: {"t": ท่อนใหม่} … {"done": true, "image": …} หรือ {"error": …}
    const reader = r.body.getReader(), dec = new TextDecoder();
    let buf = "", tw = null, end = null;
    while (!end) {
      const { value, done } = await reader.read();
      if (stale()) { reader.cancel().catch(() => {}); return; }
      if (done) break;
      buf += dec.decode(value, { stream: true });
      let nl;
      while ((nl = buf.indexOf("\n")) >= 0) {
        const line = buf.slice(0, nl).trim(); buf = buf.slice(nl + 1);
        if (!line) continue;
        const msg = JSON.parse(line);
        if (msg.t) {
          if (!tw) {   // ท่อนแรกมาถึง: เลิกโชว์ shimmer เริ่มพิมพ์คำตอบ
            typing(false); setState("answering");
            const m = document.createElement("div");
            m.className = "msg bot"; m.innerHTML = AVA + '<div class="a-body"></div>';
            chat.appendChild(m); tw = typewriter(m);
          }
          tw.push(msg.t);
        } else if (msg.done || msg.error) { end = msg; break; }
      }
    }
    if (!tw) { fail(end && end.error); return; }          // พังก่อนได้สักคำ
    if (!(end && end.error)) speakAnswer(tw.text, askLang);
    const ok = !(end && end.error);   // ตอบไม่จบ ไม่ต้องขอดาว
    tw.finish({ image: (end && end.image) || null, photos: (end && end.photos) || [], rateQ: ok ? question : "" }, () => {
      if (stale()) return;
      if (end && end.error) { addMsg("bot", t().sysErr, { warn: true }); speakAnswer(tw.text, askLang); }   // ขาดกลางทาง: อ่านส่วนที่ได้
    });
  } catch (e) {
    fail();
  }
}

// ---- ทักทาย: แขนโบก (เซิร์ฟเวอร์) + หน้าหุ่นยิ้ม (state greeting) + พูดคำทักทาย ----
// ทักเมื่อไม่มีใครแตะจอนานเกิน GREET_IDLE_MS แล้วมีคนแตะครั้งแรก หรือเมื่อเซนเซอร์ส่ง "greet" มาทาง /events
const GREET_IDLE_MS = 60 * 1000;   // ให้ตรงกับ GREET_IDLE_SECONDS ใน config.py
const GREET_MIN_MS = 3000;         // หน้ายิ้มค้างอย่างน้อยเท่ากับเวลาแขนโบก
let lastActive = -Infinity;        // เปิดเครื่องมา คนแรกที่แตะได้รับการทักเลย
let greeting = null;               // Promise ระหว่างกำลังทัก (ไมค์รอให้ทักเสร็จก่อน ไม่งั้นได้ยินเสียงตัวเอง)

// เตรียมเสียงคำทักทายไว้ตั้งแต่เปิดจอ (เซิร์ฟเวอร์เก็บไฟล์ไว้ ครั้งต่อไปได้ทันที)
setTimeout(() => warmTts(T.th.greet, "th"), 2000);

function greet() {
  if (greeting || busy() || listening) return;
  lastActive = Date.now();
  setState("greeting");
  fetch("/greet", { method: "POST" }).catch(() => {});
  const spoken = new Promise((res) => speak(t().greet, lang, res));
  const minTime = new Promise((res) => setTimeout(res, GREET_MIN_MS));
  greeting = Promise.all([spoken, minTime]).then(() => {
    greeting = null;
    lastActive = Date.now();
    if (state === "greeting") setState("idle");
  });
}
function onActivity(e) {
  const quiet = Date.now() - lastActive > GREET_IDLE_MS;
  lastActive = Date.now();
  if (e && e.target.closest && e.target.closest('[data-action="newChat"]')) return;
  if (quiet) greet();
}
document.addEventListener("pointerdown", onActivity, true);
document.addEventListener("keydown", onActivity, true);

// ---- ไมค์ (STT) ----
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
let recog = null, listening = false;
function toggleMic() {
  if (!recog) return;
  if (listening) { recog.stop(); listening = false; setState("idle"); return; }
  if (busy()) return;
  if (greeting) { greeting.then(toggleMic); return; }   // ทักให้จบก่อน แล้วเริ่มฟังเอง
  stopSpeech();
  setState("listening"); listening = true;
  try { recog.start(); } catch (e) { listening = false; setState("idle"); }
}
if (SR) {
  recog = new SR();
  recog.lang = t().speech; recog.interimResults = false; recog.maxAlternatives = 1;
  recog.onresult = (e) => { listening = false; ask(e.results[0][0].transcript, { voice: true }); };
  recog.onerror = () => { listening = false; addMsg("bot", t().noHear, { warn: true }); setState("idle"); };
  recog.onend = () => { listening = false; if (state === "listening") setState("idle"); };
  mic.addEventListener("click", toggleMic);
} else {
  mic.style.display = "none";
}

// ---- พิมพ์ ----
composer.addEventListener("submit", (e) => {
  e.preventDefault();
  if (busy()) return;
  const q = input.value; input.value = ""; composer.classList.remove("has-text");
  ask(q, { voice: false });
});
input.addEventListener("input", () => composer.classList.toggle("has-text", input.value.trim() !== ""));

// ---- เครื่องสแกน QR (USB แบบคีย์บอร์ด) ----
// เครื่องสแกน "พิมพ์" รหัสรัวมาก แล้วกด Enter เอง — คนพิมพ์ไม่เร็วขนาดนี้ จึงแยกออกจากการพิมพ์ปกติได้
// อ่านจากปุ่มจริงที่กด (e.code) ไม่ใช่ตัวอักษร (e.key) → เครื่องตั้งคีย์บอร์ดเป็นภาษาไทยอยู่ก็อ่านรหัสถูก
const SCAN_GAP_MS = 60, SCAN_MIN_LEN = 3;   // ห่างกันเกิน 60ms = ไม่ใช่เครื่องสแกน
const SCAN_PUNCT = { Minus: "-_", Equal: "=+", BracketLeft: "[{", BracketRight: "]}", Backslash: "\\|",
  Semicolon: ";:", Quote: "'\"", Backquote: "`~", Comma: ",<", Period: ".>", Slash: "/?", Space: "  ",
  NumpadSubtract: "--", NumpadAdd: "++", NumpadMultiply: "**", NumpadDivide: "//", NumpadDecimal: ".." };
function scanChar(code, shift, caps) {
  let m;
  if ((m = /^Key([A-Z])$/.exec(code))) return shift !== caps ? m[1] : m[1].toLowerCase();
  if ((m = /^Digit(\d)$/.exec(code))) return shift ? ")!@#$%^&*("[m[1]] : m[1];
  if ((m = /^Numpad(\d)$/.exec(code))) return m[1];
  const p = SCAN_PUNCT[code];
  return p ? p[shift ? 1 : 0] : "";
}
let scanBuf = "", scanLast = 0, scanSnap = null;
document.addEventListener("keydown", (e) => {
  const now = performance.now();
  if (now - scanLast > SCAN_GAP_MS || e.repeat) {   // เริ่มชุดใหม่: จำข้อความในช่องพิมพ์ไว้ก่อนรหัสจะไหลเข้าไป
    scanBuf = "";
    scanSnap = document.activeElement === input ? input.value : null;
  }
  scanLast = now;
  if (e.code === "Enter" || e.code === "NumpadEnter" || e.key === "Enter") {
    const code = scanBuf; scanBuf = "";
    if (code.length < SCAN_MIN_LEN) return;   // Enter ของคนพิมพ์ → ส่งคำถามตามปกติ
    e.preventDefault(); e.stopImmediatePropagation();
    if (scanSnap !== null) { input.value = scanSnap; composer.classList.toggle("has-text", scanSnap.trim() !== ""); }
    onScan(code.trim());
    return;
  }
  if (e.ctrlKey || e.altKey || e.metaKey || e.isComposing) { scanBuf = ""; return; }
  scanBuf += scanChar(e.code, e.shiftKey, !!(e.getModifierState && e.getModifierState("CapsLock")));
}, true);

// รหัสใน qr_codes.json → ส่งเป็นคำถามให้ AI (ได้รูป/แผนผังเหมือนถามเอง) หรือพูดคำตอบตายตัวเลย
function onScan(code) {
  if (attractOn) stopAttract();
  closeTour();
  if (busy() || announcing) return;
  if (recog && listening) { recog.stop(); listening = false; }
  fetch("/qr?code=" + encodeURIComponent(code) + "&lang=" + lang)
    .then((r) => (r.ok ? r.json() : null))
    .then((d) => {
      if (!d) { stopAnswer(); addMsg("bot", t().qrUnknown, { warn: true }); return; }
      if (d.question) { ask(d.question, { qr: true }); return; }
      stopAnswer();
      addMsg("user", d.label, { qr: true });
      addMsg("bot", d.answer);
      setState("answering"); speakAnswer(d.answer, lang);
    })
    .catch(() => addMsg("bot", t().sysErr, { warn: true }));
}

// ---- คำถามยอดนิยม: ต้นฉบับอยู่ใน #quickQs คัดลอกไปแถบซ้ายและแถวเหนือช่องถาม ----
document.querySelectorAll("#quickQs .chip").forEach((chip) => {
  const side = chip.cloneNode(true); side.className = "nav"; $("sideQs").appendChild(side);
  $("dockQs").appendChild(chip.cloneNode(true));
});

function newChat() {
  if (recog && listening) { recog.stop(); listening = false; }
  stopSpeech();
  convo++;
  chat.innerHTML = "";
  setView("welcome");
  setState("idle");
}

// ---- เมนูที่เที่ยว/ของฝาก: กดไล่ หมวด → รายชื่อ → รายละเอียด (ข้อมูลจาก /menu โหลดครั้งเดียว ไม่เรียก AI) ----
let menuData = null;
const loadMenu = () => fetch("/menu").then((r) => (r.ok ? r.json() : null)).then((d) => { menuData = d; }).catch(() => {});
loadMenu();
const pick = (o) => (o && (o[lang] || o.th)) || "";   // ชื่อตามภาษา (ไม่มีอังกฤษ → ไทย)
const L = (o) => escapeHtml(pick(o));

// ต่อเมนูเป็นข้อความในแชท: บับเบิลผู้ใช้ = ปุ่มที่แตะ (ข้อความดิบ addMsg escape ให้), บับเบิลหุ่น = ตัวเลือกชั้นถัดไป
function menuStep(label, html, back) {
  addMsg("user", label);
  const m = document.createElement("div");
  m.className = "msg bot";
  m.innerHTML = AVA + '<div class="a-body">' + html + '<div class="menu-nav">' +
    (back ? `<button type="button" class="menu-btn" ${back}>← ${t().back}</button>` : "") +
    `<button type="button" class="menu-btn" data-action="newChat">🏠 ${t().home}</button></div></div>`;
  chat.appendChild(m); scrollDown();
  m.querySelectorAll("img").forEach((i) => i.addEventListener("load", scrollDown, { once: true }));
}
const district = (d) => (d ? `📍 ${t().districtPre}${escapeHtml(d)}` : "");

function openMenu(b) {
  const [sec, i, j] = (b.dataset.menu || b.dataset.menuCat || b.dataset.menuItem).split(":");
  const s = menuData && menuData[sec];
  if (!s || !s.categories.length) return false;
  if (i === undefined) {
    menuStep(pick(s.label), `<p class="md-p">${t().menuPick}</p><div class="menu-grid">` +
      s.categories.map((c, k) => `<button type="button" class="menu-btn" data-menu-cat="${sec}:${k}">${c.icon} ${L(c.label)}</button>`).join("") +
      "</div>");
    return true;
  }
  const c = s.categories[i];
  if (j === undefined) {
    menuStep(`${c.icon} ${pick(c.label)}`, `<p class="md-p">${t().menuItems}</p><div class="menu-list">` +
      c.items.map((it, k) => `<button type="button" class="menu-item" data-menu-item="${sec}:${i}:${k}">` +
        (it.photo ? `<img src="${it.photo}" alt="">` : `<span class="m-icon">${c.icon}</span>`) +
        `<span><b>${L(it.name)}</b><small>${district(it.district)}</small></span></button>`).join("") +
      "</div>", `data-menu="${sec}"`);
    return true;
  }
  const it = c.items[j];
  menuStep(pick(it.name), '<div class="place-card">' +
    (it.photo ? `<img class="place-photo" src="${it.photo}" alt="${L(it.name)}">` : `<div class="m-icon">${c.icon}</div>`) +
    `<h3>${L(it.name)}</h3><small>${district(it.district)}</small>` +
    (it.highlight ? `<p>${escapeHtml(it.highlight)}</p>` : "") + "</div>", `data-menu-cat="${sec}:${i}"`);
  return true;
}

document.addEventListener("click", (e) => {
  const b = e.target.closest("[data-q], [data-action], [data-menu], [data-menu-cat], [data-menu-item]");
  if (!b) return;
  const action = b.dataset.action;
  if (action === "newChat") { newChat(); return; }
  if (action === "closeTour") { closeTour(); return; }
  if (busy()) return;   // กันแตะรัวระหว่างหุ่นกำลังคิด/พูด
  if (b.dataset.menu || b.dataset.menuCat || b.dataset.menuItem) {
    // เมนูยังไม่มา (โหลดไม่ทัน/เคยพัง) → ลองโหลดใหม่ก่อน ถ้ายังไม่ได้จริง ๆ ชิปค่อยตกไปถาม AI แบบเดิม
    (menuData ? Promise.resolve() : loadMenu()).then(() => {
      if (!openMenu(b) && b.dataset.q && !busy()) askChip(b);
    });
    return;
  }
  if (action === "showMap") { showMap(); return; }
  if (action === "campusTour") { openTour(); return; }
  askChip(b);
});
function askChip(b) {
  const q = (lang === "en" && b.dataset.qEn) || b.dataset.q || b.textContent.trim();
  ask(q, { voice: false });   // data-q = คำถามเต็ม, ป้ายบนปุ่มย่อให้สั้น
}

document.querySelectorAll("#langSeg button").forEach((b) => b.addEventListener("click", () => applyLang(b.dataset.lang)));

// ---- แนะนำสถานที่วิทยาลัย: ทัวร์ 3 มิติ (static/campus_tour.html) เต็มจอ — โหลดตอนเปิด ปิดแล้วทิ้ง (คืนหน่วยความจำ WebGL) ----
const TOUR_SRC = "/static/campus_tour.html", TOUR_IDLE_MS = 5 * 60 * 1000;
const tourEl = $("tourView"), tourFrame = tourEl.querySelector("iframe");
// ใช้เปิดลิงก์ในคำตอบด้วย (เช่น ฟอร์มสมัครเรียนออนไลน์) — เว็บนอกดักการแตะใน iframe ไม่ได้ (คนละ origin)
// เลยให้เวลานานกว่าก่อนกลับโหมดรอ จะได้กรอกฟอร์มทัน
const EXTERNAL_IDLE_MS = 15 * 60 * 1000;
let tourOpen = false, tourIdleMs = TOUR_IDLE_MS;
function openTour(src = TOUR_SRC) {
  if (tourOpen) return;
  if (recog && listening) { recog.stop(); listening = false; }
  stopSpeech();
  tourOpen = true; idleSince = Date.now();
  tourIdleMs = src === TOUR_SRC ? TOUR_IDLE_MS : EXTERNAL_IDLE_MS;
  tourFrame.src = src;
  tourEl.classList.add("open");
}
function closeTour() {
  if (!tourOpen) return;
  tourOpen = false; idleSince = Date.now();
  tourEl.classList.remove("open");
  tourFrame.src = "about:blank";
}
// แตะ/ลากในทัวร์ไม่ถึง document หน้านี้ → ดักใน iframe เองเพื่อนับว่ายังมีคนใช้อยู่ (ไฟล์เดียวกัน origin เดียวกัน)
tourFrame.addEventListener("load", () => {
  try {
    const d = tourFrame.contentDocument;
    if (d) ["pointerdown", "wheel", "keydown"].forEach((ev) => d.addEventListener(ev, () => { idleSince = Date.now(); }, { capture: true, passive: true }));
  } catch (e) {}
});

// ---- lightbox ----
const lightbox = $("lightbox");
lightbox.addEventListener("click", () => lightbox.classList.remove("open"));
chat.addEventListener("click", (e) => {
  const link = e.target.closest("[data-open-url]");
  if (link) { e.preventDefault(); openTour(link.dataset.openUrl); return; }
  const star = e.target.closest("[data-stars]");
  if (star) { sendRating(star); return; }
  if (e.target.classList.contains("map-thumb") || e.target.classList.contains("place-photo")) {
    lightbox.querySelector("img").src = e.target.src;
    lightbox.classList.add("open");
  }
});

setView("welcome");
applyLang(lang);   // ตั้งภาษา + ส่งสถานะ idle ไปเซิร์ฟเวอร์

// ---- GPIO button via SSE ----
const evtSrc = new EventSource("/events");
evtSrc.onmessage = (e) => {
  if (e.data === "mic-start" && !listening && !busy()) { stopAttract(); closeTour(); onActivity(); toggleMic(); }
  if (e.data === "greet") { stopAttract(); greet(); }   // เซนเซอร์เจอคนเดินมา
};

// ---- โหมดรอ: ไม่มีใครใช้นาน → เปิดวิดีโอวนเต็มจอ, แตะจอ/เซนเซอร์เจอคน → กลับหน้าถามตอบ (เริ่มคุยใหม่) ----
// วิดีโอมาจาก /attract (ไฟล์ใน web/static/videos/) ไม่มีวิดีโอ = โชว์ตราวิทยาลัยแทน
const attractEl = $("attract"), video = attractEl.querySelector("video");
let attractCfg = { videos: [], after: 90 }, attractOn = false, vidIdx = 0, vidFails = 0;
fetch("/attract").then((r) => (r.ok ? r.json() : null)).then((d) => { if (d) attractCfg = d; }).catch(() => {})
  .then(() => startAttract());   // เปิดหน้าเว็บมา เริ่มที่โหมดรอเลย

function playVideo() {
  const list = attractCfg.videos || [];
  attractEl.classList.toggle("no-video", !list.length || vidFails >= list.length);
  if (attractEl.classList.contains("no-video")) return;
  video.src = list[vidIdx % list.length];
  video.loop = list.length === 1;
  video.muted = false;
  // เบราว์เซอร์บางตัวห้ามเล่นมีเสียงเอง (บน Pi ตั้ง kiosk ให้เล่นได้แล้ว) → ลองแบบเงียบแทน
  video.play().catch(() => { video.muted = true; video.play().catch(() => {}); });
}
video.addEventListener("ended", () => { vidIdx++; playVideo(); });
video.addEventListener("error", () => { if (!attractOn) return; vidFails++; vidIdx++; playVideo(); });
video.addEventListener("playing", () => { vidFails = 0; });

function startAttract() {
  if (attractOn) return;
  newChat();   // คนต่อไปเริ่มหน้าใหม่ ไม่เห็นบทสนทนาของคนก่อน
  attractOn = true; vidFails = 0;
  attractEl.classList.add("open");
  playVideo();
}
function stopAttract() {
  if (!attractOn) return;
  attractOn = false;
  attractEl.classList.remove("open");
  video.pause();
  idleSince = Date.now();
}
// แตะจอ: ปิดวิดีโอ (onActivity ที่ดักไว้ข้างบนจะทักทายให้เอง ถ้าเงียบมานานพอ)
attractEl.addEventListener("click", stopAttract);
document.addEventListener("pointerdown", () => { idleSince = Date.now(); }, true);
document.addEventListener("keydown", () => { idleSince = Date.now(); }, true);
setInterval(() => {
  if (attractOn || state !== "idle" || listening || greeting || announcing) return;
  // เปิดทัวร์ทิ้งไว้: ให้เวลานานกว่าปกติ (ทัวร์อัตโนมัติยาว ~3-4 นาที) แล้วค่อยปิดเข้าโหมดรอ
  const after = (attractCfg.after || 90) * 1000, limit = tourOpen ? Math.max(after, tourIdleMs) : after;
  if (Date.now() - idleSince > limit) { closeTour(); startAttract(); }
}, 2000);

// ---- ประกาศตามเวลา: ถามเซิร์ฟเวอร์ทุก 15 วิ ว่ามีประกาศถึงเวลาไหม (ตั้งใน robot/announcements.json) ----
// ถ้าหุ่นกำลังคุยกับคนอยู่ รอให้ตอบจบก่อนค่อยประกาศ (รอเกิน 5 นาทีแล้วข้ามไป)
const ANN_STALE_MS = 5 * 60 * 1000, ANN_MIN_MS = 6000;
const annEl = $("announce");
let annDone;
try { annDone = new Set(JSON.parse(store.get("annDone") || "[]")); } catch (e) { annDone = new Set(); }
const annQueue = [];
let announcing = false;

function pollAnnouncements() {
  fetch("/announcements/due").then((r) => (r.ok ? r.json() : null)).then((d) => {
    for (const a of (d && d.due) || []) {
      if (annDone.has(a.id) || annQueue.some((q) => q.id === a.id)) continue;
      annQueue.push({ ...a, at: Date.now() });
      warmTts(plainForSpeech(a.text), "th");   // เตรียมเสียงประกาศไว้ก่อน
    }
    runAnnouncements();
  }).catch(() => {});
}
function runAnnouncements() {
  if (announcing || !annQueue.length) return;
  if (busy() || listening || greeting) { setTimeout(runAnnouncements, 3000); return; }
  const a = annQueue.shift();
  annDone.add(a.id);
  store.set("annDone", JSON.stringify([...annDone].slice(-50)));
  if (Date.now() - a.at > ANN_STALE_MS) { runAnnouncements(); return; }
  const useEn = lang === "en" && a.text_en;
  const text = useEn ? a.text_en : a.text;
  announcing = true;
  if (attractOn) video.pause();
  $("announceText").textContent = text;
  annEl.classList.add("open");
  setState("answering");   // หน้าหุ่นขยับปากตอนประกาศ
  const spoken = new Promise((res) => speak(plainForSpeech(text), useEn ? "en" : "th", res));
  const minTime = new Promise((res) => setTimeout(res, ANN_MIN_MS));
  Promise.all([spoken, minTime]).then(() => {
    annEl.classList.remove("open");
    announcing = false;
    setState("idle");
    if (attractOn) video.play().catch(() => {});
    runAnnouncements();
  });
}
pollAnnouncements();
setInterval(pollAnnouncements, 15000);
