from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from blog.services import (
    annotate_comments,
    filter_published_posts,
    paginate_posts,
)
from .forms import UserEditForm, UserRegistrationForm


User = get_user_model()


def registration(request):
    form = UserRegistrationForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('blog:index')

    return render(
        request,
        'users/registration.html',
        {'form': form},
    )


def profile(request, username):
    profile = get_object_or_404(
        User,
        username=username,
    )

    post_list = annotate_comments(
        profile.posts.all(),
    )

    if request.user != profile:
        post_list = filter_published_posts(post_list)

    page_obj = paginate_posts(request, post_list)

    return render(
        request,
        'users/profile.html',
        {
            'profile': profile,
            'page_obj': page_obj,
        },
    )


@login_required
def edit_profile(request):
    form = UserEditForm(
        request.POST or None,
        instance=request.user,
    )

    if form.is_valid():
        form.save()
        return redirect(
            'users:profile',
            username=request.user.username,
        )

    return render(
        request,
        'users/edit_profile.html',
        {'form': form},
    )
