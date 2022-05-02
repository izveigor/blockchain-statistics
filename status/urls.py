from django.urls import path
from . import views

urlpatterns = [
    path('', views.BlockListView.as_view(), name="main"),
    path('search', views.timeline_view, name="search"),
    path('about', views.about, name="about"),
]
