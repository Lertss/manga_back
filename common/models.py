from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=1000)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.timestamp}"

    @classmethod
    def add_comment(cls, user, text, obj):
        comment = cls.objects.create(user=user, text=text)
        obj.comments.add(comment)

    @classmethod
    def remove_comment(cls, comment_id, obj):
        try:
            comment = cls.objects.get(id=comment_id)
            obj.comments.remove(comment)
            comment.delete()
        except cls.DoesNotExist:
            pass
