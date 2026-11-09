from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Category, Comment, Post
from .services import (
    annotate_comments,
    filter_published_posts,
    paginate_posts,
)


def index(request):
    post_list = filter_published_posts(
        annotate_comments(Post.objects.all()),
    )
    page_obj = paginate_posts(request, post_list)

    return render(
        request,
        'blog/index.html',
        {
            'page_obj': page_obj,
        },
    )


def post_detail(request, post_id):
    post = get_object_or_404(
        annotate_comments(Post.objects.all()),
        pk=post_id,
    )

    if post.author != request.user:
        post = get_object_or_404(
            filter_published_posts(
                annotate_comments(Post.objects.all()),
            ),
            pk=post_id,
        )

    comments = post.comments.select_related(
        'author',
    )

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

    post_list = filter_published_posts(
        annotate_comments(category.posts.all()),
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
    post = get_object_or_404(
        annotate_comments(Post.objects.all()),
        pk=post_id,
    )

    if post.author != request.user:
        post = get_object_or_404(
            filter_published_posts(
                annotate_comments(Post.objects.all()),
            ),
            pk=post_id,
        )

    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return redirect(
            'blog:post_detail',
            post_id=post.pk,
        )

    comments = post.comments.select_related('author')

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
    comment = get_object_or_404(
        Comment,
        pk=comment_id,
        post_id=post_id,
    )

    if comment.author != request.user:
        return redirect(
            'blog:post_detail',
            post_id=post_id,
        )

    form = CommentForm(
        request.POST or None,
        instance=comment,
    )

    if form.is_valid():
        form.save()
        return redirect(
            'blog:post_detail',
            post_id=post_id,
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
    comment = get_object_or_404(
        Comment,
        pk=comment_id,
        post_id=post_id,
    )

    if comment.author != request.user:
        return redirect(
            'blog:post_detail',
            post_id=post_id,
        )

    if request.method == 'POST':
        comment.delete()
        return redirect(
            'blog:post_detail',
            post_id=post_id,
        )

    return render(
        request,
        'blog/comment.html',
        {
            'comment': comment,
        },
    )
