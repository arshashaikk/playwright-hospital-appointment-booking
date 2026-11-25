# Testing Guide (for the Playwright phase)

## Starting the app in a known state
```powershell
# clean app
.\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000

# with defects injected
$env:BUGS="double_book,wrong_doctor"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000
```
`GET /api/health` shows which flags are active. Call `POST /api/test/reset` in `beforeEach`.

## Bug flags
| Flag | Effect | Best detected by |
|------|--------|------------------|
| `double_book` | API accepts taken/unavailable slots | API test: POST a slot that is `available: false`; UI test: two bookings of one slot |
| `weak_phone` | API accepts any non-empty phone | API test with `abc`; UI blocks it, so bypass the UI via `request.post` |
| `wrong_doctor` | confirmation shows the next doctor in the list | UI test: compare selected doctor with `conf-doctor` |
| `duplicate_submit` | same email can book the same doctor/date repeatedly | UI: book, go back, book again; or double-click confirm |

## Selectors (`data-testid`)
| Area | IDs |
|------|-----|
| Search | `department-select`, `doctor-search`, `doctor-list`, `doctor-{id}`, `no-doctors` |
| Schedule | `date-input`, `slot-grid`, `slot-{HH:MM}` (disabled when taken), `no-slots` |
| Form | `summary`, `name-input`, `phone-input`, `email-input`, `name-error`, `phone-error`, `email-error`, `server-error`, `confirm-btn` |
| Confirmation | `confirmation`, `conf-id`, `conf-doctor`, `conf-department`, `conf-date`, `conf-time`, `conf-name`, `conf-phone`, `conf-email`, `book-another` |

Note on time display: the UI shows times in 12-hour format ("9:30 AM", including slot button text,
the summary and `conf-time`), but `data-testid`s and API values stay 24-hour (`slot-09:30`, `"09:30"`).
Select slots by test id, and assert `conf-time` as e.g. `9:30 AM`.

## Doctor ids
1 Dr. Asha Rao (cardiology) · 2 Dr. Vikram Shah (cardiology) · 3 Dr. Meera Iyer (neurology) ·
4 Dr. Rohan Das (orthopedics) · 5 Dr. Sana Khan (pediatrics) · 6 Dr. Liam Ortiz (dermatology)

## Suggested scenarios
- Happy path: department → doctor → date/slot → details → confirm → verify every `conf-*` field.
- Unavailable slots are disabled in the grid; the API rejects them with 409.
- Phone validation: letters, too short, too long, empty; valid with spaces/dashes/`+`.
- Email and name validation messages.
- Confirmation doctor/date/time equal the selection (run for each doctor).
- Duplicate: double-click confirm yields a single booking; rebooking same doctor/date gives 409 banner.
- Race: two contexts book the same slot; exactly one succeeds.
- Search filters, empty-search result (`no-doctors`), date outside the 30-day window (`no-slots`).
