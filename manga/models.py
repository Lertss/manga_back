from __future__ import unicode_literals

from datetime import datetime

from django.core.validators import RegexValidator
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import gettext_lazy as _

from io import BytesIO
from PIL import Image
from django.core.files import File
from django.utils.text import slugify

from django.db import models

from manga_back.constants import MANGA_GENRES, MANGA_TAGS, COUNTRY_CHOICES, CATEGORY_CHOICES


class Author(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(_('First name'), max_length=50)
    last_name = models.CharField(_('Last name'), max_length=50)
    slug = models.SlugField(null=False, unique=True)

    def __str__(self):
        return f'{self.first_name}, {self.last_name}'

    def get_absolute_url(self):
        return f'/{self.slug}/'


class Country(models.Model):
    id = models.AutoField(primary_key=True)
    counts = models.CharField(max_length=50, choices=COUNTRY_CHOICES, unique=True)

    def __str__(self):
        return self.counts


class Genre(models.Model):
    id = models.AutoField(primary_key=True)
    genr = models.CharField(max_length=50, choices=MANGA_GENRES, unique=True)

    def __str__(self):
        return self.genr


class Tags(models.Model):
    id = models.AutoField(primary_key=True)
    tag_name = models.CharField(max_length=50, choices=MANGA_TAGS, unique=True)

    def __str__(self):
        return self.tag_name


class Category(models.Model):

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50, choices=CATEGORY_CHOICES, unique=True)

    def get_absolute_url(self):
        return f'/{self.slug}/'

    def __str__(self):
        return self.title


class Manga(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category')
    id = models.AutoField(primary_key=True)
    name_manga = models.CharField(_('name_manga'), max_length=100, blank=False)
    name_original = models.CharField(_('name_original'), max_length=100, blank=True)
    english_only_field = models.CharField(max_length=255,unique=True,blank=True, validators=[RegexValidator(r'^[a-zA-Z0-9]*$', 'Only alphanumeric characters are allowed.')])
    author = models.ManyToManyField(Author, related_name='actors')
    time_prod = models.DateTimeField(default=timezone.now)
    counts = models.ManyToManyField(Country, related_name='country')
    tags = models.ManyToManyField(Tags, related_name='tags')
    genre = models.ManyToManyField(Genre, related_name='genre')
    decency = models.BooleanField(default=False, help_text="For adults? yes/no")
    average_rating = models.FloatField(default=0)  # Средняя оценка
    total_ratings = models.PositiveIntegerField(default=0)  # Количество оценок
    review = models.TextField(max_length=1000)
    avatar = models.ImageField(upload_to='static/images/avatars/',
                               default='default/none_avatar.png/',
                               blank=True)
    thumbnail = models.ImageField(upload_to='media/products/miniava', blank=True, null=True)
    comments = models.ManyToManyField('common.Comment', related_name='manga_comments', blank=True)

    slug = models.SlugField(null=False, unique=True)

    def __str__(self):
        return self.name_manga

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

    def add_comment(self, user, text):
        from common.models import Comment
        comment = Comment.objects.create(user=user, text=text)
        self.comments.add(comment)

    def remove_comment(self, comment_id):
        from common.models import Comment
        try:
            comment = Comment.objects.get(id=comment_id)
            self.comments.remove(comment)
            comment.delete()
        except Comment.DoesNotExist:
            pass


    def make_thumbnail(self, avatar):
        img = Image.open(avatar)
        img = img.resize((120, 170))

        thumb_io = BytesIO()
        img.save(thumb_io, 'PNG', quality=85)

        thumbnail = File(thumb_io, name=avatar.name)
        return thumbnail

    def save(self, *args, **kwargs):
        if not self.id:
            super().save(*args, **kwargs)

        self.slug = slugify(f"{self.english_only_field}-{self.id}")
        super().save(*args, **kwargs)







class Chapter(models.Model):
    id = models.AutoField(primary_key=True)
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE, related_name='chapters')
    volumes = models.IntegerField(blank=False)
    num = models.FloatField(blank=False)
    title = models.CharField(max_length=50, null=True, blank=True)
    time_prod = models.DateTimeField(default=timezone.now)
    comments = models.ManyToManyField('common.Comment', related_name='chapter_comments', blank=True)
    slug = models.SlugField(null=False, unique=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-num"]

    def get_absolute_url(self):
        return f'/{self.manga.slug}/{self.slug}/'

    def data_g(self):
        return self.time_prod.strftime("%m/%d/%Y")

    def add_comment(self, user, text):
        from common.models import Comment
        comment = Comment.objects.create(user=user, text=text)
        self.comments.add(comment)

    def remove_comment(self, comment_id):
        from common.models import Comment
        try:
            comment = Comment.objects.get(id=comment_id)
            self.comments.remove(comment)
            comment.delete()
        except Comment.DoesNotExist:
            pass


class Gallery(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to='static/images/gallery/')
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='galleries')

    def get_image(self):
        if self.image:
            return 'http://127.0.0.1:8000' + self.image.url
        return ''







