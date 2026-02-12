# Task 011: Fix Crash - Negative Padding in Player Hand

## Description
The application currently crashes on startup or when rendering the player's hand. Logcat analysis reveals a `java.lang.IllegalArgumentException: Padding must be non-negative`.

## Root Cause
In `GameScreen.kt` (around line 195), a negative padding value is being applied, likely in an attempt to overlap cards in the `PlayerHandArea`. Jetpack Compose does not allow negative padding.

## Error Log (from device)
```
02-12 01:15:59.753 27228 27228 E AndroidRuntime: FATAL EXCEPTION: main
02-12 01:15:59.753 27228 27228 E AndroidRuntime: Process: sk.zoliky, PID: 27228
02-12 01:15:59.753 27228 27228 E AndroidRuntime: java.lang.IllegalArgumentException: Padding must be non-negative
02-12 01:15:59.753 27228 27228 E AndroidRuntime: 	at androidx.compose.foundation.layout.PaddingElement.<init>(Padding.kt:336)
02-12 01:15:59.753 27228 27228 E AndroidRuntime: 	at sk.zoliky.ui.GameScreenKt$PlayerHandArea$1$1.invoke(GameScreen.kt:195)
```

## Requirements
- Locate the negative padding in `GameScreen.kt` and replace it with a valid layout strategy (e.g., using a custom `Layout` or `offset` for overlapping).
- Ensure the app launches successfully without crashing.

## Model Selection
- **gemini-3-flash-preview**: Sufficient for fixing this layout bug.

## Priority: BLOCKER
