# Demo submission · ESD Innovation Challenge, Government Digital Services

**Team SvaKrit AI** · Chirag Makvana, Bansi Chirag Makvana · Hyderabad
**Innovation Day & Grand Finale:** Sunday 25 October 2026, 9:00 AM, 105 Auditorium, Himalaya Block, IIIT Hyderabad

The four items the demo guide asks for, in one place. The videos are attached to the GitHub release
[`demo-2026-10-25`](https://github.com/chiragmakvana/meeseva-saathi/releases/tag/demo-2026-10-25) so they can be downloaded or streamed without cloning the repository.

| # | Item | File | Length / size | SHA-256 (first 16) |
|---|---|---|---|---|
| 1 | Final pitch deck (PDF, 14 slides) | [SvaKritAI_FinalPitchDeck.pdf](SvaKritAI_FinalPitchDeck.pdf) · [release copy](https://github.com/chiragmakvana/meeseva-saathi/releases/download/demo-2026-10-25/SvaKritAI_FinalPitchDeck.pdf) | 1.9 MB | 2d89ef8c74fef6c1 |
| 2 | Recorded demo video (3–5 min) | [SvaKritAI_Demo.mp4](https://github.com/chiragmakvana/meeseva-saathi/releases/download/demo-2026-10-25/SvaKritAI_Demo.mp4) | 3:29 · 1080p · 20 MB | 085bd61e11beac78 |
| 3 | Team pitch video (≤ 8 min, both members on their modules) | [SvaKritAI_TeamPitch.mp4](https://github.com/chiragmakvana/meeseva-saathi/releases/download/demo-2026-10-25/SvaKritAI_TeamPitch.mp4) | 7:56 · 1080p · 25 MB | 601719996780d347 |
| 4 | GitHub repository | https://github.com/chiragmakvana/meeseva-saathi (public) | — | — |

Supporting material in this folder:

- [`TEAM_PITCH_SCRIPT.md`](TEAM_PITCH_SCRIPT.md) and [`SvaKritAI_TeamPitch_Script.pdf`](SvaKritAI_TeamPitch_Script.pdf): the pitch, slide by slide, with speaker and timing.
- [`DEMO_VIDEO_SCRIPT.md`](DEMO_VIDEO_SCRIPT.md): the demo video, scene by scene.
- [`LIVE_DEMO_STEPS.md`](LIVE_DEMO_STEPS.md): the live-demo runbook with screenshots, used for the stage demo on 25 October.
- [`../RESEARCH.md`](../RESEARCH.md), [`../API.md`](../API.md), [`../DATABASE.md`](../DATABASE.md), [`../TESTING.md`](../TESTING.md): research, API reference, database design, test report (42 automated tests).

## What the jury sees in 60 seconds

1. **Problem:** MeeSeva serves 32.5 lakh transactions a month across 391 services, yet 42 lakh applications are pending beyond their time limit and 92 lakh have been rejected, and the portal speaks only English and Telugu. Citizens do not know which service they need, what to carry, or what a status means.
2. **Solution:** MeeSeva Saathi, a multilingual AI companion (Telugu, English, Hindi, Urdu; text and voice) that maps a life situation to the right service, prepares the document checklist, explains every status in plain words, and gives the ESD Wing a dashboard of what citizens ask and where they get stuck.
3. **Built:** FastAPI backend, 12-table database, Azure OpenAI grounded in the service catalogue with a rules-engine fallback, OTP login with citizen and official roles, GIGW 3.0 / WCAG 2.1 AA interface, 42 automated tests. Runs offline for reviewers with one command.
4. **Ask:** a pilot with the ESD Wing on one district's most-requested services, against the real service master, measuring first-time success and repeat visits.

## Run it yourself (5 minutes)

```bash
git clone https://github.com/chiragmakvana/meeseva-saathi.git && cd meeseva-saathi
python -m venv .venv && .venv\Scripts\activate      # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m app.seed --demo
uvicorn app.main:app --reload
```

Citizen app at http://127.0.0.1:8000, officials' dashboard at http://127.0.0.1:8000/official (demo official 9000000001). The OTP is shown on screen; no SMS gateway is connected in the prototype.

Contact: chirag@svakrit.ai · +91 90999 32030
