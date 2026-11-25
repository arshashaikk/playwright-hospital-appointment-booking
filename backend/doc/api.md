# API Reference

Base URL: `http://127.0.0.1:8000` (or `http://localhost:5173` through the Vite proxy).
Interactive docs: `http://127.0.0.1:8000/docs`.

## GET /api/health
Returns service status and the active bug flags.
```json
{ "status": "ok", "bugs": [] }
```

## GET /api/departments
```json
[{ "id": "cardiology", "name": "Cardiology" }, ...]
```
Departments: cardiology, neurology, orthopedics, pediatrics, dermatology.

## GET /api/doctors
Query params (both optional): `department` (id), `q` (case-insensitive match on name or specialty).
```json
[{ "id": 1, "name": "Dr. Asha Rao", "department": "cardiology",
   "specialty": "Cardiologist", "experience": 14 }]
```

## GET /api/doctors/{doctor_id}/slots?date=YYYY-MM-DD
| Status | Meaning |
|--------|---------|
| 200 | list of slots; empty list if the date is in the past or more than 30 days ahead |
| 404 | unknown doctor |
| 422 | malformed date |

```json
[{ "time": "09:00", "available": true }, { "time": "09:30", "available": false }]
```

## POST /api/appointments
Request:
```json
{ "doctor_id": 1, "date": "2026-11-26", "time": "09:30",
  "name": "Test User", "phone": "9876543210", "email": "t@example.com" }
```
Response `201`:
```json
{ "id": "1882CE48", "doctor_id": 1, "doctor_name": "Dr. Asha Rao",
  "specialty": "Cardiologist", "department": "cardiology",
  "date": "2026-11-26", "time": "09:30",
  "name": "Test User", "phone": "9876543210", "email": "t@example.com" }
```

| Status | Cause |
|--------|-------|
| 404 | doctor not found |
| 409 | slot unavailable, **or** same email already booked this doctor on that date |
| 422 | invalid name / phone / email / date / time, or date in the past |

Validation errors from Pydantic come back as `{"detail": [{"msg": "Value error, ...", ...}]}`;
conflict/not-found errors as `{"detail": "message"}`.

## GET /api/appointments/{id}
Returns the stored appointment, or `404`.

## GET /api/test/appointments
Test helper: returns every stored appointment (used to assert that no duplicates were created).

## POST /api/test/reset
Clears all bookings. Intended for test setup only.
```json
{ "status": "reset" }
```
