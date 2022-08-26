import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.db import IntegrityError
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import User, Group, Post, Follow

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ViewsTests(TestCase):
    """Тесты обработчиков страниц."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='leo')
        cls.another_user = User.objects.create_user(username='tiger')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.another_authorized_client = Client()
        cls.another_authorized_client.force_login(cls.another_user)
        cls.group = Group.objects.create(title='Название группы',
                                         slug='address',
                                         description='Описание группы')
        cls.group_another = Group.objects.create(title='Название',
                                                 slug='addr',
                                                 description='Описание')
        cls.another_post = Post.objects.create(text='Текст поста',
                                               author=cls.another_user,
                                               group=cls.group)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.name_image = 'posts/small.gif'
        self.image = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        self.post = Post.objects.create(text='Текст поста',
                                        author=ViewsTests.user,
                                        group=ViewsTests.group,
                                        image=self.image)

    def test_name_template(self):
        """Тест использования view-функциями ожидаемых HTML-шаблонов."""
        names_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': ViewsTests.group.slug}):
                        'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': ViewsTests.user.username}):
                        'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}):
                        'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
                'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:follow_index'): 'posts/follow.html'
        }
        for name, template in names_templates.items():
            with self.subTest(Имя=name):
                response = ViewsTests.authorized_client.get(name)
                self.assertTemplateUsed(response, template)

    def test_index_correct_context(self):
        """Тест передачи в шаблон index правильного контекста."""
        response = ViewsTests.authorized_client.get(reverse('posts:index'))
        first = response.context['page_obj'][0]
        self.assertEqual(first.id, self.post.id)
        self.assertEqual(first.text, self.post.text)
        self.assertEqual(first.author.username, self.post.author.username)
        self.assertEqual(first.group, self.post.group)
        self.assertEqual(first.image, self.post.image)

    def test_group_posts_correct_context(self):
        """Тест передачи в шаблон group_list правильного контекста."""
        response = ViewsTests.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': ViewsTests.group.slug})
        )
        self.assertEqual(response.context['group'], ViewsTests.group)
        first = response.context['page_obj'][0]
        self.assertEqual(first.id, self.post.id)
        self.assertEqual(first.text, self.post.text)
        self.assertEqual(first.author.username,
                         self.post.author.username)
        self.assertEqual(first.image, self.post.image)

    def test_profile_correct_context(self):
        """Тест передачи в шаблон profile правильного контекста."""
        response = ViewsTests.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': ViewsTests.user.username})
        )
        self.assertEqual(response.context['author'], ViewsTests.user)
        first = response.context['page_obj'][0]
        self.assertEqual(first.id, self.post.id)
        self.assertEqual(first.text, self.post.text)
        self.assertEqual(first.author.username,
                         self.post.author.username)
        self.assertEqual(first.image, self.post.image)

    def test_post_detail_correct_context(self):
        """Тест передачи в шаблон post_detail правильного контекста."""
        response = ViewsTests.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response.context.get('post').text,
                         self.post.text)
        self.assertEqual(response.context.get('post').pub_date,
                         self.post.pub_date)
        self.assertEqual(response.context.get('post').author,
                         self.post.author)
        self.assertEqual(response.context.get('post').group,
                         self.post.group)
        self.assertEqual(response.context.get('post').image,
                         self.post.image)

    def test_post_create_correct_context(self):
        """Тест передачи в шаблон create_post правильного контекста."""
        names = (
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for name in names:
            response = ViewsTests.authorized_client.get(name)
            for key, value in form_fields.items():
                with self.subTest(Поле=key):
                    form_field = response.context.get('form').fields.get(key)
                    self.assertIsInstance(form_field, value)

    def test_exist_is_edit(self):
        """Тест проверки is_edit."""
        response = ViewsTests.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        self.assertTrue(response.context['is_edit'])

    def test_cash_index(self):
        """Тест кэша главной страницы."""
        post = Post.objects.create(text='Test cash', author=ViewsTests.user)
        response_before = ViewsTests.guest_client.get(reverse('posts:index'))
        post.delete()
        response_after = ViewsTests.guest_client.get(reverse('posts:index'))
        self.assertEqual(response_before.content, response_after.content)
        cache.clear()
        response_after_2 = ViewsTests.guest_client.get(reverse('posts:index'))
        self.assertNotEqual(response_before.content, response_after_2.content)

    def test_create_follow_authorized(self):
        """Тест создания подписок авторизованным пользователем."""
        ViewsTests.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': ViewsTests.another_user.username}
                    )
        )
        self.assertTrue(Follow.objects.filter(author=ViewsTests.another_user,
                                              user=ViewsTests.user))

    def test_delete_follow_authorized(self):
        """Тест удаления подписок авторизованным пользователем."""
        ViewsTests.authorized_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': ViewsTests.another_user.username}
                    )
        )
        self.assertFalse(Follow.objects.filter(author=ViewsTests.another_user,
                                               user=ViewsTests.user))

    def test_new_post(self):
        """Тест новой записи пользователя появляется в ленте подписавшихся."""
        me = User.objects.create(username='me')
        ViewsTests.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': me.username}
                    )
        )
        new_post = Post.objects.create(author=me, text='Test 1')
        response = ViewsTests.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(new_post, response.context['page_obj'][0])
        response = ViewsTests.another_authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_self_follow(self):
        """Тест подписки на самого себя."""
        with self.assertRaisesMessage(IntegrityError, 'author_not_user'):
            Follow.objects.create(author=ViewsTests.user, user=ViewsTests.user)
