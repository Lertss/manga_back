import random

from django.contrib.auth.models import AbstractUser
from django.db import IntegrityError
from django.db import models
from django.utils.text import slugify

from manga.models import Manga
from manga_back.constants import GENDER_SELECTION, NAME_LIST_MANGA


class CustomUser(AbstractUser):
    gender = models.CharField(max_length=15, choices=GENDER_SELECTION)
    adult = models.BooleanField(default=False, help_text="For adults? yes/no")
    avatar = models.ImageField(upload_to='static/images/avatars/user/', blank=True)
    slug = models.SlugField(null=False, unique=True)
    first_name = None
    last_name = None
    comments = models.ManyToManyField('common.Comment', related_name='user_comments', blank=True)

    def add_comment(self, text):
        from common.models import Comment
        Comment.add_comment(self, text, self)

    def remove_comment(self, comment_id):
        from common.models import Comment
        Comment.remove_comment(comment_id, self)

    def get_absolute_url(self):
        return f'/{self.slug}/'

    def get_avatar(self):
        if self.avatar:
            return 'http://127.0.0.1:8000' + self.avatar.url
        return ''

    def save(self, *args, **kwargs):
        if not self.avatar:
            self.avatar = 'static/images/avatars/user/none_avatar_user.jpg'
        if not self.slug:
            self.slug = slugify(self.username)
            while True:
                try:
                    super().save(*args, **kwargs)
                except IntegrityError:
                    self.slug = f'{self.slug}-{random.randint(1, 10000)}'
                else:
                    break
        else:
            super().save(*args, **kwargs)


class MangaList(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='list_manga')
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE)
    name = models.CharField(max_length=15, choices=NAME_LIST_MANGA)

    class Meta:
        unique_together = ['user', 'manga']









from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chapter = models.ForeignKey('manga.Chapter', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)


    class Meta:
        ordering = ['-created_at']
