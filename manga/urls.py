from django.urls import path, include

from manga import views

urlpatterns = [
    path('latest_chapter/', views.GlawaListView.as_view()),
    path('home/', views.MangaListHome.as_view()),
    path('allManga/', views.allManga.as_view()),
    path('<slug:manga_slug>/<slug:glawa_slug>/', views.ShowGlawa.as_view()),
    path('<slug:manga_slug>/', views.ShowManga.as_view()),

]
