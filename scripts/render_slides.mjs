// Renders the pitch deck's slide HTML files (1920×1080 sections with inline styles) to PNG for the pitch video.
//   node scripts/render_slides.mjs <deckProjectDir> <assetsDir> <outDir>
// <assetsDir> holds the images referenced as /_blob/<id>; blobmap.json in it maps id -> file name.
import { chromium } from "playwright";
import { readFileSync, readdirSync, mkdirSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";

const [, , deckDir, assetsDir, outDir] = process.argv;
mkdirSync(outDir, { recursive: true });
const blobmap = JSON.parse(readFileSync(join(assetsDir, "blobmap.json"), "utf8"));
const fonts = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Mono:wght@400;600&display=swap">';
const css = `<style>html,body{margin:0;background:#000}section{position:relative;width:1920px;height:1080px;box-sizing:border-box;overflow:hidden}
section *{box-sizing:border-box}h1,h2,h3,p{margin:0}aside{display:none}
x-shape[kind="arrow-right"]{display:inline-block;clip-path:polygon(0 32%,62% 32%,62% 0,100% 50%,62% 100%,62% 68%,0 68%)}
img{display:block}</style>`;
const wrap = (body) => `<!doctype html><html><head><meta charset="utf-8">${fonts}${css}</head><body>${body}</body></html>`;

const b = await chromium.launch();
const p = await (await b.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 })).newPage();
const order = JSON.parse(readFileSync(join(deckDir, "deck.json"), "utf8")).order;
for (const id of order) {
  let html = readFileSync(join(deckDir, "slides", `${id}.html`), "utf8");
  html = html.replace(/\/_blob\/([0-9a-f]{32})/g, (m, bid) => "data:image/png;base64," + readFileSync(join(assetsDir, blobmap[bid])).toString("base64"));
  await p.setContent(wrap(html), { waitUntil: "networkidle" });
  await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(400);
  await p.screenshot({ path: join(outDir, `${id}.png`), clip: { x: 0, y: 0, width: 1920, height: 1080 } });
  console.log("rendered", id);
}
// Disclosure card for the draft pitch video.
await p.setContent(wrap(`<section style="background:#0B2F4F;color:#F6F4F0;font-family:'IBM Plex Sans',Arial,sans-serif;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:32px">
  <p style="font-family:'IBM Plex Mono',monospace;font-size:26px;letter-spacing:2px;color:#E07B00">DRAFT · NOT FOR SUBMISSION</p>
  <h1 style="font-size:84px;font-weight:600;line-height:1.1">Team pitch — draft with AI-generated voices</h1>
  <p style="font-size:36px;line-height:1.45;color:#BFD8E8">The voices standing in for Chirag and Bansi are synthetic. The team records this script in their own voices for the final submission, as the demo guidelines require.</p></section>`), { waitUntil: "networkidle" });
await p.waitForTimeout(300); await p.screenshot({ path: join(outDir, "note.png"), clip: { x: 0, y: 0, width: 1920, height: 1080 } });
writeFileSync(join(outDir, "order.json"), JSON.stringify(order));
await b.close();
console.log("done");
