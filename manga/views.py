from rest_framework import filters, generics, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from manga.models import Author, Chapter, Manga, Page
from manga_back.service import data_acquisition_and_serialization

from .serializers import (
    AuthorSerializer,
    ChapterSerializer,
    MangaCreateUpdateSerializer,
    MangaLastSerializer,
    MangaListSerializer,
    MangaSerializer,
    PageSerializer,
)
from .service import service
from .service.service import filtering_and_exclusion


class AllManga(generics.ListAPIView):
    filter_backends = (filters.OrderingFilter,)
    serializer_class = MangaSerializer
    ordering_fields = ["name_manga", "created_at"]

    def get_queryset(self):
        # Get the query parameters 'genres', 'category', 'country_name' and 'tags'
        queryset = filtering_and_exclusion(self)

        return queryset


class Search(viewsets.ModelViewSet):
    """Manga search class"""

    queryset, serializer_class = data_acquisition_and_serialization(Manga, MangaLastSerializer)
    filter_backends = (filters.SearchFilter,)
    search_fields = ["name_manga", "name_original", "english_only_field"]


class ShowManga(APIView):
    """Manga display class"""

    def get(self, request, manga_slug, format=None):
        manga = get_object_or_404(Manga, slug=manga_slug)
        serializer = MangaSerializer(manga)
        return Response(serializer.data)


class MangaViewSet(viewsets.ModelViewSet):
    """Handles CRUD operations on the Manga model."""

    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Manga.objects.all()
    serializer_class = MangaCreateUpdateSerializer
    lookup_field = "slug"

    def partial_update(self, request, *args, **kwargs):
        """Handles PATCH requests for partial updates."""
        return super().partial_update(request, *args, **kwargs)


class AuthorViewSet(viewsets.ModelViewSet):
    """Defines a viewset for CRUD operations on the Author model"""

    queryset, serializer_class = data_acquisition_and_serialization(Author, AuthorSerializer)
    permission_classes = [IsAuthenticatedOrReadOnly]


class AllFilter(APIView):
    """Returns manga filters, country authors, genres, tags, categories"""

    def get(self, request, format=None):
        return Response(service.data_filter(), status=status.HTTP_200_OK)


class ChapterViewSet(viewsets.ModelViewSet):
    """Handling create, read, update, and delete operations in the Chapter model."""

    queryset, serializer_class = data_acquisition_and_serialization(Chapter, ChapterSerializer)
    lookup_field = "slug"
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        """Overrides the standard create method to handle the creation of a new Chapter instance"""
        pages_data = request.data.pop("image", [])
        numb = request.data.pop("page_number", [])

        # Get manga slug from the request
        manga_slug = request.data.get("manga", None)
        if manga_slug:
            # Get a manga object based on a slug
            manga = get_object_or_404(Manga, slug=manga_slug)
        else:
            return Response({"manga": "This field is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Add manga to the query data
        request.data["manga"] = manga.id

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        chapter_instance = serializer.instance
        for image, page_number in zip(pages_data, numb):
            service.create_page_chapter(chapter_instance, image, page_number)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=["patch"], url_path="update-title")
    def update_title(self, request, slug=None):
        """Changes chapter title"""
        return service.update_field_chapter(self, request, "title", "Title updated successfully.")

    @action(detail=True, methods=["patch"], url_path="update-volume")
    def update_volume(self, request, slug=None):
        """Changes volume number"""
        return service.update_field_chapter(self, request, "volume", "Volume updated successfully.")

    @action(detail=True, methods=["patch"], url_path="update-chapter-number")
    def update_chapter_number(self, request, slug=None):
        """Changes chapter number"""
        return service.update_field_chapter(self, request, "chapter_number", "Chapter number updated successfully.")

    @action(
        detail=True,
        methods=["POST"],
    )
    def add_comment_to_chapter(self, request, slug=None):
        """Creating a comment to a chapter"""
        content = request.data.get("content")
        if content:
            service.create_comment(
                request.user,
                chapter=get_object_or_404(Chapter, slug=slug),
                content=content,
            )
            return Response({"message": "Comment added successfully."}, status=201)
        else:
            return Response({"error": "Content field is required."}, status=400)


class ShowChapter(APIView):
    """Chapter display"""

    def get(self, request, manga_slug, chapter_slug, format=None):
        chapter = get_object_or_404(Chapter, manga__slug=manga_slug, slug=chapter_slug)
        serializer = ChapterSerializer(chapter)
        return Response(serializer.data)


class PageViewSet(viewsets.ModelViewSet):
    """Handling create, read, update, and delete operations in the Page model."""

    queryset, serializer_class = data_acquisition_and_serialization(Page, PageSerializer)
    parser_classes = (MultiPartParser, FormParser)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_manga_to_list(request):
    """Adds a manga to the reader's manga list"""
    manga_list, created = service.mangalist_get_or_create(request)
    if not created:
        manga_list.name = request.data.get("name")
        manga_list.save()
    return Response({"message": "Manga added to the list successfully."})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def remove_manga_from_list(request):
    """Removes a manga from the reader's manga list"""
    manga_list = service.mangalist_remove(request)
    if manga_list:
        manga_list.delete()
        return Response({"message": "Manga removed from the list successfully."})
    else:
        return Response({"message": "Manga was not found in the list."})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def manga_in_user_list(request, manga_slug):
    """Returns the status of a manga from the reader's manga list"""
    manga_list = service.mangalist_filter(request, manga_slug)
    if manga_list:
        return Response({"in_list": True, "list_name": manga_list.name})
    else:
        return Response({"in_list": False})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_manga_list(request):
    """Returns the reader's manga lists"""
    serialized_data = MangaListSerializer(service.mangalist_filter_by_user(request.user), many=True)
    return Response(serialized_data.data)


class TopMangaView(APIView):
    """Returns the top of the manga"""

    def get(self, request, format=None):
        return Response(service.top_manga_objects_annotate_serializer().data)


class TopMangaLastYearView(APIView):
    """Returns the top manga of the last year"""

    def get(self, request, format=None):
        return Response(service.top_manga_last_year_filter_serializer().data)


class TopMangaCommentsView(APIView):
    """Returns the top manga by comments"""

    def get(self, request, format=None):
        return Response(service.top_manga_comments_annotate_serializer().data)


class RandomMangaView(APIView):
    """Returns random manga"""

    def get(self, request, format=None):
        return Response(service.random_manga())


@api_view(["GET"])
def last_hundred_chapters(request):
    """Returns the last added chapters"""
    return Response(service.one_hundred_last_added_chapters())
