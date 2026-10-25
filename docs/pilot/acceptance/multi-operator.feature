Feature: Multi-operator access over three channels

  @happy @CP-ACCESS-001
  Scenario: Channel is shown before start
    Given a ZES EVSE reachable through Hubject
    When the driver opens the EVSE
    Then the app shows the channel "Hubject" before the session starts

  @happy @CP-ACCESS-002
  Scenario: Cheaper channel wins
    Given an EVSE reachable through Hubject and bilateral OCPI
    And the bilateral guest price is lower
    When the session is started
    Then the bilateral OCPI channel is used

  @happy @CP-ACCESS-003
  Scenario: Daily K1 evidence
    When the daily count runs
    Then reachable EVSEs are counted per channel, family and power class
