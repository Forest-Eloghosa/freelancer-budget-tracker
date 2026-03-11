from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Transaction
from .models import Category
from .forms import CategoryForm
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

@login_required
def categories(request):
    categories = Category.objects.filter(user=request.user)
    return render(request, 'budget/categories.html', {'categories': categories})


@login_required
def add_category(request):
    form = CategoryForm(request.POST or None)

    if form.is_valid():
        category = form.save(commit=False)
        category.user = request.user
        category.save()
        return redirect('categories')

    return render(request, 'budget/add_category.html', {'form': form})


@login_required
def delete_category(request, category_id):
    category = Category.objects.get(id=category_id, user=request.user)
    category.delete()
    return redirect('categories')


def add_transaction(request):
    return render(request, 'budget/add_transaction.html')


def transactions(request):
    return render(request, 'budget/transactions.html')


