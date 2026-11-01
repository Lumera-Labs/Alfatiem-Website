from django.contrib import admin
from django.utils.html import format_html

from core.admin_utils import BilingualForm, thumb

from .models import Category, Post, PostImage


class PostImageInline(admin.TabularInline):
    model = PostImage
    form = BilingualForm
    fields = ["preview", "image", "caption_en", "caption_ar", "position"]
    readonly_fields = ["preview"]
    extra = 1

    @admin.display(description="")
    def preview(self, obj):
        return thumb(obj.image, 90)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = BilingualForm
    list_display = ["cover_thumb", "title_en", "category", "date", "is_published", "is_featured"]
    list_display_links = ["cover_thumb", "title_en"]
    list_editable = ["is_published", "is_featured"]
    list_filter = ["is_published", "category", "date"]
    search_fields = ["title_en", "title_ar", "summary_en", "body_en"]
    date_hierarchy = "date"
    prepopulated_fields = {"slug": ["title_en"]}
    readonly_fields = ["cover_preview"]
    inlines = [PostImageInline]
    save_on_top = True
    fieldsets = [
        (None, {"fields": ["category", ("date", "year_only"), ("is_published", "is_featured"), "cover", "cover_preview"]}),
        ("English", {"fields": ["title_en", "summary_en", "body_en"]}),
        ("Arabic", {"fields": ["title_ar", "summary_ar", "body_ar"],
                    "description": "If you leave the Arabic empty, the English is shown on the Arabic site."}),
        ("Web address", {"fields": ["slug"], "classes": ["collapse"]}),
    ]

    @admin.display(description="")
    def cover_thumb(self, obj):
        return thumb(obj.cover, 64)

    @admin.display(description="current photo")
    def cover_preview(self, obj):
        return thumb(obj.cover, 240)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    form = BilingualForm
    list_display = ["name_en", "name_ar", "position"]
    list_editable = ["position"]
    prepopulated_fields = {"slug": ["name_en"]}
