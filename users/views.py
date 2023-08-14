from dj_rest_auth.registration.views import RegisterView
from requests import Response
from rest_framework.views import APIView

from manga.models import Manga
from manga_back import settings
from .models import MangaList
from .serializers import CustomRegisterSerializer, MangaListSerializer
from dj_rest_auth.views import UserDetailsView
from .serializers import CustomUserDetailsSerializer

class CustomRegisterView(RegisterView):
    serializer_class = CustomRegisterSerializer

    def get_initial_fields(self):
        initial_fields = super().get_initial_fields()
        initial_fields += ['gender', 'birthdate']
        return initial_fields

class CustomUserDetailsView(UserDetailsView):
    serializer_class = CustomUserDetailsSerializer

from rest_framework import generics
from .models import CustomUser

class OtherUserDetailView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserDetailsSerializer







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
