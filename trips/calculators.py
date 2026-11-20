from decimal import Decimal, ROUND_HALF_UP


def round_currency(value: Decimal) -> Decimal:
    """Στρογγύλεμα σε δύο δεκαδικά ψηφία."""
    return Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def convert_foreign_currency(amount: Decimal, exchange_rate: Decimal) -> Decimal:
    """Μετατροπή ξένου νομίσματος σε EUR (ποσό / ισοτιμία) με στρογγύλεμα."""
    amt = Decimal(str(amount))
    rate = Decimal(str(exchange_rate))
    if rate <= Decimal('0'):
        return round_currency(amt)
    return round_currency(amt / rate)


def calculate_declared_cost(corporate_payments: Decimal, traveler_expenses: Decimal) -> Decimal:
    """Υπολογισμός συνολικού δηλωμένου κόστους."""
    return round_currency(Decimal(str(corporate_payments)) + Decimal(str(traveler_expenses)))


def calculate_approved_cost(declared_cost: Decimal, rejected_traveler_expense: Decimal) -> Decimal:
    """Υπολογισμός εγκεκριμένου κόστους μετά από απορρίψεις."""
    return round_currency(Decimal(str(declared_cost)) - Decimal(str(rejected_traveler_expense)))


def calculate_traveler_balance(
    approved_traveler_expenses: Decimal,
    advances: Decimal,
    already_paid_refunds: Decimal,
) -> Decimal:
    """
    Υπόλοιπο ταξιδιώτη = εγκεκριμένες δαπάνες που πλήρωσε ο ταξιδιώτης
    − προκαταβολές − ήδη καταβληθείσες επιστροφές.
    """
    return round_currency(
        Decimal(str(approved_traveler_expenses))
        - Decimal(str(advances))
        - Decimal(str(already_paid_refunds))
    )


def calculate_trip_totals(trip):
    """
    Υπολογίζει τα οικονομικά μεγέθη ενός ταξιδιού βάσει των εξόδων και προκαταβολών.
    """
    expenses = trip.expenses.filter(is_active=True)

    # 1. Συνολικό Δηλωμένο (Corporate Paid + Traveler Paid)
    total_declared = sum(
        (
            Decimal(str(exp.corporate_paid))
            + Decimal(str(exp.traveler_paid))
            for exp in expenses
        ),
        Decimal('0.00'),
    )

    # 2. Εγκεκριμένο Κόστος (Μόνο τα έξοδα με status == 'APPROVED')
    approved_expenses = expenses.filter(status='APPROVED')
    total_approved = sum(
        (
            Decimal(str(exp.corporate_paid))
            + Decimal(str(exp.traveler_paid))
            for exp in approved_expenses
        ),
        Decimal('0.00'),
    )
    
    

    # 3. Συνολικές Προκαταβολές
    total_advances = sum(
        (Decimal(str(adv.amount)) for adv in trip.advances.all()),
        Decimal('0.00'),
    )


    # 4. Υπόλοιπο / Ισοζύγιο (Εγκεκριμένα ταξιδιώτη − Προκαταβολές)
    traveler_approved_paid = sum(
        (Decimal(str(exp.traveler_paid)) for exp in approved_expenses),
        Decimal('0.00'),
    )

    balance = traveler_approved_paid - total_advances

    return {
        'total_declared': round_currency(total_declared),
        'total_approved': round_currency(total_approved),
        'total_advances': round_currency(total_advances),
        'balance': round_currency(balance),
    }