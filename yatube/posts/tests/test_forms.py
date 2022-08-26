import shutil
import tempfile

from django.conf import settings
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import User, Group, Post, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CreateFormTests(TestCase):
    """Тесты форм."""

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
        cls.new_group = Group.objects.create(title='Название',
                                             slug='addr',
                                             description='Описание')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized1_client = Client()
        self.authorized1_client.force_login(CreateFormTests.user)
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
                                        author=CreateFormTests.user,
                                        group=CreateFormTests.group)

    def test_create_post(self):
        """Тест создания записи."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст 2',
            'group': CreateFormTests.group.id,
            'image': self.image
        }
        self.authorized_client.post(reverse('posts:post_create'),
                                    data=form_data, follow=True)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(text='Текст 2', author=CreateFormTests.user.id,
                                group=CreateFormTests.group.id,
                                image=f'posts/{self.image.name}').exists()
        )

    def test_edit_post(self):
        """Тест изменения записи."""
        form_data = {
            'text': 'Текст 3',
            'group': CreateFormTests.new_group.id
        }
        CreateFormTests.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(text='Текст 3', author=CreateFormTests.user.id,
                                group=CreateFormTests.new_group.id,
                                pub_date=self.post.pub_date).exists()
        )

    def test_POST_from_guest_to_edit(self):
        """Тест POSTa неавторизованного пользователя на редактирование."""
        form_data = {
            'text': 'Текст 4',
            'group': CreateFormTests.new_group.id
        }
        response = CreateFormTests.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(id=self.post.id,
                                text=self.post.text,
                                pub_date=self.post.pub_date,
                                author=CreateFormTests.user.id,
                                group=CreateFormTests.group.id).exists()
        )
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{self.post.id}/edit/'
        )

    def test_POST_from_guest_to_create(self):
        """Тест POSTa неавторизованного пользователя на создание."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст 5',
            'group': CreateFormTests.group.id
        }
        response = CreateFormTests.guest_client.post(
            reverse('posts:post_create'), data=form_data, follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFalse(
            Post.objects.filter(text='Текст 5', author=CreateFormTests.user.id,
                                group=CreateFormTests.group.id).exists()
        )
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_POST_from_authorized_but_not_author_to_edit(self):
        """Тест POSTa авторизованного пользователя, но не автора."""
        form_data = {
            'text': 'Текст 6',
            'group': CreateFormTests.new_group.id
        }
        response = CreateFormTests.another_authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(id=self.post.id,
                                text=self.post.text,
                                pub_date=self.post.pub_date,
                                author=CreateFormTests.user.id,
                                group=CreateFormTests.group.id).exists()
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )

    def test_create_new_post_without_group(self):
        """Тест создания поста без группы."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст 7'
        }
        CreateFormTests.authorized_client.post(reverse('posts:post_create'),
                                               data=form_data, follow=True)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(text='Текст 7',
                                author=CreateFormTests.user).exists()
        )

    def test_create_new_comment(self):
        """Тест: после успешной отправки комментарий появляется в БД."""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Comment'
        }
        CreateFormTests.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(Comment.objects.filter(post=self.post,
                                               author=CreateFormTests.user,
                                               text='Comment').exists())

    def test_non_authorized_no_comment(self):
        """Тест: неавторизованный пользователь не может оставить
        комментарий."""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Comment'
        }
        CreateFormTests.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comments_count)
