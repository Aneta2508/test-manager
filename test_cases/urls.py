from django.urls import path
from . import views

app_name = 'test_cases'

urlpatterns = [
    # Projekty
    path('', views.project_list, name='project_list'),
    path('add/', views.project_add, name='project_add'),
    path('<int:pk>/', views.project_detail, name='project_detail'),
    path('<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('<int:pk>/delete/', views.project_delete, name='project_delete'),

    # Plany testów
    path('<int:project_pk>/plans/add/', views.test_plan_add, name='test_plan_add'),
    path('plans/<int:pk>/edit/', views.test_plan_edit, name='test_plan_edit'),
    path('plans/<int:pk>/delete/', views.test_plan_delete, name='test_plan_delete'),

    # Przypadki testowe
    path('plans/<int:plan_pk>/cases/add/', views.test_case_add, name='test_case_add'),
    path('cases/<int:pk>/', views.test_case_detail, name='test_case_detail'),
    path('cases/<int:pk>/edit/', views.test_case_edit, name='test_case_edit'),
    path('cases/<int:pk>/delete/', views.test_case_delete, name='test_case_delete'),
]