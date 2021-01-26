#!/usr/bin/env python
from genice2_dev import template

import sys
from genice2_rdf.formats._RDF import __doc__ as doc
import distutils.core

setup = distutils.core.run_setup("setup.py")

print(template(sys.stdin.read(), doc, setup))
