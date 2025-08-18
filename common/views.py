from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from manga_back.service import data_acquisition_and_serialization

from .models import Comment, MangaRating
from .permissions import IsOwnerOrReadOnly
from .serializers import CommentGetSerializer, CommentSerializer, MangaRatingSerializer
from .service.service import comment_object_filter, mangarating_object_filter


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for interacting with comments.

    Allows authenticated users to create, update, and delete comments. Only owners can modify their comments.
    """

    queryset, serializer_class = data_acquisition_and_serialization(Comment, CommentSerializer)
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        """
        Save a new comment with the current user as the owner.

        Args:
            serializer (CommentSerializer): The serializer instance.

        Returns:
            None
        """
        serializer.save(user=self.request.user)


class MangaCommentsView(generics.ListCreateAPIView):
    """
    API view to display and create comments for a manga.
    """

    serializer_class = CommentGetSerializer

    def get_queryset(self):
        """
        Get queryset of comments for a specific manga.

        Returns:
            QuerySet: Comments for the manga.
        """
        return comment_object_filter("manga", self.kwargs["slug"])

    def perform_create(self, serializer):
        """
        Save a new manga comment with the current user as the owner.

        Args:
            serializer (CommentSerializer): The serializer instance.

        Returns:
            None
        """
        serializer.save(user=self.request.user)


class ChapterCommentsView(generics.ListAPIView):
    """
    API view to display comments for a chapter.
    """

    serializer_class = CommentGetSerializer

    def get_queryset(self):
        """
        Get queryset of comments for a specific chapter.

        Returns:
            QuerySet: Comments for the chapter.
        """
        return comment_object_filter("chapter", self.kwargs["chapter_slug"])


class MangaRatingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for interacting with manga ratings.

    Allows users to create or update their rating for a manga. If a rating exists, it is updated;
    otherwise, a new rating is created.
    """

    queryset, serializer_class = data_acquisition_and_serialization(MangaRating, MangaRatingSerializer)

    def create(self, request, *args, **kwargs):
        """
        Create or update a manga rating for the current user.

        Args:
            request: The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: The response containing the rating data.
        """
        existing_rating = mangarating_object_filter(request.data.get("manga"), request.data.get("user"))
        if existing_rating:
            serializer = self.get_serializer(existing_rating, data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        """
        Save a new manga rating with the current user as the owner.

        Args:
            serializer (MangaRatingSerializer): The serializer instance.

        Returns:
            None
        """
        serializer.save(user=self.request.user)
