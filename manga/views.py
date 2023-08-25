from django.http import Http404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView

from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from .serializers import *


class MangaListHome(APIView):
    def get(self, request, format=None):
        manga = Manga.objects.all()
        serializer_all = MangaSerializer(manga, many=True)
        last_manga = Manga.objects.order_by('-time_prod')[:10]
        serializer_lastmanga = MangaSerializer(last_manga, many=True)
        last_chapter = Chapter.objects.all()
        #
        serializer_chapter = ChapterSerializer(last_chapter, many=True)

        serializer = [serializer_lastmanga.data, serializer_all.data, serializer_chapter.data]
        return Response(serializer)


class allManga(APIView):
    def get(self, request, ):
        manga = Manga.objects.all()
        serializer = MangalastSerializer(manga, many=True)
        return Response(serializer.data)


class ShowManga(APIView):
    def get_object(self, manga_slug):
        try:
            return Manga.objects.get(slug=manga_slug)
        except Manga.DoesNotExist:
            raise Http404

    def get(self, request, manga_slug, format=None):
        category = self.get_object(manga_slug)
        serializer = MangaSerializer(category)
        return Response(serializer.data)


# class ShowManga(APIView):
#     def get(self):
#         id = 1
#         person = Manga.objects.get(pk=id)
#         serializer = MangaSerializer(person, many=True)
#         return Response(serializer.data)


class MangaCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Manga.objects.all()
    serializer_class = MangaCreateUpdateSerializer


class MangaUpdateView(RetrieveUpdateAPIView):
    queryset = Manga.objects.all()
    serializer_class = MangaCreateUpdateSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticated]


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class AllFilter(APIView):
    def get(self, request, format=None):
        authors = Author.objects.all()
        countries = Country.objects.all()
        genres = Genre.objects.all()
        tags = Tag.objects.all()
        categories = Category.objects.all()

        author_serializer = AuthorSerializer(authors, many=True)
        country_serializer = CountrySerializer(countries, many=True)
        genre_serializer = GenreSerializer(genres, many=True)
        tags_serializer = TagsSerializer(tags, many=True)
        category_serializer = CategorySerializer(categories, many=True)

        data = {
            'authors': author_serializer.data,
            'countries': country_serializer.data,
            'genres': genre_serializer.data,
            'tags': tags_serializer.data,

        }

        return Response(data, status=status.HTTP_200_OK)

















from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from .models import Chapter, Page
from .serializers import ChapterSerializer, PageSerializer

class ChapterViewSet(viewsets.ModelViewSet):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer

    def create(self, request, *args, **kwargs):
        pages_data = request.data.pop('image', [])
        numb = request.data.pop('page_number', [])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        chapter_instance = serializer.instance
        print(chapter_instance)# Отримати створений екземпляр розділу
        for image, page_number in zip(pages_data, numb):
            Page.objects.create(chapter=chapter_instance, image=image, page_number=page_number)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        pages_data = request.data.pop('pages', [])  # Оновити налаштування ключа для сторінок
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Оновити сторінки
        for page_data in pages_data:
            page_id = page_data.get('id', None)
            if page_id:
                page_instance = Page.objects.get(id=page_id)
                PageSerializer(page_instance, data=page_data, partial=True).is_valid(raise_exception=True)
                page_instance.save()

        return Response(serializer.data)
    @action(detail=True, methods=['patch'], url_path='update-title')
    def update_title(self, request, pk=None):
        instance = self.get_object()
        title = request.data.get('title')
        if title is not None:
            instance.title = title
            instance.save()
            return Response({'message': 'Title updated successfully.'})
        return Response({'error': 'Title field is required.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='update-volume')
    def update_volume(self, request, pk=None):
        instance = self.get_object()
        volume = request.data.get('volume')
        if volume is not None:
            instance.volume = volume
            instance.save()
            return Response({'message': 'Volume updated successfully.'})
        return Response({'error': 'Volume field is required.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='update-chapter-number')
    def update_chapter_number(self, request, pk=None):
        instance = self.get_object()
        chapter_number = request.data.get('chapter_number')
        if chapter_number is not None:
            instance.chapter_number = chapter_number
            instance.save()
            return Response({'message': 'Chapter number updated successfully.'})
        return Response({'error': 'Chapter number field is required.'}, status=status.HTTP_400_BAD_REQUEST)


class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    parser_classes = (MultiPartParser, FormParser)
