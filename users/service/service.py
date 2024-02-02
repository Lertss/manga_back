from users.models import CustomUser, Notification
from users.serializers import CustomUserLastDetailsSerializer


def extract_and_serialize_data_on_recent_users():
    """This feature extracts and serializes information about the last 10 users."""
    latest_users = CustomUser.objects.all().order_by("-date_joined")[:10]
    serializer = CustomUserLastDetailsSerializer(latest_users, many=True)
    return serializer


def get_notifications(user, unread_only: bool = False):
    """This function returns the notifications for the specified user.
    If unread_only is set to True, it returns only unread notifications; otherwise,
    it returns all notifications for the user."""
    if unread_only:
        return Notification.objects.filter(user=user, is_read=False)
    else:
        return Notification.objects.filter(user=user)
