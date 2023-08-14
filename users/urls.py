from dj_rest_auth.registration.views import VerifyEmailView, ConfirmEmailView
from dj_rest_auth.views import PasswordResetConfirmView
from django.urls import path, include
from users.views import CustomRegisterView, CustomUserDetailsView, OtherUserDetailView, GenderUpdateView, \
    AdultUpdateView, AvatarUpdateView, change_email

urlpatterns = [
    path('user/update/gender/', GenderUpdateView.as_view(), name='user-update-gender'),
    path('user/update/adult/', AdultUpdateView.as_view(), name='user-update-adult'),
    path('user/update/avatar/', AvatarUpdateView.as_view(), name='user-update-avatar'),
    path('change-email/', change_email, name='change-email'),


    path('users/<int:pk>/', OtherUserDetailView.as_view(), name='other-user-detail'),
    path('user/', CustomUserDetailsView.as_view(), name='rest_user_details'),

    path('registration/account-confirm-email/<str:key>/', ConfirmEmailView.as_view()),
    # Needs to be defined before the registration path
    path('registration/', CustomRegisterView.as_view(), name='account_signup'),
    path('account-confirm-email/', VerifyEmailView.as_view(),
         name='account_email_verification_sent'),
    path('password/reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),

    path('registration/', include('dj_rest_auth.registration.urls')),
    path('', include('dj_rest_auth.urls')),


]
