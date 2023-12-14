from rest_framework import generics
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from manga.serializers import MangaListSerializer
from users.models import MangaList
from .models import Comment
from .models import MangaRating
from .permissions import IsOwnerOrReadOnly
from .serializers import CommentGetSerializer, CommentSerializer
from .serializers import MangaRatingSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_manga_list(request):
    user = request.user
    manga_list = MangaList.objects.filter(user=user)
    serialized_data = MangaListSerializer(manga_list, many=True)
    return Response(serialized_data.data)


class MangaCommentsView(generics.ListCreateAPIView):
    serializer_class = CommentGetSerializer

    def get_queryset(self):
        manga_slug = self.kwargs['slug']
        return Comment.objects.filter(manga__slug=manga_slug)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ChapterCommentsView(generics.ListAPIView):
    serializer_class = CommentGetSerializer

    def get_queryset(self):
        chapter_slug = self.kwargs['chapter_slug']
        return Comment.objects.filter(chapter__slug=chapter_slug)


class MangaRatingViewSet(viewsets.ModelViewSet):
    queryset = MangaRating.objects.all()
    serializer_class = MangaRatingSerializer

    def create(self, request, *args, **kwargs):
        manga_id = request.data.get('manga')
        user_id = request.data.get('user')
        existing_rating = MangaRating.objects.filter(manga=manga_id, user=user_id).first()

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
