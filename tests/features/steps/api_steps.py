"""API-level step definitions (Playwright APIRequestContext)."""
from behave import given, then, when

from support.helpers import (
    all_appointments,
    booking_payload,
    find_doctor,
    first_available_slot,
    first_unavailable_slot,
    iso_in,
    post_booking,
)


def _record(context, doctor_name, time, iso, doctor_id):
    context.booking.update(doctor_name=doctor_name, doctor_id=doctor_id, date=iso, time=time)


# ---------------------------------------------------------------- Given
@given('another patient has booked an available slot with "{doctor}" tomorrow')
def step_other_booked(context, doctor):
    d, iso = find_doctor(context.api, doctor), iso_in(1)
    time = first_available_slot(context.api, d["id"], iso)
    res = post_booking(context.api, booking_payload(d["id"], iso, time, email="other.patient@example.com"))
    assert res.status == 201, res.text()
    _record(context, doctor, time, iso, d["id"])


@given('a patient "{email}" already has an appointment with "{doctor}" tomorrow')
def step_patient_has_appointment(context, email, doctor):
    d, iso = find_doctor(context.api, doctor), iso_in(1)
    time = first_available_slot(context.api, d["id"], iso)
    res = post_booking(context.api, booking_payload(d["id"], iso, time, email=email))
    assert res.status == 201, res.text()
    _record(context, doctor, time, iso, d["id"])


# ---------------------------------------------------------------- When
@when('another patient books the same slot through the API')
def step_other_books_same_slot(context):
    b = context.booking
    res = post_booking(
        context.api,
        booking_payload(b["doctor_id"], b["date"], b["time"], email="other.patient@example.com"),
    )
    assert res.status == 201, f"Setup failed, other patient's booking returned {res.status}"


@when('I submit a booking request for an unavailable slot of "{doctor}" tomorrow')
def step_submit_unavailable(context, doctor):
    d, iso = find_doctor(context.api, doctor), iso_in(1)
    time = first_unavailable_slot(context.api, d["id"], iso)
    context.responses.append(post_booking(context.api, booking_payload(d["id"], iso, time)))


@when('two different patients book the same slot of "{doctor}" tomorrow')
def step_two_patients(context, doctor):
    d, iso = find_doctor(context.api, doctor), iso_in(1)
    time = first_available_slot(context.api, d["id"], iso)
    for email in ("patient.one@example.com", "patient.two@example.com"):
        context.responses.append(post_booking(context.api, booking_payload(d["id"], iso, time, email=email)))


@when('I submit a booking request for "{doctor}" tomorrow with phone "{phone}"')
def step_submit_with_phone(context, doctor, phone):
    d, iso = find_doctor(context.api, doctor), iso_in(1)
    time = first_available_slot(context.api, d["id"], iso)
    context.responses.append(post_booking(context.api, booking_payload(d["id"], iso, time, phone=phone)))


@when('the same booking request for "{doctor}" tomorrow is submitted twice')
def step_same_twice(context, doctor):
    d, iso = find_doctor(context.api, doctor), iso_in(1)
    payload = booking_payload(d["id"], iso, first_available_slot(context.api, d["id"], iso))
    context.responses.append(post_booking(context.api, payload))
    context.responses.append(post_booking(context.api, payload))


# ---------------------------------------------------------------- Then
@then("the response status should be {status:d}")
def step_status(context, status):
    actual = context.responses[-1].status
    assert actual == status, f"Expected {status}, got {actual}: {context.responses[-1].text()}"


@then("the first request should succeed with status {status:d}")
def step_first_ok(context, status):
    actual = context.responses[0].status
    assert actual == status, f"Expected {status}, got {actual}: {context.responses[0].text()}"


@then("the second request should be rejected with status {status:d}")
def step_second_rejected(context, status):
    actual = context.responses[1].status
    assert actual == status, (
        f"Second request was NOT rejected: expected {status}, got {actual}: {context.responses[1].text()}"
    )


@then("no appointment should be stored")
def step_none_stored(context):
    assert all_appointments(context.api) == []


@then("the system should hold exactly {n:d} appointment")
def step_hold_count(context, n):
    actual = len(all_appointments(context.api))
    assert actual == n, f"Expected {n} stored appointment(s), found {actual}"
