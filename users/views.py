from dj_rest_auth.registration.views import RegisterView
from rest_framework.response import Response
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
    """
    Expansion of the standard registration class to include additional fields.
    """

    serializer_class = CustomRegisterSerializer

    def get_initial_fields(self):
        """
        Get the initial fields for registration, including gender and adult.

        Returns:
            list: List of initial fields for registration.
        """
        initial_fields = super().get_initial_fields()
        initial_fields += ["gender", "adult"]
        return initial_fields


class CustomUserDetailsView(RetrieveAPIView):
    """
    API view to display the current user's data.
    """

    permission_classes = [IsAuthenticated]
    queryset, serializer_class = data_acquisition_and_serialization(CustomUser, CustomUserDetailsSerializer)

    def get_object(self):
        """
        Get the current user object.

        Returns:
            CustomUser: The current user instance.
        """
        return self.request.user


class OtherUserDetailView(generics.RetrieveAPIView):
    """
    API view to display another user's data by slug.
    """

    queryset, serializer_class = data_acquisition_and_serialization(CustomUser, CustomUserDetailsSerializer)
    lookup_field = "slug"


class LatestUsersView(APIView):
    """
    API view to display ten newly created users.
    """

    def get(self, request):
        """
        Get the last ten created users.

        Args:
            request: The HTTP request object.

        Returns:
            Response: Serialized data of the last ten users.
        """
        return Response(extract_and_serialize_data_on_recent_users())


class UpdateUserViewMixin:
    """
    Mixin class providing common behavior for updating user information.
    """

    serializer_class = None
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Get the current user object.

        Returns:
            CustomUser: The current user instance.
        """
        return self.request.user


class GenderUpdateView(UpdateUserViewMixin, generics.UpdateAPIView):
    """
    API view for updating the user's gender.
    """

    serializer_class = GenderUpdateSerializer


class AdultUpdateView(UpdateUserViewMixin, generics.UpdateAPIView):
    """
    API view for updating the user's age of majority.
    """

    serializer_class = AdultUpdateSerializer


class AvatarUpdateView(UpdateUserViewMixin, generics.UpdateAPIView):
    """
    API view for updating the user's profile image.
    """

    serializer_class = AvatarUpdateSerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_email(request):
    """
    API view to change the user's email address.

    Args:
        request: The HTTP request object.

    Returns:
        Response: Result of the email change operation.
    """
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
    """
    API view to display a list of all notifications for the authenticated user.
    """

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Get all notifications for the authenticated user.

        Returns:
            QuerySet: All notifications for the user.
        """
        return get_notifications(self.request.user)


class NotificationListView(generics.ListAPIView):
    """
    API view to display a list of unread notifications for the authenticated user.
    """

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Get unread notifications for the authenticated user.

        Returns:
            QuerySet: Unread notifications for the user.
        """
        return get_notifications(self.request.user, False)


class UpdateNotificationIsReadView(generics.UpdateAPIView):
    """
    API view to update the is_read field in the notification to mark it as read.
    """

    permission_classes = [IsAuthenticated]
    serializer_class, queryset = data_acquisition_and_serialization(Notification, NotificationSerializer)

    def perform_update(self, serializer):
        """
        Mark the notification as read and save the instance.

        Args:
            serializer (NotificationSerializer): The serializer instance.

        Returns:
            None
        """
        serializer.instance.is_read = True
        serializer.save()
