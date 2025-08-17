from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers

from common.models import Comment
from common.serializers import CommentUserPageSerializer
from manga.serializers import ChapterNotificationSerializer, MangaListSerializer
from users.models import GENDER_SELECTION, CustomUser

from .models import Notification


class CustomRegisterSerializer(RegisterSerializer):
    """
    Serializer for user registration with additional fields.

    Handles gender, adult status, and avatar image.
    """

    gender = serializers.ChoiceField(choices=GENDER_SELECTION, required=True)
    adult = serializers.BooleanField(required=True)
    avatar = serializers.ImageField(
        default="static/images/avatars/user/none_avatar_user.jpg",
        allow_null=True,
        required=False,
    )

    def custom_signup(self, request, user):
        """
        Custom signup logic for user registration.

        Args:
            request: The request object.
            user: The user instance being registered.

        Returns:
            None
        """
        user.gender = self.validated_data.get("gender")
        user.avatar = self.validated_data.get("avatar")
        user.save(update_fields=["gender", "avatar"])


class CustomUserDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed user info including manga list and comments.

    Serializes user fields, manga list, and comments via methods.
    """

    list_manga = MangaListSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            "pk",
            "username",
            "email",
            "adult",
            "gender",
            "get_avatar_url",
            "list_manga",
            "comments",
        )

    def get_comments(self, obj):
        """
        Get comments for the user.

        Args:
            obj (CustomUser): User instance.

        Returns:
            list: List of serialized comments.
        """
        comments = Comment.objects.filter(user=obj)
        return CommentUserPageSerializer(comments, many=True).data


class CustomUserLastDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer for last user details (short info).

    Serializes username, slug, and avatar URL.
    """

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "slug",
            "get_avatar_url",
        )


class GenderUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user gender.
    """

    class Meta:
        model = CustomUser
        fields = ("gender",)


class AdultUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user adult status.
    """

    class Meta:
        model = CustomUser
        fields = ("adult",)


class AvatarUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user avatar image.
    """

    class Meta:
        model = CustomUser
        fields = ("avatar",)


class EmailUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user email address.
    """

    class Meta:
        model = CustomUser
        fields = ("email",)


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for user notifications about manga chapters.

    Serializes chapter, created_at, and is_read fields.
    """

    chapter = ChapterNotificationSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ("id", "chapter", "created_at", "is_read")
