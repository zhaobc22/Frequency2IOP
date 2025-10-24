🧠 Frequency-to-IOP Conversion Toolkit

This Python script performs automatic frequency-to-pressure conversion for resonant sensors, integrating adaptive minima extraction, temperature compensation, and calibration-based linear interpolation.


⚙️ Key Features

✅ Adaptive Sliding Window Algorithm
Automatically adjusts the sampling window length to ensure sufficient local minima are captured — ideal for non-uniform or noisy signals.

✅ Temperature Compensation
Applies a user-defined correction centered at 37 °C, shifting the resonance frequency by ±0.1 Hz per °C difference (modifiable).

✅ Calibration-Based Linear Interpolation
Converts frequency to pressure using a clearly documented piecewise-linear calibration table.

⚠️ Calibration breakpoints and slope values must be updated based on your standard calibration procedure.

✅ Modular & Readable Code
Each function includes detailed English docstrings following the NumPy/SciPy documentation style.

📘 Workflow Overview

Read frequency data from the first two columns of an Excel file
(A: index/time, B: frequency).

Apply temperature compensation to normalize readings to the reference 37 °C.

Extract representative minima via an adaptive sliding window that expands where minima are sparse.

Convert frequencies to pressures via calibration-based piecewise linear interpolation.

Output or save the resulting pressure sequence (e.g., to CSV).

🧩 Algorithm Logic (Simplified)
Raw frequency series
     ↓
Temperature correction (per °C)
     ↓
Adaptive window scan (e.g., 300 → 450 → 600 samples ...)
     ↓
Average of lowest N points per window
     ↓
Piecewise linear frequency→pressure conversion
     ↓
Final pressure series

🧮 Input & Parameters
Parameter	Description	Default	Editable
file_path	Path to Excel file (.xlsx)	'D:/zhenshi.xlsx'	✅
sheet_name	Worksheet name	'Sheet1'	✅
temp_celsius	Measurement temperature (°C)	37.0	✅
temp_coeff_per_deg	Frequency correction per 1 °C	0.1 Hz/°C	✅
base_window	Initial window size (samples)	300	✅
bottom_n	Number of smallest points per window	3	✅
low_percentile	Threshold percentile for "very low" detection	5.0	✅
growth_factor	Window growth multiplier	1.5	✅
max_window	Maximum allowed window length	4×base_window	✅
📈 Calibration Table

Defined in get_default_calibration_segments().
Each segment specifies the mapping between frequency and pressure as a linear relationship.

Example entry:

{
    "f_low": 498.8,
    "f_high": 505.0,
    "p_at_low": 15.0,
    "p_at_high": 7.5
}


You must update these breakpoints and pressures according to your latest standard calibration results.


📄 License

MIT License — you are free to use, modify, and distribute with attribution.
