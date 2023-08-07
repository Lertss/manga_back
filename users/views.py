from dj_rest_auth.registration.views import RegisterView
from requests import Response

from manga_back import settings
from .serializers import CustomRegisterSerializer
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





