from dj_rest_auth.registration.views import RegisterView
from requests import Response
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from manga_back.service import data_acquisition_and_serialization

from .models import CustomUser, Notification
from .serializers import (
    AdultUpdateSerializer,
    AvatarUpdateSerializer,
    CustomRegisterSerializer,
    CustomUserDetailsSerializer,
    GenderUpdateSerializer,
    NotificationSerializer,
)
from .service.service import extract_and_serialize_data_on_recent_users, get_notifications
from .service.service_change_email import change_email_address, existing_user_func, user_instance_func


class CustomRegisterView(RegisterView):
    """Expansion of the standard re-registration class"""

    serializer_class = CustomRegisterSerializer

    def get_initial_fields(self):
        initial_fields = super().get_initial_fields()
        initial_fields += ["gender", "adult"]
        return initial_fields


class CustomUserDetailsView(RetrieveAPIView):
    """Display the current user's data"""

    permission_classes = [IsAuthenticated]
    queryset, serializer_class = data_acquisition_and_serialization(CustomUser, CustomUserDetailsSerializer)

    def get_object(self):
        return self.request.user


class OtherUserDetailView(generics.RetrieveAPIView):
    """Display another user's data."""

    queryset, serializer_class = data_acquisition_and_serialization(CustomUser, CustomUserDetailsSerializer)
    lookup_field = "slug"


class LatestUsersView(APIView):
    """Display of ten newly created users."""

    def get(self, request):
        return Response(extract_and_serialize_data_on_recent_users().data)


class UpdateUserViewMixin:
    """A mixin class providing common behavior for updating user information"""

    serializer_class = None
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class GenderUpdateView(UpdateUserViewMixin, generics.UpdateAPIView):
    """Child class of UpdateUserViewMixin class, updating the user's gender"""

    serializer_class = GenderUpdateSerializer


class AdultUpdateView(UpdateUserViewMixin, generics.UpdateAPIView):
    """Child class of the UpdateUserViewMixin class, updating the user's age of majority"""

    serializer_class = AdultUpdateSerializer


class AvatarUpdateView(UpdateUserViewMixin, generics.UpdateAPIView):
    """Child class of the UpdateUserViewMixin class, updating the user profile image"""

    serializer_class = AvatarUpdateSerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_email(request):
    """Email change function"""
    new_email = request.data.get("new_email")
    if not new_email:
        return Response({"error": "New email is required."}, status=status.HTTP_400_BAD_REQUEST)
    user_instance = user_instance_func(request.user.email)
    if user_instance:
        if user_instance.email == new_email:
            return Response(
                {"error": "New email must be different from the current email."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        existing_user = existing_user_func(new_email, user_instance)
        if existing_user:
            return Response(
                {"error": "This email is already in use."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        change_email_address(new_email, user_instance, request)
        return Response(
            {"message": "Email change request has been sent. Please check your email to confirm."},
            status=status.HTTP_200_OK,
        )
    else:
        return Response({"error": "User not found."}, status=status.HTTP_400_BAD_REQUEST)


class NotificationListProfileView(generics.ListAPIView):
    """Displays a list of all notifications for the authenticated user"""

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return get_notifications(self.request.user)


class NotificationListView(generics.ListAPIView):
    """Displays a list of unread notifications for an authenticated user."""

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return get_notifications(self.request.user, False)


class UpdateNotificationIsReadView(generics.UpdateAPIView):
    """Updates the is_read field in the notification to mark it as read"""

    permission_classes = [IsAuthenticated]
    serializer_class, queryset = data_acquisition_and_serialization(Notification, NotificationSerializer)

    def perform_update(self, serializer):
        serializer.instance.is_read = True
        serializer.save()
