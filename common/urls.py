from common.views import ChapterCommentsView, CommentViewSet, MangaCommentsView, MangaRatingViewSet
from django.urls import include, path
from rest_framework import routers


router = routers.DefaultRouter()


router.register(r"comments", CommentViewSet)
router.register(r"manga-ratings", MangaRatingViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("mangas/<slug:slug>/comments/", MangaCommentsView.as_view(), name="manga-comments"),
    path("chapters/<slug:chapter_slug>/comments/", ChapterCommentsView.as_view(), name="chapter-comments"),
]
