# Task 010: Advanced Turn Logic and Rules

## Description
Refine the turn flow logic to include drawing restrictions and discard mechanics.

## Requirements
- **Draw Phase:** Turn starts by clicking the Deck or Discard Pile.
- **Restrictions:**
    - Drawing from the Discard Pile is only allowed from the **4th round** onwards.
    - If a card is drawn from the Discard Pile, the player **must** use it in a meld during that same turn.
- **End Turn:** A turn is finalized ONLY by dragging a card from the hand onto the Discard Pile.

## Model Selection
- **gemini-3-flash-preview**: Suitable for logic refinement.

## Priority: High
