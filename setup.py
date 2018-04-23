#!/usr/bin/env python

# from distutils.core import setup, Extension
from setuptools import setup, Extension
from numpy.distutils.misc_util import get_numpy_include_dirs
import os
import codecs
import re

#Copied from wheel package
here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(os.path.dirname(__file__), 'genice_rdf', '__init__.py'),
                 encoding='utf8') as version_file:
    metadata = dict(re.findall(r"""__([a-z]+)__ = "([^"]+)""", version_file.read()))
    

setup(
    name='genice_rdf',
    version=metadata['version'],
    description='RDF format pluing for GenIce.',
    #long_description=README + '\n\n' +  CHANGES,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
    ],
    author='Masakazu Matsumoto',
    author_email='vitroid@gmail.com',
    url='https://github.com/vitroid/genice-rdf/',
    keywords=['genice', 'RDF'],

    packages=['genice_rdf',
              'genice_rdf.formats',
    ],
    
    entry_points = {
        'genice_format_hook7': [
            '_RDF    = genice_rdf.formats._RDF:hook7',
        ],
    },
    install_requires=['PairList>=0.2.2', 'genice>=0.23'],

    license='MIT',
)