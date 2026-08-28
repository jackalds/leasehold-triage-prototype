# Hardening & Review Notes

This documents a focused hardening pass over the feature-complete prototype (T1–T6).
Scope was chosen from the Risks section in [PLAN.md](PLAN.md#4-risks), which the
author had already flagged as the open gaps. Out of scope, per
[README.md](../README.md)'s "deliberately left out" list: accounts/real personal-data
storage, production deploy/infra hardening, a DPIA, and the T7 event-log stretch ticket.

## Personal data & security

**What's collected.** One field: free text describing the enquiry, submitted once per
triage request. It is never written to any database table — `backend/api/views.py`
scores it in-memory against `EnquiryCategory` and discards it. No accounts, no
cookies, no analytics, no other personal-data-shaped fields exist anywhere in the app.

**What was deliberately not built.** Account creation, any form of persistence for
submitted text, and anything that would let one enquiry be linked to another. If a
future ticket (e.g. the T7 stretch — an event log of which categories get matched)
ever needs aggregate data, it should log only the matched category slug, never the
free text itself, and would need a DPIA first, as PLAN.md already notes.

**Retention, access, deletion.** Currently moot — nothing is retained. If this went
further and *did* start storing anything (even just category-slug analytics), the
default should be the shortest retention that serves the purpose, no admin UI access
beyond what's needed to run the service, and a documented deletion path — none of
which exists today because there's nothing to delete.

**Security risks found and fixed this pass:**
- A non-string `text` value (e.g. a JSON list) crashed the endpoint with an unhandled
  500 (`AttributeError` in `match_text`'s `.lower()` call). Fixed with a type guard in
  the view, returning 400. Also added a length cap (1,200 characters, ~200 words) so
  the endpoint can't be handed arbitrarily large payloads to score.
- The public `/api/triage/` endpoint had no rate limiting. Added a per-IP throttle
  (20 requests/minute) via a small `AnonRateThrottle` subclass, scoped so it doesn't
  affect the read-only `/api/categories/` endpoints.

**Residual risk, not fixed this pass.** Nothing in the current settings enables
verbose request/SQL logging, but if that were ever turned on (debug tooling, an APM
integration), it could incidentally capture free text containing personal details —
exactly what the new textarea hint asks users not to type in. No scrubbing or
redaction exists to catch that if it happened; flagging it rather than building for a
logging configuration that doesn't exist yet. Also unresolved, and already known:
`ALLOWED_HOSTS = ["*"]` in dev, and `production.py` has no real production config —
both are pre-existing and out of scope per the "deliberately left out" list.

## Accessibility

Target standard: **WCAG 2.2 AA**. This was a manual review of the two UI components
(`TriageForm.jsx`, `ResultsScreen.jsx`) plus a lint-time guardrail — not a certified
audit.

**What was checked:**
- **1.4.3 Contrast** — the urgent-note/error red (`#c0392b`) on white measures
  ~5.44:1, above the 4.5:1 threshold for normal text.
- **2.4.7 Focus Visible** — existing `:focus-visible` outlines in `index.css` cover
  every interactive element touched this pass (textarea, buttons, the new links).
- **2.4.11 Focus Not Obscured** *(new in 2.2)* — no fixed/sticky content exists in
  this layout, so nothing can obscure a focused element. Pass by inspection.
- **2.5.8 Target Size** *(new in 2.2)* — scenario buttons and links (8px/16px padding
  on 18px text) are comfortably over the 24×24px minimum.
- **3.2.6 Consistent Help** *(new in 2.2)* — the adviser link now appears in both
  places a user can end up (the results screen and the form's own error state),
  where previously the error state had no escape hatch at all.
- **4.1.2 Name, Role, Value** — verified via the accessibility tree in a live browser
  check, not just lint: labels, hint text, error alerts, and the new-tab link
  suffixes all expose the accessible names they're meant to.

**What was improved:**
- Added `eslint-plugin-jsx-a11y`'s recommended config to `eslint.config.js` — this
  closes a real gap: the T1 AI-usage log in PLAN.md states ESLint was chosen over
  Oxlint specifically for jsx-a11y coverage, but the plugin was never actually wired
  in. `npm run lint` runs clean with it enabled.
- Added a visually-hidden "(opens in a new tab)" cue to all three `target="_blank"`
  links, so screen-reader users get a warning before being taken off-site.
- Added the privacy hint above the textarea as a real, always-present, accessible
  description (`aria-describedby`), not just placeholder text that disappears on
  input and isn't announced.

**What's left for more time:** automated `axe`/`vitest-axe` checks in the test suite
(currently a manual pass only, so nothing guards against a future regression); a
real screen-reader pass (NVDA/VoiceOver), not just the accessibility-tree read used
here; a skip link, which this single-section-per-screen layout doesn't strictly need
yet but would if the page grows.

## Self code review

Reviewing this pass as if it were a colleague's PR:

**Strengths.** Each change is small, tested, and traceable to a specific gap the
project's own PLAN.md had already named — this isn't speculative hardening. The
existing accessibility groundwork (focus management, aria-live, labelled controls)
made the a11y additions easy to integrate cleanly rather than bolt on. All backend
and frontend tests pass, and the changes were verified live in a browser, not just
by unit test.

**Risks / things I'm not fully confident in:**
- The 1,200-character cap and 20/min rate limit are reasonable-sounding defaults,
  not measured against real usage — there's no usage data to measure against yet.
  Worth revisiting once the tool has real traffic.
- `eslint-plugin-jsx-a11y`'s peer-dependency range doesn't yet cover ESLint 10, so
  installing it required `--force`. It resolved cleanly and `npm run lint` passes,
  but this is a known rough edge that a stricter CI environment (one that rejects
  peer-dep overrides) could trip on. `--legacy-peer-deps` was tried first and
  turned out to be the wrong tool here — it silently dropped
  `@testing-library/dom`, which is only ever installed as an auto-resolved peer of
  `@testing-library/react`, and broke the entire test suite until caught by running
  the tests again after the install. `--force` doesn't have that side effect.
- The throttle test clears Django's cache in `setUp`/`tearDown` because throttle
  state is cache-backed and otherwise leaks across tests. That's correct for the
  current single-process `LocMemCache` setup, but would need revisiting if the
  project ever moves to a shared cache backend or parallel test workers.
- `ADVISER_LINK` is now duplicated as a local constant in both `TriageForm.jsx` and
  `ResultsScreen.jsx` rather than pulled into a shared module. Deliberate, to keep
  this pass's diff small — but it's a real duplication a reviewer should flag, and
  the next person touching either link should keep both in sync.

**Missing tests / gaps I'd flag before merging without comment:**
- No test asserts the throttle count resets after the one-minute window — only that
  it trips at the limit.
- No automated accessibility test exists, so the WCAG checks above are a one-time
  manual pass, not a regression guard.
- The length-cap and rate-limit numbers themselves aren't tested against anything
  beyond "does the boundary return the right status code" — there's no load test or
  real-phrasing corpus behind the choice of numbers.

Nothing here feels unsafe to merge, but the peer-dependency workaround and the
untested numeric choices are the two things I'd want a second pair of eyes on.
