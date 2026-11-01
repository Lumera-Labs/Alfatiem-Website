from django import forms
from django.utils.html import format_html


class BilingualForm(forms.ModelForm):
    """Arabic fields type right-to-left; long texts get a sensible size."""

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        for name, f in self.fields.items():
            if name == "ar" or name.endswith("_ar"):
                f.widget.attrs.update({"dir": "rtl", "lang": "ar"})
            if isinstance(f.widget, forms.Textarea):
                rows = 12 if name.startswith("body") else 3
                f.widget.attrs.setdefault("rows", rows)
                f.widget.attrs.setdefault("style", "width:100%;max-width:640px")


def thumb(image, size=80):
    if not image:
        return "—"
    try:
        return format_html('<img src="{}" style="width:{}px;height:{}px;object-fit:cover;border-radius:2px">',
                           image.url, size, int(size * .75))
    except ValueError:
        return "—"
