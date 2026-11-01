from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from core.images import optimise


class Category(models.Model):
    name_en = models.CharField("name (English)", max_length=60)
    name_ar = models.CharField("name (Arabic)", max_length=60, blank=True)
    slug = models.SlugField(unique=True)
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["position", "name_en"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name_en


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True, date__lte=timezone.localdate())


class Post(models.Model):
    title_en = models.CharField("title (English)", max_length=200)
    title_ar = models.CharField("title (Arabic)", max_length=200, blank=True)
    slug = models.SlugField("web address", max_length=200, unique=True,
                            help_text="Used in the link, e.g. /news/<b>this-part</b>/. Filled in from the title.")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="posts")
    date = models.DateField(default=timezone.localdate,
                            help_text="Shown on the article. Posts dated in the future stay hidden until that day.")
    year_only = models.BooleanField("show the year only", default=False,
                                    help_text="Tick when you only know the year, not the exact day.")
    cover = models.ImageField("main photo", upload_to="news/",
                              help_text="Landscape photos work best. Large phone photos are resized automatically.")
    summary_en = models.TextField("summary (English)", max_length=400,
                                  help_text="One or two sentences shown on the news list.")
    summary_ar = models.TextField("summary (Arabic)", max_length=400, blank=True)
    body_en = models.TextField("article (English)", blank=True,
                               help_text="Leave an empty line between paragraphs.")
    body_ar = models.TextField("article (Arabic)", blank=True)
    is_published = models.BooleanField("published", default=True)
    is_featured = models.BooleanField("feature at the top of the news page", default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ["-date", "-created"]
        verbose_name = "news article"
        verbose_name_plural = "news articles"

    def __str__(self):
        return self.title_en

    def get_absolute_url(self):
        return reverse("news-detail", args=[self.slug])

    def save(self, *a, **kw):
        if not self.slug:
            base = slugify(self.title_en)[:180] or "article"
            slug, n = base, 2
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug, n = f"{base}-{n}", n + 1
            self.slug = slug
        optimise(self.cover)
        super().save(*a, **kw)


class PostImage(models.Model):
    post = models.ForeignKey(Post, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="news/gallery/")
    caption_en = models.CharField("caption (English)", max_length=200, blank=True)
    caption_ar = models.CharField("caption (Arabic)", max_length=200, blank=True)
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]
        verbose_name = "extra photo"

    def save(self, *a, **kw):
        optimise(self.image)
        super().save(*a, **kw)
