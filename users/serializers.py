from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers

from common.models import Comment
from common.serializers import CommentUserPageSerializer
from manga.serializers import ChapterNotificationSerializer, MangaListSerializer
from users.models import GENDER_SELECTION, CustomUser

from .models import Notification


class CustomRegisterSerializer(RegisterSerializer):
    gender = serializers.ChoiceField(choices=GENDER_SELECTION, required=True)
    adult = serializers.BooleanField(required=True)
    avatar = serializers.ImageField(
        default="static/images/avatars/user/none_avatar_user.jpg",
        allow_null=True,
        required=False,
    )

    def custom_signup(self, request, user):
        user.gender = self.validated_data.get("gender")
        user.avatar = self.validated_data.get("avatar")
        user.save(update_fields=["gender", "avatar"])


class CustomUserDetailsSerializer(serializers.ModelSerializer):
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
        comments = Comment.objects.filter(user=obj)
        return CommentUserPageSerializer(comments, many=True).data


class CustomUserLastDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "username",
            "slug",
            "get_avatar_url",
        )


class GenderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("gender",)


class AdultUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("adult",)


class AvatarUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("avatar",)


class EmailUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("email",)


class NotificationSerializer(serializers.ModelSerializer):
    chapter = ChapterNotificationSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ("id", "chapter", "created_at", "is_read")
