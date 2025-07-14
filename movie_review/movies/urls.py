from django.contrib import admin
from django.urls import path

from . import views

app_name = 'movies'
urlpatterns = [
    path('', views.MovieList.as_view(), name='movie-list'),
    path('<int:movie_id>', views.MovieDetail.as_view(), name='movie-detail'), 
    path('comment/create/<int:movie_id>/', views.CommentList.as_view(),  name='comment-list'),
    path('comment/list/<int:movie_id>/', views.CommentList.as_view(), name='comment-create'),
    # path('<int:movie_id>/comments/', views.M=)
]

# <타입: 매개변수 이름>