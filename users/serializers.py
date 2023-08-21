from dj_rest_auth.registration.serializers import RegisterSerializer

from common.serializers import CommentSerializer
from manga.serializers import MangalastSerializer, MangaListSerializer, ChapterSerializer
from users.models import GENDER_SELECTION, CustomUser, MangaList
from rest_framework import serializers


from rest_framework import serializers


class CustomRegisterSerializer(RegisterSerializer):
    gender = serializers.ChoiceField(choices=GENDER_SELECTION, required=True)
    adult = serializers.BooleanField(required=True)
    avatar = serializers.ImageField(default='static/images/avatars/user/none_avatar_user.jpg', allow_null=True, required=False)

    def custom_signup(self, request, user):
        user.gender = self.validated_data.get('gender')
        user.avatar = self.validated_data.get('avatar')
        user.save(update_fields=['gender', 'avatar'])



class CustomUserDetailsSerializer(serializers.ModelSerializer):
    list_manga = MangaListSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
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
            'comments'
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







from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    chapter = ChapterSerializer(read_only=True)
    class Meta:
        model = Notification
        fields = ('chapter',
                  'created_at',
                  'is_read')
