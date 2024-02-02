from django.contrib.auth import get_user_model
from django.db import models
from manga.models import Chapter, Manga
from users.models import CustomUser


class Comment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE, blank=True, null=True)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, blank=True, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.pk:
            self.user = self.user or get_user_model().objects.get(pk=self.user_id)  # Make sure the user has installed
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Comment by {self.user.username}"


class MangaRating(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE, related_name="ratings")
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "manga")

    def save(self, *args, **kwargs):
        if not self.pk:
            self.user = self.user or get_user_model().objects.get(pk=self.user_id)
        super().save(*args, **kwargs)
