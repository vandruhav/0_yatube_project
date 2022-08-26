from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group, User


class PaginatorViewsTests(TestCase):
    """Тесты паджинатора."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='leo')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(title='Название группы',
                                         slug='address',
                                         description='Описание группы')
        cls.post = (
            Post(text='Текст поста' + str(i), author=cls.user, group=cls.group)
            for i in range(settings.COUNT_OF_CREATE_POSTS)
        )
        Post.objects.bulk_create(cls.post, settings.COUNT_OF_CREATE_POSTS)

    def test_first_page_contains_ten_records(self):
        names = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'address'}),
            reverse('posts:profile', kwargs={'username': 'leo'})
        )
        for name in names:
            with self.subTest(Имя=name):
                response = self.authorized_client.get(name)
                self.assertEqual(len(response.context['page_obj']),
                                 settings.NUM_POSTS)

    def test_second_page_contains_three_records(self):
        names = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'address'}),
            reverse('posts:profile', kwargs={'username': 'leo'})
        )
        for name in names:
            with self.subTest(Имя=name):
                response = self.authorized_client.get(
                    reverse('posts:index') + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']),
                    settings.COUNT_OF_CREATE_POSTS - settings.NUM_POSTS
                )
