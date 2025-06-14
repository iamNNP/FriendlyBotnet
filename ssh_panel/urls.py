from django.urls import path
from . import views

app_name = 'ssh_panel'
 
urlpatterns = [
    path('', views.index, name='index'),
    path('stream/', views.stream_command_output, name='stream'),
    path('get_containers/', views.get_containers, name='get_containers'),
    path('stop/', views.stop_command, name='stop_command'),
    path('history_json/', views.command_history_json, name='command_history_json'),
    path('shortcuts/', views.get_shortcuts, name='get_shortcuts'),
    path('upload_shortcuts/', views.upload_shortcuts, name='upload_shortcuts'),
    path('delete_shortcut/', views.delete_shortcut, name='delete_shortcut'),
    path('get_container_outputs/', views.get_container_outputs, name='get_container_outputs'),
    path('clean_outputs/', views.clean_outputs, name='clean_outputs'),
]