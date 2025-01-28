from django.urls import path
from . import views

urlpatterns = [
    path('generate-story/', views.generate_story, name='generate_story'),
    path('', views.dashboard, name='dashboard'),
]