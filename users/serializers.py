from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers


from manga.serializers import MangaListSerializer, ChapterSerializer
from users.models import GENDER_SELECTION, CustomUser
from .models import Notification


class CustomRegisterSerializer(RegisterSerializer):
    gender = serializers.ChoiceField(choices=GENDER_SELECTION, required=True)
    adult = serializers.BooleanField(required=True)
    avatar = serializers.ImageField(default='static/images/avatars/user/none_avatar_user.jpg', allow_null=True,
                                    required=False)

    def custom_signup(self, request, user):
        user.gender = self.validated_data.get('gender')
        user.avatar = self.validated_data.get('avatar')
        user.save(update_fields=['gender', 'avatar'])


class CustomUserDetailsSerializer(serializers.ModelSerializer):
    list_manga = MangaListSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = (
            'pk',
            'username',
            'email',
            'adult',
            'gender',
            'get_avatar',
            'list_manga',
        )

class CustomUserLastDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'username',
            'slug',
            'get_avatar',
        )

class GenderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('gender',)


class AdultUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('adult',)


class AvatarUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('avatar',)


class EmailUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('email',)


class NotificationSerializer(serializers.ModelSerializer):
    chapter = ChapterSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ('chapter',
                  'created_at',
                  'is_read')
