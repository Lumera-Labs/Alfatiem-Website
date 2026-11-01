from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import render

from projects.models import ExtraPhoto, Project

from .models import Page

PAGES = ["index", "about", "services", "projects", "approvals", "inquiries", "contact"]


def page(request, slug="index"):
    if slug not in PAGES:
        raise Http404
    ctx = {"page": Page.objects.filter(slug=slug).first(), "active": slug}
    if slug in ("index", "projects"):
        qs = Project.objects.filter(is_published=True).prefetch_related("photos")
        ctx["projects_json"] = [p.as_js() for p in qs]
    if slug == "projects":
        ctx["extra_photos"] = ExtraPhoto.objects.all()
    return render(request, f"pages/{slug}.html", ctx)


def robots(request):
    if settings.NOINDEX:
        return HttpResponse("User-agent: *\nDisallow: /\n", content_type="text/plain")
    hide = "Disallow: /admin/\n" if settings.ADMIN_PATH == "admin/" else ""  # never reveal a custom admin path
    return HttpResponse(f"User-agent: *\n{hide}Sitemap: {request.build_absolute_uri('/sitemap.xml')}\n",
                        content_type="text/plain")
