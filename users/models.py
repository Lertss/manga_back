from django.contrib.auth.models import AbstractUser
from django.db import IntegrityError, models, transaction
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError

from manga.models import Manga
from manga_back.constants import GENDER_SELECTION, NAME_LIST_MANGA


class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.

    Attributes:
        gender (str): Gender of the user.
        adult (bool): Whether the user is an adult.
        avatar (ImageField): User's avatar image.
        slug (str): Unique slug for the user.
    """

    gender = models.CharField(max_length=15, choices=GENDER_SELECTION)
    adult = models.BooleanField(default=False, help_text="For adults? yes/no")
    avatar = models.ImageField(upload_to="static/images/avatars/user/", blank=True)
    slug = models.SlugField(null=False, unique=True)
    first_name = None
    last_name = None

    def save(self, *args, **kwargs):
        """
        Save the CustomUser instance to the database, ensuring unique slug and avatar.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Raises:
            ValidationError: If the username already exists.
            IntegrityError: If a database integrity error occurs.

        Returns:
            None

        Example:
            user.save()
        """
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

    def get_url(self):
        """
        Get the URL for the user profile.

        Returns:
            str: URL string for the user's profile.

        Example:
            user.get_url()
        """
        return f"/{self.slug}/"

    def get_avatar_url(self):
        """
        Get the URL of the user's avatar image.

        Returns:
            str: URL of the avatar image or empty string if not set.

        Example:
            user.get_avatar_url()
        """
        if self.avatar:
            return self.avatar.url
        return ""




class MangaList(models.Model):
    """
    Model representing a user's manga list entry.

    Attributes:
        user (CustomUser): The user who owns the list.
        manga (Manga): The manga in the list.
        name (str): The name/category of the list entry.
    """

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="list_manga")
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE)
    name = models.CharField(max_length=15, choices=NAME_LIST_MANGA)

    class Meta:
        """
        Meta options for MangaList model.
        """

        unique_together = ["user", "manga"]

    def __str__(self):
        """
        String representation of the MangaList instance.

        Returns:
            str: A string containing the username, name manga, and list category.
        """
        return f"{self.user.username}'s {self.name} - {self.manga.name_manga}"

class Notification(models.Model):
    """
    Model representing a notification for a user about a manga chapter.

    Attributes:
        user (CustomUser): The user to notify.
        chapter (Chapter): The chapter related to the notification.
        created_at (datetime): The date and time the notification was created.
        is_read (bool): Whether the notification has been read.
    """

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    chapter = models.ForeignKey("manga.Chapter", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        """
        Meta options for Notification model.
        """

        ordering = ["-created_at"]

    def __str__(self):
        """
        String representation of the Notification instance.

        Returns:
            str: A string containing the username, name manga, chapter number, and read status.
        """
        status = "read" if self.is_read else "unread"
        return (f"Notification for {self.user.username}: {self.chapter.manga.name_manga} "
                f"Chapter {self.chapter.chapter_number} ({status})")

