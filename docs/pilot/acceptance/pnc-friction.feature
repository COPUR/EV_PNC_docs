Feature: Plug&Charge start friction and success rate

  @happy @CP-PNC-001
  Scenario: Successful attempt is recorded with timings
    Given a driver with an active contract certificate
    When the cable is plugged in and energy flows 25 seconds later
    Then the attempt is recorded with pool, ISO 15118 version, timestamps and outcome "success"

  @error @CP-PNC-002
  Scenario: Pool not reachable falls back in the same screen
    Given the CPO does not query the pool that holds our certificate
    When the attempt fails
    Then the cause is "pool not reachable"
    And the app offers an app start or a guest start on the same screen

  @happy @CP-PNC-003
  Scenario: Plug&Charge preference is bounded
    Given two stops differ only in Plug&Charge support and by 5 minutes of total time
    When the driver with an active certificate plans the trip
    Then the faster stop without Plug&Charge is ranked first
