# Playwright + Behave (BDD) test suite

Python 3, [Behave](https://behave.readthedocs.io) for Gherkin features, Playwright for browser and API automation.

## Layout

```
tests/
├── run_tests.py              # starts servers, runs behave, reports bug detection
├── behave.ini                # behave config (junit XML -> reports/junit)
├── requirements.txt
├── features/
│   ├── environment.py        # hooks: browser/API setup, per-scenario reset, failure screenshots
│   ├── booking_flow.feature          # happy path, department filter, search
│   ├── slot_availability.feature     # bug 1: unavailable slots
│   ├── patient_validation.feature    # phone / email / name in the UI
│   ├── phone_validation_api.feature  # bug 2: server-side phone validation
│   ├── confirmation_details.feature  # bug 3: correct doctor on confirmation
│   ├── duplicate_booking.feature     # bug 4: duplicate submission
│   └── steps/ui_steps.py, api_steps.py
├── pages/booking_page.py     # Page Object (all selectors live here)
└── support/helpers.py        # dates, 12h formatting, API helpers
```

## Setup (once)

```powershell
cd tests
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\python -m playwright install chromium    # optional, see "Browsers"
```

## Run

```powershell
cd tests
.\.venv\Scripts\python run_tests.py                       # clean app, all scenarios (expect all PASS)
.\.venv\Scripts\python run_tests.py --tags smoke          # only @smoke
.\.venv\Scripts\python run_tests.py --headed --slowmo 400 # watch the browser
.\.venv\Scripts\python run_tests.py --bug wrong_doctor    # inject a bug (expect FAIL = detected)
.\.venv\Scripts\python run_tests.py --all-bugs            # all four bugs + summary
.\.venv\Scripts\python run_tests.py -- features/booking_flow.feature
```

The runner starts its own backend (port 8100) and frontend (port 5273), so it never collides with
your dev servers on 8000 / 5173. Add `--use-running` to test your dev servers instead.

You can also run behave directly against running servers: `.\.venv\Scripts\behave --tags=@smoke`
(env vars `BASE_URL`, `API_URL`, `BROWSER`, `HEADED`; or `-D headed=true`).

## Bug-detection mapping

| Bug flag           | Scenarios that must fail (tag)                                            |
|--------------------|---------------------------------------------------------------------------|
| `double_book`      | stale-form booking, API unavailable slot, two patients same slot          |
| `weak_phone`       | API rejects invalid phone (outline of 5)                                  |
| `wrong_doctor`     | confirmation shows selected doctor (6 doctors), stored appointment match  |
| `duplicate_submit` | same patient cannot book same doctor twice in a day                       |

Other tags: `@smoke`, `@ui`, `@api`, `@regression` (guards that pass even with a bug injected,
e.g. the UI's double-click protection).

## Reports

- Console: behave `pretty` output.
- `reports/junit/*.xml`: JUnit XML (CI friendly).
- `reports/screenshots/`: full-page screenshot for every failed step.

## Browsers

The suite launches bundled Chromium and falls back to installed Microsoft Edge, then Chrome. If
`PLAYWRIGHT_BROWSERS_PATH` points somewhere you cannot write (as on some managed machines), no
download is needed: Edge is used automatically. Force one with `BROWSER=msedge`.
