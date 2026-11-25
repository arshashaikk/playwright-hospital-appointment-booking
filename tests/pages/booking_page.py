"""Page object for the appointment booking portal (single-page React app)."""
from playwright.sync_api import Locator, Page, expect

SLOT_SEL = 'button[data-testid^="slot-"]'
DOCTOR_SEL = 'button[data-testid^="doctor-"]'  # excludes doctor-list / doctor-search (not buttons)


class BookingPage:
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url

    # ---------- locators ----------
    def tid(self, test_id: str) -> Locator:
        return self.page.get_by_test_id(test_id)

    @property
    def doctor_cards(self) -> Locator:
        return self.page.locator(DOCTOR_SEL)

    @property
    def all_slots(self) -> Locator:
        return self.page.locator(SLOT_SEL)

    @property
    def available_slots(self) -> Locator:
        return self.page.locator(f"{SLOT_SEL}:not([disabled])")

    @property
    def unavailable_slots(self) -> Locator:
        return self.page.locator(f"{SLOT_SEL}[disabled]")

    # ---------- actions ----------
    def open(self) -> None:
        self.page.goto(self.base_url)
        expect(self.tid("doctor-list")).to_be_visible()
        expect(self.doctor_cards.first).to_be_visible()

    def select_department(self, label: str) -> None:
        with self.page.expect_response(lambda r: "/api/doctors?" in r.url and "department=" in r.url):
            self.tid("department-select").select_option(label=label)

    def search(self, text: str) -> None:
        with self.page.expect_response(lambda r: "/api/doctors?" in r.url and "q=" in r.url):
            self.tid("doctor-search").fill(text)

    def doctor_names(self) -> list[str]:
        return self.doctor_cards.locator("strong").all_inner_texts()

    def select_doctor(self, name: str) -> int:
        card = self.doctor_cards.filter(has_text=name).first
        expect(card).to_be_visible()
        doctor_id = int(card.get_attribute("data-testid").removeprefix("doctor-"))
        with self.page.expect_response(lambda r: f"/api/doctors/{doctor_id}/slots" in r.url):
            card.click()
        expect(self.all_slots.first).to_be_visible()
        return doctor_id

    def set_date(self, iso: str) -> None:
        date_input = self.tid("date-input")
        if date_input.input_value() == iso:
            return
        with self.page.expect_response(lambda r: "/slots" in r.url and f"date={iso}" in r.url):
            date_input.fill(iso)
        expect(self.all_slots.first).to_be_visible()

    def pick_available_slot(self, exclude: str | None = None) -> str:
        """Click the first enabled slot (optionally skipping one) and return its 24h time."""
        expect(self.available_slots.first).to_be_visible()
        for i in range(self.available_slots.count()):
            btn = self.available_slots.nth(i)
            time = btn.get_attribute("data-testid").removeprefix("slot-")
            if time != exclude:
                btn.click()
                expect(btn).to_have_attribute("aria-pressed", "true")
                return time
        raise AssertionError("No available slot to pick")

    def fill_details(self, name: str, phone: str, email: str) -> None:
        expect(self.tid("name-input")).to_be_visible()
        self.tid("name-input").fill(name)
        self.tid("phone-input").fill(phone)
        self.tid("email-input").fill(email)

    def _wait_for_outcome(self) -> None:
        """Wait until the app shows a confirmation or any error, so 'not confirmed' checks are not racy."""
        self.page.locator('[data-testid="confirmation"], [data-testid$="-error"]').first.wait_for()

    def confirm(self) -> None:
        self.tid("confirm-btn").click()
        self._wait_for_outcome()

    def double_click_confirm(self) -> None:
        self.tid("confirm-btn").dblclick()
        self._wait_for_outcome()

    def book_another(self) -> None:
        self.tid("book-another").click()

    # ---------- reads ----------
    def confirmation_value(self, field: str) -> str:
        return self.tid(f"conf-{field}").inner_text().strip()
