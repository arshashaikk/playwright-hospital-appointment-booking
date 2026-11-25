Feature: Duplicate booking prevention
  A patient must not be able to submit the same appointment twice.

  @ui @regression
  Scenario: Double-clicking Confirm creates a single appointment
    Given the appointment portal is open
    And I have chosen doctor "Dr. Asha Rao" and an available slot tomorrow
    When I enter patient details "Priya Sharma", "9876543210", "priya@example.com"
    And I double-click the confirm button
    Then I should see the booking confirmation
    And the system should hold exactly 1 appointment

  @ui @duplicate_submit
  Scenario: Same patient cannot book the same doctor twice on the same day
    Given a patient "priya@example.com" already has an appointment with "Dr. Asha Rao" tomorrow
    And the appointment portal is open
    When I choose doctor "Dr. Asha Rao"
    And I pick a different available slot tomorrow
    And I enter patient details "Priya Sharma", "9876543210", "priya@example.com"
    And I confirm the appointment
    Then I should see the server error containing "already have an appointment"
    And I should not see a booking confirmation
    And the system should hold exactly 1 appointment

  @api @regression
  Scenario: Submitting the identical booking request twice is rejected
    When the same booking request for "Dr. Asha Rao" tomorrow is submitted twice
    Then the first request should succeed with status 201
    And the second request should be rejected with status 409
    And the system should hold exactly 1 appointment
