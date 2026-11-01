from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, render

from core.models import Page

from .models import Category, Post

PER_PAGE = 12


def news_list(request, category="", page=1):
    posts = Post.published.select_related("category")
    cats = Category.objects.filter(posts__in=posts).distinct()
    current = category
    if current:
        get_object_or_404(Category, slug=current)
        posts = posts.filter(category__slug=current)
    featured = None
    if not current and page == 1:
        featured = posts.filter(is_featured=True).first() or posts.first()
        if featured:
            posts = posts.exclude(pk=featured.pk)
    paginator = Paginator(posts, PER_PAGE)
    if page > max(paginator.num_pages, 1):
        raise Http404
    page_obj = paginator.get_page(page)
    return render(request, "news/list.html", {
        "page": Page.objects.filter(slug="news").first(), "active": "news",
        "featured": featured, "page_obj": page_obj, "categories": cats, "current": current,
    })


def news_detail(request, slug):
    post = get_object_or_404(Post.published.select_related("category").prefetch_related("images"), slug=slug)
    more = Post.published.exclude(pk=post.pk).select_related("category")[:3]
    return render(request, "news/detail.html", {
        "page": Page.objects.filter(slug="news").first(), "active": "news", "post": post, "more": more,
    })
