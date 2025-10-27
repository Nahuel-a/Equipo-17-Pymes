import importlib
import traceback

modules = [
    'app.schemas.firmas',
    'app.schemas.documents',
    'app.crud.documents',
    'app.crud.firmas',
    'app.api.routers.api_firmas',
    'app.api.routers.documents',
    'app.utils.firmas',
]

print('Running smoke imports...')
results = {}
for m in modules:
    try:
        importlib.import_module(m)
        results[m] = ('OK', None)
        print(f"[OK] {m}")
    except Exception as e:
        tb = traceback.format_exc()
        results[m] = ('ERROR', tb)
        print(f"[ERROR] {m}: {e.__class__.__name__}: {e}")
        print(tb)

# Summarize
print('\nSummary:')
for m, (status, tb) in results.items():
    print(f"{m}: {status}")

# Exit with non-zero if any error (so run_in_terminal shows non-zero exit code)
if any(status == 'ERROR' for status, _ in results.values()):
    raise SystemExit(1)
else:
    print('All imports OK')
