from rest_framework import serializers

from manga.models import Manga
from users.models import CustomUser

from .models import Comment, MangaRating


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model.

    Serializes manga, chapter, and content fields.
    """

    class Meta:
        model = Comment
        fields = ["manga", "chapter", "content"]


class CommentUserPageSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model with additional manga/chapter info.

    Adds manga_name, manga_url, chapter_name, chapter_url fields via methods.
    """

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
        """
        Get the manga name for the comment.

        Args:
            obj (Comment): Comment instance.

        Returns:
            str or None: Manga name or None.
        """
        return obj.manga.name_manga if obj.manga else None

    def get_manga_url(self, obj):
        """
        Get the manga URL for the comment.

        Args:
            obj (Comment): Comment instance.

        Returns:
            str or None: Manga URL or None.
        """
        return obj.manga.get_url() if obj.manga else None

    def get_chapter_name(self, obj):
        """
        Get the chapter name/number for the comment.

        Args:
            obj (Comment): Comment instance.

        Returns:
            int or None: Chapter number or None.
        """
        return obj.chapter.chapter_number if obj.chapter else None

    def get_chapter_url(self, obj):
        """
        Get the chapter URL (slug) for the comment.

        Args:
            obj (Comment): Comment instance.

        Returns:
            str or None: Chapter slug or None.
        """
        return obj.chapter.slug if obj.chapter else None


class CustomUserComentsSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomUser model for comments.

    Serializes username and slug fields.
    """

    class Meta:
        model = CustomUser
        fields = ("username", "slug")


class CommentGetSerializer(serializers.ModelSerializer):
    """
    Serializer for getting comment with user info.

    Serializes id, user, and content fields.
    """

    user = CustomUserComentsSerializer()

    class Meta:
        model = Comment
        fields = ["id", "user", "content"]


class MangaRatingSerializer(serializers.ModelSerializer):
    """
    Serializer for MangaRating model.

    Serializes rating and manga_slug fields. Handles creation and update of ratings.
    """

    manga_slug = serializers.SlugRelatedField(queryset=Manga.objects.all(), slug_field="slug", source="manga")

    class Meta:
        model = MangaRating
        fields = ["rating", "manga_slug"]

    def create(self, validated_data):
        """
        Create or update a MangaRating for the current user and manga.

        Args:
            validated_data (dict): Validated data for MangaRating.

        Returns:
            MangaRating: Created or updated MangaRating instance.
        """
        user = self.context["request"].user
        manga_slug = self.context["request"].data["manga_slug"]
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
