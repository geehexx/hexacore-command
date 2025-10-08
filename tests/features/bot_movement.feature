Feature: Bot movement
  Scenario: Placeholder movement handling
    Given a bot is at axial coordinate (0, 0)
    When the bot attempts to move north
    Then the engine schedules a move event
