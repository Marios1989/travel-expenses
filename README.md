# Travel Expense System

## Περιβαλλοντικές μεταβλητές (.env)
Ορίστε τις παρακάτω μεταβλητές περιβάλλοντος:
- `SECRET_KEY`: μυστικό κλειδί Django
- `DEBUG`: `True` ή `False`
- `POSTGRES_DB`: όνομα βάσης PostgreSQL
- `POSTGRES_USER`: χρήστης βάσης PostgreSQL
- `POSTGRES_PASSWORD`: κωδικός βάσης PostgreSQL
- `POSTGRES_HOST`: host βάσης (π.χ. `db` στο Docker Compose)
- `POSTGRES_PORT`: θύρα βάσης (π.χ. `5432`)

## Εκκίνηση με Docker Compose
```bash```
docker compose up --build