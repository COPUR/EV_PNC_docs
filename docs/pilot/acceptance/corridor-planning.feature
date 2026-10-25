Feature: Corridor route planning by total time
  The planner ranks plans by driving + charging + queue time over the main route and four alternative families.

  Background:
    Given the corridor model has route M and families A1, A2, A3, A4
    And a vehicle with a known charging curve leaves İstanbul with 90% state of charge

  @happy @CP-GEO-001 @CP-NAV-001
  Scenario: Plan shows the three time components
    When the driver plans İstanbul to Bodrum
    Then each candidate plan shows driving, charging and queue time separately
    And plans are ordered by their total time

  @happy @CP-GEO-002
  Scenario: EVSEs are tagged with family and cluster
    Given an EVSE 1.5 km from the O-5 geometry in an Oksijen cluster
    When the corridor index is rebuilt
    Then the EVSE carries family code M and cluster label "Oksijen"

  @happy @CP-NAV-002
  Scenario: Charging time accounts for power sharing and summer climate load
    Given the planned stop usually shares power between two vehicles
    And the trip ends on segment A4 in July
    When charging time is predicted
    Then the prediction uses the shared power level and adds the climate-load correction

  @error @CP-NAV-003
  Scenario: Re-plan when the next stop goes out of service
    Given an active trip with the next stop at Söke
    When the Söke EVSE group reports all connectors out of order
    Then the planner proposes a new plan before the driver reaches Söke

  @happy @CP-NAV-004
  Scenario: Sparse segment keeps a reserve
    Given the trip uses family A1 via Çanakkale
    When the planner picks stops
    Then the arrival state of charge at the next viable stop is at least the configured reserve
    And a nearer stop with a longer total time is not chosen

  @happy @CP-NAV-005
  Scenario: Ferry versus bridge on the Çanakkale family
    Given a predicted Gelibolu ferry wait of 50 minutes
    When the planner compares the 1915 Çanakkale Bridge and the ferry
    Then it offers the option with the lower total time and shows the crossing wait
