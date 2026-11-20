from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from django.http import Http404
from .models import Trip, Expense, AdvancePayment
from .forms import ExpenseForm, AdvancePaymentForm, TripForm
from .calculators import calculate_trip_totals
from django.urls import reverse


def _is_manager(user):
    return bool(
        user.is_authenticated
        and (user.is_superuser or getattr(user, 'role', '') == 'manager')
    )


def _get_accessible_trip(user, pk):
    if _is_manager(user):
        return get_object_or_404(Trip, pk=pk)
    return get_object_or_404(Trip, pk=pk, traveler=user)


@login_required
def trip_list(request):
    """Εμφάνιση λίστας ταξιδιών του συνδεδεμένου χρήστη"""
    if _is_manager(request.user):
        trips = Trip.objects.filter(is_active=True)
    else:
        trips = Trip.objects.filter(traveler=request.user, is_active=True)

    return render(request, 'trips/trip_list.html', {'trips': trips})


@login_required
def trip_detail(request, pk):
    """Αναλυτική προβολή ταξιδιού με τα έξοδα και τους υπολογισμούς τους"""
    trip = _get_accessible_trip(request.user, pk)
    totals = calculate_trip_totals(trip)

  
    balance = totals['balance']

    context = {
        'trip': trip,
        'totals': totals,
       
        'balance': balance,
    }
    return render(request, 'trips/trip_detail.html', context)


@login_required
def add_expense(request, trip_pk):
    """Προσθήκη νέου εξόδου σε συγκεκριμένο ταξίδι"""
    trip = _get_accessible_trip(request.user, trip_pk)

 if form.is_valid():
            expense = form.save(commit=False)
            expense.trip = trip
            if trip.start_date and trip.end_date and not (trip.start_date <= expense.date <= trip.end_date):
                form.add_error(
                    'date',
                    f"Η ημερομηνία εξόδου πρέπει να είναι μεταξύ {trip.start_date} και {trip.end_date}."
                )
            else:
                try:
                    expense.save()
                    return redirect('trips:trip_detail', pk=trip.pk)
                except Exception as exc:
                    form.add_error(None, f"Σφάλμα κατά την αποθήκευση: {exc}")
    else:
        form = ExpenseForm()

    return render(request, 'trips/add_expense.html', {'form': form, 'trip': trip})


@login_required
def add_advance(request, trip_pk):
    """Προσθήκη προκαταβολής σε συγκεκριμένο ταξίδι (μόνο manager)"""
    if not _is_manager(request.user):
        raise PermissionDenied

    trip = get_object_or_404(Trip, pk=trip_pk)

    if request.method == 'POST':
        form = AdvancePaymentForm(request.POST)
        if form.is_valid():
            advance = form.save(commit=False)
            advance.trip = trip
            advance.save()
            return redirect('trips:trip_detail', pk=trip.pk)
    else:
        form = AdvancePaymentForm()

    return render(request, 'trips/add_advance.html', {'form': form, 'trip': trip})


# --- Views για Έξοδα ---

@login_required
def expense_edit(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if not _is_manager(request.user) and expense.trip.traveler != request.user:
        raise Http404()

    trip_pk = expense.trip.pk
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('trips:trip_detail', pk=trip_pk)
    else:
        form = ExpenseForm(instance=expense)

    return render(request, 'trips/add_expense.html', {'form': form, 'trip': expense.trip})


@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if not _is_manager(request.user) and expense.trip.traveler != request.user:
        raise Http404()

    trip_pk = expense.trip.pk
    if request.method == 'POST':
        expense.delete()
        return redirect('trips:trip_detail', pk=trip_pk)
    return render(request, 'trips/expense_confirm_delete.html', {'expense': expense})


# --- Views για Προκαταβολές ---

@login_required
def advance_edit(request, pk):
    if not _is_manager(request.user):
        raise PermissionDenied

    advance = get_object_or_404(AdvancePayment, pk=pk)
    trip_pk = advance.trip.pk
    if request.method == 'POST':
        form = AdvancePaymentForm(request.POST, instance=advance)
        if form.is_valid():
            form.save()
            return redirect('trips:trip_detail', pk=trip_pk)
    else:
        form = AdvancePaymentForm(instance=advance)

    return render(request, 'trips/add_advance.html', {'form': form, 'trip': advance.trip})


@login_required
def advance_delete(request, pk):
    if not _is_manager(request.user):
        raise PermissionDenied

    advance = get_object_or_404(AdvancePayment, pk=pk)
    trip_pk = advance.trip.pk
    if request.method == 'POST':
        advance.delete()
        return redirect('trips:trip_detail', pk=trip_pk)
    return render(request, 'trips/advance_confirm_delete.html', {'advance': advance})


@login_required
@require_POST
def expense_approve(request, pk):
    if not _is_manager(request.user):
        raise PermissionDenied

    expense = get_object_or_404(Expense, pk=pk)
    expense.status = 'APPROVED'
    expense.is_approved = True
    expense.save()
    return redirect('trips:trip_detail', pk=expense.trip.pk)


@login_required
@require_POST
def expense_reject(request, pk):
    if not _is_manager(request.user):
        raise PermissionDenied

    expense = get_object_or_404(Expense, pk=pk)
    expense.status = 'REJECTED'
    expense.is_approved = False
    expense.save()
    return redirect('trips:trip_detail', pk=expense.trip.pk)


@login_required
def add_trip(request):
    if request.method == 'POST':
        form = TripForm(request.POST)
        if form.is_valid():
            trip = form.save(commit=False)
            if not _is_manager(request.user) or not trip.traveler:
                trip.traveler = request.user
            trip.save()
            return redirect('trips:trip_detail', pk=trip.pk)
    else:
        form = TripForm()

    return render(request, 'trips/add_trip.html', {'form': form})
