from dj_rest_auth.registration.views import VerifyEmailView, ConfirmEmailView
from django.urls import path, include
from users.views import CustomRegisterView, CustomUserDetailsView

urlpatterns = [
    path('dj-rest-auth/user/', CustomUserDetailsView.as_view(), name='rest_user_details'),
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('dj-rest-auth/registration/account-confirm-email/<str:key>/',ConfirmEmailView.as_view(),), # Needs to be defined before the registration path
    path('dj-rest-auth/registration/', CustomRegisterView.as_view(), name='account_signup'),
    path('dj-rest-auth/account-confirm-email/', VerifyEmailView.as_view(), name='account_email_verification_sent'),



]
