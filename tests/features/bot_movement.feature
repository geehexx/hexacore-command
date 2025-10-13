Feature: Bot movement
  Background:
    Given a movement system is registered

  Scenario: Bot moves north and completes the action
    Given a bot with id "bot-1" at axial coordinate (0, 0)
    When the bot queues a move intent toward axial coordinate (0, 1)
    Then the movement system publishes a completed move event
    And the bot position is updated to axial coordinate (0, 1)
