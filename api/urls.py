from django.urls import path
from . import views


urlpatterns = [
    path('strings/', views.create_string, name='create_string'),      
    path('strings', views.list_strings, name='list_strings'),    
    path('strings/filter-by-natural-language', views.filter_nl, name='filter_nl'),
    path('strings/<str:string_value>/', views.get_string, name='get_string'), 
    path('strings/<str:string_value>', views.delete_string, name='delete_string'),
]