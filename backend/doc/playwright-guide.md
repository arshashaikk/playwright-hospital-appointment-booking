# Playwright – explained with our hospital portal

## 1. What is Playwright?

Playwright is a library from Microsoft that **controls a real browser** (Chromium, Firefox,
WebKit, Edge, Chrome) from code: open pages, click, type, read text, and check results. It can
also make **HTTP requests** to APIs. We use the Python version in *sync* mode
(`from playwright.sync_api import ...`).

In our project Playwright is the bottom layer:

```
feature (what) -> steps (how) -> page object (where) -> Playwright (the hands)
```

## 2. Core objects

| Object | Meaning | Where it lives in our code |
|---|---|---|
| `playwright` | the entry point | `context.pw` (started in `before_all`) |
| `browser` | one running browser | `context.browser` |
| `browser context` | an isolated profile, like a fresh incognito window | created per scenario in `before_scenario` |
| `page` | one tab | `context.page` |
| `locator` | a way to find an element | returned by `page.get_by_test_id(...)` |
| `APIRequestContext` | an HTTP client | `context.api` |

Each scenario gets a new context and page, so cookies and state never leak between tests.

## 3. Locators: finding elements

We added `data-testid` attributes to the React app so tests have stable handles:

```jsx
<button data-testid="confirm-btn">Confirm appointment</button>
```

```python
page.get_by_test_id("confirm-btn")                    # exact test id
page.locator('button[data-testid^="slot-"]')          # all slot buttons (CSS)
page.locator('button[data-testid^="slot-"]:not([disabled])')   # only enabled ones
page.locator('button[data-testid^="doctor-"]').filter(has_text="Dr. Asha Rao")
```

Why test ids? Colours, wording and layout change; `data-testid` does not. Other options
Playwright offers: `get_by_role`, `get_by_label`, `get_by_text`, which are good when you want to
test what a user sees.

## 4. Actions

```python
page.goto("http://localhost:5173")
tid("name-input").fill("Priya Sharma")              # type into an input
tid("department-select").select_option(label="Cardiology")
card.click()                                         # click
tid("confirm-btn").dblclick()                        # used by the double-click test
tid("date-input").fill("2026-11-26")                 # date inputs take ISO format
```

## 5. Auto-waiting: why we have no `sleep()`

Before every action Playwright automatically waits until the element exists, is visible, stable
and enabled. A click on `slot-09:30` waits until that button is really clickable.

## 6. Assertions with `expect`

```python
from playwright.sync_api import expect

expect(tid("conf-doctor")).to_have_text("Dr. Asha Rao")
expect(tid("confirmation")).to_be_visible()
expect(tid("confirmation")).to_have_count(0)          # not present
expect(slot).to_be_disabled()
expect(tid("server-error")).to_contain_text("no longer available")
```

`expect(...)` **retries** for up to 5 seconds (our default is 8 s for actions) until the
condition is true. That removes most flaky tests. A plain Python `assert` does not retry, so use
it only for values that are already final (such as an API response).

## 7. Waiting for the network: `expect_response`

The portal loads slots from the server after you click a doctor. If a test read the slot grid
too early it would see the *previous* data. So our page object waits for the request:

```python
with page.expect_response(lambda r: f"/api/doctors/{doctor_id}/slots" in r.url):
    card.click()
expect(all_slots.first).to_be_visible()
```

Read it as: "click, and don't continue until the slots response has arrived".

The same idea in `confirm()`:

```python
self.tid("confirm-btn").click()
self.page.locator('[data-testid="confirmation"], [data-testid$="-error"]').first.wait_for()
```

It waits for *either* the confirmation or some error. Without this, the check "I should not
see a confirmation" could pass in the instant before the server answered, a false pass.

## 8. API testing with Playwright

The same library calls the backend directly, with no browser:

```python
res = context.api.post("/api/appointments", data=payload)
assert res.status == 409
```

We use it for:

1. **Fast setup** – "another patient has booked a slot" is one API call instead of a UI journey.
2. **Testing the server alone** – needed for the `weak_phone` bug, because the form validates
   the phone before the server ever sees it.
3. **Verification** – `GET /api/test/appointments` proves exactly one booking was created.

## 9. Page Object Model

`tests/pages/booking_page.py` holds every selector and UI action:

```python
class BookingPage:
    def select_doctor(self, name): ...
    def set_date(self, iso): ...
    def pick_available_slot(self, exclude=None): ...
    def fill_details(self, name, phone, email): ...
    def confirm(self): ...
```

Steps call `booking_page.confirm()` and never mention a selector. If the UI changes, you edit
one file.

## 10. Browser options

```powershell
.\.venv\Scripts\python run_tests.py --headed --slowmo 600    # watch it, 600 ms between actions
```

`environment.py` launches bundled Chromium first, then falls back to installed Edge, then
Chrome. On this machine `PLAYWRIGHT_BROWSERS_PATH` points to a protected folder, so Edge is
used. Force a browser with `BROWSER=msedge`.

## 11. Debugging tools

| Tool | How |
|---|---|
| Watch it | `--headed --slowmo 800` |
| Pause and inspect | add `context.page.pause()` inside a step and run headed; the Playwright Inspector opens |
| Failure screenshots | `tests/reports/screenshots/` (saved by the `after_step` hook) |
| Record clicks | `.\.venv\Scripts\python -m playwright codegen http://localhost:5173` |
| Trace viewer | `context.tracing.start(...)` / `stop(path="trace.zip")`, then `playwright show-trace trace.zip` |

## 12. One scenario traced end to end

`And I pick an available slot tomorrow`

1. Behave matches the line to `step_pick_slot_tomorrow` (`ui_steps.py`).
2. It computes tomorrow with `iso_in(1)` and calls `booking_page.set_date(iso)`.
3. `set_date` fills the date input inside `expect_response`, waiting for the new slots.
4. `pick_available_slot()` finds `button[data-testid^="slot-"]:not([disabled])`, clicks the first one and checks `aria-pressed="true"`.
5. The time (e.g. `09:30`) is stored in `context.booking["time"]`.
6. A later `Then` step compares the confirmation page to `fmt12("09:30")` = `9:30 AM`.

## 13. Common mistakes

- Using `time.sleep()` instead of waiting for an element or response.
- Plain `assert` on a page value that is still loading (use `expect`).
- Selectors based on text or CSS classes that change (prefer test ids).
- Sharing one browser context across tests (state leaks, order-dependent failures).
- Asserting "does not appear" without first waiting for the action to finish.
