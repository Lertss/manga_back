from django.contrib.auth import get_user_model
from django.db import models

from manga.models import Chapter, Manga
from users.models import CustomUser


class Comment(models.Model):
    """
    Model representing a comment made by a user on a manga or chapter.

    Attributes:
        user (CustomUser): The user who made the comment.
        manga (Manga): The manga related to the comment.
        chapter (Chapter): The chapter related to the comment.
        content (str): The text content of the comment.
        created_at (datetime): The date and time the comment was created.
        updated_at (datetime): The date and time the comment was last updated.
    """

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE, blank=True, null=True)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, blank=True, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Meta options for Comment model.
        """

        ordering = ["-created_at"]

    def __str__(self):
        """
        Return a string representation of the Comment instance.

        Returns:
            str: String with username of the comment's author.
        """
        return f"Comment by {self.user.username}"

    def save(self, *args, **kwargs):
        """
        Save the Comment instance to the database.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            None
        """
        if not self.pk:
            self.user = self.user or get_user_model().objects.get(pk=self.user_id)  # Make sure the user has installed
        super().save(*args, **kwargs)



class MangaRating(models.Model):
    """
    Model representing a user's rating for a manga.

    Attributes:
        user (CustomUser): The user who rated the manga.
        manga (Manga): The manga being rated.
        rating (int): The rating value (1-5).
        created_at (datetime): The date and time the rating was created.
        updated_at (datetime): The date and time the rating was last updated.
    """

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE, related_name="ratings")
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Meta options for MangaRating model.
        """

        unique_together = ("user", "manga")

    def __str__(self):
        """
        String representation of the MangaRating instance.

        Returns:
            str: A string containing the username, name manga, and rating.
        """
        return f"{self.user.username} rated {self.manga.name_manga} - {self.rating}/5"


    def save(self, *args, **kwargs):
        """
        Save the MangaRating instance to the database.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            None
        """
        if not self.pk:
            self.user = self.user or get_user_model().objects.get(pk=self.user_id)
        super().save(*args, **kwargs)

