# MeeSeva Saathi

**An AI-assisted, multilingual guide that helps every citizen of Telangana find, prepare for and follow
MeeSeva services, in Telugu, English, Hindi or Urdu, by typing or speaking.**

Submission for the **Electronic Service Delivery (ESD) Innovation Challenge**, Government Digital Services
track (Aikam / TalentFarm, ITE&C Department, Government of Telangana). Team: **SvaKrit AI**.

> Prototype. The service catalogue, fees, timelines and centre list are **sample data** prepared for the demo,
> not official MeeSeva figures. It is not connected to any government system.

---

## The problem

Citizens, especially first-time digital users, senior citizens and people who read little English, struggle
with three questions before they ever reach a MeeSeva counter:

1. **Which service do I need?** People describe a need ("my father passed away and we need the pension"),
   not a certificate name.
2. **What must I carry?** A missing document means a second trip, another day's wages and a longer queue.
3. **What does my application status mean, and what do I do now?** "Under verification" or "needs documents"
   says nothing about the next step.

## The solution

| For citizens | For ESD officials |
|---|---|
| **Ask Saathi**: describe the need in your own words and language, by text or voice; get the right service, the documents to carry, fee and time | **Insights**: the most requested services, questions by language, and the questions the catalogue could not answer (service gaps) |
| **Document checklist**: start an application, tick documents as you collect them; submit only when complete | **Feedback, tagged by AI**: sentiment and topic (documents, fees, delay, website, language, staff) |
| **Plain-language status**: what the status means and what to do next, read aloud on request | **Application processing**: update the status with remarks; the citizen is notified in their language |
| **Nearest MeeSeva centre** by location or district, with a map link | |
| **Accessible by design**: large text, high contrast, screen-reader labels, right-to-left Urdu, works on a basic phone over 4G | |

### AI functionality

- **Understanding the citizen**: language detection by script (Telugu, Devanagari, Urdu, Latin), then
  either the **Azure OpenAI** engine (gpt-5-mini, grounded in the catalogue, forced JSON output) or the
  built-in **multilingual rules engine**. The AI maps needs to services ("scholarship" → income certificate).
- **Never down**: if the AI is not configured, slow or failing, the rules engine answers instead. The app
  runs fully offline for reviewers.
- **Grounded**: the AI may answer only from the catalogue, must use the official names in the citizen's
  language, and must say "confirm at the centre" for fees and timelines.
- **Feedback analysis**: every comment is tagged with sentiment and topic (AI, with a lexicon fallback).
- **Voice**: speech-to-text and text-to-speech in the browser (te-IN, hi-IN, en-IN, ur-IN), no extra cost.

### GIGW 3.0 / accessibility

Semantic HTML, skip link, labelled controls, visible focus, keyboard operable, `aria-live` announcements,
three text sizes, high-contrast mode, `lang` and `dir="rtl"` switched with the language, reduced motion
respected, 44 px touch targets, no images or web fonts to download (fast on 4G), installable (web manifest).

## Screenshots

| Ask in Telugu | Checklist | Officials' dashboard |
|---|---|---|
| ![Ask](docs/screenshots/02-answer-te.png) | ![Checklist](docs/screenshots/05-checklist.png) | ![Dashboard](docs/screenshots/09-official.png) |

More in [`docs/screenshots/`](docs/screenshots/).

## Technology stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, FastAPI, Pydantic v2 (validation), Uvicorn |
| Database | SQLAlchemy 2 ORM; SQLite by default, any SQL database via `DATABASE_URL` (PostgreSQL in production) |
| AI | Azure OpenAI (gpt-5-mini) with a built-in multilingual rules engine as fallback |
| Frontend | HTML, CSS, vanilla JavaScript (no build step), Web Speech API for voice |
| Auth | Mobile number + 6-digit OTP (hashed, 5-minute expiry, 5 attempts); signed session tokens; citizen and official roles |
| Tests | pytest + FastAPI TestClient (41 automated tests); browser walkthrough with Playwright |

## Run it

Requirements: Python 3.11 or newer.

```bash
git clone https://github.com/chiragmakvana/meeseva-saathi.git
cd meeseva-saathi
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # optional: add Azure OpenAI settings to enable the AI engine
python -m app.seed            # create the database and load the sample data
uvicorn app.main:app --reload
```

| Open | What |
|---|---|
| http://127.0.0.1:8000 | Citizen app |
| http://127.0.0.1:8000/official | Officials' dashboard (demo official mobile: **9000000001**) |
| http://127.0.0.1:8000/docs | Interactive API documentation (Swagger) |

**Logging in:** enter any valid 10-digit mobile number (starting 6–9). No SMS is sent in the prototype; the
OTP is shown on screen (`DEMO_OTP_MODE=true`).

### Configuration (`.env`)

| Variable | Purpose | Default |
|---|---|---|
| `DATABASE_URL` | SQLAlchemy URL | `sqlite:///./meeseva_saathi.db` |
| `SECRET_KEY` | Signs sessions and hashes OTPs: **set a long random value** | demo value |
| `DEMO_OTP_MODE` | Show the OTP on screen (no SMS gateway) | `true` |
| `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_API_VERSION` | Enable the AI engine | empty → rules engine |

No keys or passwords are stored in this repository.

### Tests

```bash
pytest                         # 41 tests, runs offline
python -m scripts.test_report  # re-runs the tests and regenerates docs/TESTING.md
```

## Documentation

- [API reference](docs/API.md): every endpoint with request, response and authentication
- [Database](docs/DATABASE.md): entity-relationship diagram, tables, keys and important queries; DDL in [`db/schema.sql`](db/schema.sql)
- [Testing](docs/TESTING.md): test cases with expected and actual results, bugs found and fixed

## Project structure

```
app/
  main.py            FastAPI app, routes, startup (creates tables, loads sample data)
  config.py          settings from environment variables
  database.py        engine and sessions
  models.py          12 tables (SQLAlchemy)
  schemas.py         request/response validation
  security.py        OTP login, session tokens, roles
  assistant.py       AI layer: language detection, rules engine, Azure OpenAI, feedback tagging
  texts.py           server-side sentences in four languages
  seed.py            sample catalogue (services, documents, districts, centres)
  routers/           auth, catalogue, assistant, applications, engagement (feedback, notifications), admin
static/              citizen app (index.html, app.js, i18n.js), officials' dashboard, styles
tests/               pytest suite
db/schema.sql        database DDL (generated)
docs/                API, database, testing, screenshots
scripts/             schema export, test report
```

## Roadmap (beyond the MVP)

- Connect to the official MeeSeva service master and live application status (ESD APIs).
- SMS / WhatsApp notifications and OTP through the state gateway.
- Pre-filled application forms from DigiLocker documents, with consent.
- Kiosk mode for MeeSeva centres; Telugu speech recognition tuned for rural accents.
- Department-wise dashboards with service-level tracking.

## Team

| Member | Contribution |
|---|---|
| **Chirag Makvana** | AI assistant engine (language detection, rules engine, Azure OpenAI integration and fallback, feedback tagging), backend APIs, login and security, database design |
| **Bansi Chirag Makvana** | Citizen experience: multilingual interface, accessibility (GIGW 3.0), document checklist and status-explainer flow, officials' dashboard, test cases and walkthrough testing |

Built with AI-assisted development tools.

---

© 2026 Svakrit AI Private Limited. Shared for evaluation in the ESD Innovation Challenge.
