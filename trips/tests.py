from django.test import TestCase
from decimal import Decimal
from datetime import date
from trips.models import Trip, Expense, AdvancePayment, Category, Project
from trips.calculators import calculate_trip_totals
from django.contrib.auth import get_user_model

User = get_user_model()

class TripCalculatorTestCase(TestCase):
    def setUp(self):
        self.traveler = User.objects.create_user(username='marios', password='password')
        self.project = Project.objects.create(code="PRJ01", name="Ερευνητικό Έργο Α")
        self.category = Category.objects.create(name="Διαμονή")
        self.trip = Trip.objects.create(
            code="TRIP01",
            title="Ερευνητικό Ταξίδι",
            project=self.project,
            traveler=self.traveler,
            start_date=date(2026, 11, 18),
            end_date=date(2026, 11, 22)
        )

    def test_trip_financial_calculations(self):
        # Δημιουργία εξόδου σύμφωνα με το παράδειγμα: 610,77 corporate + 105,55 traveler = 716,32 συνολικό
        expense = Expense.objects.create(
            trip=self.trip,
            category=self.category,
            date=date(2026, 11, 19),
            amount_in_currency=Decimal('716.32'),
            corporate_paid=Decimal('610.77'),
            traveler_paid=Decimal('105.55'),
            status='PENDING'
        )
        
        # 1. Έλεγχος αρχικού δηλωμένου κόστους
        totals = calculate_trip_totals(self.trip)
        self.assertEqual(totals['total_declared'], Decimal('716.32'))
        self.assertEqual(totals['total_approved'], Decimal('0.00')) # Αρχικά 0 μέχρι να εγκριθεί!

        # 2. Έγκριση με μερική απόρριψη/μείωση ή έγκριση ως έχει
        expense.status = 'APPROVED'
        expense.save()
        
        totals = calculate_trip_totals(self.trip)
        self.assertEqual(totals['total_approved'], Decimal('716.32'))

        # 3. Προσθήκη προκαταβολής 50.00 €
        AdvancePayment.objects.create(
            trip=self.trip,
            date=date(2026, 11, 17),
            amount=Decimal('50.00'),
            reference='Προκαταβολή ταξιδιού'
        )
        
        totals = calculate_trip_totals(self.trip)
        self.assertEqual(totals['total_advances'], Decimal('50.00'))

    def test_traveler_cannot_access_other_traveler_trip(self):     
         other_traveler = User.objects.create_user(username='other_user', password='password')
         self.client.login(username='other_user', password='password')
         response = self.client.get(f'/trips/{self.trip.pk}/')  # ή reverse('trips:trip_detail', args=[self.trip.pk])
         self.assertEqual(response.status_code, 404)