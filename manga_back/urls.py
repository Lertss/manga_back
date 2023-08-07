"""

URL configuration for manga_back project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from dj_rest_auth.registration.views import VerifyEmailView, ConfirmEmailView
from dj_rest_auth.views import PasswordResetConfirmView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

import manga.urls
from users import views
from users.views import CustomRegisterView, CustomUserDetailsView
# urls.py

from django.urls import path



urlpatterns = [


                  path('dj-rest-auth/user/', CustomUserDetailsView.as_view(), name='rest_user_details'),
                  path('admin/', admin.site.urls),
                  path('api/v1/', include(manga.urls)),
                  path('dj-rest-auth/registration/account-confirm-email/<str:key>/', ConfirmEmailView.as_view()),
                  # Needs to be defined before the registration path
                  path('dj-rest-auth/registration/', CustomRegisterView.as_view(), name='account_signup'),
                  path('dj-rest-auth/account-confirm-email/', VerifyEmailView.as_view(),
                       name='account_email_verification_sent'),
                  path('password/reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(),
                       name='password_reset_confirm'),

                  path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
                  path('dj-rest-auth/', include('dj_rest_auth.urls')),


              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


