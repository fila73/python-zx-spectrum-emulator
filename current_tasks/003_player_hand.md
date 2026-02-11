# Task 003: Player Hand Management

## Description
Implement the `PlayerHand` class to manage a player's cards. This includes adding/removing cards, sorting them, and validating if the hand meets the criteria for the initial meld (42 points + pure sequence).

## Requirements
- `PlayerHand` class:
    - `addCard(card: Card)`
    - `removeCard(card: Card)`
    - `sortCards()`: Sort by Suit then Rank, or by Rank.
    - `getCards()`: Return immutable list.
- **Initial Meld Validation**:
    - `canMeld(combinations: List<List<Card>>)`:
        - Check if total points >= 42.
        - Check if at least one sequence is "pure" (no Joker).
        - Verify all combinations are valid sets or sequences.

## Priority: High
