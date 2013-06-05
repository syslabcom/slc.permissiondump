# -*- coding: utf-8 -*-
"""Installer for the slc.permissiondump package."""

from setuptools import find_packages
from setuptools import setup

import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


long_description = \
    read('README.rst') + \
    read('docs', 'CHANGELOG.rst') + \
    read('docs', 'LICENSE.rst')


setup(
    name='slc.permissiondump',
    version='0.2.dev0',
    description="Visualize a tree of local roles assigned on Plone items.",
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
    ],
    author='NiteoWeb Ltd.',
    author_email='info@niteoweb.com',
    url='http://pypi.python.org/pypi/slc.permissiondump',
    license='BSD',
    packages=find_packages(),
    install_requires=[
        'setuptools',
    ],
    extras_require={
        'development': [
            'zest.releaser',
            'check-manifest',
        ],
    },
    entry_points="""
    [zopectl.command]
    dump_roles = slc.permissiondump.dump_roles:main
    html_export = slc.permissiondump.html_export:main
    """,
    include_package_data=True,
    zip_safe=False,
)
