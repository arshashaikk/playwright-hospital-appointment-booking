"""Shared helpers: dates, time formatting and thin wrappers over the backend API."""
from datetime import date, timedelta


def iso_in(days: int) -> str:
    return (date.today() + timedelta(days=days)).isoformat()


def fmt12(t: str) -> str:
    """'09:30' -> '9:30 AM' (the format the UI displays)."""
    h, m = (int(x) for x in t.split(":"))
    return f"{h % 12 or 12}:{m:02d} {'PM' if h >= 12 else 'AM'}"


def find_doctor(api, name: str) -> dict:
    doctors = api.get("/api/doctors").json()
    match = next((d for d in doctors if d["name"] == name), None)
    assert match, f"Doctor {name!r} not found in API"
    return match


def slots_for(api, doctor_id: int, iso: str) -> list[dict]:
    return api.get(f"/api/doctors/{doctor_id}/slots", params={"date": iso}).json()


def first_available_slot(api, doctor_id: int, iso: str, exclude: str | None = None) -> str:
    for s in slots_for(api, doctor_id, iso):
        if s["available"] and s["time"] != exclude:
            return s["time"]
    raise AssertionError(f"No available slot for doctor {doctor_id} on {iso}")


def first_unavailable_slot(api, doctor_id: int, iso: str) -> str:
    for s in slots_for(api, doctor_id, iso):
        if not s["available"]:
            return s["time"]
    raise AssertionError(f"No unavailable slot for doctor {doctor_id} on {iso}")


def booking_payload(doctor_id: int, iso: str, time: str, **overrides) -> dict:
    payload = {
        "doctor_id": doctor_id,
        "date": iso,
        "time": time,
        "name": "API Patient",
        "phone": "9876543210",
        "email": "api.patient@example.com",
    }
    payload.update(overrides)
    return payload


def post_booking(api, payload: dict):
    return api.post("/api/appointments", data=payload)


def all_appointments(api) -> list[dict]:
    return api.get("/api/test/appointments").json()
