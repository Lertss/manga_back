from django.urls import path, include
from rest_framework import routers

from manga.views import MangaCreateView, MangaUpdateView, ChapterCreateView, ChapterUpdateView, ChapterListView, \
    MangaListHome, allManga, ShowChapter, ShowManga, AuthorViewSet

from users.views import add_manga_to_list, remove_manga_from_list, user_manga_list

router = routers.DefaultRouter()

router.register(r'authors', AuthorViewSet)

urlpatterns = [
    path('', include(router.urls)),

    path('add-manga-list/', add_manga_to_list, name='add-manga'),
    path('remove-manga-list/', remove_manga_from_list, name='remove-manga'),
    path('user-manga-list/', user_manga_list, name='user-manga-list'),

    path('manga/create/', MangaCreateView.as_view(), name='manga-create'),
    path('manga-update/<slug>/', MangaUpdateView.as_view(), name='manga-update'),

    path('chapter/create/', ChapterCreateView.as_view(), name='chapter-create'),
    path('chapter-update/<int:id>/', ChapterUpdateView.as_view(), name='chapter-update'),

    path('latest_chapter/', ChapterListView.as_view()),
    path('home/', MangaListHome.as_view()),
    path('allManga/', allManga.as_view()),
    path('<slug:manga_slug>/<slug:chapter_slug>/', ShowChapter.as_view()),
    path('<slug:manga_slug>/', ShowManga.as_view()),


]
