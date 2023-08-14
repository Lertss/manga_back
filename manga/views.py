from django.db.models import Q
from django.http import Http404
from django.shortcuts import render
from rest_framework import generics, viewsets

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .serializers import *
from .models import Manga


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


class ChapterListView(APIView):
    def get(self, request):
        chapters = Chapter.objects.all()
        serializer = ChapterlastSerializer(chapters, many=True, context={'request': request})
        return Response(serializer.data)



class allManga(APIView):
    def get(self, request, ):
        chapters = Chapter.objects.all()
        serializere = ChapterSerializer(chapters, many=True)
        print(serializere.data)
        manga = Manga.objects.all()
        serializer = MangaSerializer(manga, many=True)
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

class ShowChapter(APIView):  # ShowChapter
    def get_object(self, manga_slug, chapter_slug):
        try:
            return Chapter.objects.filter(manga__slug=manga_slug).get(slug=chapter_slug)
        except Chapter.DoesNotExist:
            raise Http404

    def get(self, request, manga_slug, chapter_slug, format=None):
        chapter = self.get_object(manga_slug, chapter_slug)
        serializer = ChapterSerializer(chapter)
        return Response(serializer.data)









from rest_framework.generics import CreateAPIView
from .serializers import ChapterSerializer

from rest_framework.generics import RetrieveUpdateAPIView
from .models import Chapter
from .serializers import ChapterSerializer

from rest_framework.generics import CreateAPIView
from .serializers import ChapterSerializer

from rest_framework.generics import RetrieveUpdateAPIView
from .serializers import MangaCreateUpdateSerializer

from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

class MangaCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Manga.objects.all()
    serializer_class = MangaCreateUpdateSerializer

    def perform_create(self, serializer):
        thumbnail = self.request.data.get('thumbnail')
        avatar = self.request.data.get('avatar')
        counts = self.request.data.get('counts')
        genre = self.request.data.get('genre')
        chapters = self.request.data.get('chapter')
        tags = self.request.data.get('tags')
        review = self.request.data.get('review')

        manga = serializer.save(
            thumbnail=thumbnail,
            avatar=avatar,
            # Другие поля
        )

        manga.counts.set(counts)
        manga.genre.set(genre)
        manga.chapter.set(chapters)
        manga.tags.set(tags)
        manga.review = review
        manga.save()


class MangaUpdateView(RetrieveUpdateAPIView):
    queryset = Manga.objects.all()
    serializer_class = MangaCreateUpdateSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticated]


class ChapterCreateView(CreateAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterCreateSerializer
    permission_classes = [IsAuthenticated]


class ChapterUpdateView(RetrieveUpdateAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterUpdateSerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticated]

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
