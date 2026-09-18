import math
from typing import Dict, Any, List, Tuple

# Valid time bounds: between 07:00 and 17:00
MIN_TIME = 7.0
MAX_TIME = 17.0

# Linear models for B->C->D: (low_time, high_time, slope, intercept, label)
# 07:00-07:15: duration = -36.30 * time + 367.10
# 07:16-08:15: duration = -67.64 * time + 651.50
# 08:16-09:15: duration = -80.06 * time + 811.65
# 09:16-10:15: duration = -79.88 * time + 872.11
# 10:16-11:15: duration = -60.12 * time + 728.30
# 11:16-12:15: duration = -59.07 * time + 776.71
# 12:16-13:15: duration = -63.92 * time + 897.85
# 13:16-14:15: duration = -47.59 * time + 738.65
# 14:16-15:15: duration = -34.79 * time + 614.78
# 15:16-16:15: duration = -43.84 * time + 812.27
# 16:16-17:15: duration = -63.60 * time + 1194.87
BCD_INTERVALS = [
    (7.00, 7.25, -36.30, 367.10, "07:00-07:15"),
    (7.25, 8.25, -67.64, 651.50, "07:16-08:15"),
    (8.25, 9.25, -80.06, 811.65, "08:16-09:15"),
    (9.25, 10.25, -79.88, 872.11, "09:16-10:15"),
    (10.25, 11.25, -60.12, 728.30, "10:16-11:15"),
    (11.25, 12.25, -59.07, 776.71, "11:16-12:15"),
    (12.25, 13.25, -63.92, 897.85, "12:16-13:15"),
    (13.25, 14.25, -47.59, 738.65, "13:16-14:15"),
    (14.25, 15.25, -34.79, 614.78, "14:16-15:15"),
    (15.25, 16.25, -43.84, 812.27, "15:16-16:15"),
    (16.25, 17.25, -63.60, 1194.87, "16:16-17:15")
]

# Linear models for B->C->E:
# 07:00-07:15: duration = -64.84 * time + 543.20
# 07:16-08:15: duration = -57.99 * time + 552.48
# 08:16-09:15: duration = -60.24 * time + 630.26
# 09:16-10:15: duration = -59.41 * time + 682.54
# 10:16-11:15: duration = -58.36 * time + 731.04
# 11:16-12:15: duration = -63.81 * time + 852.59
# 12:16-13:15: duration = -60.75 * time + 876.87
# 13:16-14:15: duration = -59.25 * time + 916.35
# 14:16-15:15: duration = -57.37 * time + 949.71
# 15:16-16:15: duration = -58.66 * time + 1027.28
# 16:16-17:15: duration = -58.89 * time + 1090.40
BCE_INTERVALS = [
    (7.00, 7.25, -64.84, 543.20, "07:00-07:15"),
    (7.25, 8.25, -57.99, 552.48, "07:16-08:15"),
    (8.25, 9.25, -60.24, 630.26, "08:16-09:15"),
    (9.25, 10.25, -59.41, 682.54, "09:16-10:15"),
    (10.25, 11.25, -58.36, 731.04, "10:16-11:15"),
    (11.25, 12.25, -63.81, 852.59, "11:16-12:15"),
    (12.25, 13.25, -60.75, 876.87, "12:16-13:15"),
    (13.25, 14.25, -59.25, 916.35, "13:16-14:15"),
    (14.25, 15.25, -57.37, 949.71, "14:16-15:15"),
    (15.25, 16.25, -58.66, 1027.28, "15:16-16:15"),
    (16.25, 17.25, -58.89, 1090.40, "16:16-17:15")
]


def time_to_decimal(hour: int, minute: int) -> float:
    """Convert hour and minute into decimal hours."""
    return hour + (minute / 60.0)


def format_minutes(minutes: float) -> str:
    """Format minutes into human-readable whole hours and minutes (no decimals, no seconds)."""
    total_mins = int(round(minutes))
    hrs = total_mins // 60
    mins = total_mins % 60
    if hrs > 0:
        return f"{hrs}h {mins:02d}m" if mins > 0 else f"{hrs}h 00m"
    return f"{mins}m"


def predict_bcd(time_decimal: float) -> Tuple[float, str, str]:
    """
    Calculate duration for B->C->D.
    Returns (duration_minutes, interval_label, formula_text).
    """
    for low, high, slope, intercept, label in BCD_INTERVALS:
        if low <= time_decimal <= high:
            duration = slope * time_decimal + intercept
            formula = f"{slope:.2f} * {time_decimal:.4f} + {intercept:.2f}"
            return duration, label, formula
            
    if time_decimal < 7.0:
        slope, intercept = BCD_INTERVALS[0][2], BCD_INTERVALS[0][3]
        return slope * time_decimal + intercept, BCD_INTERVALS[0][4], f"{slope:.2f} * {time_decimal:.4f} + {intercept:.2f}"
    else:
        slope, intercept = BCD_INTERVALS[-1][2], BCD_INTERVALS[-1][3]
        return slope * time_decimal + intercept, BCD_INTERVALS[-1][4], f"{slope:.2f} * {time_decimal:.4f} + {intercept:.2f}"


def predict_bce(time_decimal: float) -> Tuple[float, str, str]:
    """
    Calculate duration for B->C->E.
    Returns (duration_minutes, interval_label, formula_text).
    """
    for low, high, slope, intercept, label in BCE_INTERVALS:
        if low <= time_decimal <= high:
            duration = slope * time_decimal + intercept
            formula = f"{slope:.2f} * {time_decimal:.4f} + {intercept:.2f}"
            return duration, label, formula
            
    if time_decimal < 7.0:
        slope, intercept = BCE_INTERVALS[0][2], BCE_INTERVALS[0][3]
        return slope * time_decimal + intercept, BCE_INTERVALS[0][4], f"{slope:.2f} * {time_decimal:.4f} + {intercept:.2f}"
    else:
        slope, intercept = BCE_INTERVALS[-1][2], BCE_INTERVALS[-1][3]
        return slope * time_decimal + intercept, BCE_INTERVALS[-1][4], f"{slope:.2f} * {time_decimal:.4f} + {intercept:.2f}"


def predict_acd(x: float) -> Tuple[float, str, str]:
    """
    Calculate duration for A->C->D using the 2-sigmoid continuous equation:
    f(x) = 141.208171028210 + (-1.857763594676)x
     + (-44.149088388722) / (1 + exp(-(2.038913183625) * (x - 8.861364625860)))
     + (63.050602349853) / (1 + exp(-(1.672620676169) * (x - 14.980186722198)))
    """
    base = 141.208171028210
    slope = -1.857763594676
    z1 = -(2.038913183625) * (x - 8.861364625860)
    z2 = -(1.672620676169) * (x - 14.980186722198)
    
    # Clip z to prevent float overflow
    z1_clipped = max(min(z1, 700.0), -700.0)
    z2_clipped = max(min(z2, 700.0), -700.0)
    
    sig1 = 1.0 / (1.0 + math.exp(z1_clipped))
    sig2 = 1.0 / (1.0 + math.exp(z2_clipped))
    
    duration = base + (slope * x) + (-44.149088388722 * sig1) + (63.050602349853 * sig2)
    formula = "141.21 - 1.86*x - 44.15*sigmoid_1(x) + 63.05*sigmoid_2(x)"
    return duration, "Continuous", formula


def predict_ace(x: float) -> Tuple[float, str, str]:
    """
    Calculate duration for A->C->E:
    f(x) = 98 min (constant)
    """
    return 98.0, "Constant", "98.00 min"


def evaluate_all_routes(hour: int, minute: int) -> Dict[str, Any]:
    """
    Validate departure time and evaluate all four routes.
    Computes durations, identifies the fastest route, and calculates the exact time saved.
    """
    if not (0 <= minute <= 59):
        raise ValueError(f"Minute must be between 00 and 59. Received: {minute}")

    time_decimal = time_to_decimal(hour, minute)

    if time_decimal < MIN_TIME or time_decimal > MAX_TIME:
        raise ValueError(
            f"Departure time {hour:02d}:{minute:02d} is outside the allowed operating hours. "
            f"The only possible hours are between 07:00 and 17:00."
        )

    # Predictions
    dur_acd, interval_acd, formula_acd = predict_acd(time_decimal)
    dur_ace, interval_ace, formula_ace = predict_ace(time_decimal)
    dur_bcd, interval_bcd, formula_bcd = predict_bcd(time_decimal)
    dur_bce, interval_bce, formula_bce = predict_bce(time_decimal)

    raw_routes = [
        {
            "route": "A->C->D",
            "duration": dur_acd,
            "interval": interval_acd,
            "formula": formula_acd,
            "description": "Origin A via C to D (Sigmoidal non-linear model)"
        },
        {
            "route": "A->C->E",
            "duration": dur_ace,
            "interval": interval_ace,
            "formula": formula_ace,
            "description": "Origin A via C to E (Constant time model)"
        },
        {
            "route": "B->C->D",
            "duration": dur_bcd,
            "interval": interval_bcd,
            "formula": formula_bcd,
            "description": "Origin B via C to D (Piecewise linear model)"
        },
        {
            "route": "B->C->E",
            "duration": dur_bce,
            "interval": interval_bce,
            "formula": formula_bce,
            "description": "Origin B via C to E (Piecewise linear model)"
        }
    ]

    # Find best route (minimum duration) and worst route (maximum duration)
    best_item = min(raw_routes, key=lambda r: r["duration"])
    worst_item = max(raw_routes, key=lambda r: r["duration"])
    best_duration = best_item["duration"]
    worst_duration = worst_item["duration"]
    avg_duration = sum(r["duration"] for r in raw_routes) / len(raw_routes)

    # Departure & estimated arrival times
    dep_str = f"{hour:02d}:{minute:02d}"
    
    # Calculate arrival time for best route
    arr_total_minutes = (hour * 60 + minute) + round(best_duration)
    arr_hour = (arr_total_minutes // 60) % 24
    arr_min = arr_total_minutes % 60
    best_arr_str = f"{arr_hour:02d}:{arr_min:02d}"

    # Build enriched routes list with time savings vs best
    routes_evaluated = []
    savings_breakdown = {}

    for r in sorted(raw_routes, key=lambda x: x["duration"]):
        time_diff = r["duration"] - best_duration
        is_best = (r["route"] == best_item["route"])
        
        # Calculate specific arrival time for each route
        r_arr_tot = (hour * 60 + minute) + round(r["duration"])
        r_arr_h = (r_arr_tot // 60) % 24
        r_arr_m = r_arr_tot % 60
        r_arr_str = f"{r_arr_h:02d}:{r_arr_m:02d}"

        pct_saved = (time_diff / r["duration"] * 100.0) if r["duration"] > 0 else 0.0

        route_info = {
            "route": r["route"],
            "duration_min": round(r["duration"], 2),
            "duration_formatted": format_minutes(r["duration"]),
            "arrival_time": r_arr_str,
            "time_saved_vs_this_route": round(time_diff, 2),
            "time_saved_formatted": format_minutes(time_diff) if time_diff > 0 else "0m (Fastest)",
            "savings_percentage": round(pct_saved, 1),
            "is_best": is_best,
            "interval": r["interval"],
            "formula": r["formula"],
            "description": r["description"]
        }
        routes_evaluated.append(route_info)
        
        if not is_best:
            savings_breakdown[r["route"]] = {
                "saved_minutes": round(time_diff, 2),
                "saved_formatted": format_minutes(time_diff),
                "saved_pct": round(pct_saved, 1)
            }

    return {
        "departure_time": dep_str,
        "departure_hour": hour,
        "departure_minute": minute,
        "departure_decimal": round(time_decimal, 4),
        "best_route": best_item["route"],
        "best_duration_min": round(best_duration, 2),
        "best_duration_formatted": format_minutes(best_duration),
        "best_arrival_time": best_arr_str,
        "worst_route": worst_item["route"],
        "worst_duration_min": round(worst_duration, 2),
        "worst_duration_formatted": format_minutes(worst_duration),
        "max_time_saved_min": round(worst_duration - best_duration, 2),
        "max_time_saved_formatted": format_minutes(worst_duration - best_duration),
        "avg_duration_min": round(avg_duration, 2),
        "avg_time_saved_min": round(avg_duration - best_duration, 2),
        "avg_time_saved_formatted": format_minutes(avg_duration - best_duration),
        "routes": routes_evaluated,
        "savings_breakdown": savings_breakdown
    }


def get_hourly_comparison_profile(step_minutes: int = 15) -> List[Dict[str, Any]]:
    """
    Generate predictions across the full operating day (07:00 to 17:00)
    for chart visualizations.
    """
    profile = []
    total_steps = int((MAX_TIME - MIN_TIME) * 60 / step_minutes) + 1
    
    for step in range(total_steps):
        current_minute_offset = step * step_minutes
        t_dec = MIN_TIME + (current_minute_offset / 60.0)
        if t_dec > MAX_TIME:
            break
            
        hrs = int(t_dec)
        mins = int(round((t_dec - hrs) * 60))
        if mins >= 60:
            hrs += 1
            mins = 0
            
        acd, _, _ = predict_acd(t_dec)
        ace, _, _ = predict_ace(t_dec)
        bcd, _, _ = predict_bcd(t_dec)
        bce, _, _ = predict_bce(t_dec)
        
        candidates = {"A->C->D": acd, "A->C->E": ace, "B->C->D": bcd, "B->C->E": bce}
        best_name = min(candidates, key=candidates.get)
        
        profile.append({
            "time_label": f"{hrs:02d}:{mins:02d}",
            "time_decimal": round(t_dec, 4),
            "A->C->D": round(acd, 2),
            "A->C->E": round(ace, 2),
            "B->C->D": round(bcd, 2),
            "B->C->E": round(bce, 2),
            "best_route": best_name,
            "best_duration": round(candidates[best_name], 2)
        })
        
    return profile
