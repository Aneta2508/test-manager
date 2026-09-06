from django.urls import path
from . import views

app_name = 'defects'

urlpatterns = [
    path('', views.defect_list, name='defect_list'),
    path('add/<int:test_case_pk>/', views.defect_add, name='defect_add'),
    path('<int:pk>/', views.defect_detail, name='defect_detail'),
    path('<int:pk>/edit/', views.defect_edit, name='defect_edit'),
    path('<int:pk>/delete/', views.defect_delete, name='defect_delete'),
]