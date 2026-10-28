Feature: Data foundation for occupancy, power and faults

  @happy @CP-DATA-001
  Scenario: Status freshness decides "live"
    Given an EVSE status update received 20 minutes ago
    When the planner reads the EVSE
    Then the status is not treated as live

  @happy @CP-DATA-002
  Scenario: Faults are kept as history
    When an EVSE goes OUTOFORDER and returns AVAILABLE after 3 hours
    Then the history holds both changes with source and timestamps
    And the outage duration is 3 hours

  @happy @CP-DATA-003
  Scenario: Historical profile by hour and season
    Given eight weeks of sessions at an EVSE group
    When the occupancy profile is built
    Then it has values per weekday, hour and peak/normal

  @happy @CP-IDLE-004
  Scenario: Simultaneous sessions are recorded for power sharing
    Given two of our sessions run at the same EVSE group
    When charging periods arrive
    Then the group record shows two simultaneous sessions and their power

  @error @CP-DATA-004
  Scenario: EPDK list reconciliation finds a discrepancy
    Given our list has a 180 kW EVSE in Milas
    And the EPDK station list shows the same station at 120 kW
    When the weekly reconciliation runs
    Then a "wrong power" discrepancy is raised for that station
