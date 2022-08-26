from http import HTTPStatus

from django.test import TestCase, Client

from ..models import User, Group, Post


class URLsTests(TestCase):
    """Тесты адресов страниц."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.group = Group.objects.create(title='Название группы',
                                         slug='address',
                                         description='Описание группы')
        cls.user = User.objects.create_user(username='leo')
        cls.post = Post.objects.create(text='Текст поста', author=cls.user)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.another_user = User.objects.create_user(username='tiger')
        cls.another_authorized_client = Client()
        cls.another_authorized_client.force_login(cls.another_user)

    def test_url_exists_for_guest(self):
        """Тест доступности страниц для неавторизованного пользователя."""
        urls_of_posts = (
            '/',
            f'/group/{URLsTests.group.slug}/',
            f'/profile/{URLsTests.user.username}/',
            f'/posts/{URLsTests.post.id}/'
        )
        for url in urls_of_posts:
            with self.subTest(Страница=url):
                response = URLsTests.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_exists_for_authorized(self):
        """Тест доступности страниц для авторизованного пользователя."""
        urls_of_posts = {
            '/create/': HTTPStatus.OK,
            f'/posts/{URLsTests.post.id}/edit/': HTTPStatus.OK,
            f'/posts/{URLsTests.post.id}/comment/': HTTPStatus.FOUND,
            '/follow/': HTTPStatus.OK,
        }
        for url, status in urls_of_posts.items():
            with self.subTest(Страница=url):
                response = URLsTests.authorized_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_url_redirect_for_guest(self):
        """Тест перенаправления для неавторизованного пользователя."""
        urls_with_redirect = {
            '/create/': '/auth/login/?next=/create/',
            f'/posts/{URLsTests.post.id}/edit/':
                f'/auth/login/?next=/posts/{URLsTests.post.id}/edit/',
            f'/posts/{URLsTests.post.id}/comment/':
                f'/auth/login/?next=/posts/{URLsTests.post.id}/comment/',
            '/follow/': '/auth/login/?next=/follow/'
        }
        for url, url_to_redirect in urls_with_redirect.items():
            with self.subTest(Страница=url):
                response = URLsTests.guest_client.get(url, follow=True)
                self.assertRedirects(response, url_to_redirect)

    def test_urls_templates(self):
        """Тест шаблонов страниц."""
        urls_templates = {
            '/': 'posts/index.html',
            f'/group/{URLsTests.group.slug}/': 'posts/group_list.html',
            f'/profile/{URLsTests.user.username}/': 'posts/profile.html',
            f'/posts/{URLsTests.post.id}/': 'posts/post_detail.html',
            f'/posts/{URLsTests.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html'
        }
        for url, template in urls_templates.items():
            with self.subTest(Страница=url):
                response = URLsTests.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_non_existing_url(self):
        """Проверка доступности несуществующей страницы и её шаблона."""
        response = URLsTests.guest_client.get('/1/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_redirect_authorized_but_not_author(self):
        """Тест редиректа авторизованного пользователя, но не автора."""
        response = URLsTests.another_authorized_client.get(
            f'/posts/{URLsTests.post.id}/edit/',
            follow=True
        )
        self.assertRedirects(response, f'/posts/{URLsTests.post.id}/')
