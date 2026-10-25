# Agent Instructions & Application Architecture

## Architecture
- **Monolithic FastAPI Application**: Uses synchronous SQLAlchemy models (`app.db.tenant`) handling tenant DB resolution dynamically.
- **Frontend**: Server-side rendered (SSR) Jinja2 templates (`app/templates`) with HTMX sprinkled for quick dynamic actions (forms POST straight back for simplicity and fallback functionality).
- **Session Auth**: Stores valid sessions in memory `SESSIONS` dict mapped to user_ids. Cookies drive authentication and isolation.
- **Demo Mode Isolation**: When `DEMO_MODE=True`, new visitors going to `/demo` get assigned a `demo_id` cookie. This maps to a copied instance of `demo_base.db` stored in `./demo_dbs/`, effectively isolating sessions natively without complex multi-tenant row logic.

## Coding Conventions
- **Dependencies**: Keep them minimal. Avoid adding massive JS/CSS frameworks.
- **Database Modularity**: Always use `get_tenant_db` from `app.db.tenant` rather than raw `SessionLocal` when working in routes. This guarantees the demo isolation logic remains intact.
- **RBAC Enforcement**: Use `RequireRole([RoleEnum...])` dependency on *every* protected endpoint. Never assume hiding a button hides the endpoint.
- **Financial Calculation Integrity**: Do not save derived totals (e.g., Outstanding Balance, Calculated Profit) back into the database tables. Calculate them on-the-fly using aggregate logic (as seen in `app/api/commercial.py` and `app/api/dashboard.py`).

## Instructions for Future Tasks
- Adding Project Stages: `ProjectStage` creation is handled upon `Project` insertion in `app/api/projects.py`. If a stage name needs altering, edit the `stage_names = ["Stage A", "Stage B", "Stage C"]` array.
- Adding Activity Templates: Templates are managed via UI `/activities/templates`. No DB modifications are needed for basic workflow unless new fields are necessary.
