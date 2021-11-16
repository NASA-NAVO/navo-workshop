#!/usr/bin/env python
"""
Check for required dependencies for the workshop.
Usage::

  % python check_env.py

"""
from distutils.version import LooseVersion

# NOTE: Update minversion values as needed.
# This should match environment.yml file.
PKGS = {'jupyter': None,
        'notebook': '6.0',
        'numpy': '1.16',
        'matplotlib': '3.2',
        'jupyterlab': 3.0,
        'astropy': '4.1',
        'pyvo': '1.2dev713',
        'astroquery': '0.4.3'
        }


def check_package(package_name, minimum_version=None, verbose=True):
    errors = False
    try:
        pkg = __import__(package_name)
    except ImportError as err:
        print(f'Error: Failed import: {err}')
        errors = True
    else:
        if package_name in ('jupyter', 'keyring'):
            installed_version = ''
        elif package_name == 'xlwt':
            installed_version = pkg.__VERSION__
        else:
            installed_version = pkg.__version__
        if (minimum_version is not None and
                LooseVersion(installed_version) <
                LooseVersion(str(minimum_version))):
            print(f'Error: {package_name} version {minimum_version} or '
                  f'later is required, you have version {installed_version}')
            errors = True
        if not errors and verbose:
            print('Found', package_name, installed_version)
    return errors


def run_checks():
    errors = []
    for package_name, min_version in PKGS.items():
        errors.append(check_package(package_name, minimum_version=min_version))
    if any(errors):
        print('\nThere are errors that you must resolve before running the '
              'tutorials.')
    else:
        print('\nYour Python environment is good to go!')


if __name__ == '__main__':
    run_checks()
