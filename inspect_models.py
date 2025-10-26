import traceback
print('Running inspect_models')
try:
    import models
    print('models module imported')
    print('Base present:', hasattr(models, 'Base'))
    print('Query present:', hasattr(models, 'Query'))
    print('models attributes:', [a for a in dir(models) if not a.startswith('__')])
except Exception:
    traceback.print_exc()
    raise
