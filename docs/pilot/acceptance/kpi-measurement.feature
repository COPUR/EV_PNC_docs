Feature: KPI measurement

  @happy @CP-KPI-001
  Scenario: Daily KPI split
    When the daily KPI job runs
    Then KPI-1 to KPI-7 are published per family, cluster and peak/normal

  @happy @CP-DATA-005
  Scenario: Data coverage KPI
    Given 120 K1 EVSEs of which 90 had a status update in the last 15 minutes
    When KPI-7 is computed
    Then it is 75%

  @happy @CP-KPI-002
  Scenario: Control and treatment groups
    Given drivers are assigned to control or treatment at enrolment
    When KPIs are computed
    Then each KPI is reported per group

  @happy @CP-KPI-003
  Scenario: Optional waiting-time question
    When a trip ends
    Then the app asks one optional question per stop and stores it with the measured wait

  @happy @CP-KPI-004
  Scenario: Location traces are coarsened after 90 days
    Given a trip trace older than 90 days
    When the retention job runs
    Then the trace is stored only as H3 resolution 8 cells
