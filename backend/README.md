
# Backend - Equipo-17-Pymes

This README documents recent backend work related to digital signatures and how to run tests locally without touching the production database.

## Original note (kept for context)

> El problema esta en como se obtiene el Token, no entiendo el porque no lo obtiene si la logica "esta bien encaminada"

You can find the auth/login code in:

- `backend/app/api/routers/auth.py` - login flow
- `backend/app/utils/oauth2.py` - token creation and verification

---

## What was added for digital signatures

- Model: `backend/app/models/document.py`
- CRUD helper: `backend/app/crud/documents.py`
- Crypto utilities: `backend/app/utils/firmas.py`
- Router: `backend/app/api/routers/firmas.py`
- Pydantic schemas: `backend/app/schemas/documents.py`
- Unit test (offline, DB-free): `backend/app/test/test_firmas.py`
- Offline SQL migration: `backend/documents_migration_offline.sql`

These additions implement signing and verification helpers and a router to expose them via HTTP endpoints. The router uses dependency injection for DB sessions and authentication; unit tests override these dependencies so they run without a database.

## Run unit tests (DB not required)

1. Create and activate a virtualenv in the repository root (PowerShell):

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
```

2. Install test dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install pytest pytest-asyncio httpx fastapi pyjwt email-validator cryptography
```

3. Run the signing unit test:

```powershell
$env:PYTHONPATH = "$(Resolve-Path backend\\app)"
pytest backend/app/test/test_firmas.py::test_firma_y_verificacion -q
```

The test generates an RSA keypair, signs a sample string, and verifies the signature. It mocks the DB CRUDs and authentication dependencies to remain fully offline.

## Offline migration

A SQL file `backend/documents_migration_offline.sql` is included with the `CREATE TABLE` statements for review. This file is intended for manual application or to be converted into an Alembic migration by maintainers with DB access.

## Notes / Security

- The router currently generates temporary private keys for demo/testing. In production, keys must be stored and managed securely (KMS, HSM, or secure DB storage).
- The public key should be associated with the `pymes` entity and stored; the API should not return private keys.
- Pydantic v2 raises deprecation warnings about `from_orm` / `orm_mode`. Consider a follow-up to migrate models to Pydantic v2 recommended patterns.

## Next steps (optional)

- Create an Alembic migration and apply to the DB (requires DB access and credentials). See `alembic/` for configuration.
- Persist public keys in the `pymes` table (requires schema change + migration).
- Add end-to-end tests that exercise the HTTP endpoints after migrations are applied.

If you want, I can prepare an Alembic migration PR targeting `main` or `development` once you confirm DB credentials/access and acceptance of schema changes.
