# Task 009: Drag-and-Drop and Grid Slot System

## Description
Implement the core interaction mechanics: dragging cards to a "snap-to-grid" slot system on the game board.

## Requirements
- **Grid System:** The central area (excluding overlays) must be divided into invisible slots (rows/columns).
- **Drag-and-Drop:** Enable dragging cards from the player's hand onto the table.
- **Snap-to-Grid:** Cards must snap to the nearest slot when released.
- **Dynamic Grid:** If the table fills up, shrink slot sizes to add a new row or column automatically.
- **Grouping:** Ensure at least one empty slot between different card groups (sets/sequences) within a row.
- **Automatic Discard:** If a complete group of 4 cards (a full Set) is formed on the table, it should flash and then be automatically moved to the discard pile.

## Model Selection
- **gemini-3-pro-preview**: Required for complex coordinate math and drag-and-drop state management.

## Priority: High
