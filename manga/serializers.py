from rest_framework import serializers

from common.serializers import CommentSerializer
from .models import *


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ("first_name",
                  "last_name",
                  "get_absolute_url"
                  )



class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ("id",
                  "counts",)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("id",
                  "genr",)


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ("id",
                  "tag_name")


class CategorySerializer(serializers.ModelSerializer):
    accounts_items = serializers.SerializerMethodField()

    class Meta:
        fields = ("id",
                  "title",
                  'accounts_items',
                  'get_absolute_url',
                  )
        model = Category

    def get_accounts_items(self, obj):
        customer_account_query = Manga.objects.filter(
            category_id=obj.id)
        serializer = MangaSerializer(customer_account_query, many=True)

        return serializer.data


class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ("id",
                  "get_image",)



class ChapterSerializer(serializers.ModelSerializer):
    galleries = GallerySerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    class Meta:
        model = Chapter
        fields = ("id",
                  "num",
                  "get_absolute_url",
                  "title",
                  "time_prod",
                  "data_g",
                  "galleries",
                  'volumes',
                  'comments')


from rest_framework import serializers


class ChapterCreateSerializer(serializers.ModelSerializer):
    galleries = GallerySerializer(many=True)  # Вложенная сериализация
    class Meta:
        model = Chapter
        fields = (
            'id',
            'num',
            'title',
            'time_prod',
            'slug',
            'get_absolute_url',
            'galleries',
            'volumes'
        )

    def create(self, validated_data):
        galleries_data = validated_data.pop('galleries')  # Витягаємо дані для галерей
        volumes_data = validated_data.pop('volumes')  # Витягаємо дані для томів

        # Створюємо розділ
        chapter = Chapter.objects.create(**validated_data)

        # Створюємо пов'язані галереї
        for gallery_data in galleries_data:
            Gallery.objects.create(chapter=chapter, **gallery_data)

        return chapter


class ChapterUpdateSerializer(serializers.ModelSerializer):
    galleries = GallerySerializer(many=True)  # Вложенна серіалізація для Gallery
    class Meta:
        model = Chapter
        fields = (
            'id',  # Включите поле id
            'num',
            'title',
            'time_prod',
            'slug',
            'get_absolute_url',
            'galleries',
            'volumes'
        )

    def update(self, instance, validated_data):
        galleries_data = validated_data.pop('galleries')  # Извлекаем данные для galleries
        volumes_data = validated_data.pop('volumes')  # Извлекаем данные для томів

        # Оновлюємо поля моделі Chapter
        instance.num = validated_data.get('num', instance.num)
        instance.title = validated_data.get('title', instance.title)
        instance.time_prod = validated_data.get('time_prod', instance.time_prod)
        instance.slug = validated_data.get('slug', instance.slug)
        instance.save()

        # Оновлюємо пов'язані об'єкти Gallery
        for gallery_data in galleries_data:
            gallery_id = gallery_data.get('id', None)
            if gallery_id:
                gallery = Gallery.objects.get(id=gallery_id, chapter=instance)
                gallery.image = gallery_data.get('image', gallery.image)
                gallery.save()
            else:
                Gallery.objects.create(chapter=instance, **gallery_data)


        return instance




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


class ChapterlastSerializer(serializers.ModelSerializer):
    manga = MangalastSerializer()
    class Meta:
        model = Chapter
        fields = ['manga',
                  'num',
                  'volumes',
                  'data_g',
                  'title',
                  'slug']


class ChapterSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ("id",
                  "num",
                  "title",
                  'volumes',
                  "data_g",
                  "get_absolute_url",)


from rest_framework import serializers


class MangaCreateUpdateSerializer(serializers.ModelSerializer):
    counts = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all(), many=True)
    genre = serializers.PrimaryKeyRelatedField(queryset=Genre.objects.all(), many=True)
    chapter = serializers.PrimaryKeyRelatedField(queryset=Chapter.objects.all(), many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tags.objects.all(), many=True)
    review = serializers.CharField(max_length=1000)
    thumbnail = serializers.ImageField(write_only=True)
    avatar = serializers.ImageField(write_only=True)

    class Meta:
        model = Manga
        fields = (
            'id',
            'name_manga',
            'name_original',
            'author',
            'time_prod',
            'counts',
            'genre',
            'chapter',
            'tags',
            'review',
            'thumbnail',
            'avatar',
            'slug',
            'get_thumbnail',
            'get_avatar',
            'get_absolute_url',

        )


class MangaSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(many=True, read_only=True)
    counts = CountrySerializer(many=True, read_only=True)
    chapter = ChapterSimpleSerializer(many=True, read_only=True)
    tags = TagsSerializer(many=True, read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
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
                  'genre',
                  'chapter',
                  'tags',
                  'comments',
                  'review',
                  'get_thumbnail',
                  'get_avatar',
                  'get_absolute_url',

                  )


