"""
predictor.py
------------
Land Boundary Prediction Engine.

Calculates realistic land boundary dimensions (North, South, East, West in feet)
based on the total land area (in sq.ft) and the selected land shape.
"""

import math
import random
from typing import Dict, Union


def _round2(value: float) -> float:
    """Round floating point value to two decimal places."""
    return round(float(value), 2)


def predict_boundaries(
    area_sqft: float,
    land_shape: str = "Other / Unknown"
) -> Dict[str, Union[float, int]]:
    """
    Predict North, South, East, and West land boundary measurements.

    Parameters
    ----------
    area_sqft : float
        Total land area entered by user in square feet. Must be > 0.
    land_shape : str
        Selected land shape: 'Square', 'Rectangular', or 'Other / Unknown'.

    Returns
    -------
    dict
        Dictionary containing north_ft, south_ft, east_ft, west_ft,
        and calculated_area_sqft.
    """
    if area_sqft <= 0:
        raise ValueError("Total land area must be greater than zero.")

    shape_normalized = str(land_shape).strip()

    if shape_normalized == "Square":
        # Square shape: North ≈ South, East ≈ West, and Length ≈ Width
        side = math.sqrt(area_sqft)

        # Introduce realistic micro-variations (±0.8% variation)
        delta_north = random.uniform(-0.008, 0.008) * side
        delta_east = random.uniform(-0.008, 0.008) * side

        north = side + delta_north
        south = (2 * side) - north  # ensures average length = side

        east = side + delta_east
        west = (2 * side) - east    # ensures average width = side

    elif shape_normalized in ["Rectangular", "Rectangle"]:
        # Rectangular shape: North ≈ South, East ≈ West, but Length != Width
        aspect_ratio = random.uniform(1.4, 2.2)

        # Calculate dimension lengths
        length = math.sqrt(area_sqft * aspect_ratio)
        width = area_sqft / length

        # Randomly choose orientation (Length along North-South or East-West)
        if random.choice([True, False]):
            ns_base, ew_base = length, width
        else:
            ns_base, ew_base = width, length

        # Small survey variations (±0.6%)
        delta_ns = random.uniform(-0.006, 0.006) * ns_base
        delta_ew = random.uniform(-0.006, 0.006) * ew_base

        north = ns_base + delta_ns
        south = (2 * ns_base) - north

        east = ew_base + delta_ew
        west = (2 * ew_base) - east

    else:
        # Other / Unknown shape: Boundaries vary noticeably but remain realistic
        base_side = math.sqrt(area_sqft)

        # Random aspect variation
        aspect = random.uniform(1.1, 1.8)
        ns_mean = base_side * math.sqrt(aspect)
        ew_mean = area_sqft / ns_mean

        # Moderate boundary variations (±2.5%)
        north = ns_mean * random.uniform(0.975, 1.025)
        south = (2 * ns_mean) - north

        east = ew_mean * random.uniform(0.970, 1.030)
        west = (2 * ew_mean) - east

    # -------------------------------------------------------------
    # Final Area Calculation & Boundary Validation
    # -------------------------------------------------------------
    avg_length = (north + south) / 2.0
    avg_width = (east + west) / 2.0
    computed_area = avg_length * avg_width

    # Fine-tune slightly to ensure calculated area equals input area exactly
    correction_factor = math.sqrt(area_sqft / computed_area) if computed_area > 0 else 1.0

    north_final = _round2(north * correction_factor)
    south_final = _round2(south * correction_factor)
    east_final = _round2(east * correction_factor)
    west_final = _round2(west * correction_factor)

    avg_len_final = (north_final + south_final) / 2.0
    avg_wid_final = (east_final + west_final) / 2.0
    calculated_area_sqft = round(avg_len_final * avg_wid_final)

    return {
        "north_ft": north_final,
        "south_ft": south_final,
        "east_ft": east_final,
        "west_ft": west_final,
        "calculated_area_sqft": calculated_area_sqft,
    }


if __name__ == "__main__":
    # Quick sanity check
    sample_area = 1652.0
    for mode in ["Square", "Rectangular", "Other / Unknown"]:
        res = predict_boundaries(sample_area, mode)
        print(f"--- Mode: {mode} ---")
        print(f"North: {res['north_ft']} ft | South: {res['south_ft']} ft")
        print(f"East:  {res['east_ft']} ft | West:  {res['west_ft']} ft")
        print(f"Calculated Area: {res['calculated_area_sqft']} sqft\n")