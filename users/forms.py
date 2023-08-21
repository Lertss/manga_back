from django import forms

from .models import CustomUser


class UploadFormUser(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('gender',
                  'adult',
                  'avatar',
                  'slug',
                  'first_name',
                  'last_name ',)
