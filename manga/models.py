from __future__ import unicode_literals

from io import BytesIO

from django.core.files import File
from django.db import models
from django.db.models import Avg
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from PIL import Image


class Author(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(_("First name"), max_length=50)
    last_name = models.CharField(_("Last name"), max_length=50)

    def __str__(self):
        return f"{self.first_name}, {self.last_name}"


class Country(models.Model):
    id = models.AutoField(primary_key=True)
    country_name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["country_name"]

    def __str__(self):
        return self.country_name


class Genre(models.Model):
    id = models.AutoField(primary_key=True)
    genre_name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["genre_name"]

    def __str__(self):
        return self.genre_name


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    tag_name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["tag_name"]

    def __str__(self):
        return self.tag_name


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.category_name


class Manga(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="category")
    name_manga = models.CharField(_("name_manga"), max_length=100, blank=False)
    name_original = models.CharField(_("name_original"), max_length=100, blank=True)
    english_only_field = models.CharField(max_length=255, unique=True, blank=False)
    author = models.ManyToManyField(Author, related_name="authors", blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    country = models.ManyToManyField(Country, related_name="country", blank=False)
    tags = models.ManyToManyField(Tag, related_name="tags", blank=False)
    genre = models.ManyToManyField(Genre, related_name="genre", blank=False)
    decency = models.BooleanField(default=False, help_text="For adults? yes/no")
    review = models.TextField(max_length=1000, blank=False)
    avatar = models.ImageField(
        upload_to="static/images/avatars/",
        default="default/none_avatar.png/",
        blank=True,
    )
    thumbnail = models.ImageField(upload_to="media/products/miniava", blank=True, null=True)
    slug = models.SlugField(null=False, unique=True)

    class Meta:
        indexes = [
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        return self.name_manga

    def average_rating(self):
        return self.ratings.aggregate(Avg("rating"))["rating__avg"]

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return ""

    def get_absolute_url(self):
        return f"/{self.slug}/"

    def save(self, *args, **kwargs):
        # Генерація slug тільки для нових об'єктів
        if not self.slug:
            self.slug = slugify(self.english_only_field)

        # Визначаємо, чи змінився аватар
        avatar_changed = False
        if self.pk:
            orig = Manga.objects.get(pk=self.pk)
            avatar_changed = orig.avatar != self.avatar

        super().save(*args, **kwargs)
        if (not self.thumbnail and self.avatar) or avatar_changed:
            self.generate_thumbnail()

    def generate_thumbnail(self):
        """Генерує та зберігає thumbnail"""
        try:
            # Перевірка наявності та типу файлу
            if not self.avatar or not self.avatar.name.lower().endswith((".png", ".jpg", ".jpeg")):
                return

            with Image.open(self.avatar) as img:
                img = img.resize((120, 170))

                thumb_io = BytesIO()
                img.save(thumb_io, format="PNG", quality=85)
                thumb_file = File(thumb_io, name=f"thumb_{self.avatar.name}")

                self.thumbnail.save(thumb_file.name, thumb_file, save=False)
                super().save(update_fields=["thumbnail"])

        except Exception as e:
            ValueError(f"Error generating thumbnail: {e}")

    def get_thumbnail_url(self):
        """Повертає URL thumbnail без спроб генерації"""
        return self.thumbnail.url if self.thumbnail else ""


class Chapter(models.Model):
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE, related_name="chapters")
    title = models.CharField(_("title"), max_length=100, blank=True)
    chapter_number = models.IntegerField(_("chapter_number"), blank=False)
    volume = models.IntegerField(_("volume"), blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(null=False, unique=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["manga", "volume", "chapter_number"],
                name="unique_chapter_per_manga",
            )
        ]

    def __str__(self):
        return f"{self.manga.name_manga} - Chapter {self.chapter_number}"

    def data_g(self):
        return self.created_at.strftime("%m/%d/%Y")

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.manga.english_only_field}-{self.volume}-{self.chapter_number}")
        super().save(*args, **kwargs)


class Page(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name="pages")  # r
    image = models.ImageField(upload_to="media/manga/pages/")
    page_number = models.PositiveIntegerField(_("page_number"))

    class Meta:
        constraints = [models.UniqueConstraint(fields=["chapter", "page_number"], name="unique_page_per_chapter")]
        ordering = ["page_number"]

    def get_image(self):
        if self.image:
            return self.image.url
        return ""

    def save(self, *args, **kwargs):
        if not self.page_number:
            last_page = Page.objects.filter(chapter__id=self.chapter_id).order_by("-page_number").first()
            if last_page:
                self.page_number = last_page.page_number + 1
            else:
                self.page_number = 1
        super().save(*args, **kwargs)
