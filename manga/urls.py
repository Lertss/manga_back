from django.urls import path, include
from rest_framework import routers

from common.views import add_manga_to_list, remove_manga_from_list, user_manga_list
from manga.views import MangaCreateView, MangaUpdateView, allManga, ShowManga, AuthorViewSet, AllFilter, ChapterViewSet, \
    PageViewSet, MangaListHome

router = routers.DefaultRouter()

router.register(r'authors', AuthorViewSet)
router.register(r'chapters', ChapterViewSet)
router.register(r'pages', PageViewSet)


urlpatterns = [
    path('all-data/', AllFilter.as_view(), name='all-data'),
    path('', include(router.urls)),

    path('add-manga-list/', add_manga_to_list, name='add-manga'),
    path('remove-manga-list/', remove_manga_from_list, name='remove-manga'),
    path('user-manga-list/', user_manga_list, name='user-manga-list'),

    path('manga/create/', MangaCreateView.as_view(), name='manga-create'),
    path('manga-update/<slug>/', MangaUpdateView.as_view(), name='manga-update'),


    path('home/', MangaListHome.as_view()),
    path('allManga/', allManga.as_view()),
    # path('<slug:manga_slug>/<slug:chapter_slug>/', ShowChapter.as_view()),
    path('<slug:manga_slug>/', ShowManga.as_view()),
]
