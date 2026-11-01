"""Shrink uploaded photos so phone pictures don't slow the site down."""
from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from PIL import Image, ImageOps

MAX_SIDE = 1800


def optimise(field, max_side=MAX_SIDE):
    """Resize an ImageField's file to max_side and re-save it as WebP. Call before model.save()."""
    f = getattr(field, "file", None)
    if not f or getattr(field, "_committed", True):
        return  # nothing new was uploaded
    try:
        img = Image.open(f)
        img = ImageOps.exif_transpose(img)
    except Exception:
        return
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA" if "A" in img.getbands() else "RGB")
    img.thumbnail((max_side, max_side), Image.LANCZOS)
    buf = BytesIO()
    img.save(buf, "WEBP", quality=82, method=5)
    name = Path(field.name).stem[:80] + ".webp"
    field.save(name, ContentFile(buf.getvalue()), save=False)
