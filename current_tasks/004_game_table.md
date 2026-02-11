# Task 004: Game Table State

## Description
Implement the `GameTable` class to manage the overall state of the game. This includes the draw deck, discard pile, players, and turn management.

## Requirements
- `GameTable` class:
    - Properties:
        - `deck`: `Deck`
        - `discardPile`: `MutableList<Card>`
        - `players`: `List<Player>` (Need `Player` class first?)
        - `currentPlayerIndex`: Int
    - Methods:
        - `startGame(playerCount: Int)`: Initialize deck, players, deal cards.
        - `drawCard()`: Draw from deck.
        - `drawFromDiscard()`: Draw from discard pile (rules apply).
        - `discardCard(card: Card)`: End turn.
        - `nextTurn()`: Advance to next player.

## Priority: High
