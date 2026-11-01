// จอเนื้อหา: คุมไมค์ (STT) + พิมพ์ → เรียก /ask → แสดงคำตอบ + พูด (TTS) + แจ้ง /state
// รองรับ 2 ภาษา (th/en) และโหมดมืด/สว่าง — ภาษาที่เลือกส่งไปเซิร์ฟเวอร์ด้วย ให้จอใบหน้าและ AI ใช้ตาม

// ---- ข้อความทุกภาษา ----
const T = {
  th: {
    brand: "ผู้ช่วยท่าหลวงฯ", college: "วิทยาลัยเทคนิคท่าหลวงซิเมนต์ไทยอนุสรณ์",
    newChat: "เริ่มคุยใหม่", newShort: "คุยใหม่",
    popular: "คำถามยอดนิยม", popularHint: "คำถามยอดนิยม — แตะถามได้เลย",
    phone: "โทร 0-3628-1295", phoneNote: "ข้อมูลไม่ครบ ติดต่อเจ้าหน้าที่ได้เลยค่ะ",
    hello: "อยากรู้อะไรเกี่ยวกับ<em>ท่าหลวงฯ</em>ดี?",
    sub: "แตะไมค์เพื่อพูด หรือพิมพ์ถามได้เลยค่ะ 😊", subNoMic: "พิมพ์คำถามด้านล่างได้เลยค่ะ 😊",
    placeholder: "ถามอะไรก็ได้เกี่ยวกับวิทยาลัย…", listening: "กำลังฟัง… พูดได้เลยค่ะ (แตะไมค์เพื่อหยุด)",
    send: "ส่ง", mic: "กดเพื่อพูด", replay: "ฟังอีกครั้ง", theme: "สลับโหมดมืด/สว่าง",
    cMap: "แผนผังวิทยาลัย", cPrograms: "สาขาที่เปิดสอน", cApply: "คุณสมบัติผู้สมัคร",
    cContact: "ช่องทางติดต่อ", cTrips: "ที่เที่ยวสระบุรี", cSouvenir: "ของฝากสระบุรี",
    hint: "หุ่นยนต์ตอบจากข้อมูลของวิทยาลัย ถ้าไม่แน่ใจ สอบถามเจ้าหน้าที่ได้นะคะ",
    spoken: "🎤 พูด", mapAlt: "แผนผังวิทยาลัย",
    mapMsg: "นี่คือแผนผังวิทยาลัยค่ะ 🗺️ แตะที่รูปเพื่อขยายดูได้เลย",
    sysErr: "ขออภัยค่ะ ระบบขัดข้อง ลองใหม่อีกครั้งนะคะ",
    noHear: "ไม่ได้ยินค่ะ ลองพูดใหม่ หรือพิมพ์คำถามดูนะคะ 🙏",
    menuPick: "เลือกหมวดได้เลยค่ะ 👇", menuItems: "แตะดูรายละเอียดได้เลยค่ะ 👇",
    back: "ย้อนกลับ", home: "หน้าแรก", districtPre: "อ.",
    greet: "สวัสดีค่ะ หนูชื่อทีแอลบอท มีอะไรให้ช่วยไหมคะ",
    rateAsk: "คำตอบนี้ช่วยได้ไหมคะ?", rateThanks: "ขอบคุณที่ให้คะแนนค่ะ 🙏", starUnit: "ดาว",
    attractSub: "สวัสดีค่ะ หนูชื่อทีแอลบอท ผู้ช่วยตอบคำถามของวิทยาลัย", attractTap: "👆 แตะจอเพื่อถามหุ่นยนต์",
    announceTag: "ประกาศ",
    states: { idle: "พร้อมรับคำถาม", greeting: "สวัสดีค่ะ 👋", listening: "กำลังฟัง…", thinking: "กำลังคิด…", answering: "กำลังตอบ", error: "เกิดข้อผิดพลาด" },
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
const busy = () => state === "thinking" || state === "answering";

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
function inlineMd(s) {
  return s
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
    .replace(/^#{1,6}\s+/gm, "").replace(/\s\*\s+/g, " ").replace(/[*#•]/g, "").replace(/\s+/g, " ").trim();
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
    m.innerHTML = (opts.voice ? '<span class="mic-tag">' + t().spoken + "</span>" : "") + escapeHtml(text);
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
    const say = plainForSpeech(text), sayLang = lang;
    r.addEventListener("click", () => { if (busy()) return; setState("answering"); speak(say, sayLang, () => setState("idle")); });
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

// ---- พูดออกเสียง (TTS) ----
function speak(text, speakLang, onEnd) {
  if (!("speechSynthesis" in window)) { if (onEnd) onEnd(); return; }
  window.speechSynthesis.cancel();
  const code = T[speakLang].speech;
  const u = new SpeechSynthesisUtterance(text);
  u.lang = code;
  const voices = window.speechSynthesis.getVoices().filter((v) => v.lang && v.lang.toLowerCase().startsWith(code.slice(0, 2)));
  const voice = voices.find((v) => /หญิง|female|woman|kanya|narisa|samantha|zira|aria|jenny/i.test(v.name)) || voices[0];
  if (voice) u.voice = voice;
  u.onend = () => onEnd && onEnd();
  u.onerror = () => onEnd && onEnd();
  window.speechSynthesis.speak(u);
}

// ---- ถาม-ตอบหลัก ----
async function ask(question, opts = {}) {
  question = (question || "").trim();
  if (!question) { setState("idle"); return; }
  const askLang = lang, myConvo = convo;
  const stale = () => myConvo !== convo;
  addMsg("user", question, { voice: !!opts.voice });
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
    const ok = !(end && end.error);   // ตอบไม่จบ ไม่ต้องขอดาว
    tw.finish({ image: (end && end.image) || null, photos: (end && end.photos) || [], rateQ: ok ? question : "" }, () => {
      if (stale()) return;
      if (end && end.error) addMsg("bot", t().sysErr, { warn: true });   // ขาดกลางทาง: ที่ได้แล้วยังอยู่
      speak(plainForSpeech(tw.text), askLang, () => { lastActive = Date.now(); setState("idle"); });
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
  window.speechSynthesis && window.speechSynthesis.cancel();
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

// ---- คำถามยอดนิยม: ต้นฉบับอยู่ใน #quickQs คัดลอกไปแถบซ้ายและแถวเหนือช่องถาม ----
document.querySelectorAll("#quickQs .chip").forEach((chip) => {
  const side = chip.cloneNode(true); side.className = "nav"; $("sideQs").appendChild(side);
  $("dockQs").appendChild(chip.cloneNode(true));
});

function newChat() {
  if (recog && listening) { recog.stop(); listening = false; }
  window.speechSynthesis && window.speechSynthesis.cancel();
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
  if (busy()) return;   // กันแตะรัวระหว่างหุ่นกำลังคิด/พูด
  if (b.dataset.menu || b.dataset.menuCat || b.dataset.menuItem) {
    // เมนูยังไม่มา (โหลดไม่ทัน/เคยพัง) → ลองโหลดใหม่ก่อน ถ้ายังไม่ได้จริง ๆ ชิปค่อยตกไปถาม AI แบบเดิม
    (menuData ? Promise.resolve() : loadMenu()).then(() => {
      if (!openMenu(b) && b.dataset.q && !busy()) askChip(b);
    });
    return;
  }
  if (action === "showMap") { showMap(); return; }
  askChip(b);
});
function askChip(b) {
  const q = (lang === "en" && b.dataset.qEn) || b.dataset.q || b.textContent.trim();
  ask(q, { voice: false });   // data-q = คำถามเต็ม, ป้ายบนปุ่มย่อให้สั้น
}

document.querySelectorAll("#langSeg button").forEach((b) => b.addEventListener("click", () => applyLang(b.dataset.lang)));

// ---- lightbox ----
const lightbox = $("lightbox");
lightbox.addEventListener("click", () => lightbox.classList.remove("open"));
chat.addEventListener("click", (e) => {
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
  if (e.data === "mic-start" && !listening && !busy()) { stopAttract(); onActivity(); toggleMic(); }
  if (e.data === "greet") { stopAttract(); greet(); }   // เซนเซอร์เจอคนเดินมา
};

// ---- โหมดรอ: ไม่มีใครใช้นาน → เปิดวิดีโอวนเต็มจอ, แตะจอ/เซนเซอร์เจอคน → กลับหน้าถามตอบ (เริ่มคุยใหม่) ----
// วิดีโอมาจาก /attract (ไฟล์ใน web/static/videos/) ไม่มีวิดีโอ = โชว์ตราวิทยาลัยแทน
const attractEl = $("attract"), video = attractEl.querySelector("video");
let attractCfg = { videos: [], after: 90 }, attractOn = false, vidIdx = 0, vidFails = 0;
fetch("/attract").then((r) => (r.ok ? r.json() : null)).then((d) => { if (d) attractCfg = d; }).catch(() => {});

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
  if (Date.now() - idleSince > (attractCfg.after || 90) * 1000) startAttract();
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
