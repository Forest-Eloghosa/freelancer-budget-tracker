from django import forms
from .models import Category, Transaction


class CategoryForm(forms.ModelForm):
    """
    Form used to create and edit user categories.

    Allows users to define a category name and assign it
    as either an income or expense type.
    """

    class Meta:
        model = Category
        fields = ['name', 'type']


class TransactionForm(forms.ModelForm):
    """
    Form used to create and edit financial transactions.

    Includes validation for positive amounts and limits
    category selection to those owned by the logged-in user.
    """

    class Meta:
        model = Transaction
        fields = ['category', 'amount', 'date', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        """
        Custom initialisation to filter category choices
        based on the logged-in user.
        """
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields
            ['category'].queryset = Category.objects.filter(user=user)

    def clean_amount(self):
        """
        Ensure that transaction amount is greater than zero.
        """
        amount = self.cleaned_data.get('amount')

        if amount is None:
            return amount

        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than 0.")

        return amount
