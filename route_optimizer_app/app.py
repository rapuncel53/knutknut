from flask import Flask, render_template, request, jsonify, redirect, url_for
from route_models import (
    evaluate_all_routes,
    get_hourly_comparison_profile,
    MIN_TIME,
    MAX_TIME
)

app = Flask(__name__)


def get_the_best_route_as_a_text_informatic(dep_hour: int, dep_min: int) -> str:
    """
    Implements the requested Knut Knut Transport informative text output,
    enhanced with exact mathematical calculations and time savings vs other routes.
    """
    evaluation = evaluate_all_routes(dep_hour, dep_min)
    
    savings_items = []
    for r in evaluation["routes"]:
        if not r["is_best"]:
            savings_items.append(
                f"<li>Saved vs <strong>{r['route']}</strong>: {r['time_saved_formatted']} ({round(r['savings_percentage'])}%)</li>"
            )
            
    savings_html = "".join(savings_items)

    out = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 30px auto; padding: 25px; border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
        <h2 style="color: #1e3a8a; margin-top: 0;">Knut Knut Transport AS</h2>
        <p style="font-size: 16px; line-height: 1.6;">
            <strong>Departure time:</strong> {dep_hour:02d}:{dep_min:02d} <br>
            <strong>Best travel route:</strong> <span style="color: #16a34a; font-weight: bold;">{evaluation['best_route']}</span> <br>
            <strong>Estimated travel time:</strong> {evaluation['best_duration_formatted']} <br>
            <strong>Estimated arrival time:</strong> {evaluation['best_arrival_time']}
        </p>
        
        <h3 style="color: #334155; font-size: 15px; border-bottom: 2px solid #e2e8f0; padding-bottom: 5px;">Time Saved Compared to Other Routes:</h3>
        <ul style="line-height: 1.8; color: #475569;">
            {savings_html}
        </ul>
        <p style="background: #ecfdf5; border-left: 4px solid #10b981; padding: 10px; color: #065f46; font-size: 14px;">
            Selecting <strong>{evaluation['best_route']}</strong> saves <strong>{evaluation['avg_time_saved_formatted']}</strong> on average compared to choosing at random!
        </p>
        <p><a href="/" style="display: inline-block; background: #2563eb; color: white; text-decoration: none; padding: 8px 16px; border-radius: 4px; font-weight: bold;">Back to Dashboard</a></p>
    </div>
    """
    return out


@app.route("/")
def index():
    """Main dashboard page."""
    # Read query parameters or default to 08:00
    hour_str = request.args.get("hour", "08")
    minute_str = request.args.get("mins", request.args.get("minute", "00"))

    error_message = None
    evaluation = None

    try:
        hour = int(hour_str)
        minute = int(minute_str)
        evaluation = evaluate_all_routes(hour, minute)
    except ValueError as e:
        error_message = str(e)
        # Fallback to default for rendering the charts
        try:
            evaluation = evaluate_all_routes(8, 0)
        except Exception:
            pass

    # Hourly profile for day-long overview charts
    hourly_profile = get_hourly_comparison_profile(step_minutes=15)

    valid_hours = [f"{h:02d}" for h in range(7, 18)]
    common_minutes = [f"{m:02d}" for m in [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]]

    return render_template(
        "index.html",
        evaluation=evaluation,
        error_message=error_message,
        current_hour=f"{int(hour_str):02d}" if hour_str.isdigit() else "08",
        current_minute=f"{int(minute_str):02d}" if minute_str.isdigit() else "00",
        valid_hours=valid_hours,
        common_minutes=common_minutes,
        hourly_profile=hourly_profile
    )


@app.route("/get_best_route", methods=["GET"])
def get_route():
    """
    Endpoint matching the knut_knut_app.py specification.
    Supports either HTML text or JSON via query param ?format=json
    """
    hour_str = request.args.get("hour", "08")
    minute_str = request.args.get("mins", request.args.get("minute", "00"))
    out_format = request.args.get("format", "html").lower()

    try:
        hour = int(hour_str)
        minute = int(minute_str)
    except ValueError:
        return "<p style='color: red;'>Invalid hour or minute parameter. Must be integers.</p><p><a href='/'>Back</a></p>", 400

    try:
        if out_format == "json":
            res = evaluate_all_routes(hour, minute)
            return jsonify(res)
        
        # Default HTML informative card
        return get_the_best_route_as_a_text_informatic(hour, minute)
    except ValueError as e:
        return f"""
        <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 30px auto; padding: 20px; border: 1px solid #f87171; background: #fef2f2; border-radius: 8px;">
            <h3 style="color: #b91c1c; margin-top: 0;">Input Error</h3>
            <p style="color: #7f1d1d;">{str(e)}</p>
            <p><a href="/" style="color: #2563eb;">Back to Planner</a></p>
        </div>
        """, 400


@app.route("/api/predict", methods=["GET"])
def api_predict():
    """REST API endpoint to get route predictions and savings in JSON format."""
    hour_str = request.args.get("hour")
    minute_str = request.args.get("minute", request.args.get("mins", "00"))

    if hour_str is None:
        return jsonify({"error": "Missing 'hour' query parameter (e.g. ?hour=8&minute=30)"}), 400

    try:
        hour = int(hour_str)
        minute = int(minute_str)
        result = evaluate_all_routes(hour, minute)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/profile", methods=["GET"])
def api_profile():
    """REST API endpoint returning 15-minute resolution curve across the full day."""
    step = request.args.get("step", 15)
    try:
        step_min = max(5, min(60, int(step)))
    except ValueError:
        step_min = 15
    profile = get_hourly_comparison_profile(step_minutes=step_min)
    return jsonify({"profile": profile})


if __name__ == "__main__":
    print("<starting Knut Knut Route Optimizer App>")
    print("Listening at http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
