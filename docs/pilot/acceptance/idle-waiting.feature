Feature: Reducing idle waiting at chargers

  @happy @CP-IDLE-001
  Scenario: Queue prediction labels its source
    Given EVSE group X has live status and EVSE group Y has only history
    When queue time is predicted for both
    Then X is labelled "live" and Y is labelled "historical"

  @happy @CP-IDLE-002
  Scenario: Long queue triggers an alternative before arrival
    Given the predicted queue at the planned stop is 18 minutes on a normal day
    When the driver is 20 km before the stop
    Then the app offers an alternative stop with a lower total time

  @happy @CP-IDLE-003
  Scenario: Move-your-vehicle notice at the end condition
    Given a DC session where the CPO ends sessions at 85% state of charge
    When the vehicle reaches 85%
    Then the app notifies the driver to move the vehicle
    And shows the occupancy fee the CPO publishes, if any

  @happy @CP-PEAK-001
  Scenario: Peak calendar tags samples
    Given the peak calendar has a test holiday period from 2027-03-19 to 2027-03-22
    When a session starts on 2027-03-18
    Then the session is tagged "peak"

  @happy @CP-PEAK-002
  Scenario: Peak trips always show an alternative family
    Given the peak calendar is active
    When the driver plans a 650 km trip to Bodrum
    Then the planner uses the peak occupancy profile
    And shows at least one plan on an alternative family
