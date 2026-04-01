from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    path('categories/', views.categories, name='categories'),
    path(
        'add-category/',
        views.add_category,
        name='add_category',
    ),
    path(
        'delete-category/<int:category_id>/',
        views.delete_category,
        name='delete_category',
    ),
    path(
        'edit-category/<int:category_id>/',
        views.edit_category,
        name='edit_category',
    ),

    path('add/', views.add_transaction, name='add_transaction'),
    path('transactions/', views.transactions, name='transactions'),
    path(
        'edit-transaction/<int:transaction_id>/',
        views.edit_transaction,
        name='edit_transaction',
    ),
    path(
        'delete-transaction/<int:transaction_id>/',
        views.delete_transaction,
        name='delete_transaction',
    ),
    path('signup/', views.signup_view, name='signup'),
]
