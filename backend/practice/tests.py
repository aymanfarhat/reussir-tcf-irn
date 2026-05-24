from django.test import SimpleTestCase


class HomeViewTests(SimpleTestCase):
    def test_home_page_requires_login(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])
