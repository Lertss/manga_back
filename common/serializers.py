from rest_framework import serializers

from manga.models import Manga
from users.models import CustomUser
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'manga',
            'chapter',
            'content'
        ]
class CustomUserComentsSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'slug'
        )

class CommentGetSerializer(serializers.ModelSerializer):
    user = CustomUserComentsSerializer()
    class Meta:
        model = Comment
        fields = [
            'id',
            'user',
            'content'
        ]


from rest_framework import serializers
from .models import MangaRating


class MangaRatingSerializer(serializers.ModelSerializer):
    manga_slug = serializers.SlugRelatedField(
        queryset=Manga.objects.all(),
        slug_field='slug',
        source='manga'
    )

    class Meta:
        model = MangaRating
        fields = [f'rating', 'manga_slug']

    def create(self, validated_data):
        user = self.context['request'].user
        manga_slug = self.context['request'].data['manga_slug']  # Припустимо, що дані надходять в запиті
        manga = Manga.objects.get(slug=manga_slug)

        # Перевірка чи оцінка вже існує для цього користувача та манги
        existing_rating = MangaRating.objects.filter(user=user, manga=manga).first()
        if existing_rating:
            # Якщо оцінка вже існує, просто оновлюємо її
            existing_rating.rating = validated_data['rating']
            existing_rating.save()
            return existing_rating

        validated_data['user'] = user
        validated_data['manga'] = manga
        return super().create(validated_data)
