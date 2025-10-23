from django.urls import path
from . import views

urlpatterns = [
    path('strings/', views.strings_view, name='strings_view'),  
    path('strings/filter-by-natural-language/', views.filter_nl, name='filter_nl'),  
    path('strings/<str:string_value>/', views.get_or_delete_string, name='get_or_delete_string'),  
]


