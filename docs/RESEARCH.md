# Research notes: MeeSeva and the citizen experience

What we found before and while building, and how each finding shaped MeeSeva Saathi. Figures were read on
21 October 2026; portal counters change daily.

## 1. MeeSeva at a glance (official portal)

| Figure | Value | Source |
|---|---|---|
| Active services | 391 (August 2026 statistics) | [MeeSeva portal](https://ts.meeseva.telangana.gov.in/meeseva/home.htm) |
| Departments | 38 | same |
| Active centres | 5,265 | same |
| Transactions, August 2026 | 32,51,539 (₹650.54 crore) | same |
| Total requests to date | 18.79 crore | same |
| Total rejected to date | 92.2 lakh (about 4.9% of requests) | same |
| Pending beyond SLA (from Jan 2025) | 42.1 lakh | same |
| Portal languages | English, Telugu | same |

The homepage also shows a smaller set of counters (81 services, 523 centres) that the page does not reconcile
with the monthly statistics; we use the August 2026 figures. The November 2025 launch of MeeSeva on WhatsApp
cited "more than 580 G2C services across nearly 40 departments" and "5,000 MeeSeva centres"
([News On AIR, 19 Nov 2025](https://www.newsonair.gov.in/telangana-govt-launches-meeseva-on-whatsapp-for-people-to-access-govt-to-citizen-services)).

**Takeaway:** MeeSeva is large and heavily used. Even a small improvement in first-time success rates affects
lakhs of citizens a month.

## 2. Official service timelines (used in the catalogue)

From the MeeSeva Revenue Department service catalogue, as reproduced by an RTI-services site
([filemyrti.com](https://filemyrti.com/blog/telangana-meeseva-revenue-certificates-rti); verify on the portal
before relying on them):

| Certificate | Published timeline |
|---|---|
| Income, EWS, EBC, agriculture income | 7 working days |
| Residence | 6 working days |
| Caste / community, OBC, family membership | 30 working days |
| No property | 60 working days |
| Late registration of birth or death | 60 working days |
| Minority | 365 days |

Saathi's catalogue uses these for the services it covers. **Fees in the catalogue are sample values**; we did
not find an authoritative, current fee table, and secondary sources disagree (for example ₹35 + ₹10 for a
caste certificate on one site, ₹25 on an older citizen charter).

## 3. Where citizens get stuck

| Finding | Evidence | What Saathi does about it |
|---|---|---|
| People describe a need, not a service name | Support guides and RTI services exist to tell citizens *which* certificate they need; the portal is organised by department, not by life situation | The assistant maps needs to services ("scholarship" → income certificate; "pension after a death" → death certificate, then family-member certificate) and asks one clarifying question when unsure |
| Documents cause delays and rejections | A Telangana Police SOP records that "citizens uploaded unclear and blank documents", causing delays and repeat summons ([Cyberabad PMS SOP](https://cybpms.telangana.gov.in/static/assetss/doc/MeesevaservicesSOP.pdf)); 92 lakh rejections to date | A document checklist per service, filled from the catalogue; submission is blocked until every document is ticked; officers' remarks reach the citizen in their language |
| Status is opaque | Third-party guides explain what "under verification" means and recommend RTI requests to learn the reason for a delay or rejection | Every status has "what this means" and "what to do next", read aloud on request; a notification is sent on every change |
| Language | The portal offers English and Telugu only; Hyderabad has a large Urdu-speaking population and many migrant Hindi speakers; first-time digital users read little English | Telugu, Hindi, Urdu and English; voice in and out; script-based language detection so a citizen can type in any language regardless of the interface setting |
| App and portal glitches | Public complaints about unclickable fields and failed submissions after the T App Folio merger (April 2025, X) | A deliberately simple, dependency-free interface that degrades gracefully: works without the AI, without fonts, without JavaScript features such as speech |
| No feedback loop to the ESD wing | Complaints are scattered across centres, social media and RTI | The officials' dashboard surfaces top services, unanswered questions (service gaps), and AI-tagged feedback by sentiment and topic |

## 4. MeeSeva on WhatsApp (November 2025)

The state launched an AI-driven WhatsApp channel (80969 58096) covering applications, bill and challan
payments, tracking and downloads. It supplements, rather than replaces, the 5,000 centres.

**Positioning:** Saathi is not another front end. It is the *preparation and explanation* layer: it helps the
citizen choose the right service, carry the right documents and understand each status, and it gives the
department insight into what citizens actually ask. It is API-first, so the same assistant can sit behind the
WhatsApp channel, the portal, the mobile app and centre kiosks.

## 5. Standards: GIGW 3.0 and WCAG 2.1 AA

The Guidelines for Indian Government Websites and Apps 3.0 ([guidelines.india.gov.in](https://guidelines.india.gov.in/))
adopt WCAG 2.1 success criteria and add guidance on mobile and cognitive accessibility, Indian-language
support, logo alt text, accessible documents and grievance mechanisms.

What the prototype implements: semantic HTML and landmarks; skip link; labelled form controls; keyboard
operation with visible focus; `aria-live` announcements; three text sizes; a high-contrast mode; 44 px
touch targets; `lang` and `dir` switched per language (right-to-left Urdu); reduced-motion support; no
dependency on images for meaning; small page weight suitable for 4G.

What a production version would add: an accessibility statement, STQC certification, WCAG audit by a
third party, and user testing with senior citizens and persons with disabilities.

## 6. What we would validate next with the ESD wing

1. The real service master and document lists (replace sample data).
2. Status vocabulary and the plain-language explanations, with MeeSeva operators.
3. Telugu, Hindi and Urdu wording with native speakers; speech recognition accuracy with rural accents.
4. Which "unanswered questions" are true service gaps versus missing keywords.
5. Integration points: application status API, SMS gateway, WhatsApp channel.

## Sources

- MeeSeva portal, statistics and department list: https://ts.meeseva.telangana.gov.in/meeseva/home.htm
- News On AIR, MeeSeva on WhatsApp, 19 Nov 2025: https://www.newsonair.gov.in/telangana-govt-launches-meeseva-on-whatsapp-for-people-to-access-govt-to-citizen-services
- Cyberabad Police, MeeSeva services SOP: https://cybpms.telangana.gov.in/static/assetss/doc/MeesevaservicesSOP.pdf
- Revenue certificate timelines (secondary): https://filemyrti.com/blog/telangana-meeseva-revenue-certificates-rti
- GIGW 3.0: https://guidelines.india.gov.in/ and the 2025 manual (PDF) linked from it
- Wikipedia, Mee Seva (Telangana), for history: https://en.wikipedia.org/wiki/Mee_Seva_(Telangana)
