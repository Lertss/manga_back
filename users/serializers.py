from dj_rest_auth.registration.serializers import RegisterSerializer

from users.models import GENDER_SELECTION, CustomUser, MangaList
from rest_framework import serializers


class CustomRegisterSerializer(RegisterSerializer):
    gender = serializers.ChoiceField(choices=GENDER_SELECTION, required=True)
    birthdate = serializers.DateField(required=True)
    avatar = serializers.ImageField(default='default/none_avatar_user.png/', allow_null=True, required=False)

    def save(self, request):
        user = super().save(request)
        user.gender = self.validated_data.get('gender')
        user.birthdate = self.validated_data.get('birthdate')
        user.avatar = self.validated_data.get('avatar')
        user.save()
        return user

class MangaListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MangaList
        fields = '__all__'  # Або перерахуйте поля, які ви хочете включити в серіалайзер

class CustomUserDetailsSerializer(serializers.ModelSerializer):
    mangalist = MangaListSerializer(many=True, read_only=True)
    class Meta:
        model = CustomUser
        fields = (
            'pk',
            'email',
            'birthdate',
            'gender',
            'mangalist'
        )

