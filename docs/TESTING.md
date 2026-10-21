# Testing

Automated tests: **42 passed, 0 failed** (generated 21 Oct 2026 16:24 by `python -m scripts.test_report`, from the actual pytest run).

Each test runs against a fresh database with the sample catalogue. The AI provider is mocked where a test needs it, so the suite runs offline and gives the same result every time.

| Module | Test case | Expected result | Actual result | Status |
|---|---|---|---|---|
| Applications | Start an application | Draft created with reference number and document checklist | Draft created with reference number and document checklist | Pass |
| Applications | Submit with documents not ticked | Rejected; missing documents listed | Rejected; missing documents listed | Pass |
| Applications | Tick all documents and submit; then try to edit or delete | Submitted; later edits and deletes refused (409) | Submitted; later edits and deletes refused (409) | Pass |
| Applications | Edit, list and delete a draft | Saved, listed, deleted | Saved, listed, deleted | Pass |
| Applications | Open another citizen's application | Not found (404) | Not found (404) | Pass |
| Applications | Unknown service; one-letter applicant name | Rejected with validation errors | Rejected with validation errors | Pass |
| AI assistant | Ask for a service in English, Telugu, Hindi and Urdu (6 phrasings) — "I need an income certificate for my scholarship" | Correct service, language and document list | Correct service, language and document list | Pass |
| AI assistant | Ask for a service in English, Telugu, Hindi and Urdu (6 phrasings) — "నాకు ఆదాయ ధృవీకరణ పత్రం కావాలి" | Correct service, language and document list | Correct service, language and document list | Pass |
| AI assistant | Ask for a service in English, Telugu, Hindi and Urdu (6 phrasings) — "मुझे जाति प्रमाण पत्र चाहिए" | Correct service, language and document list | Correct service, language and document list | Pass |
| AI assistant | Ask for a service in English, Telugu, Hindi and Urdu (6 phrasings) — "مجھے پیدائش سرٹیفکیٹ چاہیے" | Correct service, language and document list | Correct service, language and document list | Pass |
| AI assistant | Ask for a service in English, Telugu, Hindi and Urdu (6 phrasings) — "police verification for my new job" | Correct service, language and document list | Correct service, language and document list | Pass |
| AI assistant | Ask for a service in English, Telugu, Hindi and Urdu (6 phrasings) — "how do I pay my current bill" | Correct service, language and document list | Correct service, language and document list | Pass |
| AI assistant | Ask in Telugu while the app is set to English | Reply written in Telugu | Reply written in Telugu | Pass |
| AI assistant | Ask for a service MeeSeva does not offer | Polite 'not found' plus popular service suggestions | Polite 'not found' plus popular service suggestions | Pass |
| AI assistant | Ask one answerable and one unanswerable question | Both logged; dashboard shows 2 questions, 1 unanswered | Both logged; dashboard shows 2 questions, 1 unanswered | Pass |
| AI assistant | Send a one-character question | Rejected with a validation error | Rejected with a validation error | Pass |
| AI assistant | Detect language from Telugu, Devanagari, Urdu and Latin script | Correct language codes | Correct language codes | Pass |
| AI assistant | Ask with the AI engine configured | AI answer used, service card attached | AI answer used, service card attached | Pass |
| AI assistant | AI engine times out | Falls back to the rules engine; citizen still gets the answer | Falls back to the rules engine; citizen still gets the answer | Pass |
| AI assistant | Model echoes a service code or name in brackets | Echo removed; other brackets kept | Echo removed; other brackets kept | Pass |
| Login | Request OTP with an invalid mobile number | Rejected with a validation error (422) | Rejected with a validation error (422) | Pass |
| Login | Log in with a valid OTP (first time) | Account created, session token issued, profile returned | Account created, session token issued, profile returned | Pass |
| Login | Mobile number entered with +91 and spaces | Normalised and accepted | Normalised and accepted | Pass |
| Login | Log in with a wrong OTP | Rejected (401) | Rejected (401) | Pass |
| Login | Reuse an OTP that was already used | Rejected (401) | Rejected (401) | Pass |
| Login | Five wrong OTP attempts, then the right OTP | OTP locked, login rejected | OTP locked, login rejected | Pass |
| Login | Open applications without a token / with a forged token | Rejected (401) | Rejected (401) | Pass |
| Login | Update language and district; unknown district | Profile saved; unknown district rejected | Profile saved; unknown district rejected | Pass |
| Catalogue | List all services | 19 services returned | 19 services returned | Pass |
| Catalogue | List services in Telugu | Telugu service names | Telugu service names | Pass |
| Catalogue | Search services with a Telugu word | Caste certificate ranked first | Caste certificate ranked first | Pass |
| Catalogue | Open a service; open a non-existent service | Details with documents; 404 for missing | Details with documents; 404 for missing | Pass |
| Centres | Find centres near a location | Nearest centre first, sorted by distance | Nearest centre first, sorted by distance | Pass |
| Centres | Filter centres by district | Only that district's centres | Only that district's centres | Pass |
| Centres | Search with an impossible latitude | Rejected with a validation error | Rejected with a validation error | Pass |
| Officials | Citizen opens the officials' dashboard | Forbidden (403) | Forbidden (403) | Pass |
| Officials | Official marks an application 'needs documents' with remarks | Citizen notified in Telugu with remarks; notification can be marked read | Citizen notified in Telugu with remarks; notification can be marked read | Pass |
| Officials | Official updates a draft the citizen has not submitted | Refused (409) | Refused (409) | Pass |
| Officials | Official sets an unknown status | Rejected with a validation error | Rejected with a validation error | Pass |
| Feedback | Negative English and positive Telugu feedback | Tagged negative/delay and positive; dashboard average 3.5 | Tagged negative/delay and positive; dashboard average 3.5 | Pass |
| Feedback | Ratings 0 and 6 | Rejected with validation errors | Rejected with validation errors | Pass |
| System | Health check, citizen app and dashboard pages | All load | All load | Pass |

## Manual and browser testing

End-to-end walkthrough in a headless Chromium browser (mobile viewport 412×880 and desktop 1280×900), recorded in `docs/screenshots/`:

| Flow | Result |
|---|---|
| Ask in Telugu → income certificate card with documents, fee, time | Pass |
| Switch to English → police verification; unknown request → suggestions | Pass |
| Log in with mobile + OTP | Pass |
| Start residence certificate → checklist → tick all → submit | Pass |
| Give 'not helpful' feedback with a comment | Pass |
| Nearest centres list | Pass |
| Ask in Urdu (right-to-left layout) | Pass |
| Official logs in, sees insights, sets 'needs documents' with remarks | Pass |
| Citizen receives the notification in their language | Pass |
| Browser console errors during the walkthrough | None |

Live AI engine (Azure OpenAI, gpt-5-mini) checked with Telugu, Hindi, Urdu and English questions: correct service in each case, answers in about 2–3 seconds.

## Bugs found and fixed

| Bug | Fix | Retested |
|---|---|---|
| Telugu answers listed the documents twice (reply text and service card) | Show the short reply when a card is shown; 'Listen' still reads the full answer | Yes |
| Third checklist checkbox shrank when its label wrapped | Checkbox no longer shrinks | Yes |
| Changing language while a page was loading let the old page overwrite the new one | Each navigation gets a run number; stale loads stop | Yes |
| Urdu (right-to-left) pages scrolled sideways because of the skip link | Skip link hidden vertically instead of off to the side | Yes |
| AI returned empty answers in Telugu (model used its token budget on reasoning) | Minimal reasoning effort and a larger output budget | Yes |
| AI did not map 'scholarship' to the income certificate | Need-to-service guidance and keyword hints in the prompt | Yes |
| A local `.env` with real keys could make tests call the live AI | Tests blank the AI settings before loading | Yes |

## Known limitations

- Catalogue, fees, timelines and centres are sample data, not official MeeSeva figures.
- OTPs are shown on screen in demo mode; production needs an SMS gateway.
- Voice input depends on the browser's speech support (best in Chrome on Android).
- Translations are first drafts and need review by native speakers.
