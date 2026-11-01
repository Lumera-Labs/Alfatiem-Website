from django import forms
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html

from .admin_utils import BilingualForm
from .models import ContentBlock, Page, SiteSettings

PUBLIC = {"common": "/", "index": "/"}


class BlockForm(BilingualForm):
    class Meta:
        model = ContentBlock
        fields = ["en", "ar"]
        widgets = {"en": forms.Textarea(attrs={"rows": 2, "style": "width:100%"}),
                   "ar": forms.Textarea(attrs={"rows": 2, "style": "width:100%", "dir": "rtl"})}


class BlockInline(admin.TabularInline):
    model = ContentBlock
    form = BlockForm
    fields = ["kind", "en", "ar"]
    readonly_fields = ["kind"]
    extra = 0
    can_delete = False
    classes = ["blocks"]

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ["name", "text_count", "open_page"]
    fields = ["meta_title", "meta_description"]
    inlines = [BlockInline]

    def get_fields(self, request, obj=None):
        return [] if obj and obj.slug == "common" else self.fields

    @admin.display(description="texts")
    def text_count(self, obj):
        return obj.blocks.count()

    @admin.display(description="")
    def open_page(self, obj):
        url = PUBLIC.get(obj.slug, f"/{obj.slug}/")
        return format_html('<a href="{}" target="_blank">View page ↗</a>', url)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ContentBlock)
class ContentBlockAdmin(admin.ModelAdmin):
    """'Find a text': search every page's wording in one place."""
    form = BilingualForm
    list_display = ["short_en", "short_ar", "page", "kind"]
    list_filter = ["page"]
    search_fields = ["en", "ar"]
    fields = ["page", "kind", "en", "ar"]
    readonly_fields = ["page", "kind"]
    list_per_page = 50

    @admin.display(description="English")
    def short_en(self, obj):
        return obj.en[:90]

    @admin.display(description="Arabic")
    def short_ar(self, obj):
        return format_html('<span dir="rtl">{}</span>', obj.ar[:90])

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = [(None, {"fields": ["phone", "whatsapp", "email"]}),
                 ("Map", {"fields": ["maps_link", "maps_query"]})]

    def changelist_view(self, request, extra_context=None):
        obj = SiteSettings.load()
        return redirect(reverse("admin:core_sitesettings_change", args=[obj.pk]))

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
