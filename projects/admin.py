from django.contrib import admin

from core.admin_utils import BilingualForm, thumb

from .models import ExtraPhoto, Project, ProjectPhoto


class PhotoInline(admin.TabularInline):
    model = ProjectPhoto
    fields = ["preview", "image", "position"]
    readonly_fields = ["preview"]
    extra = 1

    @admin.display(description="")
    def preview(self, obj):
        return thumb(obj.image, 90)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = BilingualForm
    list_display = ["first_photo", "name_en", "sector", "year", "area", "insulation", "scaffolding", "on_home", "is_published"]
    list_display_links = ["first_photo", "name_en"]
    list_editable = ["on_home", "is_published"]
    list_filter = ["sector", "year", "insulation", "scaffolding", "is_published"]
    search_fields = ["name_en", "name_ar", "location_en", "client_en"]
    prepopulated_fields = {"code": ["name_en"]}
    inlines = [PhotoInline]
    save_on_top = True
    fieldsets = [
        (None, {"fields": [("sector", "year"), "area", ("insulation", "scaffolding"), ("on_home", "is_published")]}),
        ("English", {"fields": ["name_en", "location_en", "client_en", "contractors_en"]}),
        ("Arabic", {"fields": ["name_ar", "location_ar", "client_ar", "contractors_ar"]}),
        ("Other", {"fields": ["consultant", "code"]}),
    ]

    @admin.display(description="")
    def first_photo(self, obj):
        p = obj.photos.first()
        return thumb(p.image if p else None, 64)


@admin.register(ExtraPhoto)
class ExtraPhotoAdmin(admin.ModelAdmin):
    form = BilingualForm
    list_display = ["preview", "caption_en", "position"]
    list_editable = ["position"]

    @admin.display(description="")
    def preview(self, obj):
        return thumb(obj.image, 64)
