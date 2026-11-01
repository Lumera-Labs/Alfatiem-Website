"""{% t "about.004" %} prints an editable bilingual text as the site's
<span data-l="en">…</span><span data-l="ar">…</span> pair."""
import json
from functools import lru_cache
from pathlib import Path

from django import template
from django.core.cache import cache
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()
DEFAULTS = Path(__file__).resolve().parent.parent / "content_defaults.json"


@lru_cache(maxsize=1)
def _defaults():
    try:
        data = json.loads(DEFAULTS.read_text(encoding="utf-8"))
        return {b["key"]: (b["en"], b["ar"]) for p in data["pages"] for b in p["blocks"]}
    except Exception:
        return {}


def _blocks():
    from core.models import CONTENT_CACHE_KEY, ContentBlock
    d = cache.get(CONTENT_CACHE_KEY)
    if d is None:
        try:
            d = {k: (en, ar) for k, en, ar in ContentBlock.objects.values_list("key", "en", "ar")}
        except Exception:
            d = {}
        cache.set(CONTENT_CACHE_KEY, d, 600)
    return d


def pair(en, ar):
    ar = ar or en
    return mark_safe(f'<span data-l="en">{en}</span><span data-l="ar">{ar}</span>')


@register.simple_tag
def t(key):
    en, ar = _blocks().get(key) or _defaults().get(key) or (key, key)
    return pair(en, ar)


@register.simple_tag
def bi(en, ar):
    """Escaped bilingual pair from model fields (news, projects)."""
    return pair(escape(en or ""), escape(ar or en or ""))


AR_MONTHS = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
EN_MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


@register.simple_tag
def bidate(d):
    if not d:
        return ""
    return pair(f"{d.day} {EN_MONTHS[d.month-1]} {d.year}", f'<bdi dir="ltr">{d.day}</bdi> {AR_MONTHS[d.month-1]} <bdi dir="ltr">{d.year}</bdi>')


@register.simple_tag
def postdate(post):
    d = post.date
    if post.year_only:
        return pair(str(d.year), f'<bdi dir="ltr">{d.year}</bdi>')
    return bidate(d)


@register.filter
def paras(text):
    """Blank-line separated text to escaped <p> paragraphs."""
    from django.utils.html import escape, linebreaks
    return mark_safe(linebreaks(escape(text or "")))
