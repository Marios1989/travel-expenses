FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["sh", "-c", "python manage.py migrate && python manage.py shell -c \"from django.contrib.auth import get_user_model; User = get_user_model(); u, _ = User.objects.get_or_create(username='admin'); u.email='admin@example.com'; u.is_staff=True; u.is_superuser=True; u.is_active=True; u.set_password('AdminPass123!'); u.save(); print('ADMIN_READY')\" && python manage.py runserver 0.0.0.0:${PORT:-8000}"]
