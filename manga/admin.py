from django.contrib import admin

from manga import models

admin.site.register(models.Author)
admin.site.register(models.Country)
admin.site.register(models.Genre)

admin.site.register(models.Tags)
admin.site.register(models.Manga)


class GalleryAdm(admin.TabularInline):
    fk_name = 'glawa'
    model = models.Gallery


@admin.register(models.Glawa)
class GlawaAdmin(admin.ModelAdmin):
    inlines = [GalleryAdm, ]


class MangaAdm(admin.TabularInline):
    fk_name = 'category'
    model = models.Manga


@admin.register(models.Categorys)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [MangaAdm, ]
