from django.contrib import admin
from .models import User, Project, Category, AuditLog, Trip, Expense, AdvancePayment, Settlement
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.hashers import identify_hasher
from models import User  # ή from models import User αν το models.py είναι στη ρίζα


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Ρόλος χρήστη", {"fields": ("role",)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Ρόλος χρήστη", {"fields": ("role",)}),
    )
    list_display = ("username", "email", "first_name", "last_name", "role", "is_staff", "is_active")

    def save_model(self, request, obj, form, change):
        if obj.password:
            try:
                identify_hasher(obj.password)
            except ValueError:
                obj.set_password(obj.password)
        super().save_model(request, obj, form, change)

admin.site.register(User)
admin.site.register(Project)
admin.site.register(Category)
admin.site.register(AuditLog)
admin.site.register(Trip)
admin.site.register(Expense)
admin.site.register(AdvancePayment)
admin.site.register(Settlement)
