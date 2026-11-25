"""UI step definitions (Playwright, through the BookingPage object)."""
from behave import given, then, when
from playwright.sync_api import expect

from support.helpers import fmt12, iso_in


def _val(text: str) -> str:
    """Examples tables cannot hold empty cells in step text, so '(empty)' means ''."""
    return "" if text == "(empty)" else text


def _choose_doctor(context, name):
    context.booking["doctor_name"] = name
    context.booking["doctor_id"] = context.booking_page.select_doctor(name)


def _pick_slot_on(context, days, exclude=None):
    iso = iso_in(days)
    context.booking_page.set_date(iso)
    context.booking["date"] = iso
    context.booking["time"] = context.booking_page.pick_available_slot(exclude=exclude)


# ---------------------------------------------------------------- Given
@given("the appointment portal is open")
def step_open(context):
    context.booking_page.open()


@given('I have chosen doctor "{name}" and an available slot tomorrow')
def step_chosen_doctor_and_slot(context, name):
    _choose_doctor(context, name)
    _pick_slot_on(context, 1)


# ---------------------------------------------------------------- When
@when('I select the "{department}" department')
def step_select_department(context, department):
    context.booking_page.select_department(department)


@when('I search for "{text}"')
def step_search(context, text):
    context.booking_page.search(text)


@when('I choose doctor "{name}"')
def step_choose_doctor(context, name):
    _choose_doctor(context, name)


@when("I select the date tomorrow")
def step_select_date_tomorrow(context):
    context.booking["date"] = iso_in(1)
    context.booking_page.set_date(context.booking["date"])


@when("I pick an available slot tomorrow")
def step_pick_slot_tomorrow(context):
    _pick_slot_on(context, 1)


@when("I pick an available slot {days:d} days from today")
def step_pick_slot_days(context, days):
    _pick_slot_on(context, days)


@when("I pick a different available slot tomorrow")
def step_pick_different_slot(context):
    _pick_slot_on(context, 1, exclude=context.booking.get("time"))


@when('I enter patient details "{name}", "{phone}", "{email}"')
def step_enter_details(context, name, phone, email):
    context.booking.update(name=_val(name), phone=_val(phone), email=_val(email))
    context.booking_page.fill_details(_val(name), _val(phone), _val(email))


@when("I confirm the appointment")
def step_confirm(context):
    context.booking_page.confirm()


@when("I double-click the confirm button")
def step_double_click(context):
    context.booking_page.double_click_confirm()


# ---------------------------------------------------------------- Then: confirmation
@then("I should see the booking confirmation")
def step_see_confirmation(context):
    expect(context.booking_page.tid("confirmation")).to_be_visible()


@then("I should not see a booking confirmation")
def step_no_confirmation(context):
    expect(context.booking_page.tid("confirmation")).to_have_count(0)


@then('the confirmation should show doctor "{name}"')
def step_conf_doctor(context, name):
    expect(context.booking_page.tid("conf-doctor")).to_have_text(name)


@then('the confirmation department should be "{department}"')
def step_conf_department(context, department):
    expect(context.booking_page.tid("conf-department")).to_have_text(department)


@then("the confirmation should show the selected date and time")
def step_conf_date_time(context):
    page = context.booking_page
    expect(page.tid("conf-date")).to_have_text(context.booking["date"])
    expect(page.tid("conf-time")).to_have_text(fmt12(context.booking["time"]))


@then('the confirmation should show patient "{name}" with phone "{phone}" and email "{email}"')
def step_conf_patient(context, name, phone, email):
    page = context.booking_page
    expect(page.tid("conf-name")).to_have_text(name)
    expect(page.tid("conf-phone")).to_have_text(phone)
    expect(page.tid("conf-email")).to_have_text(email)


@then("the stored appointment for the shown reference should match the selected doctor")
def step_stored_matches(context):
    ref = context.booking_page.confirmation_value("id")
    stored = context.api.get(f"/api/appointments/{ref}").json()
    assert stored["doctor_name"] == context.booking["doctor_name"], (
        f"Stored doctor {stored['doctor_name']!r} != selected {context.booking['doctor_name']!r}"
    )
    assert stored["doctor_id"] == context.booking["doctor_id"]


# ---------------------------------------------------------------- Then: validation messages
@then("I should see a phone validation error")
def step_phone_error(context):
    expect(context.booking_page.tid("phone-error")).to_be_visible()


@then("I should see an email validation error")
def step_email_error(context):
    expect(context.booking_page.tid("email-error")).to_be_visible()


@then("I should see a name validation error")
def step_name_error(context):
    expect(context.booking_page.tid("name-error")).to_be_visible()


@then('I should see the server error containing "{text}"')
def step_server_error(context, text):
    expect(context.booking_page.tid("server-error")).to_contain_text(text)


# ---------------------------------------------------------------- Then: doctor list / summary
@then('the doctor list should contain "{name}"')
def step_list_contains(context, name):
    expect(context.booking_page.doctor_cards.filter(has_text=name)).to_have_count(1)


@then('the doctor list should not contain "{name}"')
def step_list_not_contains(context, name):
    expect(context.booking_page.doctor_cards.filter(has_text=name)).to_have_count(0)


@then("the doctor list should be empty")
def step_list_empty(context):
    expect(context.booking_page.tid("no-doctors")).to_be_visible()
    expect(context.booking_page.doctor_cards).to_have_count(0)


@then('the booking summary should mention "{text}"')
def step_summary(context, text):
    expect(context.booking_page.tid("summary")).to_contain_text(text)
    expect(context.booking_page.tid("summary")).to_contain_text(fmt12(context.booking["time"]))


# ---------------------------------------------------------------- Then: slots
@then("some slots should be unavailable and disabled")
def step_unavailable_disabled(context):
    page = context.booking_page
    assert page.unavailable_slots.count() > 0, "Expected at least one unavailable slot"
    for i in range(page.unavailable_slots.count()):
        expect(page.unavailable_slots.nth(i)).to_be_disabled()


@then("some slots should be available")
def step_some_available(context):
    assert context.booking_page.available_slots.count() > 0


@then("the slot booked by the other patient should be disabled")
def step_other_slot_disabled(context):
    slot = context.booking_page.tid(f"slot-{context.booking['time']}")
    expect(slot).to_be_disabled()
