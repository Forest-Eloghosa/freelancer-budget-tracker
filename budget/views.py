from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

import csv
import logging

import stripe

from .forms import CategoryForm, TransactionForm
from .models import Category, Profile, Transaction

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


def home(request):
    """
    Display landing page for new users.
    Redirect authenticated users to dashboard.
    """

    if request.user.is_authenticated:
        return redirect("dashboard")

    return render(request, 'budget/home.html')


def signup_view(request):
    """
    Allow a new user to create an account.
    """

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Account created successfully. Welcome!'
            )
            return redirect('login')

        messages.error(
            request,
            'Please correct the errors below.'
        )

    else:
        form = UserCreationForm()

    return render(
        request,
        'registration/signup.html',
        {'form': form}
    )


class CustomLoginView(LoginView):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard")

        return super().dispatch(
            request,
            *args,
            **kwargs
        )
    
    
@login_required
def dashboard(request):
    """
    Display the user's dashboard with totals, recent transactions,
    and guidance for first-time users.
    """
    transactions = Transaction.objects.filter(user=request.user)

    income = transactions.filter(
        category__type='income'
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    expenses = transactions.filter(
        category__type='expense'
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    balance = income - expenses
    recent_transactions = transactions.order_by('-date')[:5]
    categories_count = Category.objects.filter(user=request.user).count()
    profile, created = Profile.objects.get_or_create(user=request.user)

    context = {
        'income': float(income),
        'expenses': float(expenses),
        'balance': float(balance),
        'recent_transactions': recent_transactions,
        'categories_count': categories_count,
        'is_premium': profile.is_premium,
        'profile': profile,
    }

    return render(request, 'budget/dashboard.html', context)


@login_required
def categories(request):
    """
    Display all categories created by the logged-in user.
    """
    categories = Category.objects.filter(user=request.user)
    return render(
        request,
        'budget/categories.html',
        {'categories': categories}
    )


@login_required
def add_category(request):
    """
    Allow the user to create a new category.
    """
    form = CategoryForm(request.POST or None)

    if form.is_valid():
        category = form.save(commit=False)
        category.user = request.user
        category.save()
        messages.success(request, 'Category added successfully.')
        return redirect('categories')

    return render(request, 'budget/add_category.html', {'form': form})


@login_required
def edit_category(request, category_id):
    """
    Allow the user to edit one of their categories.
    """
    category = get_object_or_404(Category, id=category_id, user=request.user)
    form = CategoryForm(request.POST or None, instance=category)

    if form.is_valid():
        form.save()
        messages.success(request, 'Category updated successfully.')
        return redirect('categories')

    return render(request, 'budget/edit_category.html', {'form': form})


@login_required
def delete_category(request, category_id):
    """
    Delete a category belonging to the logged-in user
    after confirmation.
    """
    category = get_object_or_404(Category, id=category_id, user=request.user)

    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully.')
        return redirect('categories')

    return render(
        request,
        'budget/delete_category.html',
        {'category': category}
    )


@login_required
def add_transaction(request):
    """
    Allow the user to create a new transaction.
    """
    form = TransactionForm(request.POST or None, user=request.user)

    if form.is_valid():
        transaction = form.save(commit=False)
        transaction.user = request.user
        transaction.save()
        messages.success(request, 'Transaction added successfully.')
        return redirect('transactions')

    return render(request, 'budget/add_transaction.html', {'form': form})


@login_required
def edit_transaction(request, transaction_id):
    """
    Edit a transaction belonging to the logged-in user.
    """
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
        messages.success(request, 'Transaction updated successfully.')
        return redirect('transactions')

    return render(
        request,
        'budget/edit_transaction.html',
        {'form': form}
    )


@login_required
def delete_transaction(request, transaction_id):
    """
    Delete a transaction belonging to the logged-in user.
    """
    transaction = get_object_or_404(
        Transaction,
        id=transaction_id,
        user=request.user
    )

    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'Transaction deleted successfully.')
        return redirect('transactions')

    return render(
        request,
        'budget/delete_transaction.html',
        {'transaction': transaction}
    )


@login_required
def transactions(request):
    """
Display the user's transactions with optional filters
for category, type, and month.
    """
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


@login_required
def premium(request):
    """
    Display premium page for the logged-in user interested in upgrading.
    """
    profile, _ = Profile.objects.get_or_create(user=request.user)

    return render(
        request,
        'budget/premium.html',
        {
            'profile': profile,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY
        }
    )


@login_required
def checkout_success(request):
    """
    Display the payment success page after Stripe redirects
    the customer.
    """

    session_id = request.GET.get("session_id")

    if not session_id:
        messages.error(
            request,
            "Invalid payment session. "
            "Please complete checkout to unlock Premium features."
        )
        return redirect("premium")


    profile, _ = Profile.objects.get_or_create(user=request.user)

    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except stripe.error.StripeError:
        logger.warning(
            "Unable to verify checkout session for user_id=%s session_id=%s",
            request.user.id,
            session_id,
        )
    else:
        if (
            session.payment_status == "paid"
            and str(session.client_reference_id) == str(request.user.id)
        ):
            if not profile.is_premium:
                profile.is_premium = True
                profile.save()


    context = {
        "payment_pending": not profile.is_premium,
    }


    return render(
        request,
        "budget/checkout_success.html",
        context,
    )


@login_required
@require_POST
def create_checkout_session(request):
    """
    Create a Stripe Checkout Session for purchasing
    Premium membership.
    """

    profile, _ = Profile.objects.get_or_create(
        user=request.user
    )

    if profile.is_premium:
        messages.info(
            request,
            "You already have Premium access."
        )
        return redirect("dashboard")

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        client_reference_id=request.user.id,
        line_items=[
            {
                "price_data": {
                    "currency": "eur",
                    "product_data": {
                        "name": "Premium Budget Tracker Access",
                    },
                    "unit_amount": 500,
                },
                "quantity": 1,
            }
        ],
        success_url=(
    request.build_absolute_uri("/checkout-success/")
    + "?session_id={CHECKOUT_SESSION_ID}"
),
        cancel_url=request.build_absolute_uri(
            "/premium/"
        ),
    )

    return redirect(checkout_session.url, code=303)


@login_required
def manage_subscription(request):
    """
    Allow users to manage premium subscription.
    """
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        profile.is_premium = False
        profile.save()

        messages.success(
            request,
            'Premium membership cancelled.'
        )

        return redirect('dashboard')

    return render(
        request,
        'budget/manage_subscription.html',
        {
            'profile': profile
        }
    )


@login_required
def export_transactions(request):
    """
    Export user transactions as CSV file.
    Premium feature only.
    """

    profile, _ = Profile.objects.get_or_create(
        user=request.user
    )

    if not profile.is_premium:
        messages.error(
            request,
            "Premium membership required."
        )
        return redirect('premium')

    transactions = Transaction.objects.filter(
        user=request.user
    )

    response = HttpResponse(
        content_type='text/csv'
    )

    response[
        'Content-Disposition'
    ] = 'attachment; filename="transactions.csv"'

    writer = csv.writer(response)

    writer.writerow([
        'Date',
        'Category',
        'Amount',
        'Description'
    ])

    for transaction in transactions:
        writer.writerow([
            transaction.date,
            transaction.category.name,
            transaction.amount,
            transaction.description,
        ])

    return response


@login_required
def premium_insights(request):
    """
    Display premium financial insights.
    """

    profile, _ = Profile.objects.get_or_create(
        user=request.user
    )

    if not profile.is_premium:
        messages.error(
            request,
            "Premium membership required."
        )
        return redirect('premium')

    transactions = Transaction.objects.filter(
        user=request.user
    )

    total_transactions = transactions.count()

    context = {
        'total_transactions': total_transactions,
    }

    return render(
        request,
        'budget/premium_insights.html',
        context
    )

@csrf_exempt
def stripe_webhook(request):
    """
    Receive Stripe webhook events and activate
    Premium membership after successful payment.
    """

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET,
        )

    except ValueError:
        logger.warning("Invalid webhook payload.")
        return HttpResponse(status=400)

    except stripe.error.SignatureVerificationError:
        logger.warning("Invalid webhook signature.")
        return HttpResponse(status=400)

    try:
        if event["type"] == "checkout.session.completed":

            session = event["data"]["object"]

            if session.get("payment_status") == "paid":

                user_id = session.get("client_reference_id")

                logger.info(
                    "Stripe payment completed for user_id=%s",
                    user_id
                )

                if user_id:

                    profile, _ = Profile.objects.get_or_create(
                        user_id=user_id
                    )

                    if not profile.is_premium:
                        profile.is_premium = True
                        profile.save()

                    logger.info(
                        "Premium activated successfully for user_id=%s",
                        user_id
                    )
    except Exception:
        logger.exception("Unexpected error while processing Stripe webhook.")


    return HttpResponse(status=200)