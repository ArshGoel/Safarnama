from django.urls import path
from . import views

urlpatterns = [
    path('generate-story/', views.generate_story, name='generate_story'),
    path('', views.dashboard, name='dashboard'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('documentation/', views.documentation, name='documentation'),
    path('itinery/', views.itinery, name='itinery'),
    path('trip_suggestion/<str:trip_id>/', views.trip_result, name='trip_result'),
    path('get_weather/', views.get_weather, name='get_weather'),
]