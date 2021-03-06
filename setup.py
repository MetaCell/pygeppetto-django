import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='pygeppetto-django',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='Python Geppetto Core Server developed in Django',
    long_description=README,
    url='https://github.com/MetaCell/pygeppetto-django',
    author="MetaCell",
    author_email="info@metacell.us",
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.9',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'channels==2.1.2', 'Django==1.11.7', 'websocket-client==0.48.0',
        'requests==2.19.1', 'enforce==0.3.4', 'quantities==0.12.1'
    ]
)
