from __future__ import with_statement
from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()

def version():
    with open('VERSION') as f:
        return f.read().strip()


reqs = [line.strip() for line in open('requirements.txt')]

setup(namespace_packages = [],
    name                 = "pygc",
    version              = version(),
    description          = "Great Circle calculations in Python using Vincenty's formulae",
    long_description     = readme(),
    license              = 'MIT',
    author               = "Kyle Wilcox",
    author_email         = "wilcox.kyle@gmail.com",
    url                  = "https://github.com/axiom-data-science/pygc",
    packages             = find_packages(),
    install_requires     = reqs,
    classifiers          = [
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python',
            'Topic :: Scientific/Engineering',
        ],
)
