from rest_framework import serializers

from manga.models import Author, Category, Chapter, Country, Genre, Manga, Page, Tag
from users.models import MangaList


class AuthorSerializer(serializers.ModelSerializer):
    """
    Serializer for Author model.

    Serializes all fields of Author.
    """

    class Meta:
        model = Author
        fields = (
            "first_name",
            "last_name",
        )


class CountrySerializer(serializers.ModelSerializer):
    """
    Serializer for Country model.

    Serializes country_name fields.
    """

    class Meta:
        model = Country
        fields = ("country_name",)


class GenreSerializer(serializers.ModelSerializer):
    """
    Serializer for Genre model.

    Serializes genre_name fields.
    """

    class Meta:
        model = Genre
        fields = ("genre_name",)


class TagsSerializer(serializers.ModelSerializer):
    """
    Serializer for Tag model.

    Serializes tag_name fields.
    """

    class Meta:
        model = Tag
        fields = ("tag_name",)


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model.

    Serializes category_name fields.
    """

    class Meta:
        model = Category
        fields = ("category_name",)


class MangaLastSerializer(serializers.ModelSerializer):
    """
    Serializer for Manga model for last/top manga listings.

    Adds thumbnail and url fields via methods.
    """

    thumbnail = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        model = Manga
        fields = [
            "name_manga",
            "average_rating",
            "thumbnail",
            "url",
        ]

    def get_thumbnail_url(self, obj):
        """
        Get the thumbnail URL for the manga object.

        Args:
            obj (Manga): Manga instance.

        Returns:
            str: Thumbnail URL.
        """
        return obj.get_thumbnail_url()

    def get_url(self, obj):
        """
        Get the absolute URL for the manga object.

        Args:
            obj (Manga): Manga instance.

        Returns:
            str: Absolute URL.
        """
        return obj.get_absolute_url()

    def to_representation(self, instance):
        """
        Customize the representation of the manga instance.

        Args:
            instance (Manga): Manga instance.

        Returns:
            dict: Serialized data with thumbnail and url.
        """
        representation = super().to_representation(instance)
        representation["thumbnail"] = instance.get_thumbnail_url()
        representation["url"] = instance.get_absolute_url()
        return representation


class MangaRandomSerializer(MangaLastSerializer):
    """
    Serializer for random manga selection.

    Adds category_title field via method.
    """

    category_title = serializers.SerializerMethodField()

    class Meta:
        model = Manga
        fields = ["name_manga", "review", "get_thumbnail_url", "url", "category_title"]

    def get_category_title(self, obj):
        """
        Get the category title for the manga object.

        Args:
            obj (Manga): Manga instance.

        Returns:
            str: Category name.
        """
        return obj.category.category_name


class ChapterViewsMangaSerializer(serializers.ModelSerializer):
    """
    Serializer for Chapter model for manga views.

    Serializes basic chapter fields.
    """

    class Meta:
        model = Chapter
        fields = (
            "manga",
            "title",
            "volume",
            "chapter_number",
            "slug",
        )


class MangaCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating Manga model.

    Uses SlugRelatedField for relations and validates review and avatar.
    """

    author = serializers.SlugRelatedField(slug_field="id", queryset=Author.objects.all(), many=True)
    country = serializers.SlugRelatedField(slug_field="id", queryset=Country.objects.all(), many=True)
    genre = serializers.SlugRelatedField(slug_field="id", queryset=Genre.objects.all(), many=True)
    tags = serializers.SlugRelatedField(slug_field="id", queryset=Tag.objects.all(), many=True)
    review = serializers.CharField(max_length=1000)
    avatar = serializers.ImageField(write_only=True)

    class Meta:
        model = Manga
        fields = (
            "category",
            "name_manga",
            "name_original",
            "english_only_field",
            "author",
            "created_at",
            "country",
            "genre",
            "decency",
            "tags",
            "review",
            "avatar",
        )


class MangaSerializer(serializers.ModelSerializer):
    """
    Full serializer for Manga model with nested relations and comments.

    Serializes all main fields, relations, and computed fields.
    """

    from common.serializers import CommentSerializer

    author = AuthorSerializer(many=True, read_only=True)
    country = CountrySerializer(many=True, read_only=True)
    tags = TagsSerializer(many=True, read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    chapters = ChapterViewsMangaSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    category_title = serializers.SerializerMethodField()

    class Meta:
        model = Manga
        fields = (
            "name_manga",
            "name_original",
            "english_only_field",
            "author",
            "created_at",
            "country",
            "decency",
            "chapters",
            "genre",
            "tags",
            "comments",
            "review",
            "get_avatar_url",
            "average_rating",
            "category_title",
            "get_absolute_url",
        )

    def get_average_rating(self, obj):
        """
        Get the average rating for the manga object.

        Args:
            obj (Manga): Manga instance.

        Returns:
            float or None: Average rating or None if no ratings exist.
        """
        return obj.average_rating

    def get_category_title(self, obj):
        """
        Get the category title for the manga object.

        Args:
            obj (Manga): Manga instance.

        Returns:
            str: Category name.
        """
        return obj.category.category_name


class MangaAllSerializer(serializers.ModelSerializer):
    """
    Serializer for the Manga model for display in the catalog.

    Serializes the main fields required for display in the catalog, relationships, and calculated fields.
    """

    author = AuthorSerializer(many=True, read_only=True)
    country = CountrySerializer(many=True, read_only=True)
    tags = TagsSerializer(many=True, read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    chapters = ChapterViewsMangaSerializer(many=True, read_only=True)
    category_title = serializers.SerializerMethodField()

    class Meta:
        model = Manga
        fields = (
            "name_manga",
            "author",
            "created_at",
            "country",
            "decency",
            "chapters",
            "genre",
            "tags",
            "get_avatar_url",
            "average_rating",
            "category_title",
            "get_absolute_url",
        )

    def get_average_rating(self, obj):
        """
        Get the average rating for the manga object.

        Args:
            obj (Manga): Manga instance.

        Returns:
            float or None: Average rating or None if no ratings exist.
        """
        return obj.average_rating

    def get_category_title(self, obj):
        """
        Get the category title for the manga object.

        Args:
            obj (Manga): Manga instance.

        Returns:
            str: Category name.
        """
        return obj.category.category_name


class MangaListSerializer(serializers.ModelSerializer):
    """
    Serializer for MangaList model.

    Serializes user, manga, and name fields.
    """

    manga = MangaLastSerializer()

    class Meta:
        model = MangaList
        fields = (
            "name",
            "user",
            "manga",
        )


class PageSerializer(serializers.ModelSerializer):
    """
    Serializer for Page model.

    Serializes image, get_image, and page_number fields.
    """

    class Meta:
        model = Page
        fields = ("image", "get_image", "page_number")


class ChapterSerializer(serializers.ModelSerializer):
    """
    Serializer for Chapter model with nested pages.

    Serializes chapter fields and related pages.
    """

    pages = PageSerializer(many=True, required=False)

    class Meta:
        model = Chapter
        fields = ("manga", "title", "volume", "chapter_number", "pages", "slug")


class LastChapterSerializer(serializers.ModelSerializer):
    """
    Serializer for last chapter info.

    Serializes title, volume, chapter_number, data_g, and slug fields.
    """

    class Meta:
        model = Chapter
        fields = (
            "title",
            "volume",
            "chapter_number",
            "data_g",
            "slug",
        )


class ChapterNotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for chapter notifications.

    Serializes manga, volume, chapter_number, data_g, and slug fields.
    """

    manga = MangaLastSerializer(read_only=True)

    class Meta:
        model = Chapter
        fields = (
            "manga",
            "volume",
            "chapter_number",
            "data_g",
            "slug",
        )
