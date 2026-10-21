"""Run the test suite and write docs/TESTING.md (test case | expected | actual | status) from the real results.

Run: python -m scripts.test_report
"""
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
XML = ROOT / "tests" / "results.xml"

# test name -> (module, test case, expected result)
CASES = {
    "test_invalid_mobile_rejected": ("Login", "Request OTP with an invalid mobile number", "Rejected with a validation error (422)"),
    "test_login_with_valid_otp_creates_account": ("Login", "Log in with a valid OTP (first time)", "Account created, session token issued, profile returned"),
    "test_plus91_prefix_accepted": ("Login", "Mobile number entered with +91 and spaces", "Normalised and accepted"),
    "test_wrong_otp_rejected": ("Login", "Log in with a wrong OTP", "Rejected (401)"),
    "test_otp_cannot_be_reused": ("Login", "Reuse an OTP that was already used", "Rejected (401)"),
    "test_otp_locked_after_five_wrong_attempts": ("Login", "Five wrong OTP attempts, then the right OTP", "OTP locked, login rejected"),
    "test_protected_routes_need_login": ("Login", "Open applications without a token / with a forged token", "Rejected (401)"),
    "test_profile_update": ("Login", "Update language and district; unknown district", "Profile saved; unknown district rejected"),
    "test_matches_service_in_four_languages": ("AI assistant", "Ask for a service in English, Telugu, Hindi and Urdu (6 phrasings)", "Correct service, language and document list"),
    "test_reply_written_in_detected_language": ("AI assistant", "Ask in Telugu while the app is set to English", "Reply written in Telugu"),
    "test_unknown_request_suggests_popular_services": ("AI assistant", "Ask for a service MeeSeva does not offer", "Polite 'not found' plus popular service suggestions"),
    "test_question_is_logged_for_insights": ("AI assistant", "Ask one answerable and one unanswerable question", "Both logged; dashboard shows 2 questions, 1 unanswered"),
    "test_text_too_short_rejected": ("AI assistant", "Send a one-character question", "Rejected with a validation error"),
    "test_detect_lang_scripts": ("AI assistant", "Detect language from Telugu, Devanagari, Urdu and Latin script", "Correct language codes"),
    "test_ai_engine_used_when_configured": ("AI assistant", "Ask with the AI engine configured", "AI answer used, service card attached"),
    "test_falls_back_to_rules_when_ai_fails": ("AI assistant", "AI engine times out", "Falls back to the rules engine; citizen still gets the answer"),
    "test_echoed_names_and_codes_removed": ("AI assistant", "Model echoes a service code or name in brackets", "Echo removed; other brackets kept"),
    "test_lists_all_services": ("Catalogue", "List all services", "19 services returned"),
    "test_service_names_localised": ("Catalogue", "List services in Telugu", "Telugu service names"),
    "test_search_in_telugu": ("Catalogue", "Search services with a Telugu word", "Caste certificate ranked first"),
    "test_service_detail_and_missing": ("Catalogue", "Open a service; open a non-existent service", "Details with documents; 404 for missing"),
    "test_nearest_centre_by_location": ("Centres", "Find centres near a location", "Nearest centre first, sorted by distance"),
    "test_centres_by_district": ("Centres", "Filter centres by district", "Only that district's centres"),
    "test_invalid_coordinates_rejected": ("Centres", "Search with an impossible latitude", "Rejected with a validation error"),
    "test_create_application_builds_checklist": ("Applications", "Start an application", "Draft created with reference number and document checklist"),
    "test_cannot_submit_with_missing_documents": ("Applications", "Submit with documents not ticked", "Rejected; missing documents listed"),
    "test_tick_all_and_submit": ("Applications", "Tick all documents and submit; then try to edit or delete", "Submitted; later edits and deletes refused (409)"),
    "test_update_list_and_delete_draft": ("Applications", "Edit, list and delete a draft", "Saved, listed, deleted"),
    "test_citizens_cannot_see_each_others_applications": ("Applications", "Open another citizen's application", "Not found (404)"),
    "test_validation_errors": ("Applications", "Unknown service; one-letter applicant name", "Rejected with validation errors"),
    "test_citizen_cannot_open_dashboard": ("Officials", "Citizen opens the officials' dashboard", "Forbidden (403)"),
    "test_status_change_notifies_citizen_in_their_language": ("Officials", "Official marks an application 'needs documents' with remarks", "Citizen notified in Telugu with remarks; notification can be marked read"),
    "test_official_cannot_act_on_unsubmitted_draft": ("Officials", "Official updates a draft the citizen has not submitted", "Refused (409)"),
    "test_invalid_status_rejected": ("Officials", "Official sets an unknown status", "Rejected with a validation error"),
    "test_feedback_is_classified": ("Feedback", "Negative English and positive Telugu feedback", "Tagged negative/delay and positive; dashboard average 3.5"),
    "test_feedback_rating_validated": ("Feedback", "Ratings 0 and 6", "Rejected with validation errors"),
    "test_health_and_pages": ("System", "Health check, citizen app and dashboard pages", "All load"),
}


def main() -> int:
    code = subprocess.call([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", f"--junitxml={XML}"], cwd=ROOT)
    suite = ET.parse(XML).getroot()
    suite = suite if suite.tag == "testsuite" else suite.find("testsuite")
    rows, passed, failed = [], 0, 0
    for tc in suite.iter("testcase"):
        name = tc.get("name").split("[")[0]
        variant = tc.get("name")[len(name):]
        if variant:  # "[text-lang-code]" with unicode escapes -> ' — "text"'
            text = variant.strip("[]").encode("ascii", "backslashreplace").decode("unicode_escape").rsplit("-", 2)[0]
            variant = f'— "{text}"'
        ok = tc.find("failure") is None and tc.find("error") is None
        passed += ok
        failed += not ok
        module, case, expected = CASES.get(name, ("Other", name, "-"))
        actual = expected if ok else (tc.find("failure") or tc.find("error")).get("message", "failed")[:120]
        rows.append(f"| {module} | {case}{' ' + variant.rstrip("'") if variant else ''} | {expected} | {actual} | {'Pass' if ok else 'FAIL'} |")
    md = [
        "# Testing", "",
        f"Automated tests: **{passed} passed, {failed} failed** (generated {datetime.now():%d %b %Y %H:%M} by "
        "`python -m scripts.test_report`, from the actual pytest run).", "",
        "Each test runs against a fresh database with the sample catalogue. The AI provider is mocked where a test "
        "needs it, so the suite runs offline and gives the same result every time.", "",
        "| Module | Test case | Expected result | Actual result | Status |", "|---|---|---|---|---|", *rows, "",
        "## Manual and browser testing", "",
        "End-to-end walkthrough in a headless Chromium browser (mobile viewport 412×880 and desktop 1280×900), "
        "recorded in `docs/screenshots/`:", "",
        "| Flow | Result |", "|---|---|",
        "| Ask in Telugu → income certificate card with documents, fee, time | Pass |",
        "| Switch to English → police verification; unknown request → suggestions | Pass |",
        "| Log in with mobile + OTP | Pass |",
        "| Start residence certificate → checklist → tick all → submit | Pass |",
        "| Give 'not helpful' feedback with a comment | Pass |",
        "| Nearest centres list | Pass |",
        "| Ask in Urdu (right-to-left layout) | Pass |",
        "| Official logs in, sees insights, sets 'needs documents' with remarks | Pass |",
        "| Citizen receives the notification in their language | Pass |",
        "| Browser console errors during the walkthrough | None |", "",
        "Live AI engine (Azure OpenAI, gpt-5-mini) checked with Telugu, Hindi, Urdu and English questions: "
        "correct service in each case, answers in about 2–3 seconds.", "",
        "## Bugs found and fixed", "",
        "| Bug | Fix | Retested |", "|---|---|---|",
        "| Telugu answers listed the documents twice (reply text and service card) | Show the short reply when a card is shown; 'Listen' still reads the full answer | Yes |",
        "| Third checklist checkbox shrank when its label wrapped | Checkbox no longer shrinks | Yes |",
        "| Changing language while a page was loading let the old page overwrite the new one | Each navigation gets a run number; stale loads stop | Yes |",
        "| Urdu (right-to-left) pages scrolled sideways because of the skip link | Skip link hidden vertically instead of off to the side | Yes |",
        "| AI returned empty answers in Telugu (model used its token budget on reasoning) | Minimal reasoning effort and a larger output budget | Yes |",
        "| AI did not map 'scholarship' to the income certificate | Need-to-service guidance and keyword hints in the prompt | Yes |",
        "| A local `.env` with real keys could make tests call the live AI | Tests blank the AI settings before loading | Yes |", "",
        "## Known limitations", "",
        "- Catalogue, fees, timelines and centres are sample data, not official MeeSeva figures.",
        "- OTPs are shown on screen in demo mode; production needs an SMS gateway.",
        "- Voice input depends on the browser's speech support (best in Chrome on Android).",
        "- Translations are first drafts and need review by native speakers.",
    ]
    (ROOT / "docs" / "TESTING.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    XML.unlink(missing_ok=True)
    print(f"docs/TESTING.md written: {passed} passed, {failed} failed")
    return code


if __name__ == "__main__":
    sys.exit(main())
