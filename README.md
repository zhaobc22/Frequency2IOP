1. Frequency-to-IOP Conversion Toolkit

This Python script performs automatic frequency-to-pressure conversion for resonant sensors, integrating adaptive minima extraction, temperature compensation, and calibration-based linear interpolation.


2. Key Features

2.1 Adaptive Sliding Window Algorithm
Automatically adjusts the sampling window length to ensure sufficient local minima are captured — ideal for non-uniform or noisy signals.

2.2 Temperature Compensation
Applies a user-defined correction centered at 37 °C, shifting the resonance frequency by ±0.1 Hz per °C difference (modifiable).

2.3 Calibration-Based Linear Interpolation
Converts frequency to pressure using a clearly documented piecewise-linear calibration table.

2.4 Calibration breakpoints and slope values must be updated based on your standard calibration procedure.

2.5 Modular & Readable Code
Each function includes detailed English docstrings following the NumPy/SciPy documentation style.

3. Workflow Overview

3.1 Read frequency data from the first two columns of an Excel file
(A: index/time, B: frequency).

3.2 Apply temperature compensation to normalize readings to the reference 37 °C.

3.3 Extract representative minima via an adaptive sliding window that expands where minima are sparse.

3.4 Convert frequencies to pressures via calibration-based piecewise linear interpolation.

3.5 Output or save the resulting pressure sequence (e.g., to CSV).

