from django.apps import AppConfig


class BudgetConfig(AppConfig):
    """
    Configuration for the budget application.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'budget'
