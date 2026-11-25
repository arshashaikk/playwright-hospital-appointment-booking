Feature: Confirmation page accuracy
  The confirmation page must show exactly the doctor, date and time that were booked.

  Background:
    Given the appointment portal is open

  @ui @wrong_doctor
  Scenario Outline: Confirmation shows the selected doctor "<doctor>"
    When I choose doctor "<doctor>"
    And I pick an available slot <days> days from today
    And I enter patient details "Anita Verma", "9123456780", "anita@example.com"
    And I confirm the appointment
    Then I should see the booking confirmation
    And the confirmation should show doctor "<doctor>"
    And the confirmation department should be "<department>"
    And the confirmation should show the selected date and time

    Examples:
      | doctor          | department  | days |
      | Dr. Asha Rao    | cardiology  | 1    |
      | Dr. Vikram Shah | cardiology  | 2    |
      | Dr. Meera Iyer  | neurology   | 3    |
      | Dr. Rohan Das   | orthopedics | 4    |
      | Dr. Sana Khan   | pediatrics  | 5    |
      | Dr. Liam Ortiz  | dermatology | 6    |

  @ui @wrong_doctor
  Scenario: Booked appointment can be fetched with the reference shown on screen
    When I choose doctor "Dr. Meera Iyer"
    And I pick an available slot tomorrow
    And I enter patient details "Anita Verma", "9123456780", "anita@example.com"
    And I confirm the appointment
    Then the stored appointment for the shown reference should match the selected doctor
