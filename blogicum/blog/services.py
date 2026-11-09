from django.core.paginator import Paginator
from django.db.models import Count
from django.utils import timezone

from core import constants


def annotate_comments(queryset):
    return queryset.select_related(
        'author',
        'category',
        'location',
    ).annotate(
        comment_count=Count('comments'),
    ).order_by('-pub_date')


def filter_published_posts(queryset):
    return queryset.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    )


def paginate_posts(request, queryset):
    paginator = Paginator(
        queryset,
        constants.POSTS_BY_PAGE,
    )
    return paginator.get_page(request.GET.get('page'))
