"""Write docs/demo/DEMO_VIDEO_SCRIPT.md from the demo narration, one section per scene, so the narrated video
(SvaKritAI_Demo.mp4), the written script and the live-demo runbook always carry the same words and order.

Usage: python -m scripts.demo_script
Inputs: docs/demo/demo_segments.json, docs/demo/audio/durations.json (scripts/narrate.py),
        docs/demo/timestamps.json (scripts/record_demo.mjs; optional, used for the clock column)
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEMO = ROOT / "docs/demo"

# What the recording shows while each clip plays, the runbook steps it corresponds to, and the matching stills.
SCENE = {
    "intro": ("Home in Telugu", "Phone frame. Telugu home: question box, popular services, category tiles; slow scroll down and back. Prototype strip at the top.", "1", ["01-home-telugu.png"]),
    "telugu": ("Income certificate, in Telugu", "Typing నాకు ఆదాయ ధృవీకరణ పత్రం కావాలి; the Telugu answer and the Income Certificate card (fee, time, four documents, Listen).", "2–3", ["03-answer-telugu.png", "04-service-card-telugu.png"]),
    "pension": ("Pension after a death, in English", "Language switched to English; typing “My father passed away and we need to claim his pension”; the answer, the Death Certificate card and the “Answered by: AI” label.", "4", ["05-answer-pension.png"]),
    "unknown": ("Not a MeeSeva service", "Typing “how do I renew my passport”; the “MeeSeva does not provide…” reply with suggestion chips.", "5", ["06-unknown-request.png"]),
    "login": ("Login with OTP", "Log in: mobile 9876543210, Get OTP, the OTP shown in the orange box, name Ravi Kumar, Verify.", "6–7", ["08-login-otp.png"]),
    "checklist": ("Checklist, submit, timeline", "Residence Certificate → Start application → purpose “School admission” → three documents ticked → Submit → status “Submitted” with the four-step timeline and “What this means / What to do next”.", "8–11", ["12-checklist-empty.png", "13-checklist-complete.png", "14-submitted-timeline.png"]),
    "urdu": ("Urdu, right-to-left", "Language → اردو; the interface flips to right-to-left; typing مجھے پیدائش سرٹیفکیٹ چاہیے; the Urdu answer with the Birth Certificate card.", "13", ["16-answer-urdu.png"]),
    "dashboard": ("Officials’ dashboard", "Desktop frame. Official login (9000000001); KPI tiles, most requested services, questions by language; scroll to service gaps and tagged feedback; the Ravi Kumar row set to “Needs documents” with a remark; Save & notify.", "14–17", ["19-dashboard-top.png", "20-dashboard-gaps.png", "21-dashboard-update.png"]),
    "alerts": ("Citizen notification", "Back to the phone. Alerts tab with the badge; the notification card with the status explanation and the officer’s remark.", "18", ["22-citizen-alert.png"]),
    "about": ("Why Saathi", "The Why Saathi page: the four MeeSeva figures and findings → design decisions; slow scroll; ends on the GitHub link.", "19", ["17-why-saathi.png"]),
}


def clock(s: float) -> str:
    return f"{int(s // 60)}:{int(s % 60):02d}"


def main() -> None:
    segs = json.loads((DEMO / "demo_segments.json").read_text(encoding="utf-8"))
    dur = json.loads((DEMO / "audio/durations.json").read_text(encoding="utf-8"))
    ts_file = DEMO / "timestamps.json"
    stamps = json.loads(ts_file.read_text(encoding="utf-8")) if ts_file.exists() else {"stamps": {}, "total": None}
    total_speech = sum(dur[s["id"]] for s in segs)
    total_video = stamps.get("total")
    out = ["# Demo video script, scene by scene", "",
           f"The narrated demo (`SvaKritAI_Demo.mp4`, 1080p, {clock(total_video) if total_video else 'about 3½'} min) is built from the ten scenes below. "
           f"Each scene is one narration clip (`demo_segments.json`, Azure neural voice en-IN-Neerja) played over the screen recording; "
           f"spoken time {total_speech / 60:.1f} min. The same scenes, in the same order, are steps of the live-demo runbook (`LIVE_DEMO_STEPS.md`), "
           "so you can also record this script yourself over a live run.", "",
           "**Rebuild the video** after any change to the app or the words:", "",
           "```bash", "python -m scripts.narrate docs/demo/demo_segments.json docs/demo/audio   # clips + durations.json",
           "python -m app.seed --demo && uvicorn app.main:app --port 8000               # fresh data, in another terminal",
           "node scripts/record_demo.mjs http://127.0.0.1:8000 docs/demo               # paced recording + timestamps.json",
           "python -m scripts.build_demo_video                                          # mixes to SvaKritAI_Demo.mp4",
           "python -m scripts.demo_script                                               # regenerates this file", "```", "",
           "**Record it in your own voice instead:** run the app as in the runbook, screen-record a phone-sized window (about 420 px wide, "
           "zoom 125–150 %) plus a desktop window for the dashboard, and read each scene’s words while doing its runbook steps. "
           "Keep the mouse still while speaking; avoid reading screen text aloud; after a slip, pause two seconds and repeat the sentence (easy to cut).", "",
           "| # | Scene | Starts | Clip | Runbook steps |", "|---|---|---|---|---|"]
    for n, s in enumerate(segs, 1):
        title, _, steps, _ = SCENE[s["id"]]
        start = stamps["stamps"].get(s["id"])
        out.append(f"| {n} | {title} | {clock(start) if start is not None else '—'} | {dur[s['id']]:.0f} s | {steps} |")
    out.append("")
    for n, s in enumerate(segs, 1):
        title, screen, steps, shots = SCENE[s["id"]]
        start = stamps["stamps"].get(s["id"])
        out += [f"## Scene {n} of {len(segs)} · {title}", "",
                f"**Clip:** about {dur[s['id']]:.0f} s" + (f" · starts at {clock(start)} in the video" if start is not None else "") + f" · runbook step{'s' if '–' in steps else ''} {steps}", "",
                f"**On screen:** {screen}", "",
                f"> {s['text']}", "",
                " ".join(f"![]({'steps/' + x})" for x in shots), ""]
    out += ["---", "", "Generated by `python -m scripts.demo_script` from `demo_segments.json`, `audio/durations.json` and `timestamps.json`. "
            "To change the words, edit `demo_segments.json`, then re-run narrate, record_demo, build_demo_video and this script."]
    (DEMO / "DEMO_VIDEO_SCRIPT.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"DEMO_VIDEO_SCRIPT.md written: {len(segs)} scenes, {total_speech / 60:.1f} min of speech, video {clock(total_video) if total_video else '?'}")


if __name__ == "__main__":
    main()
