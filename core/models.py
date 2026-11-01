from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

CONTENT_CACHE_KEY = "content-blocks-v1"
SETTINGS_CACHE_KEY = "site-settings-v1"


class Page(models.Model):
    """One public page. Its texts are the ContentBlocks shown inline in the admin."""
    slug = models.SlugField(unique=True)
    name = models.CharField("page", max_length=60)
    position = models.PositiveSmallIntegerField(default=0)
    meta_title = models.CharField("browser tab title", max_length=120, blank=True)
    meta_description = models.CharField("Google description", max_length=300, blank=True,
                                        help_text="One or two sentences shown under the page link in Google results.")

    class Meta:
        ordering = ["position"]
        verbose_name = "page text"
        verbose_name_plural = "page texts"

    def __str__(self):
        return self.name


class ContentBlock(models.Model):
    page = models.ForeignKey(Page, related_name="blocks", on_delete=models.CASCADE)
    key = models.CharField(max_length=40, unique=True, editable=False)
    position = models.PositiveIntegerField(default=0, editable=False)
    kind = models.CharField("where", max_length=40, blank=True, editable=False)
    en = models.TextField("English")
    ar = models.TextField("Arabic", blank=True)

    class Meta:
        ordering = ["page__position", "position"]
        verbose_name = "text"
        verbose_name_plural = "find a text (all pages)"

    def __str__(self):
        return self.en[:60]

    def save(self, *a, **kw):
        from .security import clean_html
        self.en, self.ar = clean_html(self.en), clean_html(self.ar)
        super().save(*a, **kw)


class SiteSettings(models.Model):
    """Contact details used in links across the site (one record only)."""
    phone = models.CharField("phone (as shown)", max_length=30, default="+973 3351 8885")
    whatsapp = models.CharField("WhatsApp (as shown)", max_length=30, default="+973 3359 9360",
                                help_text="Inquiry form messages are sent to this number.")
    email = models.EmailField(default="info@alfatiem.com")
    maps_link = models.URLField("Google Maps link", max_length=500,
                                default="https://www.google.com/maps/search/?api=1&query=Al-Fatiem+Alarabi+Sanabis+Bahrain",
                                help_text="Open the office in Google Maps, choose Share, Copy link, and paste it here.")
    maps_query = models.CharField("map search text", max_length=200, default="Al-Fatiem Alarabi, Sanabis, Bahrain",
                                  help_text="What the embedded map on the Contact page searches for.")

    class Meta:
        verbose_name = "contact details"
        verbose_name_plural = "contact details"

    def __str__(self):
        return "Contact details"

    @staticmethod
    def digits(v):
        return "".join(c for c in v if c.isdigit())

    @property
    def phone_digits(self):
        return self.digits(self.phone)

    @property
    def whatsapp_digits(self):
        return self.digits(self.whatsapp)

    def save(self, *a, **kw):
        self.pk = 1
        super().save(*a, **kw)

    @classmethod
    def load(cls):
        obj = cache.get(SETTINGS_CACHE_KEY)
        if obj is None:
            obj, _ = cls.objects.get_or_create(pk=1)
            cache.set(SETTINGS_CACHE_KEY, obj, 300)
        return obj


@receiver([post_save, post_delete], sender=ContentBlock)
@receiver([post_save, post_delete], sender=Page)
def _clear_content(**kw):
    cache.delete(CONTENT_CACHE_KEY)


@receiver(post_save, sender=SiteSettings)
def _clear_settings(**kw):
    cache.delete(SETTINGS_CACHE_KEY)
