import math
from flask import Flask
from flask import request

app = Flask(__name__)

# Linear models for B->C->D: (low_hour, high_hour, slope, intercept)
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
    (7.00, 7.25, -36.30, 367.10),
    (7.25, 8.25, -67.64, 651.50),
    (8.25, 9.25, -80.06, 811.65),
    (9.25, 10.25, -79.88, 872.11),
    (10.25, 11.25, -60.12, 728.30),
    (11.25, 12.25, -59.07, 776.71),
    (12.25, 13.25, -63.92, 897.85),
    (13.25, 14.25, -47.59, 738.65),
    (14.25, 15.25, -34.79, 614.78),
    (15.25, 16.25, -43.84, 812.27),
    (16.25, 17.25, -63.60, 1194.87)
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
    (7.00, 7.25, -64.84, 543.20),
    (7.25, 8.25, -57.99, 552.48),
    (8.25, 9.25, -60.24, 630.26),
    (9.25, 10.25, -59.41, 682.54),
    (10.25, 11.25, -58.36, 731.04),
    (11.25, 12.25, -63.81, 852.59),
    (12.25, 13.25, -60.75, 876.87),
    (13.25, 14.25, -59.25, 916.35),
    (14.25, 15.25, -57.37, 949.71),
    (15.25, 16.25, -58.66, 1027.28),
    (16.25, 17.25, -58.89, 1090.40)
]


def predict_bcd(time_decimal: float) -> float:
    """Calculate duration in minutes for Route B->C->D."""
    for low, high, slope, intercept in BCD_INTERVALS:
        if low <= time_decimal <= high:
            return slope * time_decimal + intercept
    if time_decimal < 7.00:
        return BCD_INTERVALS[0][2] * time_decimal + BCD_INTERVALS[0][3]
    return BCD_INTERVALS[-1][2] * time_decimal + BCD_INTERVALS[-1][3]


def predict_bce(time_decimal: float) -> float:
    """Calculate duration in minutes for Route B->C->E."""
    for low, high, slope, intercept in BCE_INTERVALS:
        if low <= time_decimal <= high:
            return slope * time_decimal + intercept
    if time_decimal < 7.00:
        return BCE_INTERVALS[0][2] * time_decimal + BCE_INTERVALS[0][3]
    return BCE_INTERVALS[-1][2] * time_decimal + BCE_INTERVALS[-1][3]


def predict_acd(time_decimal: float) -> float:
    """
    Calculate duration in minutes for Route A->C->D using the 2-sigmoid continuous equation:
    f(x) = 141.208171028210 + (-1.857763594676)x
     + (-44.149088388722) / (1 + exp(-(2.038913183625) * (x - 8.861364625860)))
     + (63.050602349853) / (1 + exp(-(1.672620676169) * (x - 14.980186722198)))
    """
    z1 = -(2.038913183625) * (time_decimal - 8.861364625860)
    z2 = -(1.672620676169) * (time_decimal - 14.980186722198)
    sig1 = 1.0 / (1.0 + math.exp(max(min(z1, 700.0), -700.0)))
    sig2 = 1.0 / (1.0 + math.exp(max(min(z2, 700.0), -700.0)))
    return 141.208171028210 + (-1.857763594676) * time_decimal + (-44.149088388722) * sig1 + (63.050602349853) * sig2


def predict_ace(time_decimal: float) -> float:
    """Calculate duration in minutes for Route A->C->E (constant 98 min)."""
    return 98.0


def get_the_best_route_as_a_text_informatic(dep_hour, dep_min):
    # Safely parse hour and minute
    try:
        h = int(dep_hour)
    except (ValueError, TypeError):
        h = 7

    try:
        m = int(dep_min) if dep_min not in (None, "") else 0
    except (ValueError, TypeError):
        m = 0

    time_decimal = h + (m / 60.0)

    # Compute durations across all routes using the calculated models
    durations = {
        "A->C->D": predict_acd(time_decimal),
        "A->C->E": predict_ace(time_decimal),
        "B->C->D": predict_bcd(time_decimal),
        "B->C->E": predict_bce(time_decimal),
    }

    # Find the best route (shortest estimated travel time)
    best_road = min(durations, key=durations.get)
    est_travel_time = round(durations[best_road], 1)

    # Calculate average time saved compared to random selection
    avg_duration = sum(durations.values()) / len(durations)
    avg_saved = round(avg_duration - est_travel_time, 1)

    # Detailed breakdown for all routes
    breakdown_items = []
    for road in ["A->C->D", "A->C->E", "B->C->D", "B->C->E"]:
        dur = durations[road]
        if road == best_road:
            breakdown_items.append(f"<li><strong>{road}:</strong> {dur:.1f} minutes <em>(Fastest Route)</em></li>")
        else:
            saved = dur - est_travel_time
            breakdown_items.append(f"<li><strong>{road}:</strong> {dur:.1f} minutes (+{saved:.1f} min longer)</li>")
    breakdown_html = "\n        ".join(breakdown_items)

    out = f"""
    <p>
    Departure time: {h:02d}:{m:02d} <br> 
    Best travel route: {best_road} <br> 
    Estimated travel time of {est_travel_time} minutes. </p> 
    
    <div style="margin-top: 15px; padding: 12px; background: #f8fafc; border-left: 4px solid #0284c7; max-width: 500px;">
        <p style="margin: 0 0 8px 0; font-weight: bold; color: #0f172a;">All Routes Comparison:</p>
        <ul style="margin: 0; padding-left: 20px; line-height: 1.6;">
        {breakdown_html}
        </ul>
        <p style="margin: 10px 0 0 0; color: #0369a1; font-size: 0.95em;">
            Selecting <strong>{best_road}</strong> saves <strong>{avg_saved} min</strong> on average compared to choosing randomly!
        </p>
    </div>

    <p><a href="/">Back</a></p>
    """

    return out


@app.route('/')
def get_departure_time():
    return """
    	<h3>Knut Knut Transport AS</h3>
        <form action="/get_best_route" method="get">
            <label for="hour">Hour:</label>
            <select name="hour" id="hour">
                <option value="06">06</option>
                <option value="07" selected>07</option>
                <option value="08">08</option>
                <option value="09">09</option>
                <option value="10">10</option>
                <option value="11">11</option>
                <option value="12">12</option>
                <option value="13">13</option>
                <option value="14">14</option>
                <option value="15">15</option>
                <option value="16">16</option>     
                <option value="17">17</option>     
            </select>
            
            <label for="mins">Mins:</label>
            <input type="text" name="mins" size="2" placeholder="00"/>
            <input type="submit" value="Find Best Route">
        </form>
    """


@app.route("/get_best_route")
def get_route():
    departure_h = request.args.get('hour')
    departure_m = request.args.get('mins')

    route_info = get_the_best_route_as_a_text_informatic(departure_h, departure_m)
    return route_info


if __name__ == '__main__':
    print("<starting>")
    app.run()
    print("<done>")

