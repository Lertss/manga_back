from django.contrib.auth.models import AbstractUser
from django.db import IntegrityError, models, transaction
from django.utils.text import slugify
from manga.models import Manga
from manga_back.constants import GENDER_SELECTION, NAME_LIST_MANGA
from rest_framework.exceptions import ValidationError


class CustomUser(AbstractUser):
    gender = models.CharField(max_length=15, choices=GENDER_SELECTION)
    adult = models.BooleanField(default=False, help_text="For adults? yes/no")
    avatar = models.ImageField(upload_to="static/images/avatars/user/", blank=True)
    slug = models.SlugField(null=False, unique=True)
    first_name = None
    last_name = None

    def get_absolute_url(self):
        return f"/{self.slug}/"

    def get_avatar(self):
        if self.avatar:
            return "http://127.0.0.1:8000" + self.avatar.url
        return ""

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.avatar:
                self.avatar = "static/images/avatars/user/none_avatar_user.jpg"
            if not self.slug:
                self.slug = slugify(self.username)
            original_slug = self.slug
            counter = 1
            while True:
                try:
                    if CustomUser.objects.filter(username=self.username).exclude(id=self.id).exists():
                        raise ValidationError({"username": "This login already exists. Enter a new one"})
                    super().save(*args, **kwargs)
                    break
                except IntegrityError:
                    counter += 1
                    self.slug = f"{original_slug}-{counter}"


class MangaList(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="list_manga")
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE)
    name = models.CharField(max_length=15, choices=NAME_LIST_MANGA)

    class Meta:
        unique_together = ["user", "manga"]


class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    chapter = models.ForeignKey("manga.Chapter", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
