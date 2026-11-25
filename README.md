# CityCare Hospital – Appointment Booking Portal

FastAPI backend + React (Vite) frontend, built as a practice target for Playwright tests.

## Run

```powershell
# Terminal 1 – backend (http://127.0.0.1:8000, docs at /docs)
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000

# Terminal 2 – frontend (http://localhost:5173)
cd frontend
npm run dev
```

First-time setup: `python -m venv .venv; .\.venv\Scripts\pip install -r requirements.txt` in `backend/`, `npm install` in `frontend/`.

## Automated tests (Playwright + Behave BDD)

```powershell
cd tests
.\.venv\Scripts\python run_tests.py             # clean app: all scenarios pass
.\.venv\Scripts\python run_tests.py --all-bugs  # injects each bug, verifies the suite catches it
```

See [tests/README.md](tests/README.md) for layout, tags, reports and options.

## Injecting the four bugs

Start the backend with `BUGS` set to a comma-separated list:

| Flag               | Defect it re-introduces                                    |
|--------------------|------------------------------------------------------------|
| `double_book`      | Unavailable / already-taken slots are accepted by the API   |
| `weak_phone`       | Server accepts invalid phone numbers (UI validation still blocks, so test the API or bypass the UI) |
| `wrong_doctor`     | Confirmation page shows a different doctor than selected    |
| `duplicate_submit` | Same patient can book the same doctor/date repeatedly       |

```powershell
$env:BUGS="wrong_doctor,double_book"; .\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000
```

`GET /api/health` lists active bugs. `POST /api/test/reset` clears bookings (use in test `beforeEach`).

## Test hooks

Elements carry `data-testid`s: `department-select`, `doctor-search`, `doctor-{id}`, `date-input`,
`slot-{HH:MM}` (disabled when unavailable), `name-input`, `phone-input`, `email-input`, `*-error`,
`server-error`, `confirm-btn`, and `conf-*` on the confirmation page.
Slots are deterministic: some are pre-booked per doctor/date, lunch (13:xx) is excluded.
