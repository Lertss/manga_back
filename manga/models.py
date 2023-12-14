from __future__ import unicode_literals

from io import BytesIO

from PIL import Image
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.files import File
from django.db import models
from django.db.models import Avg
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from manga_back.constants import MANGA_GENRES, MANGA_TAGS, COUNTRY_CHOICES, CATEGORY_CHOICES


class Author(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(_('First name'), max_length=50)
    last_name = models.CharField(_('Last name'), max_length=50)

    def __str__(self):
        return f'{self.first_name}, {self.last_name}'


class Country(models.Model):
    id = models.AutoField(primary_key=True)
    counts = models.CharField(max_length=50, choices=COUNTRY_CHOICES, unique=True)

    def __str__(self):
        return self.counts


class Genre(models.Model):
    id = models.AutoField(primary_key=True)
    genr_name = models.CharField(max_length=50, choices=MANGA_GENRES, unique=True)

    def __str__(self):
        return self.genr_name


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    tag_name = models.CharField(max_length=50, choices=MANGA_TAGS, unique=True)

    def __str__(self):
        return self.tag_name


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    cat_name = models.CharField(max_length=50, choices=CATEGORY_CHOICES, unique=True)

    def __str__(self):
        return self.cat_name


class Manga(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category')
    name_manga = models.CharField(_('name_manga'), max_length=100, blank=False)
    name_original = models.CharField(_('name_original'), max_length=100, blank=True)
    english_only_field = models.CharField(max_length=255, unique=True, blank=False)
    author = models.ManyToManyField(Author, related_name='actors', blank=False)
    time_prod = models.DateTimeField(default=timezone.now)
    counts = models.ManyToManyField(Country, related_name='country', blank=False)
    tags = models.ManyToManyField(Tag, related_name='tags', blank=False)
    genre = models.ManyToManyField(Genre, related_name='genre', blank=False)
    decency = models.BooleanField(default=False, help_text="For adults? yes/no")
    review = models.TextField(max_length=1000, blank=False)
    avatar = models.ImageField(upload_to='static/images/avatars/',
                               default='default/none_avatar.png/',
                               blank=True)
    thumbnail = models.ImageField(upload_to='media/products/miniava', blank=True, null=True)
    slug = models.SlugField(null=False, unique=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.list_manga = None

    def __str__(self):
        return self.name_manga

    def average_rating(self):
        return self.ratings.aggregate(Avg('rating'))['rating__avg']

    def get_avatar(self):
        if self.avatar:
            return 'http://127.0.0.1:8000' + self.avatar.url
        return ''

    def get_absolute_url(self):
        return f'/{self.slug}/'

    def get_thumbnail(self):
        if self.thumbnail:
            return 'http://127.0.0.1:8000' + self.thumbnail.url
        else:
            if self.avatar:
                self.thumbnail = self.make_thumbnail(self.avatar)
                self.save()

                return 'http://127.0.0.1:8000' + self.thumbnail.url
            else:
                return ''

    def make_thumbnail(self, avatar):
        img = Image.open(avatar)
        img = img.resize((120, 170))

        thumb_io = BytesIO()
        img.save(thumb_io, 'PNG', quality=85)

        thumbnail = File(thumb_io, name=avatar.name)
        return thumbnail

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f'{slugify(self.english_only_field)}'
        super().save(*args, **kwargs)


class Chapter(models.Model):
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(_('title'), max_length=100, blank=True)
    chapter_number = models.IntegerField(_('chapter_number'), blank=False)
    volume = models.IntegerField(_('volume'), blank=False)
    time_prod = models.DateTimeField(default=timezone.now)
    slug = models.SlugField(null=False, unique=True)

    def __str__(self):
        return f"{self.manga.name_manga} - Chapter {self.chapter_number}"

    def data_g(self):
        return self.time_prod.strftime("%m/%d/%Y")

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.manga.english_only_field}-{self.volume}-{self.chapter_number}")
        super().save(*args, **kwargs)


class Page(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='pages')  # r
    image = models.ImageField(upload_to='media/manga/pages/')
    page_number = models.PositiveIntegerField(_('page_number'))

    def get_image(self):
        if self.image:
            return 'http://127.0.0.1:8000' + self.image.url
        return ''

    def save(self, *args, **kwargs):
        if not self.page_number:
            last_page = Page.objects.filter(chapter__id=self.chapter_id).order_by('-page_number').first()
            if last_page:
                self.page_number = last_page.page_number + 1
            else:
                self.page_number = 1
        super().save(*args, **kwargs)
