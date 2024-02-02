from django.urls import include, path
from manga import views
from rest_framework import routers


router = routers.DefaultRouter()

router.register(r"authors", views.AuthorViewSet, basename="author")
router.register(r"chapters", views.ChapterViewSet, basename="chapter")
router.register(r"pages", views.PageViewSet, basename="page")
router.register(r"manga", views.MangaViewSet, basename="manga")
router.register(r"search", views.Search)


urlpatterns = [
    path("random-manga/", views.RandomMangaView.as_view(), name="random-manga"),
    path("top-manga-sto/", views.TopMangaView.as_view(), name="top-manga"),
    path("top-manga-last-year/", views.TopMangaLastYearView.as_view(), name="top-manga-last-year"),
    path("top-manga-comments/", views.TopMangaCommentsView.as_view(), name="top-manga-comments"),
    path("all-data/", views.AllFilter.as_view(), name="all-data"),
    path("", include(router.urls)),
    path("add-manga-list/", views.add_manga_to_list, name="add-manga"),
    path("remove-manga-list/", views.remove_manga_from_list, name="remove-manga"),
    path("user-manga-list/", views.user_manga_list, name="user-manga-list"),
    path("manga_in_user_list/<str:manga_slug>/", views.manga_in_user_list),
    path("last-chapters/", views.last_hundred_chapters, name="get_last_chapters"),
    path("allManga/", views.AllManga.as_view(), name="all_manga"),
    path("<slug:manga_slug>/<slug:chapter_slug>/", views.ShowChapter.as_view()),
    path("<slug:manga_slug>/", views.ShowManga.as_view()),
]
