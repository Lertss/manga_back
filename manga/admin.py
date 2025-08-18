from django.contrib import admin

from manga import models

admin.site.register(models.Author)
admin.site.register(models.Country)
admin.site.register(models.Genre)

admin.site.register(models.Tag)
admin.site.register(models.Manga)
admin.site.register(models.Chapter)
admin.site.register(models.Page)


class MangaAdm(admin.TabularInline):
    fk_name = "category"
    model = models.Manga


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [
        MangaAdm,
    ]
