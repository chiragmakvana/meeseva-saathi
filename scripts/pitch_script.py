"""Write docs/demo/TEAM_PITCH_SCRIPT.md from the pitch narration, one section per slide, so the deck's speaker
notes, the draft pitch video and the written script always carry the same words.

Usage: python -m scripts.pitch_script
Inputs: docs/demo/pitch_segments.json, docs/demo/pitch_audio/durations.json (from scripts/narrate.py)
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEAKER = {"en-IN-PrabhatNeural": "Chirag", "en-IN-NeerjaNeural": "Bansi"}
ORDER = ["cover", "numbers", "citizen", "solution", "screens-ask", "screens-track", "ai", "tech", "access", "officials", "fit", "scope", "team", "close"]
TITLE = {
    "cover": "MeeSeva Saathi", "numbers": "MeeSeva today", "citizen": "Three questions stand between a citizen and the counter",
    "solution": "A companion that prepares the citizen and informs the department", "screens-ask": "Ask Saathi",
    "screens-track": "Prepare and track", "ai": "How the AI works", "tech": "Technology and testing",
    "access": "Accessibility · GIGW 3.0 and WCAG 2.1 AA", "officials": "For the ESD Wing", "fit": "Where it fits",
    "scope": "MVP and roadmap", "team": "Team SvaKrit AI", "close": "Let citizens ask in their own words",
}
ON_SCREEN = {
    "cover": "Title, one-line promise, team names, GitHub link.",
    "numbers": "Six figures from the MeeSeva portal: 391 services · 5,265 centres · 32.5 lakh transactions · 42 lakh pending beyond SLA · 92 lakh rejected · 2 languages.",
    "citizen": "The three questions: which service, what to carry, what the status means.",
    "solution": "Four cards: Ask, Prepare, Track (citizen) and Insights (ESD Wing).",
    "screens-ask": "Two phone screens: Telugu home; the pension question answered with the Death Certificate card.",
    "screens-track": "Two phone screens: submitted application with timeline and checklist; the services list.",
    "ai": "Flow: Detect → Understand → Fall back → Learn, with the grounding rules underneath.",
    "tech": "Four cards: Backend, AI, Frontend, Testing; the repository link.",
    "access": "Four cards: Language, Readable, Operable, Light.",
    "officials": "Dashboard screenshot with four points: top services, service gaps, AI-tagged feedback, processing.",
    "fit": "Three channel cards: MeeSeva on WhatsApp, portal and app, centre kiosks.",
    "scope": "Two columns: MVP built (five rows) and Next (five rows).",
    "team": "Two cards: Chirag and Bansi, with what each built.",
    "close": "The ask (a pilot with the ESD Wing) and contact details.",
}
LIVE_DEMO = ("**Live-demo option (recommended):** instead of the screenshots, switch to the running app here and say the slide 5 "
             "and slide 6 words while clicking through runbook steps 1–4 and 9–11 (`LIVE_DEMO_STEPS.md`). Keep to the same "
             "60 seconds; come back to the deck at slide 7. If the app misbehaves, stay on the slides: the words are identical.")


def main() -> None:
    segs = json.loads((ROOT / "docs/demo/pitch_segments.json").read_text(encoding="utf-8"))
    dur = json.loads((ROOT / "docs/demo/pitch_audio/durations.json").read_text(encoding="utf-8"))
    by_slide = {}
    for s in segs:
        if s["slide"] != "note":
            by_slide.setdefault(s["slide"], []).append(s)
    total = sum(dur[s["id"]] for s in segs if s["slide"] != "note")
    out = ["# Team pitch script, slide by slide", "",
           f"Two presenters, **Chirag** and **Bansi**. One section per slide of the deck, in deck order, with the exact words. "
           f"Spoken time about {total / 60:.1f} minutes plus slide changes: aim to finish under 8 minutes. "
           "The same words are in each slide's speaker notes and in the draft pitch video (`SvaKritAI_TeamPitch_DRAFT.mp4`), "
           "which you can use as a timing rehearsal.", "",
           "**Recording:** share the deck in Presenter view (notes visible to you only) or the exported PDF; camera on both of you. "
           "Record in sections if easier; cut on the slide changes. Name the file `SvaKritAI_TeamPitch.mp4`.", "",
           "| Slide | Title | Speaker | Time |", "|---|---|---|---|"]
    for n, sid in enumerate(ORDER, 1):
        who = " then ".join(dict.fromkeys(SPEAKER[s["voice"]] for s in by_slide[sid]))
        t = sum(dur[s["id"]] for s in by_slide[sid])
        out.append(f"| {n} | {TITLE[sid]} | {who} | {t:.0f} s |")
    out.append("")
    running = 0.0
    for n, sid in enumerate(ORDER, 1):
        t = sum(dur[s["id"]] for s in by_slide[sid])
        out += [f"## Slide {n} of {len(ORDER)} · {TITLE[sid]}", "",
                f"**Speaker:** {' then '.join(dict.fromkeys(SPEAKER[s['voice']] for s in by_slide[sid]))} · **about {t:.0f} s** · starts near {int(running // 60)}:{int(running % 60):02d}", "",
                f"**On screen:** {ON_SCREEN[sid]}", ""]
        for s in by_slide[sid]:
            out += [f"**{SPEAKER[s['voice']]}:**", "", f"> {s['text']}", ""]
        if sid == "screens-ask":
            out += [LIVE_DEMO, ""]
        running += t
    out += ["---", "", "Generated by `python -m scripts.pitch_script` from `pitch_segments.json`. To change the words, edit that file, "
            "then re-run this script, `python -m scripts.narrate docs/demo/pitch_segments.json docs/demo/pitch_audio` and the deck notes."]
    (ROOT / "docs/demo/TEAM_PITCH_SCRIPT.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"TEAM_PITCH_SCRIPT.md written: {len(ORDER)} slides, {total / 60:.1f} min of speech")


if __name__ == "__main__":
    main()
