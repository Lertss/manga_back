from django.contrib import admin
from .models import CustomUser, MangaList, Notification

admin.site.register(CustomUser)
admin.site.register(MangaList)
admin.site.register(Notification)
