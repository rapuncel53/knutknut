import unittest
import json
from app import app


class TestFlaskEndpoints(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_index_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Knut Knut Transport AS', response.data)
        self.assertIn(b'Departure Time Planner', response.data)

    def test_index_with_query_params(self):
        response = self.client.get('/?hour=10&mins=15')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'B-&gt;C-&gt;D', response.data)

    def test_api_predict_success(self):
        response = self.client.get('/api/predict?hour=8&minute=30')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['departure_time'], '08:30')
        self.assertIn('best_route', data)
        self.assertIn('routes', data)
        self.assertIn('savings_breakdown', data)
        self.assertEqual(len(data['routes']), 4)

    def test_api_predict_out_of_bounds(self):
        # 06:45 is before 07:00
        response = self.client.get('/api/predict?hour=6&minute=45')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

        # 17:30 is after 17:00
        response2 = self.client.get('/api/predict?hour=17&minute=30')
        self.assertEqual(response2.status_code, 400)
        data2 = json.loads(response2.data)
        self.assertIn('error', data2)

    def test_get_best_route_assignment_endpoint(self):
        # Test original knut_knut_app endpoint
        response = self.client.get('/get_best_route?hour=09&mins=15')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Departure time:</strong> 09:15', response.data)
        self.assertIn(b'Best travel route:</strong>', response.data)
        self.assertIn(b'Time Saved Compared to Other Routes:', response.data)

    def test_get_best_route_json_format(self):
        response = self.client.get('/get_best_route?hour=12&mins=00&format=json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['departure_time'], '12:00')
        self.assertIn('best_route', data)

    def test_api_profile(self):
        response = self.client.get('/api/profile?step=30')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('profile', data)
        self.assertGreater(len(data['profile']), 0)


if __name__ == '__main__':
    unittest.main()
