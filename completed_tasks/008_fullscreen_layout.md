# Task 008: Fullscreen UI and Overlay Layout

## Description
Transform the UI into a professional fullscreen game experience with overlays and a grid-based play area.

## Requirements
- **Fullscreen Mode:** Enable Edge-to-Edge display and hide system bars (status bar, navigation bar).
- **Layout Redesign:**
    - Use a green felt background for the entire screen.
    - **Right Overlay:** Place the Deck and Discard Pile vertically on the right.
    - **Left Overlay:** Place opponent icons vertically on the left, with the player's icon at the bottom left.
    - **Player Hand:** Horizontal row of cards at the bottom. Scale cards so 13 fit comfortably with small gaps.
- **Turn Timer:** Implement a 1-minute countdown per turn. Display remaining seconds as an overlay on the current player's icon.
- **Clean UI:** Remove the standard TopAppBar and placeholder text labels.

## Model Selection
- **gemini-3-pro-preview**: Recommended for complex UI layout and timer logic.

## Priority: High
