from django.urls import path
from django.urls import path, include
from . import views
from .views import register

urlpatterns =[
    path('', views.MoviesView.as_view(), name='home'),
    path("filter/", views.FilterMoviesView.as_view(), name='filter'),
    path("search/", views.Search.as_view(), name='search'),
    path("add-rating/", views.AddStarRating.as_view(), name='add_rating'),
    path("<slug:slug>/", views.MovieDetailView.as_view(), name='movie_detail'),
    path("review/<int:pk>/", views.AddReview.as_view(), name='add_review'),
    path("category/<slug:cat_slug>/", views.CategoryView.as_view(), name='category'),
    path("actor/<str:slug>/", views.ActorView.as_view(), name='actor_detail'),

    path('register/', register),

    path('pages/', include('django.contrib.flatpages.urls'), name='xz'),
]