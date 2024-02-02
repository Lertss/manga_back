from manga_back.service import data_acquisition_and_serialization
from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Comment, MangaRating
from .permissions import IsOwnerOrReadOnly
from .serializers import CommentGetSerializer, CommentSerializer, MangaRatingSerializer
from .service.service import comment_object_filter, mangarating_object_filter


class CommentViewSet(viewsets.ModelViewSet):
    """Interacting with comments"""

    queryset, serializer_class = data_acquisition_and_serialization(Comment, CommentSerializer)
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MangaCommentsView(generics.ListCreateAPIView):
    """Display comments to manga"""

    serializer_class = CommentGetSerializer

    def get_queryset(self):
        return comment_object_filter("manga", self.kwargs["slug"])

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ChapterCommentsView(generics.ListAPIView):
    """Display chapter comments"""

    serializer_class = CommentGetSerializer

    def get_queryset(self):
        return comment_object_filter("chapter", self.kwargs["chapter_slug"])


class MangaRatingViewSet(viewsets.ModelViewSet):
    """Interaction with the manga rating"""

    queryset, serializer_class = data_acquisition_and_serialization(MangaRating, MangaRatingSerializer)

    def create(self, request, *args, **kwargs):
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
        serializer.save(user=self.request.user)
