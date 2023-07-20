from rest_framework import serializers

from .models import *


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ("first_name",
                  "last_name",
                  "get_absolute_url"
                  )
        # extra_kwargs = {'actors': {'required': False}}


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
        model = Categorys

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



class GlawaSerializer(serializers.ModelSerializer):
    galleries = GallerySerializer(many=True, read_only=True)

    class Meta:
        model = Glawa
        fields = ("id",
                  "num",
                  "get_absolute_url",
                  "title",
                  "time_prod",
                  "data_g",
                  "galleries",)

class GlawaSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Glawa
        fields = ("id",
                  "num",
                  "title",
                  "get_absolute_url",
                  "data_g")

class MangaSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(many=True, read_only=True)
    counts = CountrySerializer(many=True, read_only=True)
    glaws = GlawaSimpleSerializer(many=True, read_only=True)
    tags = TagsSerializer(many=True, read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    class Meta:
        model = Manga
        fields = ('id',
                  'name_manga',
                  'name_original',
                  'author',
                  'time_prod',
                  'counts',
                  'genre',
                  'glaws',
                  'tags',
                  'review',
                  'get_thumbnail',
                  'get_avatar',
                  'get_absolute_url',
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



class GlawalastSerializer(serializers.ModelSerializer):
    manga = MangalastSerializer()

    class Meta:
        model = Glawa
        fields = ['manga', 'num', 'data_g', 'title', 'slug']
