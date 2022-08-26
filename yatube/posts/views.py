from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import User, Post, Group, Follow
from .forms import PostForm, CommentForm
from .paginator import my_paginator


def index(request):
    """Главная страница."""
    post_list = Post.objects.select_related('author', 'group').all()
    page_obj = my_paginator(request, post_list)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Страница постов по группам."""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts_of_group.select_related('author').all()
    page_obj = my_paginator(request, post_list)
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Страница профиля автора поста."""
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('group').all()
    page_obj = my_paginator(request, post_list)
    following = request.user.is_authenticated and Follow.objects.filter(
        author=author, user=request.user).exists()
    context = {
        'author': author,
        'following': following,
        'page_obj': page_obj
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Страница поста."""
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    form = CommentForm()
    context = {
        'post': post,
        'form': form,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Страница для публикации новых записей."""
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user)
    context = {
        'form': form
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    """Страница для редактирования записи."""
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'is_edit': True,
        'post': post,
        'form': form
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    """Страница комментария."""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Посты авторов, на которых подписан текущий пользователь."""
    post_list = Post.objects.filter(
        author__following__user=request.user).select_related('author', 'group')
    page_obj = my_paginator(request, post_list)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Страница подписки на автора."""
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(author=author, user=request.user)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    """Страница отписки от автора."""
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(author=author, user=request.user).delete()
    return redirect('posts:profile', username)
