from django.shortcuts import render

# Create your views here.

def dashboard(request):
    return render(request, 'budget/dashboard.html')


def add_transaction(request):
    return render(request, 'budget/add_transaction.html')


def transactions(request):
    return render(request, 'budget/transactions.html')


def categories(request):
    return render(request, 'budget/categories.html')