Feature: Guest price competition test

  @happy @CP-PRICE-001
  Scenario: Guest price follows ADR-0006 and stays fixed
    Given a B2B energy price, a session fee folded into the reference session, a 12% margin and 20% VAT
    When a guest session starts
    Then the shown price is in TL/kWh only
    And the CDR uses the same TL/kWh value

  @error @CP-PRICE-002
  Scenario: Margin above the cap is rejected
    When pricing is configured with a 22% margin
    Then the configuration is rejected until TR-06 is confirmed

  @error @CP-PRICE-002
  Scenario: Guest price far above direct card price is flagged
    Given the direct card price at an EVSE is 10.00 TL/kWh
    When the guest price is 11.80 TL/kWh
    Then the EVSE is flagged as exceeding the 15% band
