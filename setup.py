# -*- coding: utf-8 -*-
"""Installer for the slc.permissiondump package."""

import ez_setup
ez_setup.use_setuptools()

from setuptools import find_packages
from setuptools import setup

setup(
    name='slc.permissiondump',
    version='0.1',

    author='SYSLAB.COM GmbH',
    author_email='info@syslab.com',
    url='http://syslab.com/',
    license='BSD',

    packages=find_packages(),
    package_data={
        'slc.permissiondump': ['static/*.css', 'static/*.js']
    },

    entry_points="""
    [zopectl.command]
    dump_roles = slc.permissiondump.dump_roles:main
    html_export = slc.permissiondump.html_export:main
    """
)
