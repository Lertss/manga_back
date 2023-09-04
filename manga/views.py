import json
from django.http import Http404
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from common.models import Comment
from .serializers import *

#What
class MangaListHome(APIView):
    def get(self, request, format=None):
        manga = Manga.objects.all()
        serializer_all = MangaSerializer(manga, many=True)
        last_manga = Manga.objects.order_by('-time_prod')[:10]
        serializer_lastmanga = MangaSerializer(last_manga, many=True)
        last_chapter = Chapter.objects.all()
        #
        serializer_chapter = ChapterSerializer(last_chapter, many=True)

        serializer = {'last_manga': serializer_lastmanga.data,'all': serializer_all.data, 'chapter': serializer_chapter.data}
        return Response(serializer)






from rest_framework import generics
from rest_framework import viewsets, filters
from .models import Manga
from .serializers import MangaSerializer  # Додайте імпорт вашого серіалізатора


class AllManga(generics.ListAPIView):
    filter_backends = (filters.OrderingFilter,)
    serializer_class = MangaSerializer
    ordering_fields = ['name_manga', 'time_prod']
    def get_queryset(self):
        # Отримуємо параметри запиту 'genres', 'category','counts' і 'tags'
        genres = self.request.query_params.getlist('genres')
        tags = self.request.query_params.getlist('tags')
        counts = self.request.query_params.getlist('counts')
        categories = self.request.query_params.getlist('category')
        min_rating = self.request.query_params.get('min_rating')

        queryset = Manga.objects.all()

        for genre in genres:
            queryset = queryset.filter(genre__genr_name=genre)
        for tag in tags:
            queryset = queryset.filter(tags__tag_name=tag)
        for count in counts:
            queryset = queryset.filter(counts__counts=count)
        for category in categories:
            queryset = queryset.filter(category__cat_name=category)

        filter_params = {
            'genres': 'genre__genr_name',
            'tags': 'tags__tag_name',
            'countries': 'counts__counts',
            'categories': 'category__cat_name'
        }
        # Виключаємо за допомогою циклу
        for param, model_field in filter_params.items():
            excluded_values = self.request.query_params.getlist('exclude_' + param)
            print(str(excluded_values))
            # print(f'param: {param}, model_field: {model_field}, excluded_values: {excluded_values}')
            if excluded_values:
                queryset = queryset.exclude(**{model_field + '__in': excluded_values})

            print(queryset)
        # Фільтруємо за полем decency
        decency = self.request.query_params.get('decency')
        if decency in ['true', 'false']:
            queryset = queryset.filter(decency=(decency == 'true'))

        if min_rating is not None:
            min_rating = int(min_rating)
            # Фільтруємо мангу з середнім рейтингом більше або рівним min_rating
            queryset = queryset.annotate(avg_rating=Avg('ratings__rating')).filter(avg_rating__gte=min_rating)

        return queryset




class Search(viewsets.ModelViewSet):
    queryset = Manga.objects.all()
    serializer_class = MangaLastSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ['name_manga', 'name_original', 'english_only_field']




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


class MangaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Manga.objects.all()
    serializer_class = MangaCreateUpdateSerializer
    lookup_field = 'slug'

    @action(detail=True, methods=['patch'], url_path='update-category')
    def update_category(self, request, slug=None):
        instance = self.get_object()
        category_ids = request.data.get('category')

        if category_ids is not None:
            try:
                # Отримайте екземпляр категорії за допомогою ID та оновіть поле категорії
                category_instance = Category.objects.get(id=category_ids)
                instance.category = category_instance
                instance.save()
                return Response({'message': 'Категорію успішно оновлено.'})
            except Category.DoesNotExist:
                return Response({'error': 'Категорія не знайдена.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': "Поле \'category\' є обов\'язковим."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='update-name-manga')
    def update_name_manga(self, request, slug=None):
        instance = self.get_object()
        name_manga = request.data.get('name_manga')
        if name_manga is not None:
            instance.name_manga = name_manga
            instance.save()
            return Response({'message': 'Name manga updated successfully.'})
        return Response({'error': 'Name manga field is required.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='update-name-original')
    def update_name_original(self, request, slug=None):
        instance = self.get_object()
        name_original = request.data.get('name_original')
        if name_original is not None:
            instance.name_original = name_original
            instance.save()
            return Response({'message': 'Name original updated successfully.'})
        return Response({'error': 'Name original field is required.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='update-english-only-field')
    def update_english_only_field(self, request, slug=None):
        instance = self.get_object()
        english_only_field = request.data.get('english_only_field')
        if english_only_field is not None:
            instance.english_only_field = english_only_field
            instance.save()
            return Response({'message': 'English only field updated successfully.'})
        return Response({'error': 'English only field is required.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='update-author')
    def update_author(self, request, slug=None):
        instance = self.get_object()
        author_ids = request.data.getlist('author')
        if author_ids is not None:
            instance.author.clear()  # Видалити існуючі записи авторів
            instance.author.set(author_ids)  # Додати нові записи авторів
            return Response({'message': 'Author updated successfully.'})
        return Response({'error': 'Author field is required.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='update-counts')
    def update_counts(self, request, slug=None):
        instance = self.get_object()
        counts_ids = request.data.getlist('counts')
        if counts_ids is not None:
            instance.counts.clear()  # Видалити існуючі записи країн
            instance.counts.add(*counts_ids)  # Додати нові записи країн
            return Response({'message': 'Counts updated successfully.'})
        return Response({'error': 'Counts field is required.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='update-decency')
    def update_decency(self, request, slug=None):
        instance = self.get_object()
        decency = request.data.get('decency')

        if decency is not None:
            # Convert string to boolean
            decency = json.loads(decency.lower())

            instance.decency = decency
            instance.save()
            return Response({'message': 'Decency updated successfully.'})

        return Response({'error': 'Decency field is required.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='update-genre')
    def update_genre(self, request, slug=None):
        instance = self.get_object()
        genre_ids = request.data.getlist('genre')
        if genre_ids is not None:
            instance.genre.clear()  # Видалити існуючі записи жанрів
            instance.genre.add(*genre_ids)  # Додати нові записи жанрів
            return Response({'message': 'Genre updated successfully.'})
        return Response({'error': 'Genre field is required.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='update-tags')
    def update_tags(self, request, slug=None):
        instance = self.get_object()
        tags_ids = request.data.getlist('tags')
        if tags_ids is not None:
            instance.tags.clear()  # Видалити існуючі записи тегів
            instance.tags.add(*tags_ids)  # Додати нові записи тегів
            return Response({'message': 'Tags updated successfully.'})
        return Response({'error': 'Tags field is required.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='update-review')
    def update_review(self, request, slug=None):
        instance = self.get_object()
        review = request.data.get('review')
        if review is not None:
            instance.review = review
            instance.save()
            return Response({'message': 'Review updated successfully.'})
        return Response({'error': 'Review field is required.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='update-avatar')
    def update_avatar(self, request, slug=None):
        instance = self.get_object()
        avatar = request.data.get('avatar')
        if avatar is not None:
            instance.avatar = avatar
            instance.save()
            return Response({'message': 'Avatar updated successfully.'})
        return Response({'error': 'Avatar field is required.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST'])
    def add_comment_to_manga(self, request, slug=None):
        manga = get_object_or_404(Manga, slug=slug)
        content = request.data.get('content')

        if content:
            Comment.objects.create(user=request.user, manga=manga, content=content)
            return Response({'message': 'Comment added successfully.'}, status=201)
        else:
            return Response({'error': 'Content field is required.'}, status=400)


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
            'categories': category_serializer.data,
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
    lookup_field = 'slug'
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        pages_data = request.data.pop('image', [])
        numb = request.data.pop('page_number', [])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        chapter_instance = serializer.instance
        print(chapter_instance)  # Отримати створений екземпляр розділу
        for image, page_number in zip(pages_data, numb):
            Page.objects.create(chapter=chapter_instance, image=image, page_number=page_number)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    @action(detail=True, methods=['patch'], url_path='update-title')
    def update_title(self, request, slug=None):
        instance = self.get_object()
        title = request.data.get('title')
        if title is not None:
            instance.title = title
            instance.save()
            return Response({'message': 'Title updated successfully.'})
        return Response({'error': 'Title field is required.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='update-volume')
    def update_volume(self, request, slug=None):
        instance = self.get_object()
        volume = request.data.get('volume')
        if volume is not None:
            instance.volume = volume
            instance.save()
            return Response({'message': 'Volume updated successfully.'})
        return Response({'error': 'Volume field is required.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='update-chapter-number')
    def update_chapter_number(self, request, slug=None):
        instance = self.get_object()
        chapter_number = request.data.get('chapter_number')
        if chapter_number is not None:
            instance.chapter_number = chapter_number
            instance.save()
            return Response({'message': 'Chapter number updated successfully.'})
        return Response({'error': 'Chapter number field is required.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST'],)
    def add_comment_to_chapter(self, request, slug=None):
        chapter = get_object_or_404(Chapter, slug=slug)
        content = request.data.get('content')

        if content:
            Comment.objects.create(user=request.user, chapter=chapter, content=content)
            return Response({'message': 'Comment added successfully.'}, status=201)
        else:
            return Response({'error': 'Content field is required.'}, status=400)

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



class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    parser_classes = (MultiPartParser, FormParser)









from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_manga_to_list(request):
    user = request.user
    manga_id = request.data.get('manga_id')
    name = request.data.get('name')

    manga = Manga.objects.get(pk=manga_id)
    manga_list, created = MangaList.objects.get_or_create(user=user, manga=manga, defaults={'name': name})

    if not created:
        manga_list.name = name
        manga_list.save()

    return Response({'message': 'Manga added to the list successfully.'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_manga_from_list(request):
    user = request.user
    manga_id = request.data.get('manga_id')

    manga = Manga.objects.get(pk=manga_id)
    manga_list = MangaList.objects.filter(user=user, manga=manga).first()

    if manga_list:
        manga_list.delete()
        return Response({'message': 'Manga removed from the list successfully.'})
    else:
        return Response({'message': 'Manga was not found in the list.'})




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_manga_list(request):
    user = request.user
    manga_list = MangaList.objects.filter(user=user)
    serialized_data = MangaListSerializer(manga_list, many=True)  # Замініть на свій серіалайзер
    return Response(serialized_data.data)



from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Manga
from .serializers import MangaLastSerializer

class TopMangaView(APIView):
    def get(self, request, format=None):
        top_manga = Manga.objects.annotate(avg_rating=Avg('ratings__rating')).order_by('-avg_rating')[:100]
        serializer = MangaLastSerializer(top_manga, many=True)
        return Response(serializer.data)



from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Manga
from .serializers import MangaLastSerializer
from django.db.models import Avg, Q
from datetime import datetime, timedelta
from .models import Manga
class TopMangaLastYearView(APIView):
    def get(self, request, format=None):
        last_year = datetime.now() - timedelta(days=365)
        top_manga_last_year = Manga.objects.filter(time_prod__gte=last_year).annotate(avg_rating=Avg('ratings__rating')).order_by('-avg_rating')[:100]
        serializer = MangaLastSerializer(top_manga_last_year, many=True)
        return Response(serializer.data)


from django.db.models import Count
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Manga
from .serializers import MangaLastSerializer

class TopMangaCommentsView(APIView):
    def get(self, request, format=None):
        top_manga_comments = Manga.objects.annotate(num_comments=Count('comment')).order_by('-num_comments')[:100]
        serializer = MangaLastSerializer(top_manga_comments, many=True)
        return Response(serializer.data)


import random
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Manga
from .serializers import MangaLastSerializer

class RandomMangaView(APIView):
    def get(self, request, format=None):
        all_manga = list(Manga.objects.all())
        random_manga = random.sample(all_manga, 2)
        serializer = MangaRandomSerializer(random_manga, many=True)
        return Response(serializer.data)




from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Chapter, Manga
from .serializers import LastChapterSerializer, MangaLastSerializer

@api_view(['GET'])
def last_hundred_chapters(request):
    # Отримати останні сто глав
    last_hundred_chapters = Chapter.objects.order_by('-id')[:100]

    chapter_data = []
    for chapter in last_hundred_chapters:
        chapter_serializer = LastChapterSerializer(chapter)
        manga_serializer = MangaLastSerializer(chapter.manga)

        # Отримати дані з серіалізаторів
        serialized_chapter = chapter_serializer.data
        serialized_manga = manga_serializer.data

        # Додати дані манги до даних глави
        serialized_chapter['manga'] = serialized_manga

        chapter_data.append(serialized_chapter)

    return Response(chapter_data)
