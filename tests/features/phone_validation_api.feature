Feature: Server-side phone validation
  The UI validates phone numbers, but the API is the real authority and must
  reject bad data even when the form is bypassed.

  @api @weak_phone
  Scenario Outline: API rejects invalid phone "<phone>"
    When I submit a booking request for "Dr. Asha Rao" tomorrow with phone "<phone>"
    Then the response status should be 422
    And no appointment should be stored

    Examples:
      | phone           |
      | abc             |
      | 12345           |
      | 98765abcde      |
      | 123456789012345 |
      | ---             |

  @api
  Scenario Outline: API accepts valid phone "<phone>"
    When I submit a booking request for "Dr. Asha Rao" tomorrow with phone "<phone>"
    Then the response status should be 201

    Examples:
      | phone          |
      | 9876543210     |
      | +919876543210  |
      | 98765 43210    |
