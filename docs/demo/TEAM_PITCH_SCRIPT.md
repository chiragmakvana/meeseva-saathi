# Team pitch video script (up to 8 minutes)

Two presenters: **Chirag** (research, AI engine, backend, database, security) and **Bansi** (citizen
experience, accessibility, checklist and status flow, officials’ dashboard, testing). Record face-to-camera
with the deck or the app shared on screen. Target length: **7 minutes**. Each member explains the module
they built, as the demo guidelines require.

## 0:00–0:40 · Problem (Chirag, deck slides 1–3)

“Namaste. We are SvaKrit AI from Hyderabad, and this is MeeSeva Saathi.

MeeSeva serves 32 lakh transactions a month through 5,265 centres. But the official portal also shows 42 lakh
applications pending beyond their time limit since January 2025, and 92 lakh rejections to date. Behind
those numbers are three questions every citizen struggles with before they reach a counter: which service do
I need, what must I carry, and what does my status mean. And the portal speaks only English and Telugu.”

## 0:40–1:30 · Solution (Bansi, slide 4 and the home screen)

“Saathi is a companion that answers those three questions in the citizen’s own language: Telugu, Hindi, Urdu
or English, by typing or speaking.

You describe what you need in your own words. Saathi tells you the service, the documents to carry, the fee
and the time. It keeps a checklist so you never make a second trip for a missing paper. And it explains every
status in plain words and tells you what to do next. The department gets a dashboard of what citizens ask and
where they get stuck.”

## 1:30–3:30 · Product demo (Bansi drives, Chirag adds one line on the AI)

Follow the demo video script, shortened: Telugu income certificate → English pension question → checklist and
submit → Urdu → dashboard → notification.

Chirag, on the pension answer: “That mapping from a life situation to a service is the AI layer, which I will
explain in a moment.”

## 3:30–5:00 · My module: the AI engine and backend (Chirag, slides 7 and 12)

“I built the assistant and the backend.

Every question first goes through language detection by script, so a citizen can type Telugu even if the
interface is in English. Then Azure OpenAI, gpt-5-mini, answers, but only from our service catalogue: it may
not invent services, fees or timelines, it must use the official names in the citizen’s language, and it must
say ‘confirm at the centre’. If the AI is slow or unavailable, a multilingual rules engine answers from the same
catalogue, so the service is never down; reviewers can run everything offline.

The backend is FastAPI with a 12-table database: services, documents, applications with their checklists,
every question asked, feedback tagged by sentiment and topic, and notifications. Login is mobile plus OTP
with hashed codes and signed sessions; citizens see only their own applications; officials have a separate
role. Nineteen endpoints are documented, and the catalogue uses the official MeeSeva revenue timelines.”

## 5:00–6:15 · My module: citizen experience and testing (Bansi, slides 5, 6, 8, 9)

“I built what the citizen and the officer see.

The interface is Telugu-first and switches to Hindi, Urdu, with right-to-left layout, and English. It follows
GIGW 3.0 and WCAG 2.1 AA: three text sizes, a high-contrast mode, screen-reader labels, keyboard operation,
large touch targets, and voice in and out for people who read little.

The application flow has a checklist that gates submission, a four-step timeline, and ‘what this means, what
to do next’ for every status, with a notification when an officer changes it. The officials’ dashboard shows
the most-requested services, questions by language, unanswered questions as service gaps, and AI-tagged
feedback.

I wrote the test cases: 41 automated tests covering login, the assistant in four languages, applications,
officials and feedback, plus a browser walkthrough. The test report lists each case with expected and actual
results and the bugs we found and fixed.”

## 6:15–6:50 · Uniqueness and roadmap (Chirag, slides 10–11)

“What makes Saathi different: it works before the citizen applies, not just after; it is grounded, so it
never invents a fee or a document; it is the first MeeSeva experience in Hindi and Urdu; and it closes the
loop with a feedback dashboard for the ESD Wing.

It is API-first, so it can sit behind the MeeSeva WhatsApp channel launched last November, the portal and
centre kiosks. Next: the official service master, live application status, SMS OTP, DigiLocker pre-fill and
Telugu speech tuned for rural accents.”

## 6:50–7:00 · Close (both, slide 14)

Bansi: “Our ask is a pilot with the ESD Wing on one district’s most-requested services.”
Chirag: “The code, research and tests are open at github.com/chiragmakvana/meeseva-saathi. Thank you.”

---

Recording notes: one take per section is fine; sections can be stitched. Keep the deck on screen for
slides 1–4, the app for the demo, and the deck again from 3:30. Name the files
`SvaKritAI_TeamPitch.mp4`, `SvaKritAI_Demo.mp4`, `SvaKritAI_FinalPitchDeck.pdf` as the guidelines ask.
