// เดโมบน GitHub Pages: ไม่มีเซิร์ฟเวอร์และไม่มี AI — ใช้ได้ 3 หน้า: index.html (จอแชท), face.html (หน้าหุ่น), stats.html (สถิติ)
// แทนที่ fetch/EventSource ก่อนสคริปต์ของหน้าโหลด — เมนูอ่านจาก menu.json, คำถามได้คำอธิบายว่าเป็นเดโม,
// สถานะหุ่นส่งข้ามแท็บผ่าน localStorage (เปิดหน้าแชทกับหน้าหุ่นคู่กัน หน้าหุ่นจะเปลี่ยนอารมณ์ตาม)
(function () {
  const realFetch = window.fetch.bind(window);
  const NOTE = {
    th: "นี่คือเดโมหน้าจอครับ 🙂 เวอร์ชันบนเว็บยังตอบคำถามด้วย AI ไม่ได้ (หุ่นตัวจริงที่วิทยาลัยตอบได้)\n\n" +
      "ลองแตะ **🏞️ ที่เที่ยวสระบุรี** หรือ **🛍️ ของฝากสระบุรี** หรือ **🗺️ แผนผังวิทยาลัย** ดูได้เลยนะครับ " +
      "แล้วลองให้ดาวคำตอบนี้ข้างล่างได้ครับ ⭐",
    en: "This is a screen demo 🙂 The web version can't answer with AI (the real robot at the college can).\n\n" +
      "Try tapping **🏞️ Places to visit**, **🛍️ Local souvenirs** or **🗺️ Campus map**, and rate this answer below ⭐",
  };
  // ข้อมูลตัวอย่างสำหรับหน้าสถิติ (หุ่นจริงนับจากคนที่ใช้งาน)
  const SAMPLE_STATS = {
    questions_today: 37, questions_total: 412, ratings_today: 15, ratings_total: 168, average: 4.46,
    distribution: { 1: 4, 2: 6, 3: 12, 4: 39, 5: 107 },
    top: [
      { question: "เปิดสอนสาขาอะไรบ้าง", count: 58 },
      { question: "สมัครเรียนต้องมีคุณสมบัติอะไร", count: 44 },
      { question: "ติดต่อวิทยาลัยได้ช่องทางไหนบ้าง", count: 31 },
      { question: "สระบุรีมีที่เที่ยวที่ไหนบ้าง", count: 27 },
      { question: "ห้องน้ำอยู่ตรงไหน", count: 19 },
      { question: "ของฝากขึ้นชื่อของสระบุรีมีอะไรบ้าง", count: 16 },
      { question: "ผู้อำนวยการชื่ออะไร", count: 12 },
      { question: "แผนกช่างยนต์อยู่ตึกไหน", count: 9 },
    ],
    low: [
      { question: "ค่าเทอมเท่าไหร่", stars: 2, ts: "2026-11-02 10:41:07" },
      { question: "มีหอพักไหม", stars: 1, ts: "2026-11-02 09:15:52" },
      { question: "รถเมล์สายไหนผ่านวิทยาลัย", stars: 2, ts: "2026-11-01 14:03:18" },
    ],
  };
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} },
  };
  const json = (o) => Promise.resolve(new Response(JSON.stringify(o), { headers: { "Content-Type": "application/json" } }));

  window.fetch = (url, opts) => {
    const u = String(url);
    if (u === "/menu") return realFetch("menu.json");
    if (u === "/state") {
      if (opts && opts.method === "POST") { store.set("demoState", opts.body); return json({ ok: true }); }
      try { return json(JSON.parse(store.get("demoState")) || {}); } catch (e) { return json({}); }
    }
    if (u === "/rate" || u === "/greet") return json({ ok: true });
    if (u === "/attract") return json({ videos: [], after: 90 });     // โหมดรอโชว์ตราวิทยาลัย (ไม่มีวิดีโอบนเว็บ)
    if (u === "/announcements/due") return json({ due: [] });
    if (u === "/stats.json") return json(SAMPLE_STATS);
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

  // แถบเดโมมุมขวาล่าง: ลิงก์ไปอีก 2 หน้า + ปุ่มลองโหมดรอ/ประกาศ (เฉพาะหน้าแชท)
  document.addEventListener("DOMContentLoaded", () => {
    const page = document.body.classList.contains("page-face") ? "face"
      : document.body.classList.contains("page-screen") ? "screen" : "stats";
    const css = document.createElement("style");
    css.textContent =
      ".demo-bar{position:fixed;right:10px;bottom:10px;z-index:300;display:flex;gap:6px;align-items:center;" +
      "font:500 12px/1.4 system-ui,sans-serif}" +
      ".demo-bar a,.demo-bar button{padding:6px 12px;border-radius:999px;border:0;cursor:pointer;text-decoration:none;" +
      "font:inherit;background:rgba(20,24,32,.85);color:#fff;box-shadow:0 2px 10px rgba(0,0,0,.3)}" +
      ".demo-bar .tag{order:9;padding:6px 10px;border-radius:999px;font-weight:700;letter-spacing:.08em;background:#f59e0b;color:#111;cursor:default}" +
      // หน้าสถิติ: วางเป็นแถบบนสุดของหน้า (ไม่ลอยทับตัวเลข)
      ".demo-bar.inflow{position:static;justify-content:flex-end;flex-wrap:wrap;max-width:960px;margin:0 auto 14px}" +
      // มือถือ หน้าแชท: เหลือป้าย DEMO ปุ่มเดียวใต้แถบบน แตะแล้วค่อยกางเมนู (ไม่บังแชท/ช่องพิมพ์)
      "@media (max-width:640px){.demo-bar.float{top:64px;left:10px;right:auto;bottom:auto;flex-direction:column;align-items:flex-start}" +
      ".demo-bar.float .tag{order:-1;cursor:pointer}.demo-bar.float .tag::after{content:' ▾'}" +
      ".demo-bar.float:not(.open)>:not(.tag){display:none}}";
    document.head.appendChild(css);
    const bar = document.createElement("div");
    bar.className = "demo-bar " + (page === "stats" ? "inflow" : "float");
    const add = (label, href, onClick) => {
      const el = document.createElement(href ? "a" : "button");
      const [icon, ...rest] = label.split(" ");
      el.innerHTML = icon + '<span class="lbl"> ' + rest.join(" ") + "</span>";
      el.title = rest.join(" ");
      if (href) { el.href = href; el.target = "_blank"; el.rel = "noopener"; } else el.addEventListener("click", onClick);
      bar.appendChild(el);
    };
    if (page === "screen") {
      add("📺 ลองโหมดรอ", null, () => window.startAttract && window.startAttract());
      add("📢 ลองประกาศ", null, () => {
        if (!window.runAnnouncements) return;
        annQueue.push({ id: "demo-" + Date.now(), text: "ได้เวลาพักเที่ยงแล้วครับ ทานข้าวให้อร่อยนะครับ",   // eslint-disable-line no-undef
          text_en: "It's lunchtime. Enjoy your meal!", at: Date.now() });
        window.runAnnouncements();
      });
    }
    if (page !== "screen") add("💬 หน้าแชท", "index.html");
    if (page !== "face") add("🤖 หน้าหุ่น", "face.html");
    if (page !== "stats") add("📊 สถิติ", "stats.html");
    const tag = document.createElement("span");
    tag.textContent = page === "stats" ? "DEMO · ข้อมูลตัวอย่าง" : "DEMO";
    tag.title = "เดโม — ไม่มี AI";
    tag.className = "tag";
    tag.addEventListener("click", () => bar.classList.toggle("open"));
    bar.appendChild(tag);
    if (page === "stats") document.body.prepend(bar); else document.body.appendChild(bar);
  });
})();
