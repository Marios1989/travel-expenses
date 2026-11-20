from django import forms
from .models import Trip, Expense, AdvancePayment

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = [
            'category', 'date', 'amount_in_currency', 'currency', 
            'exchange_rate', 'corporate_paid', 'traveler_paid', 'description'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'amount_in_currency': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'currency': forms.TextInput(attrs={'class': 'form-control'}),
            'exchange_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'corporate_paid': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'traveler_paid': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'category': 'Κατηγορία εξόδου',
            'date': 'Ημερομηνία εξόδου',
            'amount_in_currency': 'Ποσό στο νόμισμα συναλλαγής',
            'currency': 'Νόμισμα (π.χ. EUR, USD)',
            'exchange_rate': 'Ισοτιμία (μονάδες ξένου νομίσματος ανά 1 EUR)',
            'corporate_paid': 'Πληρώθηκε από εταιρεία (EUR)',
            'traveler_paid': 'Πληρώθηκε από ταξιδιώτη (EUR)',
            'description': 'Περιγραφή / Σημειώσεις',
            }
        help_texts = {
            'exchange_rate': 'Πόσες μονάδες ξένου νομίσματος αντιστοιχούν σε 1 EUR (για EUR βάλε 1).',
        }

class AdvancePaymentForm(forms.ModelForm):
    class Meta:
        model = AdvancePayment
        fields = ['amount', 'date', 'reference']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
        }
class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ['code', 'title', 'project', 'traveler']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'project': forms.Select(attrs={'class': 'form-select'}),
            'traveler': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            
        }
