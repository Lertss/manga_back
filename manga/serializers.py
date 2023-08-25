from rest_framework import serializers

from common.serializers import CommentSerializer
from users.models import MangaList
from .models import *


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ("id",
                  "counts",)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("id",
                  "genr_name",)


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id",
                  "tag_name")


class CategorySerializer(serializers.ModelSerializer):
    accounts_items = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("id",
                  "title",
                  )





class MangalastSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        model = Manga
        fields = ['name_manga', 'thumbnail', 'url']

    def get_thumbnail(self, obj):
        return obj.get_thumbnail()

    def get_url(self, obj):
        return obj.get_absolute_url()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['thumbnail'] = instance.get_thumbnail()
        representation['url'] = instance.get_absolute_url()
        return representation



class ChapterViewsMangaSerializer(serializers.ModelSerializer):


    class Meta:
        model = Chapter
        fields = ('id',
                  'manga',
                  'title',
                  'volume',
                  'chapter_number',
                  'slug')



class MangaCreateUpdateSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='id', queryset=Author.objects.all(), many=True)
    counts = serializers.SlugRelatedField(slug_field='id', queryset=Country.objects.all(), many=True)
    genre = serializers.SlugRelatedField(slug_field='id', queryset=Genre.objects.all(), many=True)
    tags = serializers.SlugRelatedField(slug_field='id', queryset=Tag.objects.all(), many=True)
    review = serializers.CharField(max_length=1000)
    avatar = serializers.ImageField(write_only=True)

    class Meta:
        model = Manga
        fields = (
            'category',
            'name_manga',
            'name_original',
            'english_only_field',
            'author',
            'time_prod',
            'counts',
            'genre',
            'decency',
            'tags',
            'review',
            'avatar',
        )


class MangaSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(many=True, read_only=True)
    counts = CountrySerializer(many=True, read_only=True)
    tags = TagsSerializer(many=True, read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    chapters = ChapterViewsMangaSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Manga
        fields = ('id',
                  'name_manga',
                  'name_original',
                  'english_only_field',
                  'average_rating',
                  'total_ratings',
                  'author',
                  'time_prod',
                  'counts',
                  'decency',
                  'chapters',
                  'genre',
                  'tags',
                  'comments',
                  'review',
                  'get_avatar',
                  )


class MangaListSerializer(serializers.ModelSerializer):
    manga = MangalastSerializer()

    class Meta:
        model = MangaList
        fields = (
            'id',
            'name',
            'user',
            'manga',
        )






from rest_framework import serializers
from .models import Chapter, Page

class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ('id',
                  'image',
                  'page_number')

class ChapterSerializer(serializers.ModelSerializer):
    pages = PageSerializer(many=True, required=False)  # Додайте required=False


    class Meta:
        model = Chapter
        fields = ('id',
                  'manga',
                  'title',
                  'volume',
                  'chapter_number',
                  'pages',
                  'slug')



class LastChapterSerializer(serializers.ModelSerializer):
    manga = MangalastSerializer(many=True, read_only=True)


    class Meta:
        model = Chapter
        fields = ('manga',
                  'title',
                  'volume',
                  'chapter_number',
                  'slug')