from django import forms
from .models import Category, Transaction


class CategoryForm(forms.ModelForm):
    """
    Form used to create and edit user categories.
    """

    class Meta:
        model = Category
        fields = ['name', 'type']


class TransactionForm(forms.ModelForm):
    """
    Form used to create and edit financial transactions.
    """

    class Meta:
        model = Transaction
        fields = ['category', 'amount', 'date', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        """
        Filter category choices to the logged-in user's categories.
        """
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)

    def clean_amount(self):
        """
        Ensure transaction amount is greater than zero.
        """
        amount = self.cleaned_data.get('amount')

        if amount is None:
            return amount

        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than 0.")

        return amount
