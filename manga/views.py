from django.db.models import Avg
from rest_framework import filters, generics, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from manga.models import Author, Chapter, Manga, Page
from manga_back.service import data_acquisition_and_serialization

from .serializers import (
    AuthorSerializer,
    ChapterSerializer,
    MangaAllSerializer,
    MangaCreateUpdateSerializer,
    MangaLastSerializer,
    MangaListSerializer,
    MangaSerializer,
    PageSerializer,
)
from .service import service
from .service.service import filtering_and_exclusion


class MangaPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50

class AllManga(generics.ListAPIView):
    """
    API view to list all manga with filtering and ordering.
    """
    filter_backends = (filters.OrderingFilter,)
    serializer_class = MangaAllSerializer
    ordering_fields = ["name_manga", "created_at"]
    pagination_class = MangaPagination

    def get_queryset(self):
        """
        Get the queryset of manga filtered by query parameters.

        Returns:
            QuerySet: Filtered manga queryset.
        """
        queryset = filtering_and_exclusion(self)
        return (
            queryset.select_related("category")
            .prefetch_related("author", "country", "genre", "tags", "chapters")
            .annotate(average_rating=Avg("ratings__rating"))
        )


class Search(viewsets.ModelViewSet):
    """
    ViewSet for searching manga by name, original name, or English field.
    """

    queryset, serializer_class = data_acquisition_and_serialization(Manga, MangaLastSerializer)
    filter_backends = (filters.SearchFilter,)
    search_fields = ["name_manga", "name_original", "english_only_field"]


class ShowManga(APIView):
    """
    API view to display a single manga by slug.
    """

    def get(self, request, manga_slug, format=None):
        """
        Retrieve and serialize a manga by slug.

        Args:
            request: The HTTP request object.
            manga_slug (str): Slug of the manga.
            format: Optional format.

        Returns:
            Response: Serialized manga data.
        """
        manga = get_object_or_404(Manga, slug=manga_slug)
        serializer = MangaSerializer(manga)
        return Response(serializer.data)


class MangaViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling CRUD operations on the Manga model.
    """

    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Manga.objects.all()
    serializer_class = MangaCreateUpdateSerializer
    lookup_field = "slug"

    def partial_update(self, request, *args, **kwargs):
        """
        Handle PATCH requests for partial updates of Manga.

        Args:
            request: The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: The response from the parent method.
        """
        return super().partial_update(request, *args, **kwargs)


class AuthorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations on the Author model.
    """

    queryset, serializer_class = data_acquisition_and_serialization(Author, AuthorSerializer)
    permission_classes = [IsAuthenticatedOrReadOnly]


class AllFilter(APIView):
    """
    API view to return manga filters, country authors, genres, tags, and categories.
    """

    def get(self, request, format=None):
        """
        Retrieve filter data for manga.

        Args:
            request: The HTTP request object.
            format: Optional format.

        Returns:
            Response: Serialized filter data.
        """
        return Response(service.data_filter(), status=status.HTTP_200_OK)


class ChapterViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling create, read, update, and delete operations in the Chapter model.
    """

    queryset, serializer_class = data_acquisition_and_serialization(Chapter, ChapterSerializer)
    lookup_field = "slug"
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        """
        Handle creation of a new Chapter instance, including pages.

        Args:
            request: The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: Serialized chapter data.
        """
        pages_data = request.data.pop("image", [])
        numb = request.data.pop("page_number", [])
        manga_slug = request.data.get("manga", None)
        if manga_slug:
            manga = get_object_or_404(Manga, slug=manga_slug)
        else:
            return Response({"manga": "This field is required."}, status=status.HTTP_400_BAD_REQUEST)
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
        """
        Update the title of a chapter.

        Args:
            request: The HTTP request object.
            slug (str): Slug of the chapter.

        Returns:
            Response: Result of the update operation.
        """
        return service.update_field_chapter(self, request, "title", "Title updated successfully.")

    @action(detail=True, methods=["patch"], url_path="update-volume")
    def update_volume(self, request, slug=None):
        """
        Update the volume number of a chapter.

        Args:
            request: The HTTP request object.
            slug (str): Slug of the chapter.

        Returns:
            Response: Result of the update operation.
        """
        return service.update_field_chapter(self, request, "volume", "Volume updated successfully.")

    @action(detail=True, methods=["patch"], url_path="update-chapter-number")
    def update_chapter_number(self, request, slug=None):
        """
        Update the chapter number of a chapter.

        Args:
            request: The HTTP request object.
            slug (str): Slug of the chapter.

        Returns:
            Response: Result of the update operation.
        """
        return service.update_field_chapter(self, request, "chapter_number", "Chapter number updated successfully.")

    @action(detail=True, methods=["POST"])
    def add_comment_to_chapter(self, request, slug=None):
        """
        Create a comment for a chapter.

        Args:
            request: The HTTP request object.
            slug (str): Slug of the chapter.

        Returns:
            Response: Result of the comment creation.
        """
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
    """
    API view to display a single chapter by manga and chapter slug.
    """

    def get(self, request, manga_slug, chapter_slug, format=None):
        """
        Retrieve and serialize a chapter by manga and chapter slug.

        Args:
            request: The HTTP request object.
            manga_slug (str): Slug of the manga.
            chapter_slug (str): Slug of the chapter.
            format: Optional format.

        Returns:
            Response: Serialized chapter data.
        """
        chapter = get_object_or_404(Chapter, manga__slug=manga_slug, slug=chapter_slug)
        serializer = ChapterSerializer(chapter)
        return Response(serializer.data)


class PageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling create, read, update, and delete operations in the Page model.
    """

    queryset, serializer_class = data_acquisition_and_serialization(Page, PageSerializer)
    parser_classes = (MultiPartParser, FormParser)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_manga_to_list(request):
    """
    Add a manga to the reader's manga list.

    Args:
        request: The HTTP request object.

    Returns:
        Response: Result of the add operation.
    """
    manga_list, created = service.mangalist_get_or_create(request)
    if not created:
        manga_list.name = request.data.get("name")
        manga_list.save()
    return Response({"message": "Manga added to the list successfully."})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def remove_manga_from_list(request):
    """
    Remove a manga from the reader's manga list.

    Args:
        request: The HTTP request object.

    Returns:
        Response: Result of the remove operation.
    """
    manga_list = service.mangalist_remove(request)
    if manga_list:
        manga_list.delete()
        return Response({"message": "Manga removed from the list successfully."})
    else:
        return Response({"message": "Manga was not found in the list."})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def manga_in_user_list(request, manga_slug):
    """
    Return the status of a manga from the reader's manga list.

    Args:
        request: The HTTP request object.
        manga_slug (str): Slug of the manga.

    Returns:
        Response: Status of the manga in the user's list.
    """
    manga_list = service.mangalist_filter(request, manga_slug)
    if manga_list:
        return Response({"in_list": True, "list_name": manga_list.name})
    else:
        return Response({"in_list": False})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_manga_list(request):
    """
    Return the reader's manga lists.

    Args:
        request: The HTTP request object.

    Returns:
        Response: Serialized manga list data.
    """
    serialized_data = MangaListSerializer(service.mangalist_filter_by_user(request.user), many=True)
    return Response(serialized_data.data)


class TopMangaView(APIView):
    """
    API view to return the top manga.
    """

    def get(self, request, format=None):
        """
        Retrieve top manga data.

        Args:
            request: The HTTP request object.
            format: Optional format.

        Returns:
            Response: Serialized top manga data.
        """
        return Response(service.top_manga_objects_annotate_serializer().data)


class TopMangaLastYearView(APIView):
    """
    API view to return the top manga of the last year.
    """

    def get(self, request, format=None):
        """
        Retrieve top manga data for the last year.

        Args:
            request: The HTTP request object.
            format: Optional format.

        Returns:
            Response: Serialized top manga data for the last year.
        """
        return Response(service.top_manga_last_year_filter_serializer().data)


class TopMangaCommentsView(APIView):
    """
    API view to return the top manga by comments.
    """

    def get(self, request, format=None):
        """
        Retrieve top manga data by comments.

        Args:
            request: The HTTP request object.
            format: Optional format.

        Returns:
            Response: Serialized top manga data by comments.
        """
        return Response(service.top_manga_comments_annotate_serializer().data)


class RandomMangaView(APIView):
    """
    API view to return random manga.
    """

    def get(self, request, format=None):
        """
        Retrieve random manga data.

        Args:
            request: The HTTP request object.
            format: Optional format.

        Returns:
            Response: Serialized random manga data.
        """
        return Response(service.random_manga())


@api_view(["GET"])
def last_hundred_chapters(request):
    """
    Return the last added chapters.

    Args:
        request: The HTTP request object.

    Returns:
        Response: Serialized data of the last added chapters.
    """
    return Response(service.one_hundred_last_added_chapters())
