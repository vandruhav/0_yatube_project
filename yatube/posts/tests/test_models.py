from django.test import TestCase
from django.conf import settings

from ..models import User, Group, Post, Comment, Follow


class GroupModelTest(TestCase):
    """Тесты модели Group."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(title='Название группы',
                                         slug='address',
                                         description='Описание группы')

    def test_models_have_correct_object_names(self):
        """Проверка работы __str__."""
        self.assertEqual(str(GroupModelTest.group), GroupModelTest.group.title)

    def test_verbose_and_help(self):
        """Проверка полей verbose_name и help_text."""
        verboses = {
            'title': 'Имя группы',
            'slug': 'Адрес группы',
            'description': 'Описание группы'
        }
        for field, value in verboses.items():
            with self.subTest(Поле=field):
                self.assertEqual(
                    GroupModelTest.group._meta.get_field(field).verbose_name,
                    value
                )


class PostModelTest(TestCase):
    """Тесты модели Post."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='leo')
        cls.post = Post.objects.create(text='Текст поста' * 2, author=cls.user)

    def test_models_have_correct_object_names(self):
        """Проверка работы __str__."""
        self.assertEqual(
            str(PostModelTest.post),
            PostModelTest.post.text[:settings.FIRST_SYMBOLS_OF_POST]
        )

    def test_verbose_and_help(self):
        """Проверка полей verbose_name и help_text."""
        verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор поста',
            'group': 'Группа',
            'image': 'Картинка'
        }
        for field, value in verboses.items():
            with self.subTest(Поле=field):
                self.assertEqual(
                    PostModelTest.post._meta.get_field(field).verbose_name,
                    value
                )
        helps = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост'
        }
        for field, value in helps.items():
            with self.subTest(Поле=field):
                self.assertEqual(
                    PostModelTest.post._meta.get_field(field).help_text,
                    value
                )


class CommentModelTest(TestCase):
    """Тесты модели Comment."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='leo')
        cls.post = Post.objects.create(text='Текст поста', author=cls.user)
        cls.comment = Comment.objects.create(post=cls.post, text='Комментарий',
                                             author=cls.user)

    def test_models_have_correct_object_names(self):
        """Проверка работы __str__."""
        self.assertEqual(
            str(CommentModelTest.comment),
            CommentModelTest.comment.text
        )

    def test_verbose_and_help(self):
        """Проверка полей verbose_name и help_text."""
        verboses = {
            'post': 'Пост комментария',
            'author': 'Автор комментария',
            'text': 'Текст комментария',
            'pub_date': 'Дата комментирования'
        }
        for field, value in verboses.items():
            with self.subTest(Поле=field):
                self.assertEqual(
                    CommentModelTest.comment._meta.get_field(
                        field).verbose_name,
                    value
                )
        helps = {
            'post': 'К какому посту добавить комментарий',
            'text': 'Добавьте комментарий'
        }
        for field, value in helps.items():
            with self.subTest(Поле=field):
                self.assertEqual(
                    CommentModelTest.comment._meta.get_field(field).help_text,
                    value
                )


class FollowModelTest(TestCase):
    """Тесты модели Follow."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='leo')
        cls.another_user = User.objects.create_user(username='tiger')
        cls.follow = Follow.objects.create(author=cls.user,
                                           user=cls.another_user)

    def test_models_have_correct_object_names(self):
        """Проверка работы __str__."""
        self.assertEqual(str(FollowModelTest.follow),
                         (f'{FollowModelTest.follow.user.username} подписан '
                          f'на {FollowModelTest.follow.author.username}'))

    def test_verbose_and_help(self):
        """Проверка полей verbose_name и help_text."""
        verboses = {
            'author': 'Автор поста',
            'user': 'Подписчик'
        }
        for field, value in verboses.items():
            with self.subTest(Поле=field):
                self.assertEqual(
                    FollowModelTest.follow._meta.get_field(field).verbose_name,
                    value
                )
