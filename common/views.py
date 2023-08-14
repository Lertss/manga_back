# manga/views.py
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated

from common.models import Comment
from manga.models import Manga, Glawa
from .serializers import CommentSerializer, CommentSerializerUpdate


class MangaCommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        manga_pk = self.kwargs['manga_pk']
        manga = Manga.objects.get(pk=manga_pk)
        return manga.comments.all()

    def perform_create(self, serializer):
        manga_id = self.kwargs['manga_pk']
        manga = Manga.objects.get(pk=manga_id)
        serializer.save(user=self.request.user, manga_comments=manga)

class GlawaCommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        glawa_pk = self.kwargs['glawa_pk']
        manga = Glawa.objects.get(pk=glawa_pk)
        return manga.comments.all()

    def perform_create(self, serializer):
        glawa_id = self.kwargs['glawa_pk']
        glawa = Glawa.objects.get(pk=glawa_id)
        serializer.save(user=self.request.user, glawa_comments=glawa)

class CommentUpdateView(generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializerUpdate
    permission_classes = [IsAuthenticated]


class CommentDeleteView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticated]
