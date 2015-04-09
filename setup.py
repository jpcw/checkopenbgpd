# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os
import sys


version = '0.4.dev0'

here = os.path.abspath(os.path.dirname(__file__))

def read_file(*pathes):
    path = os.path.join(here, *pathes)
    if os.path.isfile(path):
        with open(path, 'r') as desc_file:
            return desc_file.read()
    else:
        return ''

desc_files = (('README.rst',), ('docs', 'CHANGES.rst'),
                ('docs', 'CONTRIBUTORS.rst'))

long_description = '\n\n'.join([read_file(*pathes) for pathes in desc_files])

install_requires=['nagiosplugin']

if sys.version_info < (2, 7):
    extras_require = {'test': ['setuptools', 'mock', 'unittest2', 'argparse']}
    install_requires.append('argparse')
else:
    extras_require = {'test': ['setuptools', 'mock']}

setup(name='checkopenbgpd',
      version=version,
      description="Check OpenBGPD sessions Nagios|Icinga|shinken|etc plugin",
      long_description=long_description,
      platforms = ["any"],
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",        "License :: OSI Approved :: BSD License",
        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: POSIX :: BSD :: OpenBSD',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Monitoring',
        ],
      keywords="Nagios Icinga plugin check openbgpd openbsd monitoring",
      author="Jean-Philippe Camguilhem",
      author_email="jp.camguilhem__at__gmail.com",
      url="https://github.com/jpcw/checkopenbgpd/",
      license="BSD",
      packages=find_packages("src"),
      package_dir = {"": "src"},
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      test_suite='checkopenbgpd.tests',
      extras_require=extras_require,
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      check_openbgpd = checkopenbgpd:main
      """,
      )

# vim:set et sts=4 ts=4 tw=80:
