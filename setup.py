#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
# setup.py
#

from distutils.core import setup

setup(name        ='Nodesnap',
      version     ='pre-alpha',
      description ='Utility for making network nodes backup',
      author      ='Jimmy Thrasibule',
      package_dir = {'': 'src/lib'},
      packages    = ['app', 'fs', 'net', 'util'],
      scripts     = ['src/scripts/nodesnap'],
      license     = 'GNU Affero General Public License version 3',
      keywords    = 'omniswitch cisco node network backup ssh telnet',
      classifiers = [
                     'Development Status :: 2 - Pre-Alpha',
                     'Environment :: Console',
                     'Intended Audience :: System Administrators',
                     'License :: OSI Approved :: GNU Affero General Public License v3',
                     'Natural Language :: English',
                     'Operating System :: Unix',
                     'Programming Language :: Python',
                     'Topic :: System :: Archiving :: Backup',
                     'Topic :: System :: Networking',
                    ],
      )
