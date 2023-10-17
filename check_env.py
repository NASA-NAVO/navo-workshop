#!/usr/bin/env python
"""
Check for required dependencies for the workshop.
Usage::

  % python check_env.py

"""
from packaging.version import Version

# NOTE: Update minversion values as needed.
# Set both min and max versions to avoid ambiguity.
# This should match environment.yml file.
PKGS = {'jupyter': None,
        'numpy': ('1.24', None),
        'matplotlib': ('3.2', None),
        'jupyterlab': ('3.1', None),
        'astropy': ('5.2', None),
        'scipy': ('1.0', None),
        'pyvo': ('1.4', None),
        'astroquery': ('0.4.7dev', None),
        'jupytext': ('1.14', None)
        }


def check_package(package_name, versions=None, verbose=True):
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
        if versions is not None:
            if (versions[0] is not None
                    and Version(installed_version) < Version(versions[0])):

                print(f'Error: {package_name} version {versions[0]} or '
                      f'later is required, you have version {installed_version}')
                errors = True
            if (versions[1] is not None
                    and Version(versions[1]) < Version(installed_version)):

                print(f'Error: {package_name} version {versions[1]} or '
                      f'older is required, you have version {installed_version}')
                errors = True
        if not errors and verbose:
            print('Found', package_name, installed_version)

    return errors


def run_checks():
    errors = []
    for package_name in PKGS:
        errors.append(check_package(package_name, versions=PKGS[package_name]))

    if any(errors):
        print('\nThere are errors that you must resolve before running the '
              'tutorials.')
    else:
        print('\nYour Python environment is good to go!')


if __name__ == '__main__':
    run_checks()
