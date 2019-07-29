#!/usr/bin/env python
import sys
from tool import line_replacer
import genice_rdf
from genice_rdf.formats._RDF import __doc__
import distutils.core

setup = distutils.core.run_setup("setup.py")

d = {
    "%%usage%%"   : "\n".join(__doc__.splitlines()[2:]),
    "%%summary%%" : __doc__.splitlines()[1],
    "%%version%%" : setup.get_version(),
    "%%package%%" : setup.get_name(),
    "%%url%%"     : setup.get_url(),
    "%%genice%%"  : "[GenIce](https://github.com/vitroid/GenIce)",
    "%%requires%%": "\n".join(setup.install_requires),
}


for line in sys.stdin:
    print(line_replacer(line, d), end="")
