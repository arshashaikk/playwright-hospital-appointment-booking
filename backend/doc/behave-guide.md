# Behave – explained with our hospital portal

## 1. What is Behave?

Behave is the BDD tool for Python. It does three things:

1. Reads `.feature` files (Gherkin).
2. For each step line, finds the Python function that matches it (a **step definition**).
3. Runs them in order and reports pass / fail.

It does not control a browser by itself. In our project the step functions call **Playwright**
to do that.

## 2. Folder map

```
tests/
├── behave.ini                # Behave settings
├── run_tests.py              # our runner (starts servers, runs behave, reports bug detection)
└── features/
    ├── *.feature             # scenarios in plain English
    ├── environment.py        # hooks (setup / teardown)
    └── steps/
        ├── ui_steps.py       # steps that use the browser
        └── api_steps.py      # steps that call the API directly
```

Behave expects exactly this shape: a `features/` folder, an optional `environment.py`, and a
`steps/` subfolder.

## 3. Step definitions

```gherkin
When I choose doctor "Dr. Asha Rao"
```

is matched by:

```python
@when('I choose doctor "{name}"')
def step_choose_doctor(context, name):
    _choose_doctor(context, name)      # name == "Dr. Asha Rao"
```

Rules:

- The text in the decorator is the **pattern**. `{name}` captures a value. `{days:d}` captures an integer.
- `@given`, `@when`, `@then` are labels only; Behave matches on the text. Still, use them correctly for readability.
- The same step can be used by any scenario in any feature file.
- Two steps with the same pattern raise an `AmbiguousStep` error.
- If a step has no function, Behave prints `undefined` along with a ready-to-paste Python skeleton.

### Our steps in practice

| Gherkin | Function | What it does |
|---|---|---|
| `I select the "Cardiology" department` | `step_select_department` | picks the dropdown value, waits for the doctor list to reload |
| `I pick an available slot tomorrow` | `step_pick_slot_tomorrow` | sets tomorrow's date, clicks first enabled slot, remembers the time |
| `I confirm the appointment` | `step_confirm` | clicks Confirm, waits for a confirmation or an error |
| `another patient has booked an available slot with "Dr. Asha Rao" tomorrow` | `step_other_booked` | calls the API to take a slot |
| `the system should hold exactly 1 appointment` | `step_hold_count` | reads `/api/test/appointments` and counts |

### The `(empty)` convention

A step like `I enter patient details "", "9876543210", ...` cannot capture an empty value with
Behave's default parser, so our steps treat the literal text `(empty)` as an empty string.

## 4. `context`: sharing data between steps

`context` is an object that lives for one scenario. Steps use it as a notebook:

```python
# step 1 – "I pick an available slot tomorrow"
context.booking["time"] = "09:30"

# step 2 – "the confirmation should show the selected date and time"
expect(page.tid("conf-time")).to_have_text(fmt12(context.booking["time"]))   # "9:30 AM"
```

Our `before_scenario` hook creates these attributes:

| Attribute | Contents |
|---|---|
| `context.page` | the Playwright page (browser tab) |
| `context.booking_page` | the page object (`BookingPage`) |
| `context.api` | Playwright API client for the backend |
| `context.booking` | dict: doctor, date, time, patient details chosen so far |
| `context.responses` | API responses collected by `@api` steps |

## 5. Hooks (`environment.py`)

Behave calls these functions automatically.

| Hook | Runs | Our use |
|---|---|---|
| `before_all` | once | start Playwright, verify the backend is up, launch the browser |
| `before_scenario` | before every scenario | `POST /api/test/reset`, new browser context + page |
| `after_step` | after every step | on failure, save a full-page screenshot |
| `after_scenario` | after every scenario | close the browser context |
| `after_all` | once | close browser and Playwright |

Why reset before every scenario? **Isolation.** A booking made by one scenario must not make
another scenario's slot unavailable.

## 6. Background, Outline and Tags in Behave

- **Background** runs its steps before each scenario in that feature file.
  (`patient_validation.feature` uses it to choose a doctor and slot first.)
- **Scenario Outline** expands into one scenario per Examples row; the report shows names like
  `... "abc" -- @1.1`.
- **Tags** filter runs:

```powershell
behave --tags=@smoke                 # only smoke
behave --tags=@ui --tags=~@regression   # UI, but not regression
behave --tags=@wrong_doctor          # scenarios that should catch the wrong-doctor bug
```

Our tags: `@smoke`, `@ui`, `@api`, `@regression`, and one per bug (`@double_book`,
`@weak_phone`, `@wrong_doctor`, `@duplicate_submit`).

## 7. `behave.ini`

```ini
[behave]
paths = features              # where feature files live
format = pretty               # readable console output
show_timings = true
junit = true                  # also write JUnit XML...
junit_directory = reports/junit   # ...to this folder
```

## 8. Running

Through our runner (starts its own servers on ports 8100 / 5273):

```powershell
cd tests
.\.venv\Scripts\python run_tests.py                       # everything, clean app
.\.venv\Scripts\python run_tests.py --tags smoke
.\.venv\Scripts\python run_tests.py --bug wrong_doctor    # bug injected: failures = bug detected
.\.venv\Scripts\python run_tests.py --all-bugs
.\.venv\Scripts\python run_tests.py -- features/booking_flow.feature
```

Directly (servers must already be running on 8000 / 5173):

```powershell
.\.venv\Scripts\behave --tags=@smoke -D headed=true -D slowmo=500
```

Options: `-D headed=true`, `-D slowmo=500`, `-D browser=msedge`; or env vars `BASE_URL`, `API_URL`.

## 9. Reading the output

```
Scenario: Patient books an appointment with a cardiologist   # booking_flow.feature:10
  When I choose doctor "Dr. Asha Rao"                         # steps/ui_steps.py:48
  ...
6 scenarios passed, 0 failed, 0 skipped
29 steps passed, 0 failed, 0 skipped, 0 undefined
```

- **failed**: an assertion or error inside a step; later steps in that scenario are *skipped*.
- **undefined**: a step line has no matching function.
- On failure, look in `tests/reports/screenshots/` for the page at that moment.

## 10. Reports

- **Console**: `pretty` format.
- **JUnit XML** (`reports/junit/`): machine-readable results that CI tools read.
- **Allure** (optional, not installed): interactive HTML report; needs `allure-behave` and the Allure command-line tool.

## 11. Common mistakes

- Putting selectors in steps (put them in the page object).
- Steps that depend on another scenario's data (reset and set up your own).
- Ambiguous patterns (`I choose "{x}"` and `I choose doctor "{x}"` can collide).
- Using `sleep` (use Playwright waits instead; see [playwright-guide.md](playwright-guide.md)).
