// จอเนื้อหา: คุมไมค์ (STT) + พิมพ์ → เรียก /ask → แสดงคำตอบ + พูด (TTS) + แจ้ง /state
const LABELS = {
  idle: "พร้อมรับคำถาม", listening: "กำลังฟัง…", thinking: "กำลังคิด…",
  answering: "กำลังตอบ", error: "เกิดข้อผิดพลาด",
};
const SPEECH_LANG = "th-TH";
const chat = document.getElementById("chat");
const ledText = document.querySelector(".led-text");
const ledDot = document.querySelector(".led .d");
const mic = document.getElementById("mic");
const micLabel = document.getElementById("micLabel");

// ---- สถานะ: อัปเดต UI ตัวเอง + แจ้งเซิร์ฟเวอร์ (ให้จอใบหน้า sync) ----
function setState(s) {
  document.body.className = "page-screen state-" + s;
  if (ledText) ledText.textContent = LABELS[s] || s;
  if (ledDot) ledDot.classList.toggle("live", s !== "idle");
  if (mic) mic.classList.toggle("live", s === "listening");
  if (micLabel) micLabel.textContent = s === "listening" ? "กำลังฟัง… (แตะเพื่อหยุด)" : "กดเพื่อพูด";
  fetch("/state", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ state: s }),
  }).catch(() => {});
}

// ---- ฟองข้อความ ----
function escapeHtml(s) { const d = document.createElement("div"); d.textContent = s; return d.innerHTML; }
function addMsg(role, text, opts = {}) {
  const m = document.createElement("div");
  m.className = "msg " + role;
  const tag = opts.voice ? '<span class="mic-tag">🎤 พูด</span>' : "";
  const ava = role === "bot" ? '<div class="ava"><i></i><i></i></div>' : "";
  m.innerHTML = ava + '<div class="bubble' + (opts.warn ? " warn" : "") + '">' + tag + escapeHtml(text) + "</div>";
  chat.appendChild(m); chat.scrollTop = chat.scrollHeight;
}
function typing(on) {
  let t = document.getElementById("typing");
  if (on && !t) {
    t = document.createElement("div"); t.id = "typing"; t.className = "msg bot typing";
    t.innerHTML = '<div class="ava"><i></i><i></i></div><div class="bubble"><i></i><i></i><i></i></div>';
    chat.appendChild(t); chat.scrollTop = chat.scrollHeight;
  } else if (!on && t) { t.remove(); }
}

// ---- พูดออกเสียง (TTS) ----
function speak(text, onEnd) {
  if (!("speechSynthesis" in window)) { if (onEnd) onEnd(); return; }
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = SPEECH_LANG;
  const thVoice = window.speechSynthesis.getVoices().find(v => v.lang && v.lang.toLowerCase().startsWith("th"));
  if (thVoice) u.voice = thVoice;
  u.onend = () => onEnd && onEnd();
  u.onerror = () => onEnd && onEnd();
  window.speechSynthesis.speak(u);
}

// ---- ถาม-ตอบหลัก ----
async function ask(question, opts = {}) {
  question = (question || "").trim();
  if (!question) { setState("idle"); return; }
  addMsg("user", question, { voice: !!opts.voice });
  setState("thinking"); typing(true);
  try {
    const r = await fetch("/ask", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const d = await r.json();
    typing(false);
    if (!r.ok) throw new Error(d.error || "เซิร์ฟเวอร์ขัดข้อง");
    const answer = d.answer || "";
    addMsg("bot", answer);
    setState("answering");
    speak(answer, () => setState("idle"));
  } catch (e) {
    typing(false);
    addMsg("bot", "ขออภัยค่ะ ระบบขัดข้อง ลองใหม่อีกครั้งนะคะ", { warn: true });
    setState("error");
    setTimeout(() => setState("idle"), 2500);
  }
}

// ---- ไมค์ (STT) ----
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
let recog = null, listening = false;
if (SR) {
  recog = new SR();
  recog.lang = SPEECH_LANG; recog.interimResults = false; recog.maxAlternatives = 1;
  recog.onresult = (e) => { ask(e.results[0][0].transcript, { voice: true }); };
  recog.onerror = () => { listening = false; addMsg("bot", "ไม่ได้ยินค่ะ ลองพิมพ์คำถามดูไหมคะ 🙏", { warn: true }); setState("idle"); };
  recog.onend = () => { listening = false; if (document.body.classList.contains("state-listening")) setState("idle"); };
  mic.addEventListener("click", () => {
    if (listening) { recog.stop(); listening = false; setState("idle"); return; }
    setState("listening"); listening = true;
    try { recog.start(); } catch (e) { listening = false; setState("idle"); }
  });
} else {
  mic.style.display = "none";
  if (micLabel) micLabel.textContent = "พิมพ์คำถามด้านล่างได้เลย";
}

// ---- พิมพ์ (ตัวสำรอง) ----
document.getElementById("composer").addEventListener("submit", (e) => {
  e.preventDefault();
  const inp = document.getElementById("q");
  const q = inp.value; inp.value = "";
  ask(q, { voice: false });
});

setState("idle");
