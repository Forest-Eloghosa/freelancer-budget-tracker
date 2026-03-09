from django.shortcuts import render
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from .models import Transaction
# Create your views here.

@login_required
def dashboard(request):
    total_income = Transaction.objects.filter(
        user=request.user,
        category__type='income'
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_expenses = Transaction.objects.filter(
        user=request.user,
        category__type='expense'
    ).aggregate(total=Sum('amount'))['total'] or 0

    balance = total_income - total_expenses

    recent_transactions = Transaction.objects.filter(
        user=request.user
    ).order_by('-date')[:5]

    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': balance,
        'recent_transactions': recent_transactions,
    }

    return render(request, 'budget/dashboard.html', context)


def add_transaction(request):
    return render(request, 'budget/add_transaction.html')


def transactions(request):
    return render(request, 'budget/transactions.html')


def categories(request):
    return render(request, 'budget/categories.html')