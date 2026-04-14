from django.test import TestCase
from django.urls import reverse


class URLResolutionTests(TestCase):

    def test_home_page(self):
        response = self.client.get(reverse('pages:home'))
        self.assertEqual(response.status_code, 200)

    def test_about_page(self):
        response = self.client.get(reverse('pages:about'))
        self.assertEqual(response.status_code, 200)

    def test_services_page(self):
        response = self.client.get(reverse('pages:services'))
        self.assertEqual(response.status_code, 200)

    def test_contact_page(self):
        response = self.client.get(reverse('contact:inquiry'))
        self.assertEqual(response.status_code, 200)

    def test_news_page(self):
        response = self.client.get(reverse('news:list'))
        self.assertEqual(response.status_code, 200)

    def test_products_page(self):
        response = self.client.get(reverse('products:list'))
        self.assertEqual(response.status_code, 200)

    def test_admin_requires_login(self):
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 302)
