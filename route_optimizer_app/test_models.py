import unittest
import math
from route_models import (
    time_to_decimal,
    predict_bcd,
    predict_bce,
    predict_acd,
    predict_ace,
    evaluate_all_routes,
    get_hourly_comparison_profile
)


class TestRouteModels(unittest.TestCase):

    def test_time_to_decimal(self):
        self.assertAlmostEqual(time_to_decimal(7, 0), 7.0)
        self.assertAlmostEqual(time_to_decimal(7, 15), 7.25)
        self.assertAlmostEqual(time_to_decimal(8, 30), 8.5)
        self.assertAlmostEqual(time_to_decimal(17, 0), 17.0)

    def test_ace_constant(self):
        for h in range(7, 18):
            dur, label, formula = predict_ace(float(h))
            self.assertEqual(dur, 98.0)
            self.assertEqual(label, "Constant")

    def test_bcd_intervals(self):
        # 07:00 (t=7.0): -36.30 * 7.0 + 367.10 = 113.00
        dur, label, _ = predict_bcd(7.0)
        self.assertAlmostEqual(dur, 113.00, places=2)
        self.assertEqual(label, "07:00-07:15")

        # 07:15 (t=7.25): -36.30 * 7.25 + 367.10 = 103.925
        dur, label, _ = predict_bcd(7.25)
        self.assertAlmostEqual(dur, 103.925, places=2)
        self.assertEqual(label, "07:00-07:15")

        # 07:16 (t=7.266667): -67.64 * (7 + 16/60) + 651.50
        t_716 = 7.0 + 16.0 / 60.0
        expected_716 = -67.64 * t_716 + 651.50
        dur, label, _ = predict_bcd(t_716)
        self.assertAlmostEqual(dur, expected_716, places=2)
        self.assertEqual(label, "07:16-08:15")

        # 17:00 (t=17.0): -63.60 * 17.0 + 1194.87 = 113.67
        dur, label, _ = predict_bcd(17.0)
        self.assertAlmostEqual(dur, 113.67, places=2)
        self.assertEqual(label, "16:16-17:15")

    def test_bce_intervals(self):
        # 07:00 (t=7.0): -64.84 * 7.0 + 543.20 = 89.32
        dur, label, _ = predict_bce(7.0)
        self.assertAlmostEqual(dur, 89.32, places=2)
        self.assertEqual(label, "07:00-07:15")

        # 12:00 (t=12.0): -63.81 * 12.0 + 852.59 = 86.87
        dur, label, _ = predict_bce(12.0)
        self.assertAlmostEqual(dur, 86.87, places=2)
        self.assertEqual(label, "11:16-12:15")

        # 17:00 (t=17.0): -58.89 * 17.0 + 1090.40 = 89.27
        dur, label, _ = predict_bce(17.0)
        self.assertAlmostEqual(dur, 89.27, places=2)
        self.assertEqual(label, "16:16-17:15")

    def test_acd_equation(self):
        # Test A->C->D at 07:00 (t=7.0)
        # f(7) = 141.208171028210 - 1.857763594676*7 - 44.149088388722/(1 + exp(-2.038913183625*(7 - 8.861364625860))) + 63.050602349853/(1 + exp(-1.672620676169*(7 - 14.980186722198)))
        dur, label, _ = predict_acd(7.0)
        self.assertTrue(126.0 < dur < 128.0)
        self.assertEqual(label, "Continuous")

    def test_evaluate_all_routes_structure(self):
        res = evaluate_all_routes(8, 30)
        self.assertEqual(res["departure_time"], "08:30")
        self.assertIn(res["best_route"], ["A->C->D", "A->C->E", "B->C->D", "B->C->E"])
        self.assertEqual(len(res["routes"]), 4)
        
        # Best route must have time saved = 0
        best_found = False
        for r in res["routes"]:
            if r["is_best"]:
                best_found = True
                self.assertEqual(r["time_saved_vs_this_route"], 0.0)
            else:
                self.assertGreaterEqual(r["time_saved_vs_this_route"], 0.0)
        self.assertTrue(best_found)
        
        # Max time saved should equal worst_duration - best_duration
        self.assertAlmostEqual(res["max_time_saved_min"], res["worst_duration_min"] - res["best_duration_min"], places=2)
        
        # Average time saved should equal avg_duration - best_duration
        self.assertAlmostEqual(res["avg_time_saved_min"], res["avg_duration_min"] - res["best_duration_min"], places=2)

    def test_boundary_validation(self):
        # Valid boundaries: 07:00 and 17:00
        res_7 = evaluate_all_routes(7, 0)
        self.assertEqual(res_7["departure_time"], "07:00")
        res_17 = evaluate_all_routes(17, 0)
        self.assertEqual(res_17["departure_time"], "17:00")

        # Invalid: 06:59
        with self.assertRaises(ValueError):
            evaluate_all_routes(6, 59)

        # Invalid: 17:01
        with self.assertRaises(ValueError):
            evaluate_all_routes(17, 1)

        # Invalid: minute 60
        with self.assertRaises(ValueError):
            evaluate_all_routes(8, 60)

    def test_hourly_profile(self):
        profile = get_hourly_comparison_profile(step_minutes=30)
        self.assertGreater(len(profile), 0)
        self.assertEqual(profile[0]["time_label"], "07:00")
        self.assertEqual(profile[-1]["time_label"], "17:00")


if __name__ == '__main__':
    unittest.main()
