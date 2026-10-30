// เดโมหน้าจอบน GitHub Pages: ไม่มีเซิร์ฟเวอร์และไม่มี AI
// แทนที่ fetch/EventSource ก่อน screen.js โหลด — เมนูอ่านจาก menu.json, คำถามได้คำอธิบายว่าเป็นเดโม
(function () {
  const realFetch = window.fetch.bind(window);
  const NOTE = {
    th: "นี่คือเดโมหน้าจอค่ะ 🙂 เวอร์ชันบนเว็บยังตอบคำถามด้วย AI ไม่ได้ (หุ่นตัวจริงที่วิทยาลัยตอบได้)\n\n" +
      "ลองแตะ **🏞️ ที่เที่ยวสระบุรี** หรือ **🛍️ ของฝากสระบุรี** หรือ **🗺️ แผนผังวิทยาลัย** ดูได้เลยนะคะ",
    en: "This is a screen demo 🙂 The web version can't answer with AI (the real robot at the college can).\n\n" +
      "Try tapping **🏞️ Places to visit**, **🛍️ Local souvenirs** or **🗺️ Campus map**.",
  };

  window.fetch = (url, opts) => {
    const u = String(url);
    if (u === "/menu") return realFetch("menu.json");
    if (u === "/state") return Promise.resolve(new Response("{}", { headers: { "Content-Type": "application/json" } }));
    if (u === "/ask/stream") {
      let lang = "th";
      try { lang = JSON.parse(opts.body).lang === "en" ? "en" : "th"; } catch (e) {}
      const line = (o) => JSON.stringify(o) + "\n";
      return Promise.resolve(new Response(line({ t: NOTE[lang] }) + line({ done: true, image: null, photos: [] })));
    }
    return realFetch(url, opts);
  };

  // ปุ่มกายภาพ (GPIO) ไม่มีบนเว็บ — กัน EventSource ยิง /events ซ้ำไม่หยุด
  window.EventSource = function () { return { close() {} }; };

  // ป้ายบอกว่าเป็นเดโม
  document.addEventListener("DOMContentLoaded", () => {
    const tag = document.createElement("div");
    tag.textContent = "DEMO";
    tag.title = "เดโมหน้าจอ — ไม่มี AI";
    tag.style.cssText = "position:fixed;right:10px;bottom:10px;z-index:300;padding:4px 10px;border-radius:999px;" +
      "font:600 11px/1.4 sans-serif;letter-spacing:.08em;background:#f59e0b;color:#111;opacity:.85;pointer-events:none";
    document.body.appendChild(tag);
  });
})();
