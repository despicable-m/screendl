"""urls for moviedl """
from django.urls import path
from django.urls.conf import include
from . import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('', views.MovieViewSet, basename='movie')

urlpatterns = [
    path('movie/', include(router.urls)),
    path('search/', views.MovieAPIView.as_view()),
    path('popular/', views.PopularView.as_view()),
    path('recommend/<str:tmdb_id>', views.RecommendView.as_view())
]