# apps/studio/urls.py
from django.urls import path
from . import views

app_name = 'studio'

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('create/', views.project_create, name='project_create'),
    path('<int:project_id>/', views.project_detail, name='project_detail'),
    path('<int:project_id>/delete/', views.project_delete, name='project_delete'),
    path('<int:project_id>/files/', views.file_tree, name='file_tree'),
    path('<int:project_id>/file/', views.file_content, name='file_content'),
    path('<int:project_id>/chat/', views.studio_chat, name='studio_chat'),
    path('<int:project_id>/chat/history/', views.chat_history, name='chat_history'),
    path('api/set-model/', views.set_model_preference, name='set_model_preference'),
    path('api/get-model/', views.get_model_preference, name='get_model_preference'),
]