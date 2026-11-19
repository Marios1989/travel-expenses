from decimal import Decimal
from datetime import date
from django.test import TestCase
from django.contrib.auth import get_user_model
from trips.models import Project, Category, Trip, Expense, AdvancePayment
from trips.calculators import calculate_trip_totals

User = get_user_model()


class TripTotalsScenarioTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="traveler1", password="password123")
        self.project = Project.objects.create(code="PRJ-TEST", name="Test Project")
        self.category = Category.objects.create(name="Διαμονή & Έξοδα")
        self.trip = Trip.objects.create(
            code="TRP-001",
            title="Δοκιμαστικό Ταξίδι",
            traveler=self.user,
            project=self.project,
            start_date=date(2026, 11, 1),
            end_date=date(2026, 11, 30),
            is_active=True,
        )

    def test_scenario_totals(self):
        # 1. Εταιρικό έξοδο 610,77 (εγκεκριμένο)
        Expense.objects.create(
            trip=self.trip,
            category=self.category,
            date=date(2026, 11, 5),
            amount_in_currency=Decimal("610.77"),
            currency="EUR",
            exchange_rate=Decimal("1.000000"),
            corporate_paid=Decimal("610.77"),
            traveler_paid=Decimal("0.00"),
            status="APPROVED",
            is_active=True,
        )

        # 2. Έξοδο ταξιδιώτη που εγκρίνεται: 105,55 - 14,30 = 91,25
        Expense.objects.create(
            trip=self.trip,
            category=self.category,
            date=date(2026, 11, 6),
            amount_in_currency=Decimal("91.25"),
            currency="EUR",
            exchange_rate=Decimal("1.000000"),
            corporate_paid=Decimal("0.00"),
            traveler_paid=Decimal("91.25"),
            status="APPROVED",
            is_active=True,
        )

        # 3. Απορριφθέν έξοδο ταξιδιώτη 14,30 (δηλωμένο αλλά όχι εγκεκριμένο)
        Expense.objects.create(
            trip=self.trip,
            category=self.category,
            date=date(2026, 11, 7),
            amount_in_currency=Decimal("14.30"),
            currency="EUR",
            exchange_rate=Decimal("1.000000"),
            corporate_paid=Decimal("0.00"),
            traveler_paid=Decimal("14.30"),
            status="REJECTED",
            is_active=True,
        )

        # 4. Προκαταβολή 50,00 -> υπόλοιπο ταξιδιώτη: 91,25 - 50,00 = 41,25
        AdvancePayment.objects.create(
            trip=self.trip,
            amount=Decimal("50.00"),
            date=date(2026, 11, 2),
            reference="ADV-01",
        )

        totals = calculate_trip_totals(self.trip)

        self.assertEqual(totals["total_declared"], Decimal("716.32"))
        self.assertEqual(totals["total_approved"], Decimal("702.02"))
        self.assertEqual(totals["balance"], Decimal("41.25"))