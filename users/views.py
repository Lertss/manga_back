from dj_rest_auth.registration.views import RegisterView
from requests import Response
from rest_framework.generics import RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from common.serializers import CommentSerializer
from manga.models import Manga
from manga_back import settings
from .models import MangaList, CustomUser
from .serializers import CustomRegisterSerializer, MangaListSerializer, CustomUserDetailsSerializer, \
    GenderUpdateSerializer, AdultUpdateSerializer, AvatarUpdateSerializer, EmailUpdateSerializer


class CustomRegisterView(RegisterView):
    serializer_class = CustomRegisterSerializer

    def get_initial_fields(self):
        initial_fields = super().get_initial_fields()
        initial_fields += ['gender', 'adult']
        return initial_fields

class CustomUserDetailsView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserDetailsSerializer

    def get_object(self):
        return self.request.user

from rest_framework import generics
from .models import CustomUser

class OtherUserDetailView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserDetailsSerializer
    lookup_field = 'slug'  # Додайте це поле
    # def retrieve(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance)
    #
    #     Отримати коментарі користувача та додати їх до відповіді
    #     comments = CommentSerializer(instance.comments.all(), many=True).data
    #     data = serializer.data
    #     data['comments'] = comments
    #
    #     return Response(data)


from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CustomUser
from .serializers import CustomUserLastDetailsSerializer

class LatestUsersView(APIView):
    def get(self, request):
        latest_users = CustomUser.objects.all().order_by('-date_joined')[:10]
        serializer = CustomUserLastDetailsSerializer(latest_users, many=True)
        return Response(serializer.data)















from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

class GenderUpdateView(generics.UpdateAPIView):
    serializer_class = GenderUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class AdultUpdateView(generics.UpdateAPIView):
    serializer_class = AdultUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class AvatarUpdateView(generics.UpdateAPIView):
    serializer_class = AvatarUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# class EmailUpdateView(generics.UpdateAPIView):
#     serializer_class = EmailUpdateSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_object(self):
#         return self.request.user
# users/views.py

# users/views.py
    """
    запити відправляються так: 
    {
   "new_email": "new@example.com"
 }"""
from allauth.account.models import EmailAddress
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from allauth.account.utils import user_email, send_email_confirmation
from rest_framework import status
from .models import CustomUser

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_email(request):
    new_email = request.data.get('new_email')

    if not new_email:
        return Response({'error': 'New email is required.'}, status=status.HTTP_400_BAD_REQUEST)

    user_instance = CustomUser.objects.get(email=request.user.email)

    if user_instance:
        if user_instance.email == new_email:
            return Response({'error': 'New email must be different from the current email.'}, status=status.HTTP_400_BAD_REQUEST)

        existing_user = CustomUser.objects.filter(email=new_email).exclude(id=user_instance.id).first()
        if existing_user:
            return Response({'error': 'This email is already in use.'}, status=status.HTTP_400_BAD_REQUEST)

        # Отримуємо записи в таблиці account_emailaddress для користувача
        email_addresses = EmailAddress.objects.filter(user=user_instance)

        if email_addresses.exists():
            email_address = email_addresses.first()
            email_address.email = new_email
            email_address.save()
        else:
            # Створюємо новий запис в таблиці account_emailaddress
            EmailAddress.objects.create(user=user_instance, email=new_email, primary=True, verified=False)

        # Змінюємо електронну пошту користувача на нову
        user_instance.email = new_email
        user_instance.save()

        # Відправляємо підтвердження електронної пошти на новий адрес
        user_instance.emailaddress_set.filter(primary=True).update(email=new_email, verified=False)
        send_email_confirmation(request, user_instance)

        return Response({'message': 'Email change request has been sent. Please check your email to confirm.'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'User not found.'}, status=status.HTTP_400_BAD_REQUEST)









from rest_framework import generics
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(user=user)

class NotificationDetailView(generics.RetrieveDestroyAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
