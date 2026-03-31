from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Category, Transaction
from .forms import CategoryForm, TransactionForm

# Create your views here.


@login_required
def dashboard(request):
    transactions = Transaction.objects.filter(user=request.user)

    income = transactions.filter(
        category__type='income'
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    expenses = transactions.filter(
        category__type='expense'
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    balance = income - expenses
    recent_transactions = transactions.order_by('-date')[:5]

    context = {
        'income': float(income),
        'expenses': float(expenses),
        'balance': float(balance),
        'recent_transactions': recent_transactions,
    }

    return render(request, 'budget/dashboard.html', context)


@login_required
def categories(request):
    categories = Category.objects.filter(user=request.user)
    return render(
        request,
        'budget/categories.html',
        {'categories': categories}
    )


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
    category = get_object_or_404(Category, id=category_id, user=request.user)
    category.delete()
    return redirect('categories')


@login_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id, user=request.user)
    form = CategoryForm(request.POST or None, instance=category)

    if form.is_valid():
        form.save()
        return redirect('categories')

    return render(request, 'budget/edit_category.html', {'form': form})


@login_required
def add_transaction(request):
    form = TransactionForm(request.POST or None, user=request.user)

    if form.is_valid():
        transaction = form.save(commit=False)
        transaction.user = request.user
        transaction.save()
        return redirect('transactions')

    return render(request, 'budget/add_transaction.html', {'form': form})


@login_required
def edit_transaction(request, transaction_id):
    transaction = get_object_or_404(
        Transaction,
        id=transaction_id,
        user=request.user
    )
    form = TransactionForm(
        request.POST or None,
        instance=transaction,
        user=request.user
    )

    if form.is_valid():
        form.save()
        return redirect('transactions')

    return render(
        request,
        'budget/edit_transaction.html',
        {'form': form}
    )


@login_required
def delete_transaction(request, transaction_id):
    transaction = get_object_or_404(
        Transaction,
        id=transaction_id,
        user=request.user
    )

    if request.method == 'POST':
        transaction.delete()
        return redirect('transactions')

    return render(
        request,
        'budget/delete_transaction.html',
        {'transaction': transaction}
    )


@login_required
def transactions(request):
    transactions_qs = Transaction.objects.filter(user=request.user)

    category = request.GET.get('category')
    type_filter = request.GET.get('type')
    month = request.GET.get('month')

    if category:
        transactions_qs = transactions_qs.filter(category__id=category)

    if type_filter:
        transactions_qs = transactions_qs.filter(category__type=type_filter)

    if month:
        year, month_num = month.split('-')
        transactions_qs = transactions_qs.filter(
            date__year=year,
            date__month=month_num,
        )

    context = {
        'transactions': transactions_qs.order_by('-date'),
        'categories': Category.objects.filter(user=request.user),
    }

    return render(request, 'budget/transactions.html', context)

