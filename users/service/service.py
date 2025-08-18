from users.models import CustomUser, Notification
from users.serializers import CustomUserLastDetailsSerializer


def extract_and_serialize_data_on_recent_users():
    """
    Extract and serialize information about the last 10 users.

    Returns:
        CustomUserLastDetailsSerializer: Serializer containing the last 10 users' data.

    Example:
        extract_and_serialize_data_on_recent_users()
    """
    latest_users = CustomUser.objects.all().order_by("-date_joined")[:10]
    serializer = CustomUserLastDetailsSerializer(latest_users, many=True)
    return serializer.data


def get_notifications(user, unread_only: bool = False):
    """
    Return notifications for the specified user.

    Args:
        user (CustomUser): The user for whom to retrieve notifications.
        unread_only (bool, optional): If True, return only unread notifications. Defaults to False.

    Returns:
        QuerySet: Notifications for the user.

    Example:
        get_notifications(user, unread_only=True)
    """
    if unread_only:
        return Notification.objects.filter(user=user, is_read=False)
    else:
        return Notification.objects.filter(user=user)
