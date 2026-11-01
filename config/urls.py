from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps import Sitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import path, re_path, reverse
from django.views.generic import RedirectView
from django.views.static import serve

from core import views as core
from news import views as news
from news.models import Post

admin.site.site_header = "Al-Fatiem Alarabi website"
admin.site.site_title = "Al-Fatiem admin"
admin.site.index_title = "Edit the website"
admin.site.site_url = "/"


class StaticSitemap(Sitemap):
    def items(self):
        return ["index", "about", "services", "projects", "approvals", "news", "inquiries", "contact"]

    def location(self, item):
        return "/" if item == "index" else f"/{item}/"


class NewsSitemap(Sitemap):
    def items(self):
        return Post.published.all()

    def lastmod(self, obj):
        return obj.updated


OLD = {"index": "/", "about": "/about/", "services": "/services/", "projects": "/projects/",
       "approvals": "/approvals/", "news": "/news/", "inquiries": "/inquiries/", "contact": "/contact/"}

urlpatterns = [
    path("", core.page, name="home"),
    path("news/", news.news_list, name="news"),
    path("news/page/<int:page>/", news.news_list, name="news-page"),
    path("news/category/<slug:category>/", news.news_list, name="news-cat"),
    path("news/category/<slug:category>/page/<int:page>/", news.news_list, name="news-cat-page"),
    path("news/<slug:slug>/", news.news_detail, name="news-detail"),
    path(settings.ADMIN_PATH, admin.site.urls),
    path("robots.txt", core.robots),
    path("sitemap.xml", sitemap, {"sitemaps": {"pages": StaticSitemap, "news": NewsSitemap}}),
    # links from the old static version (about.html etc.)
    re_path(r"^(?P<name>index|about|services|projects|approvals|news|inquiries|contact)\.html$",
            lambda r, name: RedirectView.as_view(url=OLD[name], permanent=True)(r)),
    path("<slug:slug>/", core.page, name="page"),
]

# uploaded photos (on most hosts the web server serves /media/ directly instead; see README)
urlpatterns.insert(0, re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}))
