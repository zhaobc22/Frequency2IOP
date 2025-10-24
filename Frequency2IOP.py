import pandas as pd
import numpy as np

# -----------------------------
# I/O: read the first two columns from Excel
# -----------------------------
def read_first_two_columns(file_path, sheet_name='Sheet1'):
    """
    Read the first two columns from an Excel file.

    Parameters
    ----------
    file_path : str
        Path to the Excel (.xlsx) file.
    sheet_name : str, optional
        Worksheet name to read (default: 'Sheet1').

    Returns
    -------
    column1_list : list
        Values from column A (could be time/index).
    column2_list : list
        Values from column B (frequency readings).
    """
    data = pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        engine='openpyxl',
        usecols="A:B"
    )
    column1_list = data.iloc[:, 0].tolist()
    column2_list = data.iloc[:, 1].tolist()
    return column1_list, column2_list


# -----------------------------
# Temperature compensation
# -----------------------------
def apply_temperature_compensation(freq_values, temp_celsius=37.0, ref_temp=37.0, temp_coeff_per_deg=0.1):
    """
    Normalize measured frequencies to the reference temperature (default: 37 °C).

    Concept
    -------
    We assume a linear temperature-frequency dependence. To express what the
    frequency would be at 'ref_temp', we apply a correction based on the
    measured temperature 'temp_celsius'.

    Model (adjust if your sign convention differs)
    ----------------------------------------------
    f_normalized = f_measured + (ref_temp - temp_celsius) * temp_coeff_per_deg

    If temp_celsius < ref_temp (colder), (ref - temp) > 0 → frequency shifts up by +0.1 per °C.
    If temp_celsius > ref_temp (warmer), (ref - temp) < 0 → frequency shifts down by -0.1 per °C.

    Parameters
    ----------
    freq_values : list[float] or np.ndarray
        Raw frequency sequence.
    temp_celsius : float
        Actual measurement temperature (user input).
    ref_temp : float
        Reference temperature to normalize to (default 37 °C).
    temp_coeff_per_deg : float
        Frequency correction per 1 °C difference (default 0.1).

    Returns
    -------
    np.ndarray
        Temperature-compensated frequency array.
    """
    freq_values = np.asarray(freq_values, dtype=float)
    correction = (ref_temp - temp_celsius) * temp_coeff_per_deg
    return freq_values + correction


# -----------------------------
# Adaptive sliding-window: average of the smallest bottom_n values
# -----------------------------
def adaptive_min_average(values,
                         start_index,
                         base_window=300,
                         bottom_n=3,
                         low_percentile=5.0,
                         growth_factor=1.5,
                         max_window=None):
    """
    Compute the average of the smallest `bottom_n` values within an ADAPTIVE window.

    Rationale
    ---------
    Only minima are meaningful for pressure conversion. In regions where local minima
    occur sparsely, we increase the window length to include enough 'very low' points.

    Condition to stop growing the window
    ------------------------------------
    For the current window segment we estimate a 'very low' threshold by the
    `low_percentile` (e.g., 5th percentile). If the count of values <= threshold
    is less than `bottom_n`, we expand the window by `growth_factor` until:
        - the count meets/exceeds bottom_n, or
        - we hit the end of the array, or
        - we reach `max_window` (safety cap).

    Parameters
    ----------
    values : np.ndarray
        1D array of (temperature-compensated) frequency values.
    start_index : int
        Starting index of the sliding window.
    base_window : int
        Initial window length (default: 300).
    bottom_n : int
        Number of smallest values to average (default: 3).
    low_percentile : float
        Percentile (0-100). Points below this are considered 'very low' (default: 5th).
    growth_factor : float
        Multiplicative factor to grow the window each time (default: 1.5).
    max_window : int or None
        Upper bound for the window length. If None, set to 4 * base_window.

    Returns
    -------
    float or None
        Average of the smallest `bottom_n` values in the final window, or None if no room.
    """
    n = len(values)
    if max_window is None:
        max_window = int(4 * base_window)

    # If even the initial window cannot fit, return None
    if start_index >= n:
        return None

    window_len = base_window
    while True:
        end = min(n, start_index + window_len)
        if end - start_index <= 0:
            return None

        window = values[start_index:end]
        # Determine how many 'very low' points we have in this window
        thr = np.percentile(window, low_percentile)
        count_very_low = np.count_nonzero(window <= thr)

        if count_very_low >= bottom_n:
            # We have enough low points; compute mean of the smallest `bottom_n`
            smallest = np.partition(window, bottom_n - 1)[:bottom_n]
            return float(np.mean(smallest))

        # Otherwise, try to expand the window
        new_window_len = int(np.ceil(window_len * growth_factor))
        if new_window_len == window_len:
            new_window_len += 1  # ensure progress

        # Safety cap: do not exceed max_window nor the array end
        if new_window_len > max_window and (start_index + window_len) >= n:
            # No more meaningful expansion possible; fallback: use whatever we have
            smallest = np.partition(window, min(bottom_n, len(window)) - 1)[:min(bottom_n, len(window))]
            return float(np.mean(smallest)) if len(smallest) > 0 else None

        window_len = min(new_window_len, max_window)
        if start_index + window_len >= n and end == n:
            # Already at the end; cannot include more data
            smallest = np.partition(window, min(bottom_n, len(window)) - 1)[:min(bottom_n, len(window))]
            return float(np.mean(smallest)) if len(smallest) > 0 else None


def build_adaptive_series(values,
                          base_window=300,
                          bottom_n=3,
                          low_percentile=5.0,
                          growth_factor=1.5,
                          max_window=None):
    """
    Generate a series of local-minimum representatives using adaptive windows
    evaluated at every valid start index.

    Parameters
    ----------
    values : array-like
        Frequency data (already temperature-compensated).
    base_window : int
        Initial window size.
    bottom_n : int
        How many smallest points to average per window.
    low_percentile : float
        Percentile used to define 'very low' points.
    growth_factor : float
        Window growth multiplier when low points are insufficient.
    max_window : int or None
        Maximum window size.

    Returns
    -------
    list of float
        Sequence of local-minimum averages (one per start index where computed).
    """
    values = np.asarray(values, dtype=float)
    out = []
    # We mimic your original behavior of scanning from 0 to N - base_window.
    # With adaptation, some windows may become larger than base_window.
    n = len(values)
    last_valid_start = max(0, n - base_window)  # maintain at least one full base window as in original code
    for i in range(last_valid_start + 1):
        avg_min = adaptive_min_average(values, i,
                                       base_window=base_window,
                                       bottom_n=bottom_n,
                                       low_percentile=low_percentile,
                                       growth_factor=growth_factor,
                                       max_window=max_window)
        if avg_min is not None:
            out.append(avg_min)
    return out


# -----------------------------
# Calibration: piecewise linear frequency → pressure
# -----------------------------
def calibrate_frequency_to_pressure(freq, segments):
    """
    Convert frequency to pressure using piecewise-linear interpolation.

    IMPORTANT:
    The numerical breakpoints and target pressures below MUST come from your
    standard calibration procedure. You SHOULD update 'segments' if your
    calibration is refined.

    Parameters
    ----------
    freq : float
        Frequency value (already temperature-compensated).
    segments : list of dict
        Each segment defines a frequency interval [f_low, f_high] (inclusive on the nearest side)
        and the corresponding pressures at the boundaries: p_at_low, p_at_high.
        We perform linear interpolation within that interval.

        Example element:
        {
            "f_low": 498.8,
            "f_high": 505.0,
            "p_at_low": 15.0,
            "p_at_high": 7.5
        }

    Returns
    -------
    float
        Interpolated pressure (extrapolated linearly if freq falls below the last segment).
    """
    # Find the segment that contains 'freq'
    for seg in segments:
        f_low = seg["f_low"]
        f_high = seg["f_high"]
        if f_low <= freq <= f_high:
            # Linear interpolation between (f_low, p_low) and (f_high, p_high)
            p_low = seg["p_at_low"]
            p_high = seg["p_at_high"]
            if f_high == f_low:
                return float(p_low)  # degenerate case
            t = (freq - f_low) / (f_high - f_low)
            return float(p_low + t * (p_high - p_low))

    # If freq is ABOVE the highest defined range, clamp/extrapolate with the first segment
    first = segments[-1]  # segments will be sorted ascending by f_low; last element has the highest f_high
    highest_f_high = first["f_high"]
    highest_p_high = first["p_at_high"]
    if freq > highest_f_high:
        # Extrapolate beyond the top segment using its slope
        f_low = first["f_low"]; p_low = first["p_at_low"]
        f_high = first["f_high"]; p_high = first["p_at_high"]
        slope = (p_high - p_low) / (f_high - f_low) if f_high != f_low else 0.0
        return float(p_high + (freq - f_high) * slope)

    # If freq is BELOW the lowest defined range, extrapolate with the lowest segment
    lowest = segments[0]
    lowest_f_low = lowest["f_low"]
    lowest_p_low = lowest["p_at_low"]
    if freq < lowest_f_low:
        f_low = lowest["f_low"]; p_low = lowest["p_at_low"]
        f_high = lowest["f_high"]; p_high = lowest["p_at_high"]
        slope = (p_high - p_low) / (f_high - f_low) if f_high != f_low else 0.0
        return float(p_low + (freq - f_low) * slope)

    # Fallback (should not reach here)
    return np.nan


def get_default_calibration_segments():
    """
    Default piecewise calibration segments derived from your original if-elif mapping.

    NOTE: These numbers are placeholders mirroring your current calibration.
    >>> You can (and should) modify these breakpoints and pressures based on
        your latest STANDARD CALIBRATION results. <<<
    The segments must be sorted by ascending frequency.

    Original mapping summary:
    - [505, 570]:  7.5 → 0
    - [498.8, 505]: 15  → 7.5
    - [493.8, 498.8]: 22.5 → 15
    - [490.2, 493.8]: 30 → 22.5
    - [487.8, 490.2]: 37.5 → 30
    - [484.8, 487.8]: 45 → 37.5
    - (< 484.8): extend the slope used below 484.8 (45 at 484.8; +2.5 per -1 Hz)

    Returns
    -------
    list[dict]
        Segments sorted by ascending f_low.
    """
    segments = [
        # Lowest band (open-ended below 484.8): we define a segment down to, say, 400 for linear extrapolation
        # At f=484.8 → P=45; slope below 484.8 was (7.5 / 3) per -1 Hz = 2.5 per Hz
        # So, extend linearly: at f=400, P = 45 + (484.8 - 400) * 2.5
        {"f_low": 400.0,   "f_high": 484.8, "p_at_low": 45 + (484.8 - 400.0) * (7.5/3.0), "p_at_high": 45.0},

        {"f_low": 484.8,   "f_high": 487.8, "p_at_low": 45.0,  "p_at_high": 37.5},
        {"f_low": 487.8,   "f_high": 490.2, "p_at_low": 37.5,  "p_at_high": 30.0},
        {"f_low": 490.2,   "f_high": 493.8, "p_at_low": 30.0,  "p_at_high": 22.5},
        {"f_low": 493.8,   "f_high": 498.8, "p_at_low": 22.5,  "p_at_high": 15.0},
        {"f_low": 498.8,   "f_high": 505.0, "p_at_low": 15.0,  "p_at_high": 7.5},
        {"f_low": 505.0,   "f_high": 570.0, "p_at_low": 7.5,   "p_at_high": 0.0},  # extend to 570 as per original 65 Hz span
    ]
    # Ensure sorted by frequency (ascending)
    segments = sorted(segments, key=lambda d: d["f_low"])
    return segments


# -----------------------------
# MAIN (example usage)
# -----------------------------
if __name__ == "__main__":
    # ---- 1) Load data
    file_path = "D:/zhenshi.xlsx"
    sheet_name = "Sheet1"
    column1, column2 = read_first_two_columns(file_path, sheet_name=sheet_name)

    # ---- 2) Temperature compensation (edit 'temp_celsius' as needed)
    # Enter the actual measurement temperature here:
    temp_celsius = 37.0   # <-- USER INPUT: set your measurement temperature (°C)
    # If your sign convention is opposite, flip the sign in apply_temperature_compensation().
    freq_tc = apply_temperature_compensation(
        column2,
        temp_celsius=temp_celsius,
        ref_temp=37.0,
        temp_coeff_per_deg=0.1  # <-- USER EDITABLE: frequency correction per 1 °C
    )

    # ---- 3) Build adaptive minima series
    adaptive_series = build_adaptive_series(
        freq_tc,
        base_window=300,    # <-- USER EDITABLE: starting window (samples)
        bottom_n=3,         # <-- USER EDITABLE: how many minima to average
        low_percentile=5.0, # <-- USER EDITABLE: 'very low' definition (percentile)
        growth_factor=1.5,  # <-- USER EDITABLE: how aggressively to expand window
        max_window=None     # <-- USER EDITABLE: cap; None defaults to 4x base_window
    )

    # ---- 4) Frequency → Pressure conversion via piecewise linear interpolation
    # >>> VERY IMPORTANT: Update these breakpoints & pressures after your STANDARD CALIBRATION procedure. <<<
    calib_segments = get_default_calibration_segments()

    pressures = [calibrate_frequency_to_pressure(f, calib_segments) for f in adaptive_series]

    # ---- 5) Output (simple print; replace with CSV export if desired)
    for p in pressures:
        print(p)

    # OPTIONAL: save to CSV for downstream analysis
    # out_df = pd.DataFrame({"pressure": pressures})
    # out_df.to_csv("pressure_results.csv", index=False)
    # print("Saved:", "pressure_results.csv")
