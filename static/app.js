// MeeSeva Saathi citizen app: a small hash-routed single-page app (no framework, no build step).
(() => {
  "use strict";
  const $ = (sel, el = document) => el.querySelector(sel);
  const main = $("#main");
  const SPEECH = { en: "en-IN", te: "te-IN", hi: "hi-IN", ur: "ur-IN" };
  const store = {
    get: (k, d) => { try { return localStorage.getItem(k) ?? d; } catch { return d; } },
    set: (k, v) => { try { v == null ? localStorage.removeItem(k) : localStorage.setItem(k, v); } catch { /* private mode */ } },
  };
  const state = { lang: store.get("saathi.lang", "te"), token: store.get("saathi.token", null), user: null, chat: [], pending: null };

  // ---------- icons (inline SVG, Feather-style) ----------
  const ICON = {
    cert: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M8 13h8M8 17h5"/>',
    land: '<path d="M3 21h18M5 21V7l7-4 7 4v14"/><path d="M9 21v-6h6v6"/>',
    reg: '<path d="M20 6 9 17l-5-5"/>',
    police: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    bill: '<path d="M13 2 3 14h9l-1 8 10-12h-9z"/>',
    ration: '<path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><path d="M3 6h18M16 10a4 4 0 0 1-8 0"/>',
    send: '<path d="m22 2-7 20-4-9-9-4z"/><path d="M22 2 11 13"/>',
    mic: '<path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2M12 19v4M8 23h8"/>',
    speaker: '<path d="M11 5 6 9H2v6h4l5 4z"/><path d="M15.5 8.5a5 5 0 0 1 0 7"/>',
    check: '<path d="M20 6 9 17l-5-5"/>',
    pin: '<path d="M21 10c0 7-9 13-9 13S3 17 3 10a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>',
    arrow: '<path d="M5 12h14M12 5l7 7-7 7"/>',
    chat: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
  };
  const ic = (name, size = "") => `<svg class="i" ${size ? `style="width:${size};height:${size}"` : ""} viewBox="0 0 24 24" aria-hidden="true">${ICON[name]}</svg>`;
  const CAT_ICON = { Certificates: "cert", "Land and property": "land", Registrations: "reg", "Police services": "police", "Bill payments": "bill", "Civil supplies": "ration" };
  const CAT_ORDER = ["Certificates", "Civil supplies", "Land and property", "Registrations", "Police services", "Bill payments"];

  // ---------- helpers ----------
  const t = (k) => (I18N[state.lang] && I18N[state.lang][k]) || I18N.en[k] || k;
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const announce = (msg) => { $("#live").textContent = msg; };
  function toast(msg) {
    const el = document.createElement("div"); el.className = "toast"; el.setAttribute("role", "status"); el.textContent = msg;
    document.body.appendChild(el); setTimeout(() => el.remove(), 3500);
  }
  async function api(path, { method = "GET", body } = {}) {
    const headers = { "Content-Type": "application/json" };
    if (state.token) headers.Authorization = `Bearer ${state.token}`;
    const sep = path.includes("?") ? "&" : "?";
    const res = await fetch(`${path}${sep}lang=${state.lang}`, { method, headers, body: body ? JSON.stringify(body) : undefined });
    if (res.status === 204) return null;
    const data = await res.json().catch(() => ({}));
    if (res.status === 401 && state.token) { logout(false); }
    if (!res.ok) { const err = new Error(typeof data.detail === "string" ? data.detail : (data.detail?.message || t("error"))); err.data = data.detail; err.status = res.status; throw err; }
    return data;
  }
  const statusChip = (s) => `<span class="status ${esc(s)}">${esc(t("status_" + s))}</span>`;
  const catName = (c) => t("cat_" + c);
  function speak(text) {
    if (!("speechSynthesis" in window)) return;
    speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text.replace(/[•·]/g, ",")); u.lang = SPEECH[state.lang]; speechSynthesis.speak(u);
  }

  // ---------- language & accessibility ----------
  function applyLang() {
    document.documentElement.lang = state.lang;
    document.documentElement.dir = state.lang === "ur" ? "rtl" : "ltr";
    document.querySelectorAll("[data-i18n]").forEach((el) => { el.textContent = t(el.dataset.i18n); });
    $("#lang").value = state.lang;
    $("#authBtn").textContent = state.token ? t("logout") : t("login");
    document.title = t("appName");
  }
  $("#lang").addEventListener("change", (e) => {
    state.lang = e.target.value; store.set("saathi.lang", state.lang); applyLang(); route();
    if (state.token) api("/api/auth/me", { method: "PATCH", body: { preferred_lang: state.lang } }).catch(() => {});
  });
  const sizes = ["", "text-lg", "text-xl"];
  let size = Number(store.get("saathi.size", 0));
  function applySize() { sizes.forEach((c) => c && document.documentElement.classList.remove(c)); if (sizes[size]) document.documentElement.classList.add(sizes[size]); }
  $("#textSize").addEventListener("click", () => { size = (size + 1) % sizes.length; store.set("saathi.size", size); applySize(); });
  $("#contrast").addEventListener("click", (e) => {
    const on = document.documentElement.classList.toggle("contrast"); e.currentTarget.setAttribute("aria-pressed", on); store.set("saathi.contrast", on ? "1" : null);
  });
  if (store.get("saathi.contrast")) { document.documentElement.classList.add("contrast"); $("#contrast").setAttribute("aria-pressed", "true"); }
  $("#authBtn").addEventListener("click", () => (state.token ? logout(true) : go("#/login")));

  function logout(navigate) {
    state.token = null; state.user = null; store.set("saathi.token", null); applyLang(); refreshBadge();
    if (navigate) go("#/");
  }
  const go = (hash) => { if (location.hash === hash) route(); else location.hash = hash; };
  function needLogin(next) { toast(t("loginNeeded")); go(`#/login?next=${encodeURIComponent(next)}`); }

  async function refreshBadge() {
    const b = $("#alertBadge");
    if (!state.token) { b.hidden = true; return; }
    try { const n = await api("/api/notifications"); b.hidden = !n.unread; b.textContent = n.unread; } catch { b.hidden = true; }
  }

  // ---------- views ----------
  // Each navigation gets a run number; a view that finishes after the user has moved on stops quietly
  // instead of overwriting the newer page (e.g. changing language while a page is loading).
  let routeRun = 0;
  class Stale extends Error {}
  const fresh = (run) => { if (run !== routeRun) throw new Stale(); };

  function serviceCardHtml(svc) {
    if (!svc) return "";
    const docs = svc.documents.map((d) => `<li>${ic("check")}<span>${esc(d.name)}</span></li>`).join("");
    const time = svc.sla_days ? `~${svc.sla_days} <small>${esc(t("days"))}</small>` : "—";
    return `<div class="card svc-card">
      <div class="dept">${esc(svc.department)}</div>
      <h3>${esc(svc.name)}</h3>
      <div class="facts"><div>${esc(t("fee"))}<b>₹${svc.fee_inr}</b></div><div>${esc(t("tl3"))}<b>${time}</b></div><div>${esc(t("documents"))}<b>${svc.documents.length}</b></div></div>
      <h4 style="margin:.2rem 0">${esc(t("documents"))}</h4><ul class="doclist">${docs}</ul>
      <p class="note">${esc(t("sample"))}</p>
      <div class="row" style="margin-top:.6rem">
        <a class="btn" href="#/new/${svc.id}">${ic("cert")} ${esc(t("startApp"))}</a>
        <a class="btn secondary" href="#/centres">${ic("pin")} ${esc(t("nearest"))}</a>
      </div>
    </div>`;
  }

  function feedbackHtml(queryId, serviceId) {
    return `<div class="row fb" data-q="${queryId}" data-s="${serviceId ?? ""}" style="margin-top:.5rem">
      <span class="muted">${esc(t("helpful"))}</span>
      <button class="chip" data-r="5">${esc(t("yes"))}</button><button class="chip" data-r="2">${esc(t("no"))}</button>
    </div>`;
  }

  // With a service card on screen, show only the first and last line of the reply (the card lists the
  // documents); "Listen" still reads the full answer aloud for citizens who prefer audio.
  function shortReply(m) {
    if (!m.service || m.source !== "rules") return m.reply;
    const lines = m.reply.split("\n").filter(Boolean);
    return lines.length > 2 ? `${lines[0]}\n${lines[lines.length - 1]}` : m.reply;
  }

  function renderChat() {
    const box = $("#chat"); if (!box) return;
    box.innerHTML = state.chat.map((m) => m.role === "user"
      ? `<div class="msg user">${esc(m.text)}</div>`
      : `<div class="msg bot">
           <div class="who"><span class="av" aria-hidden="true">S</span>${esc(t("appName"))}${m.source ? `<span class="src">${esc(t("answeredBy"))}: ${esc(m.source === "ai" ? t("engineAI") : t("engineRules"))}</span>` : ""}</div>
           ${esc(shortReply(m))}
           <div class="row" style="margin-top:.5rem"><button class="chip say" data-i="${m.i}">${ic("speaker")} ${esc(t("listen"))}</button></div>
           ${serviceCardHtml(m.service)}
           ${m.suggestions?.length ? `<div class="chips">${m.suggestions.map((s) => `<button class="chip ask" data-text="${esc(s.name)}">${esc(s.name)}</button>`).join("")}</div>` : ""}
           ${state.token && m.query_id ? feedbackHtml(m.query_id, m.service?.id) : ""}
         </div>`).join("");
    box.querySelectorAll(".say").forEach((b) => b.addEventListener("click", () => speak(state.chat[b.dataset.i].reply)));
    box.querySelectorAll(".ask").forEach((b) => b.addEventListener("click", () => ask(b.dataset.text)));
    box.querySelectorAll(".fb button").forEach((b) => b.addEventListener("click", () => sendFeedback(b)));
    box.lastElementChild?.scrollIntoView({ block: "nearest" });
  }

  async function sendFeedback(btn) {
    const wrap = btn.closest(".fb"); const rating = Number(btn.dataset.r);
    let comment = "";
    if (rating < 4) comment = window.prompt(t("whatWrong")) || "";
    try {
      await api("/api/feedback", { method: "POST", body: { rating, comment, query_id: Number(wrap.dataset.q), service_id: wrap.dataset.s ? Number(wrap.dataset.s) : null } });
      wrap.innerHTML = `<span class="muted">${esc(t("thanks"))}</span>`; announce(t("thanks"));
    } catch (e) { toast(e.message); }
  }

  async function ask(text) {
    text = (text || "").trim(); if (text.length < 2) return;
    if (!$("#chat")) { state.pending = text; go("#/ask"); return; }
    state.chat.push({ role: "user", text }); renderChat();
    try {
      const r = await api("/api/assistant/ask", { method: "POST", body: { text, lang: state.lang } });
      state.chat.push({ role: "bot", i: state.chat.length, ...r }); renderChat(); announce(r.reply);
    } catch (e) { state.chat.push({ role: "bot", i: state.chat.length, reply: e.message }); renderChat(); }
  }

  function composerHtml(id) {
    return `<form class="composer" id="${id}">
      <label class="sr-only" for="${id}-q">${esc(t("askPlaceholder"))}</label>
      <input id="${id}-q" type="text" autocomplete="off" placeholder="${esc(t("askPlaceholder"))}" maxlength="500">
      <button type="button" class="btn secondary mic" aria-pressed="false">${ic("mic")} ${esc(t("speak"))}</button>
      <button class="btn" type="submit">${ic("send")} ${esc(t("send"))}</button>
    </form>`;
  }
  function wireComposer(id) {
    const form = $(`#${id}`); const input = $(`#${id}-q`); const btn = form.querySelector(".mic");
    form.addEventListener("submit", (e) => { e.preventDefault(); const q = input.value; input.value = ""; ask(q); });
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) { btn.addEventListener("click", () => toast(t("voiceUnsupported"))); return; }
    let rec = null;
    btn.addEventListener("click", () => {
      if (rec) { rec.stop(); return; }
      rec = new SR(); rec.lang = SPEECH[state.lang]; rec.interimResults = false; rec.maxAlternatives = 1;
      rec.onresult = (e) => ask(e.results[0][0].transcript);
      rec.onerror = () => toast(t("error"));
      rec.onend = () => { rec = null; btn.innerHTML = `${ic("mic")} ${esc(t("speak"))}`; btn.setAttribute("aria-pressed", "false"); };
      rec.start(); btn.innerHTML = `${ic("mic")} ${esc(t("stop"))}`; btn.setAttribute("aria-pressed", "true"); announce(t("listening"));
    });
  }

  async function viewHome(run) {
    const svcs = await api("/api/services").catch(() => []);
    fresh(run);
    const counts = {}; svcs.forEach((s) => { counts[s.category] = (counts[s.category] || 0) + 1; });
    const cats = CAT_ORDER.filter((c) => counts[c]);
    const pop = svcs.filter((s) => ["INC", "CST", "RES", "BIR", "RAT", "PVC"].includes(s.code));
    main.innerHTML = `
      <section class="hero"><h1>${esc(t("heroTitle"))}</h1><p>${esc(t("heroSub"))}</p>${composerHtml("home")}</section>
      <h2>${esc(t("popular"))}</h2>
      <div class="chips">${pop.map((s) => `<button class="chip ask" data-text="${esc(s.name)}">${esc(s.name)}</button>`).join("")}</div>
      <h2>${esc(t("browse"))}</h2>
      <div class="tiles">${cats.map((c) => `<a class="tile" href="#/services?category=${encodeURIComponent(c)}"><span class="ic">${ic(CAT_ICON[c], "26px")}</span><b>${esc(catName(c))}</b><small>${counts[c]} ${esc(t("services"))}</small></a>`).join("")}</div>
      <h2>${esc(t("howTitle"))}</h2>
      <div class="steps"><div><b>1 · ${esc(t("step1"))}</b>${esc(t("step1d"))}</div><div><b>2 · ${esc(t("step2"))}</b>${esc(t("step2d"))}</div><div><b>3 · ${esc(t("step3"))}</b>${esc(t("step3d"))}</div></div>`;
    main.querySelectorAll(".ask").forEach((b) => b.addEventListener("click", () => ask(b.dataset.text)));
    wireComposer("home");
  }

  async function viewAsk() {
    main.innerHTML = `<h1>${esc(t("askTitle"))}</h1><p class="muted">${esc(t("askHint"))}</p>
      <div id="popular"></div><div id="chat" class="chat" aria-live="polite"></div>${composerHtml("askForm")}`;
    renderChat(); wireComposer("askForm");
    if (state.pending) { const q = state.pending; state.pending = null; ask(q); }
    else if (!state.chat.length) {
      const svcs = await api("/api/services").catch(() => []);
      if (!$("#popular")) return;
      const pop = svcs.filter((s) => ["INC", "CST", "RES", "BIR", "PVC", "ELB"].includes(s.code));
      $("#popular").innerHTML = `<h2>${esc(t("popular"))}</h2><div class="chips">${pop.map((s) => `<button class="chip ask" data-text="${esc(s.name)}">${esc(s.name)}</button>`).join("")}</div>`;
      $("#popular").querySelectorAll(".ask").forEach((b) => b.addEventListener("click", () => ask(b.dataset.text)));
    }
    $("#askForm-q")?.focus({ preventScroll: true });
  }

  async function viewServices(category) {
    main.innerHTML = `<h1>${esc(category ? catName(category) : t("servicesTitle"))}</h1>
      <label for="s">${esc(t("search"))}</label><input id="s" type="search" placeholder="${esc(t("search"))}">
      <div id="list"></div>`;
    const load = async (q = "") => {
      const svcs = await api(`/api/services?q=${encodeURIComponent(q)}${category && !q ? `&category=${encodeURIComponent(category)}` : ""}`);
      if (!$("#list")) return;
      let last = "";
      $("#list").innerHTML = svcs.map((s) => {
        const head = s.category !== last && !category && !q ? `<h2>${ic(CAT_ICON[s.category] || "cert")} ${esc(catName(s.category))}</h2>` : "";
        last = s.category;
        return `${head}<a class="card list-item" href="#/service/${s.id}" style="text-decoration:none;color:inherit"><div><b>${esc(s.name)}</b>
          <div class="muted">₹${s.fee_inr}${s.sla_days ? ` · ~${s.sla_days} ${esc(t("days"))}` : ""}</div></div>${ic("arrow")}</a>`;
      }).join("");
    };
    let timer; $("#s").addEventListener("input", (e) => { clearTimeout(timer); timer = setTimeout(() => load(e.target.value), 250); });
    load();
  }

  async function viewService(id, run) {
    const s = await api(`/api/services/${id}`);
    fresh(run);
    main.innerHTML = `<a href="#/services" class="muted">← ${esc(t("back"))}</a><h1>${esc(s.name)}</h1><p>${esc(s.description)}</p>
      <h2>${esc(t("eligibility"))}</h2><p>${esc(s.eligibility)}</p>${serviceCardHtml(s)}
      <button class="chip ask" data-text="${esc(s.name)}">${ic("chat")} ${esc(t("askAbout"))}</button>`;
    main.querySelector(".ask").addEventListener("click", (e) => ask(e.currentTarget.dataset.text));
  }

  function viewLogin(next) {
    main.innerHTML = `<h1>${esc(t("loginTitle"))}</h1>
      <form id="f1" class="card"><label for="m">${esc(t("mobile"))}</label>
        <input id="m" type="tel" inputmode="numeric" pattern="[6-9][0-9]{9}" maxlength="10" required autocomplete="tel-national">
        <div class="row" style="margin-top:.75rem"><button class="btn">${esc(t("getOtp"))}</button></div></form>
      <form id="f2" class="card" hidden>
        <p id="demo" class="note"></p>
        <label for="o">${esc(t("otp"))}</label><input id="o" type="text" inputmode="numeric" maxlength="6" required autocomplete="one-time-code">
        <label for="n">${esc(t("yourName"))}</label><input id="n" type="text" maxlength="120" autocomplete="name">
        <div class="row" style="margin-top:.75rem"><button class="btn">${esc(t("verify"))}</button></div></form>`;
    $("#f1").addEventListener("submit", async (e) => {
      e.preventDefault();
      try {
        const r = await api("/api/auth/request-otp", { method: "POST", body: { mobile: $("#m").value } });
        $("#f2").hidden = false; $("#demo").textContent = r.demo_otp ? `${t("demoOtp")} ${r.demo_otp}` : ""; $("#demo").hidden = !r.demo_otp; $("#o").focus();
      } catch (err) { toast(err.message); }
    });
    $("#f2").addEventListener("submit", async (e) => {
      e.preventDefault();
      try {
        const r = await api("/api/auth/verify-otp", { method: "POST", body: { mobile: $("#m").value, otp: $("#o").value, name: $("#n").value, preferred_lang: state.lang } });
        state.token = r.token; state.user = r.user; store.set("saathi.token", r.token); applyLang(); refreshBadge();
        go(next || "#/applications");
      } catch (err) { toast(err.message); }
    });
  }

  async function viewNewApplication(serviceId, run) {
    if (!state.token) return needLogin(`#/new/${serviceId}`);
    const s = await api(`/api/services/${serviceId}`);
    const me = state.user || await api("/api/auth/me");
    fresh(run);
    main.innerHTML = `<h1>${esc(s.name)}</h1>
      <form id="fa" class="card"><label for="an">${esc(t("applicantName"))}</label>
        <input id="an" type="text" required minlength="2" maxlength="120" value="${esc(me.name)}">
        <label for="pp">${esc(t("purpose"))}</label><input id="pp" type="text" maxlength="255">
        <div class="row" style="margin-top:.75rem"><button class="btn">${ic("check")} ${esc(t("create"))}</button></div></form>`;
    $("#fa").addEventListener("submit", async (e) => {
      e.preventDefault();
      try { const a = await api("/api/applications", { method: "POST", body: { service_id: s.id, applicant_name: $("#an").value, purpose: $("#pp").value } }); go(`#/application/${a.id}`); }
      catch (err) { toast(err.message); }
    });
  }

  const progressHtml = (a) => { const done = a.checklist.filter((c) => c.provided).length; return `<div class="progress" role="progressbar" aria-valuenow="${done}" aria-valuemax="${a.checklist.length}" aria-label="${esc(t("docsReady"))}"><i style="width:${(100 * done) / a.checklist.length}%"></i></div><small class="muted">${done}/${a.checklist.length} ${esc(t("docsReady"))}</small>`; };

  async function viewApplications(run) {
    if (!state.token) return needLogin("#/applications");
    const apps = await api("/api/applications");
    fresh(run);
    main.innerHTML = `<h1>${esc(t("appsTitle"))}</h1>` + (apps.length ? apps.map((a) => `<a class="card list-item" href="#/application/${a.id}" style="text-decoration:none;color:inherit">
      <div style="flex:1"><b>${esc(a.service.name)}</b><div class="muted">${esc(t("reference"))}: ${esc(a.reference_no)}</div>${a.status === "draft" ? progressHtml(a) : ""}</div>
      <div class="row">${statusChip(a.status)}${ic("arrow")}</div></a>`).join("")
      : `<p class="card">${esc(t("noApps"))}</p>`);
  }

  function timelineHtml(status) {
    const idx = { draft: 0, submitted: 1, under_verification: 2, needs_documents: 2, approved: 3, rejected: 3 }[status];
    const labels = [t("tl1"), t("tl2"), t("tl3"), t("tl4")];
    return `<div class="timeline" aria-label="${esc(t("status_" + status))}">${labels.map((l, i) => {
      const cls = i < idx ? "done" : i === idx ? (status === "rejected" ? "bad now" : "now") : "";
      return `<div class="${cls}">${esc(i === 3 && idx === 3 ? t("status_" + status) : l)}</div>`;
    }).join("")}</div>`;
  }

  async function viewApplication(id, run = routeRun) {
    if (!state.token) return needLogin(`#/application/${id}`);
    const a = await api(`/api/applications/${id}`);
    fresh(run);
    const editable = ["draft", "needs_documents"].includes(a.status);
    main.innerHTML = `<a href="#/applications" class="muted">← ${esc(t("back"))}</a><h1>${esc(a.service.name)}</h1>
      <p>${statusChip(a.status)} <span class="muted">${esc(t("reference"))}: ${esc(a.reference_no)}</span></p>
      ${timelineHtml(a.status)}
      <div class="explain"><b>${esc(t("whatThisMeans"))}:</b> ${esc(a.status_explained.meaning)}<br>
        <b>${esc(t("nextStep"))}:</b> ${esc(a.status_explained.next_step)}
        <div class="row" style="margin-top:.5rem"><button class="chip" id="sayStatus">${ic("speaker")} ${esc(t("listen"))}</button></div></div>
      ${a.remarks ? `<h2>${esc(t("remarks"))}</h2><p class="card note">${esc(a.remarks)}</p>` : ""}
      <h2>${esc(t("checklist"))}</h2>
      <div class="card">${progressHtml(a)}${a.checklist.map((c) => `<div class="check"><input type="checkbox" id="c${c.id}" data-id="${c.id}" ${c.provided ? "checked" : ""} ${editable ? "" : "disabled"}>
        <label for="c${c.id}" style="margin:0;font-weight:400">${esc(c.document)}</label></div>`).join("")}</div>
      ${editable ? `<div class="row"><button class="btn accent" id="submitApp" ${a.ready ? "" : "disabled"}>${ic("send")} ${esc(t("submit"))}</button>
        ${a.ready ? "" : `<span class="muted">${esc(t("notReady"))}</span>`}
        ${a.status === "draft" ? `<button class="btn danger" id="del">${esc(t("deleteDraft"))}</button>` : ""}</div>` : ""}
      ${a.status === "approved" ? `<p class="row"><a class="btn secondary" href="#/centres">${ic("pin")} ${esc(t("nearest"))}</a></p>` : ""}`;
    $("#sayStatus").addEventListener("click", () => speak(`${a.status_explained.meaning} ${a.status_explained.next_step}`));
    main.querySelectorAll(".check input").forEach((cb) => cb.addEventListener("change", async () => {
      try { await api(`/api/applications/${a.id}/checklist/${cb.dataset.id}`, { method: "PUT", body: { provided: cb.checked } }); viewApplication(id).catch(() => {}); }
      catch (e) { toast(e.message); }
    }));
    $("#submitApp")?.addEventListener("click", async () => {
      try { await api(`/api/applications/${a.id}/submit`, { method: "POST" }); viewApplication(id).catch(() => {}); announce(t("status_submitted")); }
      catch (e) { toast(e.data?.missing ? `${e.message}: ${e.data.missing.join(", ")}` : e.message); }
    });
    $("#del")?.addEventListener("click", async () => { await api(`/api/applications/${a.id}`, { method: "DELETE" }); go("#/applications"); });
  }

  async function viewCentres(run) {
    const districts = await api("/api/districts");
    fresh(run);
    main.innerHTML = `<h1>${esc(t("centresTitle"))}</h1>
      <div class="row"><button class="btn" id="loc">${ic("pin")} ${esc(t("useLocation"))}</button></div>
      <label for="d">${esc(t("orDistrict"))}</label>
      <select id="d" class="field"><option value="">—</option>${districts.map((d) => `<option value="${d.id}">${esc(state.lang === "te" ? d.name_te : d.name_en)}</option>`).join("")}</select>
      <div id="clist"></div>`;
    const show = (rows) => { if ($("#clist")) $("#clist").innerHTML = rows.map((c) => `<div class="card"><b>${esc(c.name)}</b>
      <div>${esc(c.address)}</div><div class="muted">${esc(c.open_hours)}${c.distance_km != null ? ` · ${c.distance_km} ${esc(t("km"))}` : ""}</div>
      <a class="btn secondary" style="margin-top:.5rem" href="${esc(c.map_url)}" target="_blank" rel="noopener">${ic("pin")} ${esc(t("openMap"))}</a></div>`).join(""); };
    $("#d").addEventListener("change", async (e) => show(await api(`/api/centres?district_id=${e.target.value}&limit=10`)));
    $("#loc").addEventListener("click", () => {
      if (!navigator.geolocation) return toast(t("error"));
      navigator.geolocation.getCurrentPosition(async (p) => show(await api(`/api/centres?lat=${p.coords.latitude}&lng=${p.coords.longitude}`)), () => toast(t("error")));
    });
    const initial = await api("/api/centres?limit=5");
    fresh(run);
    show(initial);
  }

  async function viewAlerts(run) {
    if (!state.token) return needLogin("#/alerts");
    const n = await api("/api/notifications");
    fresh(run);
    main.innerHTML = `<h1>${esc(t("alertsTitle"))}</h1>` + (n.items.length ? n.items.map((x) => `<div class="card" ${x.read ? "" : 'style="border-inline-start:4px solid var(--accent)"'}>
      <b>${esc(x.title)}</b><p style="white-space:pre-line">${esc(x.body)}</p><span class="muted">${new Date(x.created_at).toLocaleString()}</span></div>`).join("")
      : `<p class="card">${esc(t("noAlerts"))}</p>`);
    await Promise.all(n.items.filter((x) => !x.read).map((x) => api(`/api/notifications/${x.id}/read`, { method: "POST" })));
    refreshBadge();
  }

  // Research page for evaluators (English; figures from the official MeeSeva portal and government sources, Oct 2026).
  function viewAbout() {
    main.innerHTML = `<h1>Why MeeSeva Saathi</h1>
      <p class="muted">What we learned about MeeSeva before building, and how each finding shaped the prototype. Full notes and sources: <a href="https://github.com/chiragmakvana/meeseva-saathi/blob/main/docs/RESEARCH.md" target="_blank" rel="noopener">docs/RESEARCH.md</a>.</p>
      <div class="kpis">
        <div class="card kpi"><span class="ic">${ic("cert", "22px")}</span><div><b>391</b><span>active services, 38 departments</span></div></div>
        <div class="card kpi"><span class="ic">${ic("pin", "22px")}</span><div><b>5,265</b><span>MeeSeva centres</span></div></div>
        <div class="card kpi"><span class="ic">${ic("bill", "22px")}</span><div><b>32.5 lakh</b><span>transactions in Aug 2026</span></div></div>
        <div class="card kpi"><span class="ic">${ic("police", "22px")}</span><div><b>42 lakh</b><span>applications pending beyond SLA (since Jan 2025)</span></div></div>
      </div>
      <p class="stat-note">Source: MeeSeva portal statistics, ts.meeseva.telangana.gov.in (read 21 Oct 2026). Pending and rejection counts are the portal's own figures.</p>
      <h2>Findings → design decisions</h2>
      <div class="grid2">
        <div class="card"><h3>Citizens describe a need, not a certificate</h3><p>"My father passed away, we need the pension" is a death certificate and then a family-member certificate. The portal expects you to already know the service name.</p><p><b>→</b> Saathi maps needs to services, in the citizen's words, and asks one clarifying question when unsure.</p></div>
        <div class="card"><h3>Documents are the main cause of delay</h3><p>A Telangana Police SOP records that unclear or blank uploads lead to delays and repeat visits; 92 lakh requests have been rejected historically.</p><p><b>→</b> A per-service document checklist that must be complete before submission, and remarks that tell the citizen exactly what to bring.</p></div>
        <div class="card"><h3>Language is a barrier</h3><p>The portal is available in English and Telugu only. Hyderabad alone has a large Urdu-speaking population, and many first-time users read neither English nor formal Telugu.</p><p><b>→</b> Telugu, Hindi and Urdu alongside English, with voice input and read-aloud, and plain-language wording.</p></div>
        <div class="card"><h3>"Under verification" explains nothing</h3><p>Guides and RTI services exist only because citizens cannot tell what a status means or what to do next.</p><p><b>→</b> Every status comes with "what this means" and "what to do next", in the citizen's language, and a notification when it changes.</p></div>
        <div class="card"><h3>The ESD wing cannot see what citizens struggle with</h3><p>Complaints are scattered across centres, RTI requests and social media.</p><p><b>→</b> An officials' dashboard: most-asked services, questions the catalogue could not answer (service gaps), and feedback tagged by sentiment and topic.</p></div>
        <div class="card"><h3>MeeSeva on WhatsApp (Nov 2025) is the right channel</h3><p>The state launched an AI chat on WhatsApp for 580+ services. Citizens still need help <i>before</i> they apply.</p><p><b>→</b> Saathi is built as an API-first assistant that can sit behind the WhatsApp channel, the portal and centre kiosks alike.</p></div>
      </div>
      <h2>Standards</h2>
      <div class="card"><p>Built to the intent of <b>GIGW 3.0</b> (Guidelines for Indian Government Websites and Apps) and <b>WCAG 2.1 AA</b>: Indian-language support, screen-reader labels, keyboard operation, visible focus, three text sizes, high-contrast mode, 44 px touch targets, right-to-left Urdu, reduced-motion support, and a page weight that works over 4G.</p>
      <p class="muted">Official service timelines used in the catalogue (income 7 days, residence 6, caste and family-member 30, late registration 60) are from the MeeSeva revenue service catalogue. Fees and centre details are sample data.</p></div>`;
  }

  // ---------- router ----------
  async function route() {
    const run = ++routeRun;
    const [path, query] = (location.hash || "#/").slice(1).split("?");
    const parts = path.split("/").filter(Boolean);
    const params = new URLSearchParams(query || "");
    const current = parts[0] || "home";
    document.querySelectorAll("nav.main a").forEach((a) => { if (a.dataset.nav === current) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current"); });
    try {
      switch (parts[0]) {
        case "ask": await viewAsk(); break;
        case "services": await viewServices(params.get("category")); break;
        case "service": await viewService(parts[1], run); break;
        case "login": viewLogin(params.get("next")); break;
        case "new": await viewNewApplication(parts[1], run); break;
        case "applications": await viewApplications(run); break;
        case "application": await viewApplication(parts[1], run); break;
        case "centres": await viewCentres(run); break;
        case "alerts": await viewAlerts(run); break;
        case "about": viewAbout(); break;
        default: await viewHome(run);
      }
    } catch (e) {
      if (e instanceof Stale || run !== routeRun) return;
      main.innerHTML = `<p class="card">${esc(e.message || t("error"))}</p>`;
    }
    if (run !== routeRun) return;
    if (!["ask", undefined].includes(parts[0])) { main.querySelector("h1")?.setAttribute("tabindex", "-1"); main.querySelector("h1")?.focus({ preventScroll: true }); }
  }

  window.addEventListener("hashchange", route);
  applySize(); applyLang();
  (async () => {
    if (state.token) { try { state.user = await api("/api/auth/me"); } catch { /* expired */ } }
    refreshBadge(); route();
  })();
})();
