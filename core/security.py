"""Security helpers: HTML allow-list for editable texts, admin login throttle, response headers."""
from html import escape
from html.parser import HTMLParser

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django.urls import reverse

ALLOWED = {"bdi": {"dir"}, "b": set(), "strong": set(), "em": set(), "i": set(), "br": set(),
           "span": {"dir"}, "a": {"href"}}
VOID = {"br"}


class _Clean(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.out, self.stack = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in ALLOWED:
            return
        keep = []
        for k, v in attrs:
            if k not in ALLOWED[tag] or v is None:
                continue
            if k == "href" and not v.strip().lower().startswith(("http://", "https://", "/", "mailto:", "tel:", "#")):
                continue
            if k == "dir" and v not in ("ltr", "rtl", "auto"):
                continue
            keep.append(f' {k}="{escape(v)}"')
        self.out.append(f"<{tag}{''.join(keep)}>")
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in self.stack:
            while self.stack:
                t = self.stack.pop()
                self.out.append(f"</{t}>")
                if t == tag:
                    break

    def handle_data(self, d):
        self.out.append(escape(d, quote=False))

    def handle_entityref(self, n):
        self.out.append(f"&{n};")

    def handle_charref(self, n):
        self.out.append(f"&#{n};")


def clean_html(s):
    p = _Clean()
    p.feed(s or "")
    p.close()
    return "".join(p.out) + "".join(f"</{t}>" for t in reversed(p.stack))


def client_ip(request):
    # Behind Cloudflare Tunnel the real visitor IP arrives in CF-Connecting-IP.
    return request.META.get("HTTP_CF_CONNECTING_IP") or request.META.get("REMOTE_ADDR", "")


class SecurityMiddleware:
    LIMIT, WINDOW = 5, 15 * 60
    CSP = ("default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; "
           "img-src 'self' data:; font-src 'self'; frame-src https://www.google.com; connect-src 'self'; "
           "object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        login = request.method == "POST" and request.path == reverse("admin:login")
        key = f"login-fail:{client_ip(request)}"
        if login and (cache.get(key) or 0) >= self.LIMIT:
            return HttpResponse("Too many login attempts. Try again in 15 minutes.", status=429,
                                content_type="text/plain")
        r = self.get_response(request)
        if login:
            if r.status_code == 200:  # form shown again = wrong password
                cache.set(key, (cache.get(key) or 0) + 1, self.WINDOW)
            elif r.status_code == 302:
                cache.delete(key)
        r.setdefault("Content-Security-Policy", self.CSP)
        r.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=()")
        return r
