from manga.models import Manga
from rest_framework import serializers
from users.models import CustomUser

from .models import Comment, MangaRating


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["manga", "chapter", "content"]


class CommentUserPageSerializer(serializers.ModelSerializer):
    manga_name = serializers.SerializerMethodField()
    manga_url = serializers.SerializerMethodField()
    chapter_name = serializers.SerializerMethodField()
    chapter_url = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "manga",
            "manga_name",
            "manga_url",
            "chapter",
            "chapter_name",
            "chapter_url",
            "content",
        ]

    def get_manga_name(self, obj):
        return obj.manga.name_manga if obj.manga else None

    def get_manga_url(self, obj):
        return obj.manga.get_absolute_url() if obj.manga else None

    def get_chapter_name(self, obj):
        return obj.chapter.chapter_number if obj.chapter else None

    def get_chapter_url(self, obj):
        return obj.chapter.slug if obj.chapter else None


class CustomUserComentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("username", "slug")


class CommentGetSerializer(serializers.ModelSerializer):
    user = CustomUserComentsSerializer()

    class Meta:
        model = Comment
        fields = ["id", "user", "content"]


class MangaRatingSerializer(serializers.ModelSerializer):
    manga_slug = serializers.SlugRelatedField(queryset=Manga.objects.all(), slug_field="slug", source="manga")

    class Meta:
        model = MangaRating
        fields = ["rating", "manga_slug"]

    def create(self, validated_data):
        user = self.context["request"].user
        manga_slug = self.context["request"].data["manga_slug"]  # Suppose that the data comes in a request
        manga = Manga.objects.get(slug=manga_slug)

        # Check whether a rating already exists for this user and manga
        existing_rating = MangaRating.objects.filter(user=user, manga=manga).first()
        if existing_rating:
            # If the assessment already exists, just update it
            existing_rating.rating = validated_data["rating"]
            existing_rating.save()
            return existing_rating

        validated_data["user"] = user
        validated_data["manga"] = manga
        return super().create(validated_data)
