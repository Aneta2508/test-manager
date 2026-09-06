from django.urls import path
from . import views

app_name = 'test_library'

urlpatterns = [
    path('', views.library_list, name='library_list'),
    path('add/', views.library_add, name='library_add'),
    path('<int:pk>/', views.library_detail, name='library_detail'),
    path('<int:pk>/edit/', views.library_edit, name='library_edit'),
    path('<int:pk>/delete/', views.library_delete, name='library_delete'),
    path('<int:pk>/copy/<int:plan_pk>/', views.library_copy_to_plan, name='library_copy_to_plan'),
]