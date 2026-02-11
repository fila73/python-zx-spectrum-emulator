# Task 002: Basic Game Logic (Combinations & Scoring)

## Description
Implement the core logic for validating card combinations (sets and sequences) and calculating their point values, according to Žolíky rules.

## Requirements
- Implement `CombinationValidator` class.
- Method `isValidSet(cards: List<Card>)`: Returns true if cards form a valid set (3-4 cards of same rank, different suits).
- Method `isValidSequence(cards: List<Card>)`: Returns true if cards form a valid sequence (3+ cards of same suit, consecutive ranks).
- Method `calculatePoints(cards: List<Card>)`: Returns the total point value of the cards (for initial meld check).
- **Joker Handling**:
    - Jokers can substitute any card.
    - Validate that a Joker is used correctly in sequences.
    - Calculate points correctly (Joker takes value of replaced card).

## Priority: High
