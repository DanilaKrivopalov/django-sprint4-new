from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from . import constants
from .forms import CommentForm, PostForm
from .models import Category, Comment, Post


def get_published_posts():
    return Post.objects.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    ).select_related(
        'author',
        'category',
        'location',
    ).annotate(
        comment_count=Count('comments'),
    ).order_by('-pub_date')


def get_post_for_user(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related(
            'author',
            'category',
            'location',
        ).annotate(
            comment_count=Count('comments'),
        ),
        pk=post_id,
    )

    is_published = (
        post.is_published
        and post.pub_date <= timezone.now()
        and post.category is not None
        and post.category.is_published
    )

    if not is_published and post.author != request.user:
        raise Http404

    return post


def paginate_posts(request, post_list):
    paginator = Paginator(
        post_list,
        constants.POSTS_BY_PAGE,
    )
    return paginator.get_page(request.GET.get('page'))


def index(request):
    post_list = get_published_posts()
    page_obj = paginate_posts(request, post_list)

    return render(
        request,
        'blog/index.html',
        {
            'page_obj': page_obj,
        },
    )


def post_detail(request, post_id):
    post = get_post_for_user(request, post_id)

    comments = post.comments.select_related(
        'author',
    ).order_by('created_at')

    form = CommentForm()

    return render(
        request,
        'blog/detail.html',
        {
            'post': post,
            'comments': comments,
            'form': form,
        },
    )


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )

    post_list = get_published_posts().filter(
        category=category,
    )
    page_obj = paginate_posts(request, post_list)

    return render(
        request,
        'blog/category.html',
        {
            'category': category,
            'page_obj': page_obj,
        },
    )


@login_required
def create_post(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect(
            'users:profile',
            username=request.user.username,
        )

    return render(
        request,
        'blog/create.html',
        {'form': form},
    )


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if post.author != request.user:
        return redirect(
            'blog:post_detail',
            post_id=post.pk,
        )

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )

    if form.is_valid():
        form.save()
        return redirect(
            'blog:post_detail',
            post_id=post.pk,
        )

    return render(
        request,
        'blog/create.html',
        {'form': form},
    )


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if post.author != request.user:
        return redirect(
            'blog:post_detail',
            post_id=post.pk,
        )

    form = PostForm(instance=post)

    if request.method == 'POST':
        post.delete()
        return redirect(
            'users:profile',
            username=request.user.username,
        )

    return render(
        request,
        'blog/create.html',
        {'form': form},
    )


@login_required
def add_comment(request, post_id):
    post = get_post_for_user(request, post_id)

    form = CommentForm(
        request.POST or None,
    )

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return redirect(
            'blog:post_detail',
            post_id=post.pk,
        )

    comments = post.comments.select_related(
        'author',
    ).order_by('created_at')

    return render(
        request,
        'blog/detail.html',
        {
            'post': post,
            'comments': comments,
            'form': form,
        },
    )


@login_required
def edit_comment(request, post_id, comment_id):
    post = get_post_for_user(request, post_id)

    comment = get_object_or_404(
        Comment,
        pk=comment_id,
        post=post,
    )

    if comment.author != request.user:
        return redirect(
            'blog:post_detail',
            post_id=post.pk,
        )

    form = CommentForm(
        request.POST or None,
        instance=comment,
    )

    if form.is_valid():
        form.save()
        return redirect(
            'blog:post_detail',
            post_id=post.pk,
        )

    return render(
        request,
        'blog/comment.html',
        {
            'form': form,
            'comment': comment,
        },
    )


@login_required
def delete_comment(request, post_id, comment_id):
    post = get_post_for_user(request, post_id)

    comment = get_object_or_404(
        Comment,
        pk=comment_id,
        post=post,
    )

    if comment.author != request.user:
        return redirect(
            'blog:post_detail',
            post_id=post.pk,
        )

    if request.method == 'POST':
        comment.delete()
        return redirect(
            'blog:post_detail',
            post_id=post.pk,
        )

    return render(
        request,
        'blog/comment.html',
        {
            'comment': comment,
        },
    )
