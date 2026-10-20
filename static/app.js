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
  const state = { lang: store.get("saathi.lang", "te"), token: store.get("saathi.token", null), user: null, chat: [] };

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
    if (navigate) go("#/ask");
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

  function serviceCardHtml(svc, queryId) {
    if (!svc) return "";
    const docs = svc.documents.map((d) => `<li>${esc(d.name)}</li>`).join("");
    return `<div class="card svc-card">
      <h3>${esc(svc.name)}</h3>
      <div class="facts"><span>${esc(t("fee"))}: ₹${svc.fee_inr}</span><span>~${svc.sla_days} ${esc(t("days"))}</span><span>${esc(svc.department)}</span></div>
      <h4>${esc(t("documents"))}</h4><ul>${docs}</ul>
      <p class="muted">${esc(t("sample"))}</p>
      <div class="row">
        <a class="btn" href="#/new/${svc.id}">${esc(t("startApp"))}</a>
        <a class="btn secondary" href="#/centres">${esc(t("nearest"))}</a>
      </div>
    </div>`;
  }

  function feedbackHtml(queryId, serviceId) {
    return `<div class="row fb" data-q="${queryId}" data-s="${serviceId ?? ""}">
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
    const box = $("#chat");
    box.innerHTML = state.chat.map((m) => m.role === "user"
      ? `<div class="msg user">${esc(m.text)}</div>`
      : `<div class="msg bot">${esc(shortReply(m))}
           <div class="row" style="margin-top:.4rem"><button class="chip say" data-i="${m.i}">${esc(t("listen"))}</button></div>
           ${serviceCardHtml(m.service, m.query_id)}
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
    state.chat.push({ role: "user", text }); renderChat();
    try {
      const r = await api("/api/assistant/ask", { method: "POST", body: { text, lang: state.lang } });
      state.chat.push({ role: "bot", i: state.chat.length, ...r }); renderChat(); announce(r.reply);
    } catch (e) { state.chat.push({ role: "bot", i: state.chat.length, reply: e.message }); renderChat(); }
  }

  async function viewAsk(run) {
    main.innerHTML = `<h1>${esc(t("askTitle"))}</h1><p class="muted">${esc(t("askHint"))}</p>
      <div id="popular"></div>
      <div id="chat" class="chat" aria-live="polite"></div>
      <form class="composer" id="askForm">
        <label class="sr-only" for="q">${esc(t("askPlaceholder"))}</label>
        <input id="q" type="text" autocomplete="off" placeholder="${esc(t("askPlaceholder"))}" maxlength="500">
        <button type="button" class="btn secondary" id="mic" aria-pressed="false">${esc(t("speak"))}</button>
        <button class="btn" type="submit">${esc(t("send"))}</button>
      </form>`;
    renderChat();
    if (!state.chat.length) {
      const svcs = await api("/api/services").catch(() => []);
      fresh(run);
      const pop = svcs.filter((s) => ["INC", "CST", "RES", "BIR", "PVC", "ELB"].includes(s.code));
      $("#popular").innerHTML = `<h2>${esc(t("popular"))}</h2><div class="chips">${pop.map((s) => `<button class="chip ask" data-text="${esc(s.name)}">${esc(s.name)}</button>`).join("")}</div>`;
      $("#popular").querySelectorAll(".ask").forEach((b) => b.addEventListener("click", () => ask(b.dataset.text)));
    }
    $("#askForm").addEventListener("submit", (e) => { e.preventDefault(); const q = $("#q"); ask(q.value); q.value = ""; q.focus(); });
    setupMic();
  }

  function setupMic() {
    const btn = $("#mic"); const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) { btn.addEventListener("click", () => toast(t("voiceUnsupported"))); return; }
    let rec = null;
    btn.addEventListener("click", () => {
      if (rec) { rec.stop(); return; }
      rec = new SR(); rec.lang = SPEECH[state.lang]; rec.interimResults = false; rec.maxAlternatives = 1;
      rec.onresult = (e) => ask(e.results[0][0].transcript);
      rec.onerror = () => toast(t("error"));
      rec.onend = () => { rec = null; btn.textContent = t("speak"); btn.setAttribute("aria-pressed", "false"); };
      rec.start(); btn.textContent = t("stop"); btn.setAttribute("aria-pressed", "true"); announce(t("listening"));
    });
  }

  async function viewServices() {
    main.innerHTML = `<h1>${esc(t("servicesTitle"))}</h1>
      <label for="s">${esc(t("search"))}</label><input id="s" type="search" placeholder="${esc(t("search"))}">
      <div id="list"></div>`;
    const load = async (q = "") => {
      const svcs = await api(`/api/services?q=${encodeURIComponent(q)}`);
      if (!$("#list")) return;
      $("#list").innerHTML = svcs.map((s) => `<div class="card list-item"><div><b>${esc(s.name)}</b>
        <div class="muted">${esc(s.category)} · ₹${s.fee_inr}</div></div><a class="btn secondary" href="#/service/${s.id}">→<span class="sr-only">${esc(s.name)}</span></a></div>`).join("");
    };
    let timer; $("#s").addEventListener("input", (e) => { clearTimeout(timer); timer = setTimeout(() => load(e.target.value), 250); });
    load();
  }

  async function viewService(id, run) {
    const s = await api(`/api/services/${id}`);
    fresh(run);
    main.innerHTML = `<h1>${esc(s.name)}</h1><p>${esc(s.description)}</p>
      <h2>${esc(t("eligibility"))}</h2><p>${esc(s.eligibility)}</p>${serviceCardHtml(s)}`;
  }

  function viewLogin(next) {
    main.innerHTML = `<h1>${esc(t("loginTitle"))}</h1>
      <form id="f1" class="card"><label for="m">${esc(t("mobile"))}</label>
        <input id="m" type="tel" inputmode="numeric" pattern="[6-9][0-9]{9}" maxlength="10" required autocomplete="tel-national">
        <div class="row" style="margin-top:.75rem"><button class="btn">${esc(t("getOtp"))}</button></div></form>
      <form id="f2" class="card" hidden>
        <p id="demo" class="muted"></p>
        <label for="o">${esc(t("otp"))}</label><input id="o" type="text" inputmode="numeric" maxlength="6" required autocomplete="one-time-code">
        <label for="n">${esc(t("yourName"))}</label><input id="n" type="text" maxlength="120" autocomplete="name">
        <div class="row" style="margin-top:.75rem"><button class="btn">${esc(t("verify"))}</button></div></form>`;
    $("#f1").addEventListener("submit", async (e) => {
      e.preventDefault();
      try {
        const r = await api("/api/auth/request-otp", { method: "POST", body: { mobile: $("#m").value } });
        $("#f2").hidden = false; $("#demo").textContent = r.demo_otp ? `${t("demoOtp")} ${r.demo_otp}` : ""; $("#o").focus();
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
        <div class="row" style="margin-top:.75rem"><button class="btn">${esc(t("create"))}</button></div></form>`;
    $("#fa").addEventListener("submit", async (e) => {
      e.preventDefault();
      try { const a = await api("/api/applications", { method: "POST", body: { service_id: s.id, applicant_name: $("#an").value, purpose: $("#pp").value } }); go(`#/application/${a.id}`); }
      catch (err) { toast(err.message); }
    });
  }

  async function viewApplications(run) {
    if (!state.token) return needLogin("#/applications");
    const apps = await api("/api/applications");
    fresh(run);
    main.innerHTML = `<h1>${esc(t("appsTitle"))}</h1>` + (apps.length ? apps.map((a) => `<div class="card list-item">
      <div><b>${esc(a.service.name)}</b><div class="muted">${esc(t("reference"))}: ${esc(a.reference_no)}</div></div>
      <div class="row">${statusChip(a.status)}<a class="btn secondary" href="#/application/${a.id}">→<span class="sr-only">${esc(a.reference_no)}</span></a></div></div>`).join("")
      : `<p class="card">${esc(t("noApps"))}</p>`);
  }

  async function viewApplication(id, run = routeRun) {
    if (!state.token) return needLogin(`#/application/${id}`);
    const a = await api(`/api/applications/${id}`);
    fresh(run);
    const editable = ["draft", "needs_documents"].includes(a.status);
    main.innerHTML = `<h1>${esc(a.service.name)}</h1>
      <p>${statusChip(a.status)} <span class="muted">${esc(t("reference"))}: ${esc(a.reference_no)}</span></p>
      <div class="explain"><b>${esc(t("whatThisMeans"))}:</b> ${esc(a.status_explained.meaning)}<br>
        <b>${esc(t("nextStep"))}:</b> ${esc(a.status_explained.next_step)}
        <div class="row" style="margin-top:.4rem"><button class="chip" id="sayStatus">${esc(t("listen"))}</button></div></div>
      ${a.remarks ? `<h2>${esc(t("remarks"))}</h2><p class="card">${esc(a.remarks)}</p>` : ""}
      <h2>${esc(t("checklist"))}</h2>
      <div class="card">${a.checklist.map((c) => `<div class="check"><input type="checkbox" id="c${c.id}" data-id="${c.id}" ${c.provided ? "checked" : ""} ${editable ? "" : "disabled"}>
        <label for="c${c.id}" style="margin:0;font-weight:400">${esc(c.document)}</label></div>`).join("")}</div>
      ${editable ? `<div class="row"><button class="btn" id="submitApp" ${a.ready ? "" : "disabled"}>${esc(t("submit"))}</button>
        ${a.ready ? "" : `<span class="muted">${esc(t("notReady"))}</span>`}
        ${a.status === "draft" ? `<button class="btn danger" id="del">${esc(t("deleteDraft"))}</button>` : ""}</div>` : ""}`;
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
      <div class="row"><button class="btn" id="loc">${esc(t("useLocation"))}</button></div>
      <label for="d">${esc(t("orDistrict"))}</label>
      <select id="d" class="field"><option value="">—</option>${districts.map((d) => `<option value="${d.id}">${esc(state.lang === "te" ? d.name_te : d.name_en)}</option>`).join("")}</select>
      <div id="clist"></div>`;
    const show = (rows) => { $("#clist").innerHTML = rows.map((c) => `<div class="card"><b>${esc(c.name)}</b>
      <div>${esc(c.address)}</div><div class="muted">${esc(c.open_hours)}${c.distance_km != null ? ` · ${c.distance_km} ${esc(t("km"))}` : ""}</div>
      <a class="btn secondary" href="${esc(c.map_url)}" target="_blank" rel="noopener">${esc(t("openMap"))}</a></div>`).join(""); };
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
    main.innerHTML = `<h1>${esc(t("alertsTitle"))}</h1>` + (n.items.length ? n.items.map((x) => `<div class="card" ${x.read ? "" : 'style="border-color:var(--accent)"'}>
      <b>${esc(x.title)}</b><p style="white-space:pre-line">${esc(x.body)}</p><span class="muted">${new Date(x.created_at).toLocaleString()}</span></div>`).join("")
      : `<p class="card">${esc(t("noAlerts"))}</p>`);
    await Promise.all(n.items.filter((x) => !x.read).map((x) => api(`/api/notifications/${x.id}/read`, { method: "POST" })));
    refreshBadge();
  }

  // ---------- router ----------
  async function route() {
    const run = ++routeRun;
    const [path, query] = (location.hash || "#/ask").slice(1).split("?");
    const parts = path.split("/").filter(Boolean);
    const params = new URLSearchParams(query || "");
    document.querySelectorAll("nav.main a").forEach((a) => a.toggleAttribute("aria-current", a.getAttribute("href") === `#/${parts[0] || "ask"}`));
    document.querySelectorAll("nav.main a[aria-current]").forEach((a) => a.setAttribute("aria-current", "page"));
    try {
      switch (parts[0]) {
        case "services": await viewServices(); break;
        case "service": await viewService(parts[1], run); break;
        case "login": viewLogin(params.get("next")); break;
        case "new": await viewNewApplication(parts[1], run); break;
        case "applications": await viewApplications(run); break;
        case "application": await viewApplication(parts[1], run); break;
        case "centres": await viewCentres(run); break;
        case "alerts": await viewAlerts(run); break;
        default: await viewAsk(run);
      }
    } catch (e) {
      if (e instanceof Stale || run !== routeRun) return;
      main.innerHTML = `<p class="card">${esc(e.message || t("error"))}</p>`;
    }
    if (run !== routeRun) return;
    main.querySelector("h1")?.setAttribute("tabindex", "-1"); main.querySelector("h1")?.focus({ preventScroll: true });
  }

  window.addEventListener("hashchange", route);
  applySize(); applyLang();
  (async () => {
    if (state.token) { try { state.user = await api("/api/auth/me"); } catch { /* expired */ } }
    refreshBadge(); route();
  })();
})();
