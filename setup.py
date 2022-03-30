# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='django-restful-admin-ppb',
    version='1.1.4',
    description='Python Django RestFul Admin (forked by PPB)',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/surface-security/django-restful-admin-ppb/',
    author='PPB - InfoSec Engineering',
    author_email='surface@paddypowerbetfair.com',
    license='MIT',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    packages=['django_restful_admin'],
    # What does your project relate to?
    keywords='django restful admin',
    install_requires=[
        'django>=2.0.0',
        'djangorestframework>=3.0.0'
    ]
)
