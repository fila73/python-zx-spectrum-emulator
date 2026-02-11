# Task 005: Melding Mechanics

## Description
Implement the logic for players to place melds on the table, add cards to existing melds, and replace Jokers. Enforce the "Initial Meld" rule (42 points).

## Requirements
- **GameTable Updates**:
    - Property `melds`: List of placed melds (List of Cards).
    - Track `hasMelded` state for each player.
- **Actions**:
    - `meld(playerId, melds: List<List<Card>>)`:
        - If first time: Validate total points >= 42 + pure sequence.
        - If already melded: Validate each new meld is valid set/seq.
    - `addToMeld(playerId, meldIndex, card, position)`:
        - Add card to existing meld if valid.
        - Only allowed if player `hasMelded`.
    - `replaceJoker(playerId, meldIndex, card)`:
        - Replace Joker in a meld with the actual card.
        - Take Joker into hand.
        - Only allowed if player `hasMelded`.
- **Game End**:
    - Detect when player empties hand (after discard).

## Priority: High
