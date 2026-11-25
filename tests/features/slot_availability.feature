Feature: Time slot availability
  Patients must never be able to book a time slot that is not available.

  Background:
    Given the appointment portal is open

  @ui
  Scenario: Unavailable slots are disabled in the slot grid
    When I choose doctor "Dr. Asha Rao"
    And I select the date tomorrow
    Then some slots should be unavailable and disabled
    And some slots should be available

  @ui
  Scenario: A slot that was just booked shows as unavailable to the next patient
    Given another patient has booked an available slot with "Dr. Asha Rao" tomorrow
    When I choose doctor "Dr. Asha Rao"
    And I select the date tomorrow
    Then the slot booked by the other patient should be disabled

  @ui @double_book
  Scenario: Slot taken while the patient is filling in the form is rejected
    When I choose doctor "Dr. Asha Rao"
    And I pick an available slot tomorrow
    And I enter patient details "Late Booker", "9876543210", "late@example.com"
    And another patient books the same slot through the API
    And I confirm the appointment
    Then I should see the server error containing "no longer available"
    And I should not see a booking confirmation

  @api @double_book
  Scenario: API rejects a booking for an unavailable slot
    When I submit a booking request for an unavailable slot of "Dr. Asha Rao" tomorrow
    Then the response status should be 409

  @api @double_book
  Scenario: Two different patients cannot book the same slot
    When two different patients book the same slot of "Dr. Vikram Shah" tomorrow
    Then the first request should succeed with status 201
    And the second request should be rejected with status 409
