// Records a silent screen walkthrough of the citizen app and the officials' dashboard for the demo video.
// Needs the app running (python -m app.seed --demo; uvicorn app.main:app --port 8000) and Playwright:
//   npm i playwright && npx playwright install chromium
//   node scripts/record_walkthrough.mjs [baseUrl] [outDir]      (SPEED=1 for a quick preview)
// Output: <outDir>/walkthrough.webm (convert: ffmpeg -i walkthrough.webm -c:v libx264 -pix_fmt yuv420p walkthrough.mp4)
import { chromium } from "playwright";
import { mkdirSync, renameSync, readdirSync } from "node:fs";
import { join } from "node:path";

const B = process.argv[2] || "http://127.0.0.1:8000";
const OUT = process.argv[3] || "docs/demo";
mkdirSync(OUT, { recursive: true });

const b = await chromium.launch();
// Phone-sized app embedded in a 1280x800 frame so the recording is a normal 16:10 video.
const ctx = await b.newContext({ viewport: { width: 1280, height: 800 }, recordVideo: { dir: OUT, size: { width: 1280, height: 800 } } });
const p = await ctx.newPage();
const SPEED = Number(process.env.SPEED || 2.8); // 1 = quick preview; 2.8 ≈ a 4-minute video for narration
const pause = (ms) => p.waitForTimeout(ms * SPEED);
const typeSlow = async (sel, text) => { await p.click(sel); await p.type(sel, text, { delay: 60 }); };

// Frame page: the citizen app in a phone-width iframe on the left, blank on the right (keeps the recording readable).
await p.setContent(`<body style="margin:0;background:#e9edf2;display:flex;justify-content:center;align-items:center;height:800px">
  <iframe id="f" src="${B}/#/" style="width:430px;height:780px;border:0;border-radius:24px;box-shadow:0 10px 40px rgba(0,0,0,.25);background:#fff"></iframe></body>`);
const f = p.frameLocator("#f");
const app = () => p.frames().find((fr) => fr.url().startsWith(B));
await pause(2500);

// 1. Home (Telugu) → income certificate in Telugu
await f.locator("#home-q").click(); await f.locator("#home-q").type("నాకు ఆదాయ ధృవీకరణ పత్రం కావాలి", { delay: 70 }); await pause(600);
await f.locator("#home button[type=submit]").click(); await pause(5000);
await app().evaluate(() => window.scrollBy({ top: 500, behavior: "smooth" })); await pause(2500);

// 2. English: pension question, then an unknown request
await f.locator("#lang").selectOption("en"); await pause(1500);
await f.locator("#askForm-q").type("My father passed away and we need to claim his pension", { delay: 45 }); await f.locator("#askForm button[type=submit]").click(); await pause(6000);
await f.locator("#askForm-q").type("how do I renew my passport", { delay: 45 }); await f.locator("#askForm button[type=submit]").click(); await pause(4500);

// 3. Login
await app().evaluate(() => { location.hash = "#/login"; }); await pause(1200);
await f.locator("#m").type("9876543210", { delay: 80 }); await f.locator("#f1 button").click(); await pause(1500);
const otp = (await f.locator("#demo").textContent()).match(/(\d{6})/)[1];
await f.locator("#o").type(otp, { delay: 120 }); await f.locator("#n").type("Ravi Kumar", { delay: 60 }); await pause(800); await f.locator("#f2 button").click(); await pause(1500);

// 4. Residence certificate: checklist → submit → timeline
const svcs = await (await p.request.get(`${B}/api/services`)).json(); const res = svcs.find((s) => s.code === "RES");
await app().evaluate((id) => { location.hash = `#/new/${id}`; }, res.id); await pause(1500);
await f.locator("#fa button").click(); await pause(2000);
const n = await f.locator(".check input").count();
for (let i = 0; i < n; i++) { await f.locator(".check input").nth(i).check(); await pause(1200); }
await pause(800); await f.locator("#submitApp").click(); await pause(3500);

// 5. Urdu
await f.locator("#lang").selectOption("ur"); await pause(1000); await app().evaluate(() => { location.hash = "#/ask"; }); await pause(1200);
await f.locator("#askForm-q").type("مجھے پیدائش سرٹیفکیٹ چاہیے", { delay: 70 }); await f.locator("#askForm button[type=submit]").click(); await pause(5000);
await f.locator("#lang").selectOption("en"); await pause(800);

// 6. Officials' dashboard (full window)
await p.goto(`${B}/official`); await pause(1000); await p.click("#f button"); await pause(1200);
const od = (await p.textContent("#demo")).match(/(\d{6})/)[1]; await p.type("#o", od, { delay: 120 }); await p.click("#v"); await pause(2500);
await p.evaluate(() => window.scrollTo({ top: 700, behavior: "smooth" })); await pause(2500);
await p.evaluate(() => window.scrollTo({ top: 1500, behavior: "smooth" })); await pause(2500);
await p.evaluate(() => window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" })); await pause(2000);
const sel = p.locator("select.field").first(); await sel.selectOption("needs_documents"); await p.locator('input[placeholder="Remarks for the citizen"]').first().fill("Please bring the rent agreement."); await pause(800);
await p.locator(".upd").first().click(); await pause(2500);

// 7. Citizen alerts, then Why Saathi
await p.setContent(`<body style="margin:0;background:#e9edf2;display:flex;justify-content:center;align-items:center;height:800px">
  <iframe id="f" src="${B}/#/alerts" style="width:430px;height:780px;border:0;border-radius:24px;box-shadow:0 10px 40px rgba(0,0,0,.25);background:#fff"></iframe></body>`);
await pause(3500);
await app().evaluate(() => { location.hash = "#/about"; }); await pause(3000);
await app().evaluate(() => window.scrollBy({ top: 600, behavior: "smooth" })); await pause(3000);

await ctx.close(); await b.close();
const webm = readdirSync(OUT).find((x) => x.endsWith(".webm"));
renameSync(join(OUT, webm), join(OUT, "walkthrough.webm"));
console.log("Recorded", join(OUT, "walkthrough.webm"));
