from decimal import Decimal
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal, ROUND_HALF_UP


class User(AbstractUser):
    ROLE_CHOICES = (
        ('traveler', 'Ταξιδιώτης'),
        ('manager', 'Διαχειριστής / Εγκριτής'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='traveler')
    is_active = models.BooleanField(default=True)


class Project(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    grant_agreement = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=255)
    changes = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"[{self.timestamp}] {self.user}: {self.action}"


class Expense(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Σε εκκρεμότητα'),
        ('APPROVED', 'Εγκρίθηκε'),
        ('REJECTED', 'Απορρίφθηκε'),
    ]
    trip = models.ForeignKey('Trip', on_delete=models.CASCADE, related_name='expenses')
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    date = models.DateField()

    amount_in_currency = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='EUR')
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=6, default=Decimal('1.000000'))
    corporate_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    traveler_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    description = models.TextField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    is_approved = models.BooleanField(default=False)

    def clean(self):
        super().clean()
        if self.trip and self.date:
            if self.trip.start_date and self.trip.end_date:
                if not (self.trip.start_date <= self.date <= self.trip.end_date):
                    raise ValidationError(
                        f"Προειδοποίηση: Η ημερομηνία εξόδου ({self.date}) "
                        f"βρίσκεται εκτός των ημερομηνιών του ταξιδιού "
                        f"({self.trip.start_date} έως {self.trip.end_date})."
                    )

    def save(self, *args, **kwargs):
        self.is_approved = (self.status == 'APPROVED')
        super().save(*args, **kwargs)

    def calculate_total(self):
        rate = self.exchange_rate if self.exchange_rate and self.exchange_rate > 0 else Decimal('1')
        if self.currency == 'EUR':
         eur_amount = self.amount_in_currency
        else:
         eur_amount = self.amount_in_currency / rate
        return eur_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return round(self.amount_in_currency * self.exchange_rate, 2)

    def __str__(self):    
        return f"{self.date} - {self.category}: {self.amount_in_currency} {self.currency}"


class AdvancePayment(models.Model):
    trip = models.ForeignKey('Trip', on_delete=models.CASCADE, related_name='advances')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    reference = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Advance {self.amount} EUR for {self.trip}"


class Trip(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Πρόχειρο'),
        ('submitted', 'Υποβλήθηκε'),
        ('approved', 'Εγκρίθηκε'),
        ('rejected', 'Απορρίφθηκε'),
        ('closed', 'Ολοκληρώθηκε'),
    )
    code = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    traveler = models.ForeignKey(User, on_delete=models.PROTECT, related_name='trips')
    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name='trips')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} - {self.title}"


class Settlement(models.Model):
    trip = models.OneToOneField(Trip, on_delete=models.CASCADE, related_name='settlement')
    calculated_balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    already_paid_refunds = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    final_payable = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    is_closed = models.BooleanField(default=False)

    def __str__(self):
        return f"Settlement for {self.trip} - Balance: {self.calculated_balance}"