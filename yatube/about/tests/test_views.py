from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class AboutViewsTests(TestCase):
    """Тесты обработчиков страниц."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

    def test_about_page_accessible_by_name(self):
        """URL, генерируемый при помощи имени, доступен."""
        names_of_about = (reverse('about:author'), reverse('about:tech'))
        for name in names_of_about:
            with self.subTest(Имя=name):
                response = AboutViewsTests.guest_client.get(name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_names_templates(self):
        """Тест использования view-функциями ожидаемых HTML-шаблонов."""
        names_templates = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html'
        }
        for name, template in names_templates.items():
            with self.subTest(Имя=name):
                response = AboutViewsTests.guest_client.get(name)
                self.assertTemplateUsed(response, template)
