import json
import threading
import unittest
import urllib.error
import urllib.request

from app.server import create_server


class WebAppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = create_server("127.0.0.1", 0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def test_root_serves_landing_page_and_security_headers(self):
        with urllib.request.urlopen(f"{self.base_url}/", timeout=2) as response:
            body = response.read().decode("utf-8")
            self.assertEqual(response.status, 200)
            self.assertIn("Dockerized Web App", body)
            self.assertIn("X-Content-Type-Options", response.headers)
            self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
            self.assertEqual(response.headers["X-Frame-Options"], "DENY")
            self.assertIn("Content-Security-Policy", response.headers)

    def test_health_returns_json_status(self):
        with urllib.request.urlopen(f"{self.base_url}/health", timeout=2) as response:
            body = json.loads(response.read().decode("utf-8"))
            self.assertEqual(response.status, 200)
            self.assertEqual(body, {"status": "UP", "service": "dockerwebapp"})
            self.assertIn("application/json", response.headers["Content-Type"])

    def test_unknown_path_is_not_found(self):
        with self.assertRaises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(f"{self.base_url}/not-a-real-route", timeout=2)
        self.assertEqual(caught.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
