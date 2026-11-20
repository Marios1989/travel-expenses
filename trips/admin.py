from django.contrib import admin
from .models import User, Project, Category, AuditLog, Trip, Expense, AdvancePayment, Settlement

admin.site.register(User)
admin.site.register(Project)
admin.site.register(Category)
admin.site.register(AuditLog)
admin.site.register(Trip)
admin.site.register(Expense)
admin.site.register(AdvancePayment)
admin.site.register(Settlement)