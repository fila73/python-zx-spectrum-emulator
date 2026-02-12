# Task 009: Dynamic Grid and Grouping

## Description
Implement a responsive grid system for the table area that auto-arranges melds and supports dynamic resizing.

## Requirements
- **Dynamic Grid:**
    - The table area should automatically flow melds (sets/sequences) into a grid.
    - As more melds are added, the grid should adjust (e.g., scale down or scroll) to fit them.
- **Grouping:**
    - Cards dropped on the table should be visually grouped into distinct melds.
    - Dropping a card on an existing meld should add it to that specific group.
- **Auto-Discard:**
    - [x] Full sets of 4 cards are automatically removed (Already implemented).
- **Visuals:**
    - Melds should have slightly different background or spacing to distinguish them.

## Model Selection
- **gemini-3-flash-preview**: Good for UI logic and Compose layouts.

## Priority: Medium
