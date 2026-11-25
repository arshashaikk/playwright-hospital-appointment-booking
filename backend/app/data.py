"""Seed data and in-memory store for the hospital portal."""
from datetime import date

DEPARTMENTS = [
    {"id": "cardiology", "name": "Cardiology"},
    {"id": "neurology", "name": "Neurology"},
    {"id": "orthopedics", "name": "Orthopedics"},
    {"id": "pediatrics", "name": "Pediatrics"},
    {"id": "dermatology", "name": "Dermatology"},
]

DOCTORS = [
    {"id": 1, "name": "Dr. Asha Rao", "department": "cardiology", "specialty": "Cardiologist", "experience": 14},
    {"id": 2, "name": "Dr. Vikram Shah", "department": "cardiology", "specialty": "Interventional Cardiologist", "experience": 9},
    {"id": 3, "name": "Dr. Meera Iyer", "department": "neurology", "specialty": "Neurologist", "experience": 11},
    {"id": 4, "name": "Dr. Rohan Das", "department": "orthopedics", "specialty": "Orthopedic Surgeon", "experience": 16},
    {"id": 5, "name": "Dr. Sana Khan", "department": "pediatrics", "specialty": "Pediatrician", "experience": 7},
    {"id": 6, "name": "Dr. Liam Ortiz", "department": "dermatology", "specialty": "Dermatologist", "experience": 5},
]

# 09:00 - 16:30 in 30 minute steps, lunch hour (13:xx) excluded
ALL_SLOTS = [
    f"{h:02d}:{m:02d}"
    for h in range(9, 17)
    for m in (0, 30)
    if h != 13
]

# (doctor_id, iso_date, time) -> appointment id
BOOKED: dict[tuple[int, str, str], str] = {}
APPOINTMENTS: dict[str, dict] = {}


def get_doctor(doctor_id: int):
    return next((d for d in DOCTORS if d["id"] == doctor_id), None)


def prebooked(doctor_id: int, iso_date: str, time: str) -> bool:
    """Deterministic 'already taken' slots so tests are repeatable."""
    d = date.fromisoformat(iso_date)
    return (doctor_id + d.day + int(time[:2]) + int(time[3:]) // 30) % 4 == 0


def is_available(doctor_id: int, iso_date: str, time: str) -> bool:
    return (
        time in ALL_SLOTS
        and not prebooked(doctor_id, iso_date, time)
        and (doctor_id, iso_date, time) not in BOOKED
    )


def reset():
    BOOKED.clear()
    APPOINTMENTS.clear()
