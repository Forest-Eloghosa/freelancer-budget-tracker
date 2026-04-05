from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordResetForm, SetPasswordForm, UserCreationForm
)
from .models import Category, Transaction


class BootstrapAuthForm(AuthenticationForm):
    """
    AuthenticationForm with Bootstrap CSS classes applied to all widgets.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'autocomplete': 'username',
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'autocomplete': 'current-password',
        })


class BootstrapPasswordResetForm(PasswordResetForm):
    """
    PasswordResetForm with Bootstrap CSS classes applied to all widgets.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'autocomplete': 'email',
        })


class BootstrapSetPasswordForm(SetPasswordForm):
    """
    SetPasswordForm with Bootstrap CSS classes applied to all widgets.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'autocomplete': 'new-password',
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'autocomplete': 'new-password',
        })


class BootstrapUserCreationForm(UserCreationForm):
    """
    UserCreationForm with Bootstrap CSS classes applied to all widgets.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class CategoryForm(forms.ModelForm):
    """
    Form used to create and edit user categories.
    """

    class Meta:
        model = Category
        fields = ['name', 'type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
        }


class TransactionForm(forms.ModelForm):
    """
    Form used to create and edit financial transactions.
    """

    class Meta:
        model = Transaction
        fields = ['category', 'amount', 'date', 'description']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}
            ),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
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
