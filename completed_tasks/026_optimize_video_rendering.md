# Task: Optimize Video Rendering

## Objective
Optimize `ULA.render_screen` in `src/ula.py` using `numpy` to improve performance. The current nested loop implementation is slow in Python.

## Plan
1.  Analyze `ULA.render_screen` logic.
2.  Implement a NumPy-based version of the rendering logic.
3.  Verify that the new implementation produces the same output as the original.
4.  Run existing video tests to ensure no regressions.
5.  Compare performance (if possible).

## Verification
- `pytest tests/test_ula_video.py` must pass.
