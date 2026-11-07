from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from blog import constants
from blog.models import Post
from blog.views import get_published_posts

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

    is_owner = (
        request.user.is_authenticated
        and request.user == profile
    )

    if is_owner:
        post_list = Post.objects.filter(
            author=profile,
        ).select_related(
            'author',
            'category',
            'location',
        ).annotate(
            comment_count=Count('comments'),
        ).order_by('-pub_date')
    else:
        post_list = get_published_posts().filter(
            author=profile,
        )

    paginator = Paginator(
        post_list,
        constants.POSTS_BY_PAGE,
    )
    page_obj = paginator.get_page(
        request.GET.get('page'),
    )

    return render(
        request,
        'users/profile.html',
        {
            'profile': profile,
            'post_list': page_obj.object_list,
            'page_obj': page_obj,
            'is_owner': is_owner,
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
