from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Sets hashed password for Kostas'

    def handle(self, *args, **options):
        User = get_user_model()
        user = User.objects.filter(username='Kostas').first()
        if user:
            user.set_password('Avgeros2027!')
            user.is_active = True
            user.save()
            self.stdout.write(self.style.SUCCESS('Password updated for Kostas'))
        else:
            self.stdout.write(self.style.WARNING('User Kostas not found'))
