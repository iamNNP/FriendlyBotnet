from django.urls import path
from . import views

app_name = 'ssh_panel'
 
urlpatterns = [
    path('', views.index, name='index'),
    path('stream/', views.stream_command_output, name='stream'),
] 