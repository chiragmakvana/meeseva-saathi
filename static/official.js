// Officials' dashboard: insights from citizen questions and feedback, and application processing.
(() => {
  "use strict";
  const $ = (s) => document.querySelector(s);
  const main = $("#main");
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const LANG = { en: "English", te: "Telugu", hi: "Hindi", ur: "Urdu" };
  const STATUSES = ["submitted", "under_verification", "needs_documents", "approved", "rejected"];
  let token = null;
  try { token = sessionStorage.getItem("saathi.official"); } catch { /* ignore */ }

  async function api(path, opts = {}) {
    const res = await fetch(path, { method: opts.method || "GET", headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
      body: opts.body ? JSON.stringify(opts.body) : undefined });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Request failed");
    return data;
  }

  function login() {
    main.innerHTML = `<h1>Official login</h1><form id="f" class="card">
      <label for="m">Official mobile number</label><input id="m" type="tel" maxlength="10" value="9000000001" required>
      <div class="row" style="margin-top:.75rem"><button class="btn">Get OTP</button></div>
      <div id="step2" hidden><p id="demo" class="muted"></p><label for="o">OTP</label><input id="o" type="text" maxlength="6">
      <div class="row" style="margin-top:.75rem"><button class="btn" type="button" id="v">Verify</button></div></div>
      <p id="err" role="alert" class="muted"></p></form>`;
    $("#f").addEventListener("submit", async (e) => {
      e.preventDefault();
      try { const r = await api("/api/auth/request-otp", { method: "POST", body: { mobile: $("#m").value } });
        $("#step2").hidden = false; $("#demo").textContent = r.demo_otp ? `Demo OTP: ${r.demo_otp}` : ""; $("#o").focus(); }
      catch (err) { $("#err").textContent = err.message; }
    });
    main.addEventListener("click", async (e) => {
      if (e.target.id !== "v") return;
      try { const r = await api("/api/auth/verify-otp", { method: "POST", body: { mobile: $("#m").value, otp: $("#o").value } });
        if (r.user.role !== "official") throw new Error("This number is not registered as an official.");
        token = r.token; try { sessionStorage.setItem("saathi.official", token); } catch { /* ignore */ } dashboard(); }
      catch (err) { $("#err").textContent = err.message; }
    });
  }

  const bars = (obj, label) => {
    const entries = Object.entries(obj || {}); const max = Math.max(1, ...entries.map(([, v]) => v));
    return entries.length ? `<table><tbody>${entries.map(([k, v]) => `<tr><td style="width:40%">${esc(label ? label(k) : k)}</td>
      <td><div class="bar" style="width:${(100 * v) / max}%" aria-hidden="true"></div></td><td style="width:3rem">${v}</td></tr>`).join("")}</tbody></table>` : `<p class="muted">No data yet.</p>`;
  };

  async function dashboard() {
    $("#logout").hidden = false;
    let ins, apps;
    try { [ins, apps] = await Promise.all([api("/api/admin/insights"), api("/api/admin/applications")]); }
    catch (e) { token = null; try { sessionStorage.removeItem("saathi.official"); } catch { /* ignore */ } return login(); }
    const q = ins.queries, f = ins.feedback;
    main.innerHTML = `<h1>Citizen service insights</h1>
      <div class="kpis">
        <div class="card kpi"><span class="muted">Questions asked</span><b>${q.total}</b></div>
        <div class="card kpi"><span class="muted">Answered from catalogue</span><b>${q.answered_pct ?? "–"}${q.answered_pct != null ? "%" : ""}</b></div>
        <div class="card kpi"><span class="muted">Unanswered (service gaps)</span><b>${q.unmatched}</b></div>
        <div class="card kpi"><span class="muted">Average rating</span><b>${f.avg_rating ?? "–"}</b></div>
      </div>
      <div class="card"><h2>Most requested services</h2>${bars(Object.fromEntries(q.top_services.map((s) => [s.service, s.count])))}</div>
      <div class="card"><h2>Questions by language</h2>${bars(q.by_language, (k) => LANG[k] || k)}</div>
      <div class="card"><h2>Recent questions the catalogue could not answer</h2>
        ${q.recent_unanswered.length ? `<table><thead><tr><th>Question</th><th>Language</th></tr></thead><tbody>${q.recent_unanswered.map((r) => `<tr><td>${esc(r.text)}</td><td>${esc(LANG[r.lang] || r.lang)}</td></tr>`).join("")}</tbody></table>` : `<p class="muted">None.</p>`}</div>
      <div class="card"><h2>Feedback (AI-tagged)</h2>
        <h3>Sentiment</h3>${bars(f.sentiment)}<h3>Topics</h3>${bars(f.topics)}
        ${f.recent.length ? `<table><thead><tr><th>Rating</th><th>Comment</th><th>Sentiment</th><th>Topic</th></tr></thead><tbody>${f.recent.map((r) => `<tr><td>${r.rating}/5</td><td>${esc(r.comment) || "–"}</td><td>${esc(r.sentiment)}</td><td>${esc(r.topic)}</td></tr>`).join("")}</tbody></table>` : ""}</div>
      <div class="card"><h2>Applications</h2>${bars(ins.applications.by_status)}
        <table><thead><tr><th>Reference</th><th>Service</th><th>Applicant</th><th>Docs</th><th>Status</th><th>Update</th></tr></thead><tbody>
        ${apps.map((a) => `<tr><td>${esc(a.reference_no)}</td><td>${esc(a.service)}</td><td>${esc(a.applicant_name)}</td><td>${a.documents_ready ? "Ready" : "Incomplete"}</td>
          <td>${esc(a.status)}</td><td>${a.status === "draft" ? '<span class="muted">Not submitted</span>' : `<label class="sr-only" for="s${a.id}">New status for ${esc(a.reference_no)}</label>
          <select id="s${a.id}" class="field">${STATUSES.map((s) => `<option ${s === a.status ? "selected" : ""}>${s}</option>`).join("")}</select>
          <label class="sr-only" for="r${a.id}">Remarks</label><input id="r${a.id}" type="text" placeholder="Remarks for the citizen" value="${esc(a.remarks)}">
          <button class="btn secondary upd" data-id="${a.id}">Save &amp; notify</button>`}</td></tr>`).join("")}</tbody></table></div>`;
    main.querySelectorAll(".upd").forEach((b) => b.addEventListener("click", async () => {
      const id = b.dataset.id;
      try { await api(`/api/admin/applications/${id}/status`, { method: "POST", body: { status: $(`#s${id}`).value, remarks: $(`#r${id}`).value } }); dashboard(); }
      catch (e) { alert(e.message); }
    }));
  }

  $("#logout").addEventListener("click", () => { token = null; try { sessionStorage.removeItem("saathi.official"); } catch { /* ignore */ } $("#logout").hidden = true; login(); });
  token ? dashboard() : login();
})();
