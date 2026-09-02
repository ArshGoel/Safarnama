from django.urls import path
from . import views

urlpatterns = [
    path('generate-story/', views.generate_story, name='generate_story'),
    path('', views.dashboard, name='dashboard'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('chatbot/clear/', views.clear_chat, name='clear_chat'),
    path('documentation/', views.documentation, name='documentation'),
    path('documentation/upload/', views.upload_document, name='upload_document'),
    path('documentation/view/<int:doc_id>/', views.view_document_file, name='view_document_file'),
    path('documentation/rename/<int:doc_id>/', views.rename_document, name='rename_document'),
    path('documentation/delete/<int:doc_id>/', views.delete_document, name='delete_document'),
    path('destination/<slug:slug>/', views.destination_detail, name='destination_detail'),
    path('planner/', views.travel_planner, name='travel_planner'),
    path('itinery/', views.itinery, name='itinery'),
    path('trip_suggestion/<str:trip_id>/', views.trip_result, name='trip_result'),
    path('get_weather/', views.get_weather, name='get_weather'),
]