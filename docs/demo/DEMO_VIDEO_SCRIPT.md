# Demo video script (3–5 minutes)

A silent screen recording of this walkthrough is in `docs/demo/walkthrough.mp4` (generated with
`node scripts/record_walkthrough.mjs`). Record your voice over it, or re-record the screen yourself with
the same steps. Target length: **4 minutes**. Speak slowly; pause on each screen.

Setup before recording: `python -m app.seed --demo`, `uvicorn app.main:app`, open http://127.0.0.1:8000 in
Chrome at a phone-sized window (about 420 px wide) for the citizen app, and a desktop window for the
dashboard. Language set to Telugu on first load.

| Time | On screen | Say (English; switch to Telugu for the first question if you prefer) |
|---|---|---|
| 0:00–0:20 | Home in Telugu | “This is MeeSeva Saathi. Saathi means companion. A citizen opens it on any phone and sees one question box, the popular services, and the categories, in Telugu by default. The top strip says clearly that this is a prototype.” |
| 0:20–0:55 | Type in Telugu: నాకు ఆదాయ ధృవీకరణ పత్రం కావాలి → answer card | “I type, or speak, that I need an income certificate. Saathi answers in Telugu: which service, the four documents to carry, the fee and the official seven-day timeline, with a card and a Listen button that reads it aloud for someone who cannot read well.” |
| 0:55–1:35 | Switch to English; type “My father passed away and we need to claim his pension” | “Citizens describe a situation, not a certificate name. Here the AI understands that a pension claim needs a death certificate first, lists the documents, and even points to the family-member certificate that comes next. The small label shows the answer came from the AI; if the AI is ever down, the built-in catalogue engine answers instead.” |
| 1:35–1:55 | Type “how do I renew my passport” | “When something is not a MeeSeva service, Saathi says so and offers the closest services instead of guessing. Every unanswered question is logged for the department.” |
| 1:55–2:25 | Log in with mobile + OTP (OTP shown on screen) | “To start an application you log in with your mobile number and a one-time password. In the prototype the OTP is shown on screen because no SMS gateway is connected.” |
| 2:25–3:05 | Start Residence Certificate → checklist → tick three documents → Submit → timeline | “Saathi creates a document checklist for the service. The citizen ticks each document as they collect it, and cannot submit until the list is complete. That is the single biggest cause of repeat visits removed. After submission, a timeline shows where the application is, with ‘what this means’ and ‘what to do next’ in the citizen’s language.” |
| 3:05–3:25 | Switch to Urdu; ask مجھے پیدائش سرٹیفکیٹ چاہیے | “The same works in Urdu, with the whole interface switching to right-to-left, and in Hindi. The official portal today is in English and Telugu only.” |
| 3:25–4:05 | Desktop: officials’ dashboard | “For the ESD Wing: what citizens ask most, in which languages, the questions the catalogue could not answer, which are candidates for new services, and feedback tagged by sentiment and topic. An officer updates an application here with remarks.” |
| 4:05–4:20 | Phone: Alerts | “And the citizen receives that update as a notification, in their language, with the officer’s remarks.” |
| 4:20–4:35 | Why Saathi page | “The research behind the design, with the official numbers, is inside the app. Thank you.” |

Tips: keep the mouse still while speaking; avoid reading the exact screen text aloud; if you make a
mistake, pause two seconds and repeat the sentence (easy to cut later).
