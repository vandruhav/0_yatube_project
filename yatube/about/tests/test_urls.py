from http import HTTPStatus

from django.test import TestCase, Client


class AboutURLsTests(TestCase):
    """Тесты адресов страниц."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

    def test_about_url_exists_for_guest(self):
        """Тест доступности страниц для неавторизованного пользователя."""
        urls_of_about = ('/about/author/', '/about/tech/')
        for url in urls_of_about:
            with self.subTest(Страница=url):
                response = AboutURLsTests.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_urls_templates(self):
        """Тест шаблонов страниц."""
        urls_templates = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }
        for url, template in urls_templates.items():
            with self.subTest(Страница=url):
                response = AboutURLsTests.guest_client.get(url)
                self.assertTemplateUsed(response, template)
