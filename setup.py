#!/usr/bin/env python
#
# Setup script
#
# For license information, see LICENSE.TXT

# python2.5 compatibility
from __future__ import with_statement

# Work around mbcs bug in distutils. 
# http://bugs.python.org/issue10945
import codecs 
try: 
    codecs.lookup('mbcs') 
except LookupError: 
    ascii = codecs.lookup('ascii') 
    func = lambda name, enc=ascii: {True: enc}.get(name=='mbcs') 
    codecs.register(func) 


import os
# Use the VERSION file to get the version
version_file = os.path.join(os.path.dirname(__file__), 'pagenerator', 'VERSION')
with open(version_file) as fh:
    my_version = fh.read().strip()



# setuptools
from setuptools import setup, find_packages

# Prevent setuptools from trying to add extra files to the source code
# manifest by scanning the version control system for its contents.
from setuptools.command import sdist
try:
    del sdist.finders[:]
except:
    pass

#################
import sys
def makeRed(string):
    return "\033[31m%s\033[m" % string


#################

setup(
    name = "pagenerator",
    description = "A simple page web generator",
    version = my_version,
    url = "https://github.com/shirayu/pagenerator",
    license = "GNU GENERAL PUBLIC LICENSE, Version 3",
    keywords = [],
    maintainer = "Yuta Hayashibe",
    maintainer_email = "yuta@hayashibe.jp",
    author = "Yuta Hayashibe",
    author_email = "yuta@hayashibe.jp",
    classifiers = [
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Topic :: Text Processing :: General',
    ],
    packages = find_packages(),
    zip_safe=False, # since normal files will be present too?
    scripts=["pagenerator/scripts/pagenerator",
        ],
    install_requires=['markdown'],
    )

