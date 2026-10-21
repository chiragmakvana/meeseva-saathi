// Records the demo walkthrough at 1080p, pacing each step to its narration clip, and writes the timestamps
// needed to mix the narration in (scripts/build_demo_video.py does the mixing).
//   node scripts/record_demo.mjs <baseUrl> <demoDir>     e.g. node scripts/record_demo.mjs http://127.0.0.1:8000 docs/demo
// Expects <demoDir>/audio/durations.json from `python -m scripts.narrate docs/demo/demo_segments.json docs/demo/audio`.
import { chromium } from "playwright";
import { readFileSync, writeFileSync, readdirSync, renameSync } from "node:fs";
import { join } from "node:path";

const B = process.argv[2] || "http://127.0.0.1:8000";
const DIR = process.argv[3] || "docs/demo";
const dur = JSON.parse(readFileSync(join(DIR, "audio", "durations.json"), "utf8"));
const GAP = 1.2; // seconds of silence after each clip

const W = 1920, H = 1080;
const b = await chromium.launch();
const ctx = await b.newContext({ viewport: { width: W, height: H }, recordVideo: { dir: DIR, size: { width: W, height: H } } });
const started = Date.now();
const p = await ctx.newPage();
const stamps = {};
const ts = () => (Date.now() - started) / 1000;
const sleep = (ms) => p.waitForTimeout(ms);
let segStart = 0;
const begin = (id) => { segStart = Date.now(); stamps[id] = ts(); };
const end = async (id) => { const need = (dur[id] + GAP) * 1000 - (Date.now() - segStart); if (need > 0) await sleep(need); };

const phone = (hash) => `<body style="margin:0;background:linear-gradient(135deg,#0f4c81,#e9edf2 60%);display:flex;justify-content:center;align-items:center;height:${H}px;font-family:system-ui">
  <div style="position:absolute;left:120px;top:120px;width:520px;color:#fff"><p style="font-size:46px;font-weight:700;margin:0 0 12px">MeeSeva Saathi</p><p style="font-size:26px;opacity:.9;margin:0">AI-assisted, multilingual guide to MeeSeva services</p><p style="font-size:20px;opacity:.75;margin-top:24px">Prototype · ESD Innovation Challenge 2026 · Team SvaKrit AI</p></div>
  <iframe id="f" src="${B}/${hash}" style="width:460px;height:940px;border:0;border-radius:28px;box-shadow:0 20px 60px rgba(0,0,0,.35);background:#fff;zoom:1.1;margin-left:420px"></iframe></body>`;
const f = p.frameLocator("#f");
const app = () => p.frames().find((fr) => fr.url().startsWith(B));
const click = (sel) => app().evaluate((q) => document.querySelector(q).click(), sel);
const type = async (sel, text, delay) => { await f.locator(sel).focus(); await p.keyboard.type(text, { delay }); };

await p.setContent(phone("#/")); await sleep(2500);

begin("intro"); await sleep(1500); await app().evaluate(() => window.scrollBy({ top: 420, behavior: "smooth" })); await sleep(3000);
await app().evaluate(() => window.scrollTo({ top: 0, behavior: "smooth" })); await end("intro");

begin("telugu"); await type("#home-q", "నాకు ఆదాయ ధృవీకరణ పత్రం కావాలి", 70); await sleep(500);
await click("#home button[type=submit]"); await sleep(5000); await app().evaluate(() => window.scrollBy({ top: 520, behavior: "smooth" })); await end("telugu");

begin("pension"); await f.locator("#lang").selectOption("en"); await sleep(1500);
await type("#askForm-q", "My father passed away and we need to claim his pension", 45); await click("#askForm button[type=submit]"); await sleep(6000);
await app().evaluate(() => window.scrollBy({ top: -300, behavior: "smooth" })); await end("pension");

begin("unknown"); await type("#askForm-q", "how do I renew my passport", 45); await click("#askForm button[type=submit]"); await sleep(4500); await end("unknown");

const svcs = await (await p.request.get(`${B}/api/services`)).json(); const res = svcs.find((s) => s.code === "RES");
begin("login"); await app().evaluate((h) => { location.hash = h; }, `#/login?next=${encodeURIComponent(`#/new/${res.id}`)}`); await sleep(1200);
await type("#m", "9876543210", 80); await click("#f1 button"); await sleep(1500);
const otp = (await f.locator("#demo").textContent()).match(/(\d{6})/)[1];
await type("#o", otp, 120); await type("#n", "Ravi Kumar", 60); await sleep(800); await click("#f2 button"); await sleep(1500); await end("login");

begin("checklist"); await sleep(600);
await click("#fa button"); await sleep(2000);
const n = await f.locator(".check input").count();
for (let i = 0; i < n; i++) { await app().evaluate((i) => document.querySelectorAll(".check input")[i].click(), i); await sleep(1300); }
await sleep(800); await click("#submitApp"); await sleep(3500); await end("checklist");

begin("urdu"); await f.locator("#lang").selectOption("ur"); await sleep(1000); await app().evaluate(() => { location.hash = "#/ask"; }); await sleep(1200);
await type("#askForm-q", "مجھے پیدائش سرٹیفکیٹ چاہیے", 70); await click("#askForm button[type=submit]"); await sleep(5000);
await f.locator("#lang").selectOption("en"); await end("urdu");

begin("dashboard"); await p.goto(`${B}/official`); await sleep(1000); await p.click("#f button"); await sleep(1200);
const od = (await p.textContent("#demo")).match(/(\d{6})/)[1]; await p.type("#o", od, { delay: 120 }); await p.click("#v"); await sleep(2500);
await p.evaluate(() => window.scrollTo({ top: 600, behavior: "smooth" })); await sleep(3000);
await p.evaluate(() => window.scrollTo({ top: 1300, behavior: "smooth" })); await sleep(3000);
await p.evaluate(() => window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" })); await sleep(2000);
await p.locator("select.field").first().selectOption("needs_documents"); await p.locator('input[placeholder="Remarks for the citizen"]').first().fill("Please bring the rent agreement."); await sleep(800);
await p.locator(".upd").first().click(); await sleep(2500); await end("dashboard");

begin("alerts"); await p.setContent(phone("#/alerts")); await sleep(3000); await end("alerts");

begin("about"); await app().evaluate(() => { location.hash = "#/about"; }); await sleep(2500); await app().evaluate(() => window.scrollBy({ top: 650, behavior: "smooth" })); await end("about");
await sleep(1500);

const total = ts();
await ctx.close(); await b.close();
const webm = readdirSync(DIR).find((x) => x.endsWith(".webm"));
renameSync(join(DIR, webm), join(DIR, "demo_raw.webm"));
writeFileSync(join(DIR, "timestamps.json"), JSON.stringify({ stamps, total }, null, 1));
console.log("Recorded demo_raw.webm,", total.toFixed(1), "s; timestamps.json written");
