# Planning Pack — Leasehold Enquiry Triage Prototype

## 1. Problem restatement

Leaseholders and park homeowners often arrive at the LAS website stressed, unsure of the
correct legal term for their problem, and unsure what to do next. The first useful thing
we can offer isn't advice — it's **clarity**: help them describe their situation, map it
to a plausible category, and give them a clear, low-jargon next step (a guide to read, or
a route to a human adviser).

**For this first version, "useful" means:**

- A person can describe their situation in under a minute, in their own words or by
  picking a common scenario.
- They get back a plain-English category, a short explanation of what it usually means,
  and one clear next action.
- If we're not confident, we say so and route them to a human — we never guess with false
  confidence.
- The result is never framed as legal advice or a statement of their rights.

**Out of scope for v1:** case-specific advice, account creation, storing real personal
data, a general-purpose chatbot, and park home enquiries — LEASE runs park home
guidance as a wholly separate subsite (`parkhomes.lease-advice.org`), so triaging into
it would mean either duplicating content I have no basis to write, or building a second
information architecture. Left as a deliberate gap rather than a guess.

## 2. Assumptions

- **Advice boundary:** the tool categorises enquiries; it never asserts legal
  conclusions ("you have the right to…"). Copy is deliberately hedged ("this often
  means…") and every result screen includes a visible route to a human adviser.
- **Classification approach:** a simple keyword/rule-based matcher, not an LLM call.
  Transparent, unit-testable, no hallucination risk, and cheap to run. Noted as a
  possible future enhancement (e.g. LLM-assisted rewriting of guidance copy) but only
  ever behind human review — never generating the categorisation itself.
- **Content model:** categories, plain-English summaries, and next-step copy live in
  Wagtail so a non-technical content team could edit them without a deploy — mirroring
  how LAS likely already manages guidance content.
- **User needs:** assume varying literacy and possible disability access needs, mobile
  use, and emotional stress. Plain English (roughly age 9 reading level), generous
  spacing, no unexplained legal jargon, calm tone.
- **Category coverage:** checked against lease-advice.org's real navigation rather than
  guessing. Their site groups guidance under: _Leasehold essentials, Costs and charges,
  Lease extension, Buying and selling, Building management, Disputes,_ and _Shared
  ownership_ — each with more specific subtopics. For a first triage slice I've picked
  seven enquiry-level categories that map directly onto real LEASE guidance pages,
  rather than the whole tree:
  - Service charges (`costs-and-charges/service-charges`)
  - Ground rent (`costs-and-charges/ground-rent`)
  - Major works / Section 20 consultation (`costs-and-charges/section-20-consultation`)
  - Lease extension (`lease-extension`)
  - Right to manage (`building-management/right-to-manage`)
  - Repairs and maintenance (`building-management/repairs`)
  - Breaching your lease / forfeiture threat (`disputes/breaching-your-lease-and-forfeiture`)

  Plus an explicit "not sure" / "something else" outcome, always routed to a human.

- **Data:** dummy data only. No real names, addresses, or case details are persisted.
  If an enquiry is stored at all in this prototype, it's anonymised/session-scoped —
  explicitly flagged as not production-ready for personal data without a DPIA.
- **Team shape:** assume a small team (1-3 engineers) maintains this, so the stack stays
  boring and standard rather than clever.

## 3. Task breakdown (first vertical slice)

| #                             | Ticket                                                                | Done means…                                                                                                                                                                                                                           |
| ----------------------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| T1                            | Repo & tooling scaffold — Django + DRF backend, React (Vite) frontend | Both apps run locally from README steps; a health-check endpoint confirms they can talk to each other                                                                                                                                 |
| T2                            | Category content model in Wagtail                                     | `EnquiryCategory` snippet (name, plain-English summary, next step, keywords, guide link, urgency flag); seeded with the 7 categories above plus "not sure", editable in Wagtail admin, exposed via API                                |
| T3                            | Triage API endpoint                                                   | `POST /api/triage` accepts free text or a scenario id, returns ranked category matches + confidence, with a defined "no confident match" response; matcher logic covered by unit tests                                                |
| T4                            | Accessible intake form (frontend)                                     | Free-text field **and** "choose a common situation" buttons; labelled inputs, visible focus states, error handling; keyboard-only and screen-reader usable                                                                            |
| T5                            | Results screen                                                        | Shows top match (or top 2-3 if ambiguous) in plain English — what it usually means, next step, link to full guide — plus a persistent "speak to an adviser" / "browse all topics" escape hatch on every outcome, including "not sure" |
| T6                            | Automated tests                                                       | Backend: matcher unit tests + API test (happy path + no-match path). Frontend: component test for form submission and results rendering. Documented run commands                                                                      |
| T7 (stretch, noted not built) | Anonymised "category chosen" event log                                | Would help LAS see what people are actually asking about — listed as a natural next step, deliberately left out of this slice                                                                                                         |

Tickets are ordered so each is independently demoable — T1-T3 give a working backend
slice, T4-T5 make it usable, T6 hardens it.

## 4. Risks

- **Testing:** the matcher is rule-based, so it's easy to unit test — but brittle to
  phrasing. A reviewer should check the _false-negative_ rate (real enquiries that get
  "no match") as closely as the happy-path matches.
- **Accessibility:** must work with screen reader and keyboard only. A reviewer should
  check colour contrast, logical focus order, and that ambiguous/error states are
  announced to assistive tech, not just shown visually.
- **Personal data:** no real data is used or stored. The free-text field is the highest
  residual risk even with dummy data — people naturally type names, addresses, or case
  details unprompted. Flagged as needing input warnings/redaction and a DPIA before any
  real deployment.
- **Security:** sanitise free-text input before it touches the Wagtail/Django admin
  (stored XSS risk), rate-limit the public triage endpoint, and restrict CORS to the
  known frontend origin.
- **Advice-boundary risk (specific to this service):** the single biggest thing a
  reviewer should scrutinise. Copy must never read as a legal conclusion or a statement
  of rights, and the human-adviser escape hatch must be present on every possible
  outcome, not just the confident ones.

## AI usage note

**Planning (Part 1)**

- Verified myself: checked invented category names against the real lease-advice.org
  navigation rather than keeping guessed ones; cut "park homes" as a category after
  confirming LEASE runs it as a separate subsite.
- Adjusted plan to take account of limitations and further instructions outlined by Part 2
