// Officials' dashboard: insights from citizen questions and feedback, and application processing.
(() => {
  "use strict";
  const $ = (s) => document.querySelector(s);
  const main = $("#main");
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const LANG = { en: "English", te: "Telugu", hi: "Hindi", ur: "Urdu" };
  const STATUS_LABEL = { draft: "Draft", submitted: "Submitted", under_verification: "Under verification", needs_documents: "Needs documents", approved: "Approved", rejected: "Rejected" };
  const STATUSES = ["submitted", "under_verification", "needs_documents", "approved", "rejected"];
  const I = {
    chat: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>', check: '<path d="M20 6 9 17l-5-5"/>',
    alert: '<circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/>', star: '<path d="m12 2 3.1 6.3 6.9 1-5 4.9 1.2 6.8L12 17.8 5.8 21l1.2-6.8-5-4.9 6.9-1z"/>',
  };
  const ic = (n) => `<svg class="i" style="width:22px;height:22px" viewBox="0 0 24 24" aria-hidden="true">${I[n]}</svg>`;
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
    main.innerHTML = `<h1>Official login</h1><form id="f" class="card" style="max-width:520px">
      <label for="m">Official mobile number</label><input id="m" type="tel" maxlength="10" value="9000000001" required>
      <div class="row" style="margin-top:.75rem"><button class="btn">Get OTP</button></div>
      <div id="step2" hidden><p id="demo" class="note"></p><label for="o">OTP</label><input id="o" type="text" maxlength="6">
      <div class="row" style="margin-top:.75rem"><button class="btn" type="button" id="v">Verify</button></div></div>
      <p id="err" role="alert" class="muted"></p></form>`;
    $("#f").addEventListener("submit", async (e) => {
      e.preventDefault();
      try { const r = await api("/api/auth/request-otp", { method: "POST", body: { mobile: $("#m").value } });
        $("#step2").hidden = false; $("#demo").textContent = r.demo_otp ? `Demo OTP (no SMS in the prototype): ${r.demo_otp}` : ""; $("#o").focus(); }
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
    const entries = Object.entries(obj || {}).sort((a, b) => b[1] - a[1]); const max = Math.max(1, ...entries.map(([, v]) => v));
    return entries.length ? `<table><tbody>${entries.map(([k, v]) => `<tr><td style="width:45%">${esc(label ? label(k) : k)}</td>
      <td><div class="bar" style="width:${(100 * v) / max}%" aria-hidden="true"></div></td><td style="width:3rem;text-align:end"><b>${v}</b></td></tr>`).join("")}</tbody></table>` : `<p class="muted">No data yet.</p>`;
  };
  const pill = (s) => `<span class="pill ${esc(s)}">${esc(s)}</span>`;

  async function dashboard() {
    $("#logout").hidden = false;
    let ins, apps;
    try { [ins, apps] = await Promise.all([api("/api/admin/insights"), api("/api/admin/applications")]); }
    catch (e) { token = null; try { sessionStorage.removeItem("saathi.official"); } catch { /* ignore */ } return login(); }
    const q = ins.queries, f = ins.feedback;
    const pendingBeyond = apps.filter((a) => a.status === "submitted" || a.status === "under_verification").length;
    main.innerHTML = `<h1>Citizen service insights</h1><p class="muted">Last 30 days · what citizens ask, where they get stuck, and how they feel.</p>
      <div class="kpis">
        <div class="card kpi"><span class="ic">${ic("chat")}</span><div><b>${q.total}</b><span>Questions asked</span></div></div>
        <div class="card kpi"><span class="ic">${ic("check")}</span><div><b>${q.answered_pct ?? "–"}${q.answered_pct != null ? "%" : ""}</b><span>Answered from the catalogue</span></div></div>
        <div class="card kpi"><span class="ic" style="background:var(--warn-soft);color:var(--warn)">${ic("alert")}</span><div><b>${q.unmatched}</b><span>Unanswered · service gaps</span></div></div>
        <div class="card kpi"><span class="ic" style="background:var(--ok-soft);color:var(--ok)">${ic("star")}</span><div><b>${f.avg_rating ?? "–"}</b><span>Average rating (${f.count})</span></div></div>
      </div>
      <div class="grid2" style="margin-top:.75rem">
        <div class="card"><h2 style="margin-top:0">Most requested services</h2>${bars(Object.fromEntries(q.top_services.map((s) => [s.service, s.count])))}</div>
        <div class="card"><h2 style="margin-top:0">Questions by language</h2>${bars(q.by_language, (k) => LANG[k] || k)}<p class="stat-note">The MeeSeva portal offers English and Telugu only.</p></div>
      </div>
      <div class="card"><h2 style="margin-top:0">Questions the catalogue could not answer <span class="muted" style="font-weight:400">· candidates for new services or better keywords</span></h2>
        ${q.recent_unanswered.length ? `<table><thead><tr><th>Question</th><th>Language</th><th>When</th></tr></thead><tbody>${q.recent_unanswered.map((r) => `<tr><td>${esc(r.text)}</td><td>${esc(LANG[r.lang] || r.lang)}</td><td class="muted">${new Date(r.at).toLocaleDateString()}</td></tr>`).join("")}</tbody></table>` : `<p class="muted">None.</p>`}</div>
      <div class="grid2">
        <div class="card"><h2 style="margin-top:0">Feedback sentiment <span class="muted" style="font-weight:400">· AI-tagged</span></h2>${bars(f.sentiment)}</div>
        <div class="card"><h2 style="margin-top:0">Feedback topics</h2>${bars(f.topics)}</div>
      </div>
      <div class="card"><h2 style="margin-top:0">Recent feedback</h2>
        ${f.recent.length ? `<table><thead><tr><th>Rating</th><th>Comment</th><th>Sentiment</th><th>Topic</th></tr></thead><tbody>${f.recent.map((r) => `<tr><td>${"★".repeat(r.rating)}<span style="color:var(--line)">${"★".repeat(5 - r.rating)}</span></td><td>${esc(r.comment) || "–"}</td><td>${pill(r.sentiment)}</td><td>${esc(r.topic)}</td></tr>`).join("")}</tbody></table>` : `<p class="muted">None yet.</p>`}</div>
      <div class="card"><h2 style="margin-top:0">Applications <span class="muted" style="font-weight:400">· ${pendingBeyond} awaiting action</span></h2>${bars(ins.applications.by_status, (k) => STATUS_LABEL[k] || k)}
        <table style="margin-top:.75rem"><thead><tr><th>Reference</th><th>Service</th><th>Applicant</th><th>Documents</th><th>Status</th><th>Update</th></tr></thead><tbody>
        ${apps.map((a) => `<tr><td><code>${esc(a.reference_no)}</code></td><td>${esc(a.service)}</td><td>${esc(a.applicant_name)}</td><td>${a.documents_ready ? '<span class="pill positive">Complete</span>' : '<span class="pill negative">Incomplete</span>'}</td>
          <td><span class="status ${esc(a.status)}">${esc(STATUS_LABEL[a.status])}</span></td><td>${a.status === "draft" ? '<span class="muted">Not submitted</span>' : `<label class="sr-only" for="s${a.id}">New status for ${esc(a.reference_no)}</label>
          <select id="s${a.id}" class="field">${STATUSES.map((s) => `<option value="${s}" ${s === a.status ? "selected" : ""}>${STATUS_LABEL[s]}</option>`).join("")}</select>
          <label class="sr-only" for="r${a.id}">Remarks</label><input id="r${a.id}" type="text" placeholder="Remarks for the citizen" value="${esc(a.remarks)}" style="margin-top:.3rem">
          <button class="btn secondary upd" data-id="${a.id}" style="margin-top:.3rem">Save &amp; notify</button>`}</td></tr>`).join("")}</tbody></table></div>`;
    main.querySelectorAll(".upd").forEach((b) => b.addEventListener("click", async () => {
      const id = b.dataset.id;
      try { await api(`/api/admin/applications/${id}/status`, { method: "POST", body: { status: $(`#s${id}`).value, remarks: $(`#r${id}`).value } }); dashboard(); }
      catch (e) { alert(e.message); }
    }));
  }

  $("#logout").addEventListener("click", () => { token = null; try { sessionStorage.removeItem("saathi.official"); } catch { /* ignore */ } $("#logout").hidden = true; login(); });
  token ? dashboard() : login();
})();
