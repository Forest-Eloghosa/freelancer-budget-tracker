from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add/', views.add_transaction, name='add_transaction'),
    path('transactions/', views.transactions, name='transactions'),
    path('categories/', views.categories, name='categories'),
]