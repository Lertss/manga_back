from dj_rest_auth.registration.views import ConfirmEmailView, VerifyEmailView
from dj_rest_auth.views import PasswordResetConfirmView
from django.urls import include, path
from users import views
from users.views import UpdateNotificationIsReadView


urlpatterns = [
    path("notifications/profile/", views.NotificationListProfileView.as_view(), name="notification-list"),
    path("notifications/", views.NotificationListView.as_view(), name="notification-detail"),
    path(
        "notifications/<int:pk>/mark-as-read/", UpdateNotificationIsReadView.as_view(), name="notification-mark-as-read"
    ),
    path("user/update/gender/", views.GenderUpdateView.as_view(), name="user-update-gender"),
    path("user/update/adult/", views.AdultUpdateView.as_view(), name="user-update-adult"),
    path("user/update/avatar/", views.AvatarUpdateView.as_view(), name="user-update-avatar"),
    path("change-email/", views.change_email, name="change-email"),
    path("users/<slug:slug>/", views.OtherUserDetailView.as_view(), name="other-user-detail"),
    path("last-users/", views.LatestUsersView.as_view(), name="latest-users"),
    path("user/", views.CustomUserDetailsView.as_view(), name="rest_user_details"),
    path("registration/account-confirm-email/<str:key>/", ConfirmEmailView.as_view()),
    # Needs to be defined before the registration path
    path("registration/", views.CustomRegisterView.as_view(), name="account_signup"),
    path("account-confirm-email/", VerifyEmailView.as_view(), name="account_email_verification_sent"),
    path("password/reset/confirm/<uidb64>/<token>/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("registration/", include("dj_rest_auth.registration.urls")),
    path("", include("dj_rest_auth.urls")),
]
