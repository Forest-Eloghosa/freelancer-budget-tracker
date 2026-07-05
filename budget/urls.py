from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path(
        'dashboard/',
        views.dashboard,
        name='dashboard'
    ),

    path(
        'categories/',
        views.categories,
        name='categories'
    ),

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

    path(
        'add/',
        views.add_transaction,
        name='add_transaction'
    ),

    path(
        'transactions/',
        views.transactions,
        name='transactions'
    ),

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

    path(
        'signup/',
        views.signup_view,
        name='signup'
    ),

    path(
        'premium/',
        views.premium,
        name='premium'
    ),

    path(
        'create-checkout-session/',
        views.create_checkout_session,
        name='create_checkout_session'
    ),

    path(
        'checkout-success/',
        views.checkout_success,
        name='checkout_success'
    ),

    path(
        'manage-subscription/',
        views.manage_subscription,
        name='manage_subscription'
    ),

    path(
        'export-transactions/',
        views.export_transactions,
        name='export_transactions'
    ),

    path(
        'premium-insights/',
        views.premium_insights,
        name='premium_insights'
    ),

    path(
    "stripe/webhook/",
    views.stripe_webhook,
    name="stripe_webhook",
   ),
]
