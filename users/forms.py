from django import forms

from .models import CustomUser


class UploadFormUser(forms.ModelForm):
    """
    Form for uploading and updating CustomUser profile information.

    Fields:
        gender (str): Gender of the user.
        adult (bool): Whether the user is an adult.
        avatar (ImageField): User's avatar image.
        slug (str): Unique slug for the user.
        first_name (str): First name of the user.
        last_name (str): Last name of the user.
    """

    class Meta:
        model = CustomUser
        fields = (
            "gender",
            "adult",
            "avatar",
            "slug",
            "first_name",
            "last_name ",
        )
