from django.urls import path, include
from rest_framework import routers

from common.views import MangaCommentViewSet, ChapterCommentViewSet, CommentUpdateView, CommentDeleteView

router = routers.DefaultRouter()

router.register(r'mangas/(?P<manga_pk>\d+)', MangaCommentViewSet, basename='mangacomment')
router.register(r'chapters/(?P<chapter_pk>\d+)', ChapterCommentViewSet, basename='chapteracomment')

urlpatterns = [

    path('update/<int:pk>', CommentUpdateView.as_view(), name='comment-update'),
    path('delete/<int:pk>', CommentDeleteView.as_view(), name='comment-delete'),
    path('create/', include(router.urls)),

]
