from django.db.models.signals import post_save
from django.dispatch import receiver

from manga.models import Chapter
from users.models import MangaList, Notification


@receiver(post_save, sender=Chapter)
def create_notification(sender, instance, created, **kwargs):
    """
    Signal receiver that creates notifications for users when a new chapter is created.

    Args:
        sender (type): The model class sending the signal (Chapter).
        instance (Chapter): The instance of Chapter that was saved.
        created (bool): Whether this is a new Chapter instance.
        **kwargs: Additional keyword arguments.

    Returns:
        None

    Example:
        # Automatically called by Django when a Chapter is created
    """
    if created:
        users_with_manga = MangaList.objects.filter(manga=instance.manga).values_list("user", flat=True)
        for user_id in users_with_manga:
            Notification.objects.create(user_id=user_id, chapter=instance)
