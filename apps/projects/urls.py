from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_projects, name='list_projects'),
    path('generate/', views.generate_project, name='generate_project'),
    path('approve/', views.approve_project, name='approve_project'),
    path('<int:project_id>/delete/', views.delete_project, name='delete_project'),
]