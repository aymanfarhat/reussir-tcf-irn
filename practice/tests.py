from django.test import SimpleTestCase


class HomeViewTests(SimpleTestCase):
    def test_home_page_loads(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TCF IRN practice app")
