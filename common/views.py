# manga/views.py
from rest_framework import viewsets, generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from common.models import Comment
from manga.models import Manga, Chapter
from .serializers import CommentSerializer, CommentSerializerUpdate


class MangaCommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        manga_pk = self.kwargs['manga_pk']
        manga = Manga.objects.get(pk=manga_pk)
        return manga.comments.all()

    def perform_create(self, serializer):
        manga_pk  = self.kwargs['manga_pk']  # Витягніть ID розділу з URL
        manga = get_object_or_404(Manga, id=manga_pk)
        text = serializer.validated_data['text']
        manga.add_comment(self.request.user, text)

class ChapterCommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        chapter_pk = self.kwargs['chapter_pk']
        manga = Chapter.objects.get(pk=chapter_pk)
        return manga.comments.all()

    def perform_create(self, serializer):
        chapter_id = self.kwargs['chapter_pk']  # Витягніть ID розділу з URL
        chapter = get_object_or_404(Chapter, id=chapter_id)
        text = serializer.validated_data['text']
        chapter.add_comment(self.request.user, text)

class CommentUpdateView(generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializerUpdate
    permission_classes = [IsAuthenticated]


class CommentDeleteView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticated]



