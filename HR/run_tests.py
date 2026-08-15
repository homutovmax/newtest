#!/usr/bin/env python3
"""Regression test runner for HR pipeline.
   Run before deploy to catch regressions.
   Usage: python run_tests.py [--verbose]"""
import sys, os, time, importlib, importlib.util, inspect

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

VERBOSE = '--verbose' in sys.argv or '-v' in sys.argv
TEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests')

passed = 0
failed = 0
errors = []


def run_test(func):
    global passed, failed
    name = func.__name__
    try:
        func()
        passed += 1
        if VERBOSE:
            print(f'  PASS  {name}')
    except AssertionError as e:
        failed += 1
        msg = str(e) if str(e) else 'assertion failed'
        errors.append(f'{name}: {msg}')
        print(f'  FAIL  {name}')
        if VERBOSE:
            print(f'        {msg}')
    except Exception as e:
        failed += 1
        errors.append(f'{name}: {e}')
        print(f'  FAIL  {name} (exception)')
        if VERBOSE:
            import traceback
            traceback.print_exc()


print('=' * 55)
print('  HR PIPELINE — REGRESSION TESTS')
print('=' * 55)

t0 = time.time()

# Discover and run all test modules
test_files = sorted(f for f in os.listdir(TEST_DIR) if f.startswith('test_') and f.endswith('.py'))
if not test_files:
    print('  No test_*.py files found in tests/')
    sys.exit(1)

for tf in test_files:
    mod_name = tf[:-3]
    print(f'\n[{mod_name}]')
    spec = importlib.util.spec_from_file_location(mod_name, os.path.join(TEST_DIR, tf))
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as e:
        print(f'  FAIL  module import error: {e}')
        errors.append(f'{mod_name}: import error: {e}')
        failed += 1
        continue

    for name, func in inspect.getmembers(mod, inspect.isfunction):
        if name.startswith('test_'):
            run_test(func)

elapsed = time.time() - t0

print()
print('=' * 55)
total = passed + failed
print(f'  RESULTS: {passed} passed, {failed} failed ({total} total)')
print(f'  Time: {elapsed:.1f}s')
print('=' * 55)
if errors:
    print('\nFAILURES:')
    for e in errors:
        print(f'  {e}')

if failed > 0:
    sys.exit(1)
else:
    print('\n  ALL TESTS PASSED')
