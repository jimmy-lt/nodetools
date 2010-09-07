#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
try:
    import app.nodesnap
except ImportError, e:
    raise ImportError(str(e) +
"""
    A critical module could not be imported.
""")

if __name__ == '__main__':
    import sys


    if len(sys.argv) == 2:
        # TODO: manage command line options.
        #
        # We run the nodesnap application, assuming the first argument
        # is the configuration file.
        APP = app.nodesnap.Nodesnap(sys.argv[1])
        APP.run()
