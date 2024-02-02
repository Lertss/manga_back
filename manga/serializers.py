from manga.models import Author, Category, Chapter, Country, Genre, Manga, Page, Tag
from rest_framework import serializers
from users.models import MangaList


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = "__all__"


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = (
            "id",
            "counts",
        )


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = (
            "id",
            "genr_name",
        )


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "tag_name")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "cat_name",
        )


class MangaLastSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        model = Manga
        fields = ["id", "name_manga", "name_original", "english_only_field", "average_rating", "thumbnail", "url"]

    def get_thumbnail(self, obj):
        return obj.get_thumbnail()

    def get_url(self, obj):
        return obj.get_absolute_url()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["thumbnail"] = instance.get_thumbnail()
        representation["url"] = instance.get_absolute_url()
        return representation


class MangaRandomSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    category_title = serializers.SerializerMethodField()

    class Meta:
        model = Manga
        fields = ["name_manga", "review", "thumbnail", "url", "category_title"]

    def get_thumbnail(self, obj):
        return obj.get_thumbnail()

    def get_url(self, obj):
        return obj.get_absolute_url()

    def get_category_title(self, obj):
        return obj.category.cat_name


class ChapterViewsMangaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ("id", "manga", "title", "volume", "chapter_number", "slug")


class MangaCreateUpdateSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field="id", queryset=Author.objects.all(), many=True)
    counts = serializers.SlugRelatedField(slug_field="id", queryset=Country.objects.all(), many=True)
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
            "time_prod",
            "counts",
            "genre",
            "decency",
            "tags",
            "review",
            "avatar",
        )


class MangaSerializer(serializers.ModelSerializer):
    from common.serializers import CommentSerializer

    author = AuthorSerializer(many=True, read_only=True)
    counts = CountrySerializer(many=True, read_only=True)
    tags = TagsSerializer(many=True, read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    chapters = ChapterViewsMangaSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    category_title = serializers.SerializerMethodField()

    class Meta:
        model = Manga
        fields = (
            "id",
            "name_manga",
            "name_original",
            "english_only_field",
            "author",
            "time_prod",
            "counts",
            "decency",
            "chapters",
            "genre",
            "tags",
            "comments",
            "review",
            "get_avatar",
            "average_rating",
            "category_title",
            "get_absolute_url",
        )

    def get_average_rating(self, obj):
        return obj.average_rating()

    def get_category_title(self, obj):
        return obj.category.cat_name


class MangaListSerializer(serializers.ModelSerializer):
    manga = MangaLastSerializer()

    class Meta:
        model = MangaList
        fields = (
            "id",
            "name",
            "user",
            "manga",
        )


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ("id", "image", "get_image", "page_number")


class ChapterSerializer(serializers.ModelSerializer):
    pages = PageSerializer(many=True, required=False)

    class Meta:
        model = Chapter
        fields = ("id", "manga", "title", "volume", "chapter_number", "pages", "slug")


class LastChapterSerializer(serializers.ModelSerializer):
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
