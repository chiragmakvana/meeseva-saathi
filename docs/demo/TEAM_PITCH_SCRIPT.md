# Team pitch script, slide by slide

Two presenters, **Chirag** and **Bansi**. One section per slide of the deck, in deck order, with the exact words. Spoken time about 7.3 minutes plus slide changes: aim to finish under 8 minutes. The same words are in each slide's speaker notes and in the draft pitch video (`SvaKritAI_TeamPitch_DRAFT.mp4`), which you can use as a timing rehearsal.

**Recording:** share the deck in Presenter view (notes visible to you only) or the exported PDF; camera on both of you. Record in sections if easier; cut on the slide changes. Name the file `SvaKritAI_TeamPitch.mp4`.

| Slide | Title | Speaker | Time |
|---|---|---|---|
| 1 | MeeSeva Saathi | Chirag | 22 s |
| 2 | MeeSeva today | Chirag | 32 s |
| 3 | Three questions stand between a citizen and the counter | Chirag | 36 s |
| 4 | A companion that prepares the citizen and informs the department | Bansi | 33 s |
| 5 | Ask Saathi | Bansi | 30 s |
| 6 | Prepare and track | Bansi | 29 s |
| 7 | How the AI works | Chirag | 47 s |
| 8 | Technology and testing | Chirag | 32 s |
| 9 | Accessibility · GIGW 3.0 and WCAG 2.1 AA | Bansi | 31 s |
| 10 | For the ESD Wing | Bansi | 32 s |
| 11 | Where it fits | Chirag | 34 s |
| 12 | MVP and roadmap | Chirag | 30 s |
| 13 | Team SvaKrit AI | Bansi | 29 s |
| 14 | Let citizens ask in their own words | Bansi then Chirag | 22 s |

## Slide 1 of 14 · MeeSeva Saathi

**Speaker:** Chirag · **about 22 s** · starts near 0:00

**On screen:** Title, one-line promise, team names, GitHub link.

**Chirag:**

> Namaste. I am Chirag Makvana, and with me is Bansi. We are SvaKrit AI from Hyderabad, and this is MeeSeva Saathi: a companion that helps every citizen of Telangana find, prepare for and follow MeeSeva services, in Telugu, English, Hindi or Urdu.

## Slide 2 of 14 · MeeSeva today

**Speaker:** Chirag · **about 32 s** · starts near 0:21

**On screen:** Six figures from the MeeSeva portal: 391 services · 5,265 centres · 32.5 lakh transactions · 42 lakh pending beyond SLA · 92 lakh rejected · 2 languages.

**Chirag:**

> MeeSeva is one of the largest citizen service networks in the country: 391 services, 5,265 centres, and 32 lakh transactions a month. But the official portal also shows 42 lakh applications pending beyond their time limit since January 2025, and 92 lakh rejections to date. And the portal speaks only English and Telugu.

## Slide 3 of 14 · Three questions stand between a citizen and the counter

**Speaker:** Chirag · **about 36 s** · starts near 0:53

**On screen:** The three questions: which service, what to carry, what the status means.

**Chirag:**

> Behind those numbers are three questions every citizen struggles with before reaching a counter. Which service do I need? People describe a situation, like my father passed away and we need the pension, not a certificate name. What must I carry? A police SOP records that unclear or missing documents cause delays and repeat visits. And what does my status mean? Under verification tells you nothing about the next step.

## Slide 4 of 14 · A companion that prepares the citizen and informs the department

**Speaker:** Bansi · **about 33 s** · starts near 1:29

**On screen:** Four cards: Ask, Prepare, Track (citizen) and Insights (ESD Wing).

**Bansi:**

> Hello, I am Bansi. Saathi answers those three questions in the citizen's own language, by typing or speaking. You describe what you need; Saathi tells you the service, the documents, the fee and the time. It keeps a checklist so you never make a second trip for a missing paper. It explains every status in plain words and tells you what to do next. And the department gets a dashboard of what citizens ask and where they get stuck.

## Slide 5 of 14 · Ask Saathi

**Speaker:** Bansi · **about 30 s** · starts near 2:02

**On screen:** Two phone screens: Telugu home; the pension question answered with the Death Certificate card.

**Bansi:**

> Here is the app. The home screen is Telugu-first, with one question box, popular services and categories. When a citizen writes that their father passed away and they need to claim his pension, the AI replies with the death certificate, the three documents to carry, the fee and time, and points to the family member certificate that comes next. Every answer has a Listen button that reads it aloud.

**Live-demo option (recommended):** instead of the screenshots, switch to the running app here and say the slide 5 and slide 6 words while clicking through runbook steps 1–4 and 9–11 (`LIVE_DEMO_STEPS.md`). Keep to the same 60 seconds; come back to the deck at slide 7. If the app misbehaves, stay on the slides: the words are identical.

## Slide 6 of 14 · Prepare and track

**Speaker:** Bansi · **about 29 s** · starts near 2:32

**On screen:** Two phone screens: submitted application with timeline and checklist; the services list.

**Bansi:**

> Starting an application creates a document checklist. The citizen ticks each document as they collect it, and cannot submit until the list is complete. After submission, a four-step timeline shows where the application is, with what this means and what to do next in the citizen's language. The catalogue covers 19 services across six categories, with the official MeeSeva timelines.

## Slide 7 of 14 · How the AI works

**Speaker:** Chirag · **about 47 s** · starts near 3:01

**On screen:** Flow: Detect → Understand → Fall back → Learn, with the grounding rules underneath.

**Chirag:**

> I built the assistant and the backend. Every question first goes through language detection by script, so a citizen can type Telugu even when the interface is in English. Then Azure OpenAI answers, but only from our service catalogue: it may not invent services, fees or timelines, it must use the official names in the citizen's language, and it must say confirm at the centre. If the AI is slow or unavailable, a multilingual rules engine answers from the same catalogue, so the service is never down. Every question and rating is logged, and feedback is tagged by sentiment and topic.

## Slide 8 of 14 · Technology and testing

**Speaker:** Chirag · **about 32 s** · starts near 3:48

**On screen:** Four cards: Backend, AI, Frontend, Testing; the repository link.

**Chirag:**

> The backend is FastAPI with a twelve-table database: services, documents, applications with their checklists, every question asked, feedback and notifications. Login is mobile plus OTP with hashed codes and signed sessions; citizens see only their own applications, and officials have a separate role. The whole repository is open, with the research notes, the schema and the test report.

## Slide 9 of 14 · Accessibility · GIGW 3.0 and WCAG 2.1 AA

**Speaker:** Bansi · **about 31 s** · starts near 4:19

**On screen:** Four cards: Language, Readable, Operable, Light.

**Bansi:**

> I built what the citizen and the officer see. The interface follows GIGW 3.0 and WCAG 2.1 double-A: Telugu, Hindi, Urdu with right-to-left layout, and English; three text sizes; a high-contrast mode; screen-reader labels; keyboard operation; large touch targets; and voice in and out for people who read little. It is light enough to work on a basic phone over 4G.

## Slide 10 of 14 · For the ESD Wing

**Speaker:** Bansi · **about 32 s** · starts near 4:50

**On screen:** Dashboard screenshot with four points: top services, service gaps, AI-tagged feedback, processing.

**Bansi:**

> The officials' dashboard shows the most requested services, questions by language, unanswered questions as service gaps, and feedback tagged by sentiment and topic. An officer updates an application with remarks, and the citizen is notified in their language. I also wrote the 42 automated tests across login, the assistant in four languages, applications, officials and feedback, plus the browser walkthrough.

## Slide 11 of 14 · Where it fits

**Speaker:** Chirag · **about 34 s** · starts near 5:22

**On screen:** Three channel cards: MeeSeva on WhatsApp, portal and app, centre kiosks.

**Chirag:**

> What makes Saathi different: it works before the citizen applies, not just after. It is grounded, so it never invents a fee or a document. It is the first MeeSeva experience in Hindi and Urdu. And it closes the loop with a feedback dashboard for the ESD Wing. It is API-first, so the same assistant can sit behind the MeeSeva WhatsApp channel launched last November, the portal, and centre kiosks.

## Slide 12 of 14 · MVP and roadmap

**Speaker:** Chirag · **about 30 s** · starts near 5:56

**On screen:** Two columns: MVP built (five rows) and Next (five rows).

**Chirag:**

> Everything on the left works today. Next, we would connect the official service master and live application status, deploy behind WhatsApp with SMS OTP, pre-fill forms from DigiLocker with consent, tune Telugu speech for rural accents, and add department dashboards. The service list, fees and centres in the prototype are sample data; the timelines follow the official revenue catalogue.

## Slide 13 of 14 · Team SvaKrit AI

**Speaker:** Bansi · **about 29 s** · starts near 6:26

**On screen:** Two cards: Chirag and Bansi, with what each built.

**Bansi:**

> We are a team of two. Chirag did the research, the AI engine, the backend, security and the database. I did the citizen experience, accessibility, the application flow, the officials' dashboard and testing. SvaKrit AI is a Hyderabad startup, DPIIT-recognised and a member of NVIDIA Inception, Microsoft for Startups and AWS Activate.

## Slide 14 of 14 · Let citizens ask in their own words

**Speaker:** Bansi then Chirag · **about 22 s** · starts near 6:55

**On screen:** The ask (a pilot with the ESD Wing) and contact details.

**Bansi:**

> Our ask is a pilot with the ESD Wing on one district's most requested services, against the real service master, measuring first-time success and repeat visits.

**Chirag:**

> The code, research and tests are open at github dot com slash chiragmakvana slash meeseva-saathi. Thank you.

---

Generated by `python -m scripts.pitch_script` from `pitch_segments.json`. To change the words, edit that file, then re-run this script, `python -m scripts.narrate docs/demo/pitch_segments.json docs/demo/pitch_audio` and the deck notes.
