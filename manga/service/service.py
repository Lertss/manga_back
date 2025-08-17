import json
import random
from datetime import timedelta

from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from common.models import Comment
from manga.models import Author, Category, Chapter, Country, Genre, Manga, Page, Tag
from manga.serializers import (
    AuthorSerializer,
    CategorySerializer,
    CountrySerializer,
    GenreSerializer,
    LastChapterSerializer,
    MangaLastSerializer,
    MangaRandomSerializer,
    TagsSerializer,
)
from users.models import MangaList


def filtering_and_exclusion(self) -> Manga:
    genres = self.request.query_params.getlist("genres")
    tags = self.request.query_params.getlist("tags")
    countries = self.request.query_params.getlist("country_name")
    categories = self.request.query_params.getlist("category")
    min_rating = self.request.query_params.get("min_rating")

    queryset = Manga.objects.all()

    for genre in genres:
        queryset = queryset.filter(genre__genre_name=genre)
    for tag in tags:
        queryset = queryset.filter(tags__tag_name=tag)
    for count in countries:
        queryset = queryset.filter(country__country_name=count)
    for category in categories:
        queryset = queryset.filter(category__category_name=category)

    filter_params = {
        "genres": "genre__genre_name",
        "tags": "tags__tag_name",
        "countries": "country__country_name",
        "categories": "category__category_name",
    }
    # We exclude with a loop
    for param, model_field in filter_params.items():
        excluded_values = self.request.query_params.getlist("exclude_" + param)
        if excluded_values:
            queryset = queryset.exclude(**{model_field + "__in": excluded_values})
    # Filter by decency field
    decency = self.request.query_params.get("decency")
    if decency in ["true", "false"]:
        queryset = queryset.filter(decency=(decency == "true"))

    if min_rating is not None:
        min_rating = int(min_rating)
        # Filter manga with an average rating greater than or equal to min_rating
        queryset = queryset.annotate(avg_rating=Avg("ratings__rating")).filter(avg_rating__gte=min_rating)

    return queryset


def get_manga_objects(manga_slug) -> Manga:
    """Returns a manga object"""
    return Manga.objects.get(slug=manga_slug)


def update_field_manga(view, request, field_name, instance_field, error_message):
    """The function is designed to update a specific text field in a Manga model object"""
    instance = view.get_object()
    field_value = request.data.get(field_name)

    if field_value is not None:
        setattr(instance, instance_field, field_value)
        instance.save()
        return Response({"message": f"{field_name} updated successfully."})

    return Response(
        {"error": f"{field_name} field is required."},
        status=status.HTTP_400_BAD_REQUEST,
    )


def update_field_key_manga(view, instance, field_name, data_key, success_message):
    """The function is designed to update a specific key field to another object in a Manga model object"""
    field_ids = view.request.data.getlist(data_key)

    if field_ids is not None:
        getattr(instance, field_name).clear()
        getattr(instance, field_name).add(*field_ids)
        return Response({"message": success_message})

    return Response(
        {"error": f"{field_name} field is required."},
        status=status.HTTP_400_BAD_REQUEST,
    )


def update_category_field_manga(view, instance, category_id):
    """The function is intended to update the manga category in the Manga model object"""
    if category_id is not None:
        try:
            category_instance = get_object_or_404(Category, id=category_id)
            instance.category = category_instance
            instance.save()
            return Response({"message": "The category has been successfully updated."})
        except Category.DoesNotExist:
            return Response({"error": "Category not found."}, status=status.HTTP_400_BAD_REQUEST)

    return Response(
        {"error": "The 'category' field is required."},
        status=status.HTTP_400_BAD_REQUEST,
    )


def update_decency_field_manga(view, instance, decency):
    """The function is intended to update the age category of the manga in the Manga model object"""
    if decency is not None:
        decency = json.loads(decency.lower())
        instance.decency = decency
        instance.save()
        return Response({"message": "Decency updated successfully."})

    return Response({"error": "Decency field is required."}, status=status.HTTP_400_BAD_REQUEST)


def data_filter():
    """Returns a list of filter objects"""
    data = {
        "authors": AuthorSerializer(Author.objects.all(), many=True).data,
        "countries": CountrySerializer(Country.objects.all(), many=True).data,
        "genres": GenreSerializer(Genre.objects.all(), many=True).data,
        "tags": TagsSerializer(Tag.objects.all(), many=True).data,
        "categories": CategorySerializer(Category.objects.all(), many=True).data,
    }
    return data


def create_page_chapter(chapter_instance, image, page_number):
    """Request to create a page"""
    Page.objects.create(chapter=chapter_instance, image=image, page_number=page_number)


def update_field_chapter(self, request, field_name, success_message):
    """Update a specific field in the Chapter model object"""
    instance = self.get_object()
    field_value = request.data.get(field_name)
    if field_value is not None:
        setattr(instance, field_name, field_value)
        instance.save()
        return Response({"message": success_message})
    return Response(
        {"error": f"{field_name} field is required."},
        status=status.HTTP_400_BAD_REQUEST,
    )


def create_comment(request_user, **kwargs):
    """Creating a request to create a comment"""
    Comment.objects.create(user=request_user, **kwargs)


def mangalist_get_or_create(request):
    """Uses the get_or_create method provided by the Django ORM to get an instance of the MangaList model or create
    one if it does not exist."""
    return MangaList.objects.get_or_create(
        user=request.user,
        manga=get_manga_objects(request.data.get("slug")),
        defaults={"name": request.data.get("name")},
    )


def mangalist_remove(request):
    """Uses a Django model named MangaList to retrieve a specific MangaList object for later deletion"""
    return MangaList.objects.filter(user=request.user, manga__slug=request.data.get("slug")).first()


def mangalist_filter(request, manga_slug):
    """Uses a Django model named MangaList to get a specific MangaList object"""
    return MangaList.objects.filter(user=request.user, manga__slug=manga_slug).first()


def mangalist_filter_by_user(request_user):
    """Gets a list of MangaList objects that are associated with a specific user"""
    return MangaList.objects.filter(user=request_user)


def top_manga_objects_annotate_serializer():
    """Returns a list of top (best) manga objects and return them as serialized data"""
    return MangaLastSerializer(
        Manga.objects.annotate(avg_rating=Avg("ratings__rating")).order_by("-avg_rating")[:100],
        many=True,
    )


def top_manga_last_year_filter_serializer():
    """Returns a list of the top (best) manga titles released in the last year, and return them as serialized data."""
    last_year = timezone.now() - timedelta(days=365)
    top_manga_last_year = (
        Manga.objects.filter(created_at__gte=last_year)
        .annotate(avg_rating=Avg("ratings__rating"))
        .order_by("-avg_rating")[:100]
    )
    return MangaLastSerializer(top_manga_last_year, many=True)


def top_manga_comments_annotate_serializer():
    """Returns a list of top manga objects by number of comments and return them as serialized data"""
    top_manga_comments = Manga.objects.annotate(num_comments=Count("comment")).order_by("-num_comments")[:100]
    return MangaLastSerializer(top_manga_comments, many=True)


def random_manga():
    """Designed to select and return data about random manga objects"""
    manga_count = Manga.objects.count()

    if manga_count == 0:
        raise NotFound(detail="Не знайдено жодної манги в базі даних")

    if manga_count >= 2:
        random_indexes = random.sample(range(1, manga_count + 1), 2)
        random_manga = Manga.objects.filter(pk__in=random_indexes)
        if random_manga.count() < 2:  # Якщо не всі об'єкти знайдені
            random_manga = list(Manga.objects.all()[:2])
    else:
        # Якщо є тільки одна манга, повертаємо її двічі
        manga = get_object_or_404(Manga, pk=1)
        random_manga = [manga, manga]

    return MangaRandomSerializer(random_manga, many=True).data


def one_hundred_last_added_chapters():
    """Designed to receive and return information about the last hundred added chapters of a manga"""
    # Get the last hundred chapters
    last_hundred_chapters = Chapter.objects.order_by("-id")[:100]

    chapter_data = []
    for chapter in last_hundred_chapters:
        chapter_serializer = LastChapterSerializer(chapter)
        manga_serializer = MangaLastSerializer(chapter.manga)

        # Get data from serializers
        serialized_chapter = chapter_serializer.data
        serialized_manga = manga_serializer.data

        # Add manga data to chapter data
        serialized_chapter["manga"] = serialized_manga

        chapter_data.append(serialized_chapter)

    return chapter_data
