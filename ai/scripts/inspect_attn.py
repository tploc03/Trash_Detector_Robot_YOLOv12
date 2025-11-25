import inspect
import importlib
import pkgutil
import ultralytics

print('ultralytics version:', getattr(ultralytics, '__version__', 'unknown'))
print('ultralytics path:', ultralytics.__file__)

found = False
for finder, name, ispkg in pkgutil.walk_packages(path=ultralytics.__path__, prefix=ultralytics.__name__ + '.'):
    if any(p in name for p in ('nn', 'modules', 'tasks', 'model', 'layers')):
        try:
            mod = importlib.import_module(name)
        except Exception as e:
            continue
        if hasattr(mod, 'AAttn'):
            cls = getattr(mod, 'AAttn')
            print('\nFound AAttn in module:', name)
            print('Class object:', cls)
            try:
                src = inspect.getsource(cls)
                print('\n--- AAttn source ---\n')
                print(src)
                print('\n--- end source ---\n')
            except Exception as e:
                print('Could not get source:', e)
            found = True
            break

if not found:
    print('AAttn class not found in ultralytics package (searched common subpackages).')
