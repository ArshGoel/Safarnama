from django.urls import path
from . import views

urlpatterns = [
    path('generate-story/', views.generate_story, name='generate_story'),
    path('dashboard/', views.dashboard, name='dashboard'),
]