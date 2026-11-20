from django.urls import path
from . import views

app_name = 'trips'

urlpatterns = [
    path('', views.trip_list, name='trip_list'),
    path('trip/<int:pk>/', views.trip_detail, name='trip_detail'),
    path('trip/<int:trip_pk>/expense/add/', views.add_expense, name='add_expense'),
    path('trip/<int:trip_pk>/advance/add/', views.add_advance, name='add_advance'),
    path('trip/add/', views.add_trip, name='add_trip'),
    
    # Νέα URLs για Επεξεργασία & Διαγραφή Εξόδων
    path('expense/<int:pk>/edit/', views.expense_edit, name='expense_edit'),
    path('expense/<int:pk>/delete/', views.expense_delete, name='expense_delete'),
    
    # Νέα URLs για Επεξεργασία & Διαγραφή Προκαταβολών
    path('advance/<int:pk>/edit/', views.advance_edit, name='advance_edit'),
    path('advance/<int:pk>/delete/', views.advance_delete, name='advance_delete'),
    path('expense/<int:pk>/approve/', views.expense_approve, name='expense_approve'),
    path('expense/<int:pk>/reject/', views.expense_reject, name='expense_reject'),
]