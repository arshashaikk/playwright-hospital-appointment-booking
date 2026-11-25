# BDD (Behaviour-Driven Development) – explained with our hospital portal

## 1. What is BDD?

BDD is a way of describing how software should behave **in plain English**, before and while
you test or build it. The description is written so that a tester, developer, doctor or product
owner can all read it and agree on it.

Traditional test:

```python
page.click("#btn-17"); assert page.text("#c3") == "Dr. Asha Rao"
```

BDD test:

```gherkin
Then the confirmation should show doctor "Dr. Asha Rao"
```

The BDD line states the **business expectation**. The code that does it lives somewhere else.

## 2. Why use it?

| Benefit | In our project |
|---|---|
| Shared understanding | The hospital's four problems become four readable test files |
| Living documentation | `tests/features/*.feature` always describes what the portal must do |
| Reuse | `I confirm the appointment` is written once and used in dozens of scenarios |
| Clear failures | "Then the confirmation should show doctor 'Dr. Asha Rao'" tells you what broke |

## 3. Gherkin: the language of BDD

Gherkin is the small set of keywords used in `.feature` files.

| Keyword | Meaning | Our example |
|---|---|---|
| `Feature` | A capability being described | `Feature: Book a hospital appointment` |
| `Scenario` | One concrete example / one test | `Scenario: Patient books an appointment with a cardiologist` |
| `Given` | The starting situation | `Given the appointment portal is open` |
| `When` | The action the user takes | `When I choose doctor "Dr. Asha Rao"` |
| `Then` | The expected result | `Then I should see the booking confirmation` |
| `And` / `But` | Continue the previous keyword | `And I pick an available slot tomorrow` |
| `Background` | Steps repeated before every scenario in the file | opens the portal |
| `Scenario Outline` + `Examples` | One scenario run for many data rows | six doctors, one scenario |
| `@tag` | Label to select or group scenarios | `@smoke`, `@wrong_doctor` |

### Given / When / Then

Think of it as **setup, action, check**:

```gherkin
Scenario: Slot taken while the patient is filling in the form is rejected
  When I choose doctor "Dr. Asha Rao"                                   # setup
  And I pick an available slot tomorrow                                  # setup
  And I enter patient details "Late Booker", "9876543210", "late@example.com"
  And another patient books the same slot through the API                # the twist
  And I confirm the appointment                                          # action
  Then I should see the server error containing "no longer available"    # check
  And I should not see a booking confirmation                            # check
```

### Scenario Outline (data-driven)

```gherkin
Scenario Outline: Invalid phone number "<phone>" is rejected in the form
  When I enter patient details "Priya Sharma", "<phone>", "priya@example.com"
  And I confirm the appointment
  Then I should see a phone validation error

  Examples:
    | phone           |
    | abc             |
    | 12345           |
    | 123456789012345 |
```

`<phone>` is replaced by each row, so this one scenario produces three tests.

## 4. How the hospital's four problems map to BDD

| Reported problem | Feature file | The behaviour in plain English |
|---|---|---|
| Unavailable slots can be booked | `slot_availability.feature` | "Two different patients cannot book the same slot" |
| Invalid phone numbers accepted | `patient_validation.feature`, `phone_validation_api.feature` | "API rejects invalid phone 'abc'" |
| Wrong doctor on confirmation | `confirmation_details.feature` | "Confirmation shows the selected doctor 'Dr. Meera Iyer'" |
| Same appointment submitted twice | `duplicate_booking.feature` | "Same patient cannot book the same doctor twice on the same day" |

## 5. Writing good scenarios

- **Describe behaviour, not clicks.** Prefer `When I choose doctor "Dr. Asha Rao"` over
  `When I click the button with id doctor-1`.
- **One scenario, one behaviour.** If the title needs "and", split it.
- **Use real data.** `"Priya Sharma", "9876543210"` is easier to read than `"test", "123"`.
- **Keep it independent.** Every scenario must work alone (we reset the data before each one).
- **Declarative over imperative.** `I enter patient details "A", "B", "C"` beats three lines for
  three fields.

## 6. Where BDD sits in the project

```
feature file (what)  ->  steps (how)  ->  page object (where)  ->  Playwright (tool)
```

See [behave-guide.md](behave-guide.md) for the step/hook layer and
[playwright-guide.md](playwright-guide.md) for the browser layer.

## 7. Glossary

- **Feature file**: a `.feature` text file containing scenarios.
- **Step**: one Given/When/Then line.
- **Step definition**: the Python function a step runs.
- **Tag**: an `@label` used to filter runs.
- **Acceptance criteria**: the conditions that make a feature "done"; scenarios are these, made executable.
