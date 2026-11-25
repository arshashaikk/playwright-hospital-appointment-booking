Feature: Book a hospital appointment
  As a patient
  I want to book an appointment online
  So that I do not need to call the hospital

  Background:
    Given the appointment portal is open

  @smoke @ui @wrong_doctor
  Scenario: Patient books an appointment with a cardiologist
    When I select the "Cardiology" department
    And I choose doctor "Dr. Asha Rao"
    And I pick an available slot tomorrow
    And I enter patient details "Priya Sharma", "9876543210", "priya@example.com"
    And I confirm the appointment
    Then I should see the booking confirmation
    And the confirmation should show doctor "Dr. Asha Rao"
    And the confirmation should show the selected date and time
    And the confirmation should show patient "Priya Sharma" with phone "9876543210" and email "priya@example.com"

  @ui
  Scenario: Selecting a department lists only its doctors
    When I select the "Cardiology" department
    Then the doctor list should contain "Dr. Asha Rao"
    And the doctor list should contain "Dr. Vikram Shah"
    And the doctor list should not contain "Dr. Meera Iyer"

  @ui
  Scenario: Searching by doctor name
    When I search for "Meera"
    Then the doctor list should contain "Dr. Meera Iyer"
    And the doctor list should not contain "Dr. Asha Rao"

  @ui
  Scenario: Searching by specialty
    When I search for "pediatric"
    Then the doctor list should contain "Dr. Sana Khan"

  @ui
  Scenario: Searching for a doctor that does not exist
    When I search for "zzzz"
    Then the doctor list should be empty

  @ui
  Scenario: Booking summary updates as the patient makes choices
    When I choose doctor "Dr. Rohan Das"
    And I pick an available slot tomorrow
    Then the booking summary should mention "Dr. Rohan Das"
