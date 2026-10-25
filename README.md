# Lightweight Project Management and Commercial ERP

A fast, resource-efficient, production-minded ERP built for small businesses to manage clients, projects, activities, payments, expenses, and profitability.

## Technology Stack
- **Backend**: Python 3.12, FastAPI
- **Database**: SQLite (SQLAlchemy 2.x, Alembic)
- **Frontend**: HTML via Jinja2, HTMX for dynamic interactions, minimal CSS
- **Authentication**: Secure Session-Based Cookies with bcrypt

## Features
- **Technical Module**: Manage clients, projects, automatic stages (Stage A, B, C), and reusable activity templates. Track project progress natively.
- **Commercial Module**: Record payments and project expenses. Accurately tracks outstanding balances and profitability. Protected strictly via Role-Based Access Control (RBAC).
- **Public Interactive Demo**: Visitors can access `/demo` to spin up an isolated DB instance with realistic demo data, avoiding modifications to core business data.

## Setup Instructions
1. Install Python 3.12+.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Initialize the database and run migrations:
   ```bash
   alembic upgrade head
   ```
4. Create the initial administrator account:
   ```bash
   python create_admin.py <username> <password>
   ```
   *Note: Do not commit the database (`erp.db`) or `.env` to version control.*
5. Run the application:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
6. (Optional) Run the demo seeder if `DEMO_MODE=True`:
   ```bash
   PYTHONPATH=. python app/db/demo_seed.py
   cp erp.db demo_base.db
   ```

## Environment Variables
See `.env.example` for details.

## Backup and Restore
- **Backup**: Since the application uses SQLite, backup the database simply by copying `erp.db` to a secure location (e.g. `cp erp.db erp_backup_$(date +%F).db`).
- **Restore**: Replace the active `erp.db` file with your backup file and restart the ASGI server.

## Testing
Run the test suite using pytest:
```bash
PYTHONPATH=. pytest app/tests/
```
