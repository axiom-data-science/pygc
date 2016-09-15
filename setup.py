from __future__ import with_statement
from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()


def version():
    with open('VERSION') as f:
        return f.read().strip()


reqs = [line.strip() for line in open('requirements.txt')]

setup(
    namespace_packages = [],
    name                 = "pygc",
    version              = version(),
    description          = "Great Circle calculations in Python using Vincenty's formulae",
    long_description     = readme(),
    license              = 'MIT',
    author               = "Kyle Wilcox",
    author_email         = "kyle@axiomdatascience.com",
    url                  = "https://github.com/axiom-data-science/pygc",
    packages             = find_packages(),
    install_requires     = reqs,
    classifiers          = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
    ],
)
