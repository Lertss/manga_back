from django.db.models import Q
from django.http import Http404
from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .serializers import *
from .models import Manga


class MangaListHome(APIView):
    def get(self, request, format=None):
        manga = Manga.objects.all()
        serializer_all = MangaSerializer(manga, many=True)
        last_manga = Manga.objects.order_by('?')[:5]
        serializer_lastmanga = MangaSerializer(last_manga, many=True)
        last_glawa = Glawa.objects.all()
        #
        serializer_glawa = GlawaSerializer(last_glawa, many=True)

        serializer = [serializer_lastmanga.data, serializer_all.data, serializer_glawa.data]
        return Response(serializer)


class allManga(APIView):
    def get(self, request, ):
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

class ShowGlawa(APIView):  # ShowChapter
    def get_object(self, manga_slug, glawa_slug):
        try:
            return Glawa.objects.filter(manga__slug=manga_slug).get(slug=glawa_slug)
        except Glawa.DoesNotExist:
            raise Http404

    def get(self, request, manga_slug, glawa_slug, format=None):
        glawa = self.get_object(manga_slug, glawa_slug)
        serializer = GlawaSerializer(glawa)
        return Response(serializer.data)


@api_view(['POST'])
def search(request):
    query = request.data.get('query', '')

    if query:
        products = Manga.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
        serializer = Manga(products, many=True)
        return Response(serializer.data)
    else:
        return Response({"products": []})
