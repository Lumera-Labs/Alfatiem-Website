from django.db import models

from core.images import optimise


class Project(models.Model):
    SECTORS = [("gov", "Ministries"), ("res", "Houses and villas"), ("com", "Commercial buildings")]
    code = models.SlugField("short code", max_length=40, unique=True)
    name_en = models.CharField("name (English)", max_length=200)
    name_ar = models.CharField("name (Arabic)", max_length=200, blank=True)
    sector = models.CharField("tab", max_length=3, choices=SECTORS)
    year = models.PositiveSmallIntegerField()
    area = models.DecimalField("insulated area (m²)", max_digits=10, decimal_places=2, null=True, blank=True)
    location_en = models.CharField("location (English)", max_length=120)
    location_ar = models.CharField("location (Arabic)", max_length=120, blank=True)
    client_en = models.CharField("client (English)", max_length=160, blank=True)
    client_ar = models.CharField("client (Arabic)", max_length=160, blank=True)
    consultant = models.CharField(max_length=80, blank=True)
    contractors_en = models.CharField("contractors (English)", max_length=300, blank=True,
                                      help_text="e.g. Main contractor: Al-Nasir Contracting W.L.L.")
    contractors_ar = models.CharField("contractors (Arabic)", max_length=300, blank=True)
    insulation = models.BooleanField("we did the insulation", default=True)
    scaffolding = models.BooleanField("we did the scaffolding", default=False)
    on_home = models.BooleanField("show under Recent projects on the home page", default=False)
    is_published = models.BooleanField("published", default=True)

    class Meta:
        ordering = ["-year", "-area"]

    def __str__(self):
        return self.name_en

    def as_js(self):
        pics = [p.image.url for p in self.photos.all()]
        d = {"id": self.code, "en": self.name_en, "ar": self.name_ar or self.name_en, "y": self.year,
             "a": float(self.area) if self.area is not None else None, "s": self.sector,
             "loc": {"en": self.location_en, "ar": self.location_ar or self.location_en},
             "sv": [k for k, on in (("eifs", self.insulation), ("scaf", self.scaffolding)) if on],
             "ph": pics, "feat": self.on_home}
        if self.client_en:
            d["cl"] = {"en": self.client_en, "ar": self.client_ar or self.client_en}
        if self.consultant:
            d["cons"] = self.consultant
        if self.contractors_en:
            d["chain"] = {"en": self.contractors_en, "ar": self.contractors_ar or self.contractors_en}
        return d


class ProjectPhoto(models.Model):
    project = models.ForeignKey(Project, related_name="photos", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="projects/")
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]
        verbose_name = "photo"

    def save(self, *a, **kw):
        optimise(self.image)
        super().save(*a, **kw)


class ExtraPhoto(models.Model):
    """Gallery under 'More residential work' on the Houses and villas tab."""
    image = models.ImageField(upload_to="projects/more/")
    caption_en = models.CharField("caption (English)", max_length=160)
    caption_ar = models.CharField("caption (Arabic)", max_length=160, blank=True)
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]
        verbose_name = "more residential work photo"
        verbose_name_plural = "more residential work photos"

    def __str__(self):
        return self.caption_en

    def save(self, *a, **kw):
        optimise(self.image)
        super().save(*a, **kw)
