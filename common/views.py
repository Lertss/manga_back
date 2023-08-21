# manga/views.py
from rest_framework import viewsets, generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from common.models import Comment
from manga.models import Manga, Chapter
from manga.serializers import MangaListSerializer
from users.models import MangaList
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



