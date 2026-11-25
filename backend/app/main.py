"""Hospital appointment booking API.

Set BUGS=double_book,weak_phone,wrong_doctor,duplicate_submit to re-introduce the
four defects described in the brief, so Playwright tests have something to catch.
"""
import os
import re
import uuid
from datetime import date, timedelta

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, field_validator

from . import data

BUGS = {b.strip() for b in os.getenv("BUGS", "").split(",") if b.strip()}
PHONE_RE = re.compile(r"^\+?\d{10,13}$")
MAX_DAYS_AHEAD = 30

app = FastAPI(title="Hospital Appointment Portal")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class BookingRequest(BaseModel):
    doctor_id: int
    date: str
    time: str
    name: str
    phone: str
    email: EmailStr

    @field_validator("name")
    @classmethod
    def _name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters")
        return v

    @field_validator("phone")
    @classmethod
    def _phone(cls, v: str) -> str:
        cleaned = re.sub(r"[\s\-()]", "", v)
        if "weak_phone" in BUGS:
            if not cleaned:
                raise ValueError("Phone is required")
            return cleaned
        if not PHONE_RE.match(cleaned):
            raise ValueError("Enter a valid phone number (10-13 digits, optional +)")
        return cleaned


@app.get("/api/health")
def health():
    return {"status": "ok", "bugs": sorted(BUGS)}


@app.get("/api/departments")
def departments():
    return data.DEPARTMENTS


@app.get("/api/doctors")
def doctors(department: str | None = None, q: str | None = None):
    result = data.DOCTORS
    if department:
        result = [d for d in result if d["department"] == department]
    if q:
        ql = q.lower()
        result = [d for d in result if ql in d["name"].lower() or ql in d["specialty"].lower()]
    return result


@app.get("/api/doctors/{doctor_id}/slots")
def slots(doctor_id: int, date_: str = Query(alias="date")):
    if not data.get_doctor(doctor_id):
        raise HTTPException(404, "Doctor not found")
    try:
        d = date.fromisoformat(date_)
    except ValueError:
        raise HTTPException(422, "Invalid date")
    today = date.today()
    if d < today or d > today + timedelta(days=MAX_DAYS_AHEAD):
        return []
    return [{"time": t, "available": data.is_available(doctor_id, date_, t)} for t in data.ALL_SLOTS]


@app.post("/api/appointments", status_code=201)
def book(req: BookingRequest):
    doctor = data.get_doctor(req.doctor_id)
    if not doctor:
        raise HTTPException(404, "Doctor not found")
    try:
        d = date.fromisoformat(req.date)
    except ValueError:
        raise HTTPException(422, "Invalid date")
    if d < date.today():
        raise HTTPException(422, "Cannot book a date in the past")
    if req.time not in data.ALL_SLOTS:
        raise HTTPException(422, "Invalid time slot")

    key = (req.doctor_id, req.date, req.time)

    # Bug 4: with duplicate_submit the same patient can book the same appointment twice
    if "duplicate_submit" not in BUGS:
        for a in data.APPOINTMENTS.values():
            if (a["email"].lower() == req.email.lower() and a["doctor_id"] == req.doctor_id
                    and a["date"] == req.date):
                raise HTTPException(409, "You already have an appointment with this doctor on that date")

    # Bug 1: with double_book unavailable slots are accepted
    if "double_book" not in BUGS and not data.is_available(*key):
        raise HTTPException(409, "This time slot is no longer available")

    appt_id = uuid.uuid4().hex[:8].upper()
    shown_doctor = doctor
    if "wrong_doctor" in BUGS:  # Bug 3: confirmation shows a different doctor
        shown_doctor = data.DOCTORS[doctor["id"] % len(data.DOCTORS)]

    appt = {
        "id": appt_id,
        "doctor_id": req.doctor_id,
        "doctor_name": shown_doctor["name"],
        "specialty": shown_doctor["specialty"],
        "department": shown_doctor["department"],
        "date": req.date,
        "time": req.time,
        "name": req.name,
        "phone": req.phone,
        "email": str(req.email),
    }
    data.APPOINTMENTS[appt_id] = appt
    data.BOOKED[key] = appt_id
    return appt


@app.get("/api/appointments/{appt_id}")
def get_appointment(appt_id: str):
    appt = data.APPOINTMENTS.get(appt_id)
    if not appt:
        raise HTTPException(404, "Appointment not found")
    return appt


@app.get("/api/test/appointments")
def list_appointments():
    """Test helper: every stored appointment (lets tests assert no duplicates were created)."""
    return list(data.APPOINTMENTS.values())


@app.post("/api/test/reset")
def reset():
    """Test helper: wipe bookings so each Playwright test starts clean."""
    data.reset()
    return {"status": "reset"}
