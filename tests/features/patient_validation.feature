Feature: Patient detail validation
  The booking form must reject invalid phone numbers, emails and names.

  Background:
    Given the appointment portal is open
    And I have chosen doctor "Dr. Asha Rao" and an available slot tomorrow

  @ui
  Scenario Outline: Invalid phone number "<phone>" is rejected in the form
    When I enter patient details "Priya Sharma", "<phone>", "priya@example.com"
    And I confirm the appointment
    Then I should see a phone validation error
    And I should not see a booking confirmation

    Examples:
      | phone           |
      | abc             |
      | 12345           |
      | 98765abcde      |
      | 123456789012345 |
      | (empty)         |

  @ui
  Scenario Outline: Valid phone format "<phone>" is accepted
    When I enter patient details "Priya Sharma", "<phone>", "priya@example.com"
    And I confirm the appointment
    Then I should see the booking confirmation

    Examples:
      | phone          |
      | 9876543210     |
      | +919876543210  |
      | 98765 43210    |
      | (987)654-3210  |

  @ui
  Scenario Outline: Invalid email "<email>" is rejected
    When I enter patient details "Priya Sharma", "9876543210", "<email>"
    And I confirm the appointment
    Then I should see an email validation error
    And I should not see a booking confirmation

    Examples:
      | email            |
      | plainaddress     |
      | missing@domain   |
      | @no-local.com    |
      | (empty)          |

  @ui
  Scenario: Name is required
    When I enter patient details "(empty)", "9876543210", "priya@example.com"
    And I confirm the appointment
    Then I should see a name validation error
    And I should not see a booking confirmation
