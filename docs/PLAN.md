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

**T1 - Repo & tooling scaffold**

- What helped: used AI to generate the Wagtail/DRF/Vite boilerplate (health-check view,
  URL wiring, `App.jsx` fetch call, README skeleton) — the kind of first-draft code
  that has one obviously-correct shape and isn't worth typing from scratch.
- What I rejected/changed: the first venv-activation command given was bash syntax
  (`source venv/bin/activate`), which doesn't work on Windows PowerShell — swapped for
  the PowerShell-specific `Activate.ps1` command instead.
- What I considered: asked about Oxlint vs ESLint; went with ESLint on the stated
  reasoning that `jsx-a11y` accessibility coverage matters more for this brief than
  Oxlint's speed advantage, rather than defaulting to whichever was suggested first.
- What I verified myself: ran the backend and actually hit `/api/health/` and
  `/admin/` rather than trusting the code as written; confirmed CORS was genuinely
  working by seeing "ok" render in the browser, not just assuming the fetch would
  succeed; generated `requirements.txt` from my own local `pip freeze` rather than
  accepting a guessed dependency list.

**T2 - Category content model in Wagtail**

- What helped: used AI to scaffold the `EnquiryCategory` snippet model, serializer,
  viewset/router wiring, and the data migration seeding the 7 categories plus "not
  sure" — boilerplate with one obviously-correct shape.
- What I verified myself: ran `makemigrations`/`migrate` and checked
  `EnquiryCategory.objects.count() == 8` in the Django shell rather than trusting the
  migration file as written; started the dev server and hit `GET /api/categories/`
  and `/api/categories/<slug>/` directly to confirm the API returns real data;
  confirmed the model appears in `get_snippet_models()` so it's genuinely editable in
  the Wagtail admin, not just decorated with `@register_snippet` and assumed to work.
- What I caught and rejected: noticed `backend/requirements.txt` had been silently
  overwritten with an unrelated package list (yt-dlp, PlexAPI, etc.) — looked like a
  `pip freeze` run against the wrong environment. Checked the project's actual venv
  was still Django 5.2.17/Wagtail 8.0 before reverting the file, rather than
  assuming either version was correct.
- What I got wrong and fixed: the first-pass `guide_link` URLs were built by
  pattern-matching the path segments named in the Part 1 plan (e.g.
  `costs-and-charges/service-charges`) under a guessed `/advice-guide/` prefix,
  without checking they resolved. All 7 came back `403` from a plain `curl` (bot
  blocking), which could have masked the real problem — retried with a browser
  user-agent and got genuine `404`s. Read the live site's actual navigation in the
  browser, found the real paths (no `/advice-guide/` prefix), corrected the seed
  migration, and re-verified all 7 URLs return `200` before treating it as done.

**T3 - Triage API endpoint**

- What helped: used AI to scaffold the keyword matcher (`matching.py`), the
  `POST /api/triage` view, and the `TriageMatchSerializer` — a rule-based first
  draft that had one obviously-correct shape given the model already built in T2.
- What I decided: confidence is a simple tiered score (0.5/0.75/0.95 by number of
  keyword hits) rather than anything more statistical — matches the plan's stated
  approach ("transparent, unit-testable, no hallucination risk") over a fancier
  scoring scheme that would be harder to justify to a non-technical reviewer.
- What I decided: picking the "not sure" scenario explicitly (`scenario_id:
  "not-sure"`) returns `confident: false` rather than a fake 100%-confidence
  match on the not-sure category itself — keeps the "always routes to a human"
  rule from Part 1 true for every path through the endpoint, not just the
  free-text no-match path.
- What I verified myself: ran the Django test suite (13 tests: matcher scoring/
  ranking/no-match cases, plus API happy path, no-match, scenario_id, and error
  cases) and got a real `OK`, not just read the test file. Caught that my first
  test draft tried to create categories with slugs the seed migration
  (`0002_seed_categories`) already inserts into the test DB, causing a
  `UNIQUE constraint failed` — rewrote the tests to use the seeded categories
  directly instead of masking the collision. Also started the dev server and hit
  `/api/triage/` with curl for the happy-path, no-match, scenario_id, and
  missing-input cases to confirm real responses matched what the tests asserted,
  then confirmed the server process was actually killed afterwards rather than
  assuming a background job had stopped.

**T4 - Accessible intake form**

- What helped: used AI to scaffold `TriageForm.jsx` (labelled textarea, scenario
  buttons sourced live from `/api/categories/`, validation/submit/error states)
  and the focus-visible/error styling in `index.css` — boilerplate with one
  obviously-correct accessible shape (real `<label>`/`<button>` elements,
  `role="alert"` on errors, focus returned to the field on validation failure).
- What I verified myself: read the rendered accessibility tree (not just the
  JSX) to confirm labels, roles, and the live region were exposed correctly;
  drove the form with clicks standing in for keyboard interaction to confirm
  the empty-submit error appears and focus returns to the textarea, that a real
  free-text enquiry resolves to the right category, and that the "Not sure"
  scenario button correctly comes back as `confident: false` rather than a
  fake match. Ran `npm run lint` and got a clean pass rather than assuming the
  scaffolded code was lint-clean.
- What I caught and rejected: started wiring a Ctrl/Cmd+Enter submit shortcut
  on the textarea, but decided against adding it — an extra interaction to
  document and test for a form with only one other required action (click
  Check my situation) isn't worth the complexity it adds. Removed the handler
  before it landed rather than leaving unused code from an abandoned idea in
  the file.
- What I decided: kept the current result rendering under the form as an
  explicitly-labelled placeholder (raw category name/summary/next-step)
  rather than building out the real results layout now — that's T5's job per
  the plan's ticket split, and building it early would mean redoing work once
  T5's actual requirements (top-2/3 ambiguous handling, persistent adviser
  escape hatch) are in scope.
- What I adjusted on request: moved the submit button under the textarea with
  a small gap and centered it, reworked the page's vertical spacing to use
  consistent flex gaps instead of ad-hoc margins, and sorted the "Not sure /
  something else" scenario button to the end of the list instead of wherever
  it fell alphabetically from the API response — content ordering concerns
  handled client-side rather than changing the Wagtail model's ordering, which
  is also used elsewhere.

**T5 - Results screen**

- What helped: used AI to scaffold `ResultsScreen.jsx` (single/ambiguous/
  not-sure layouts, urgent-category warning, persistent escape hatch) and the
  matching `index.css` rules — boilerplate with one obviously-correct shape
  given the API response already built in T3.
- What I decided: the "ambiguous" case is driven directly by the length of
  the `matches` array the backend already returns (capped at 3 by
  `MAX_MATCHES` in `matching.py`), rather than inventing a separate
  front-end ambiguity heuristic — one source of truth for "how many matches
  count as ambiguous."
- What I verified myself: checked the "speak to an adviser" and "browse all
  topics" links against the live site rather than guessing — confirmed
  `/contact-us/` is real, and that there's no single all-topics hub page, so
  "browse all topics" points at the homepage (which carries the full nav)
  instead of a guessed `/advice-guides/`-style URL that would 404. Ran the
  app in the browser and drove all three outcomes (single match, an
  ambiguous free-text enquiry matching two categories at once, and the
  explicit "Not sure" button) to confirm each renders the right heading,
  copy, and escape hatch. Read the accessibility tree to confirm the
  results heading receives focus after each submission, so screen-reader
  and keyboard users land on the new content rather than having to find it.
  Ran `npm run lint` and got a clean pass.
- What I adjusted from the site's existing style: left-aligned the
  category summary/next-step text (`.category-details`) instead of the
  centered body text used elsewhere on the page — a deliberate, narrowly
  scoped deviation, since centered multi-line paragraphs are harder to read
  for the varying-literacy/possible-disability audience assumed in the plan.
