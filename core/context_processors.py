from django.conf import settings

from .models import SiteSettings


def site(request):
    return {"site": SiteSettings.load(), "noindex": settings.NOINDEX}
