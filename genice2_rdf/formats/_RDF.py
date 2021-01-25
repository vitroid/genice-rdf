# coding: utf-8
"""
A GenIce2 format plugin to calculate radial distribution functions.

Usage:
    % genice 1c -r 3 3 3 -w tip4p -f _RDF > 1c.rdf
    % genice 1c -r 3 3 3 -w tip4p -f _RDF[OW:H=HW1=HW2] > 1c.rdf
    % analice data.gro  -O OW -H HW[12] -w tip3p -f _RDF[OW:HW1=HW2] > data.rdf

Options:
    Atom name
    Atom name and aliases chained with "=".
    json      Output in JSON format.
    range=x   Range of interest (0.9 nm)
    binw=x    Bin width (0.003 nm)

Options must be separated with colons.

You can specify the list of atom types to be calculated.

For example, in the following case, TIP4P water has four different atom
types (OW, HW1, HW2, and MW), so all the possible 10 combinations of
atom types will be examined.

    % genice 1c -r 3 3 3 -w tip4p -f _RDF > 1c.rdf

If you just want the RDF of OW and H, and HW1 and HW2 should be
abbreviated by H, specify the option string like following.

    % genice 1c -r 3 3 3 -w tip4p -f _RDF[OW:H=HW1=HW2] > 1c.rdf

"""

desc = { "ref": {},
         "brief": "Radial Distribution Functions.",
         "usage": __doc__,
         }

import itertools as it
import numpy as np
import pairlist as pl
from collections import defaultdict
import json
from logging import getLogger

def hist2rdf(hist, vol, natoms, binw, nbin):
    rdf = np.zeros(nbin)
    for r,c in hist.items():
        if r < nbin:
            rdf[int(r)] = c
    if len(natoms) == 1:
        mult   = natoms[0]**2 / 2
    else:
        mult   = natoms[0]*natoms[1]
    ri = np.arange(nbin)*binw + binw/2
    vshell = 4*np.pi*ri**2*binw
    rdf *= vol / (vshell*mult)
    return rdf


import genice2.formats
class Format(genice2.formats.Format):


    def __init__(self, **kwargs):
        logger = getLogger()
        logger.info("Hook0: Preprocess.")
        self.options={"atomtypes":{}, "json":False, "range":0.9, "binw":0.003}
        for key, value in kwargs.items():
            if key in ["JSON", "json"]:
                self.options["json"] = True
                logger.info("  JSON")
            else:
                if key == "range":
                    self.options["range"] = float(value)
                    logger.info("  Range/nm: {0}".format(self.options["range"]))
                elif key == "binw":
                    self.options["binw"] = float(value)
                    logger.info("  Range/nm: {0}".format(self.options["binw"]))
                else:
                    aliases = value.split("=")
                    aliases.append(key)
                    for alias in aliases:
                        self.options["atomtypes"][alias] = aliases[0]
                        logger.info("  {0} is an alias of {1}.".format(alias, aliases[0]))
        logger.info(self.options["atomtypes"])
        logger.info("Hook0: end.")


    def hooks(self):
        return {7:self.hook7}


    def hook7(self, lattice):
        logger = getLogger()
        atomtypes = self.options["atomtypes"]

        logger.info("Hook7: Output radial distribution functions.")
        logger.info("  Total number of atoms: {0}".format(len(lattice.atoms)))
        binw = self.options["binw"]
        nbin = int(self.options["range"]/binw)
        cellmat = lattice.repcell.mat
        rpos = defaultdict(list)
        for atom in lattice.atoms:
            resno, resname, atomname, position, order = atom
            alias = atomname
            if len(atomtypes):
                if atomname in atomtypes:
                    alias = atomtypes[atomname]
                else:
                    continue
            rpos[alias].append(lattice.repcell.abs2rel(position))
        rdf = []
        rdfname = []
        volume =  np.linalg.det(lattice.repcell.mat)
        grid = pl.determine_grid(cellmat,binw*nbin)
        logger.info("  {0}".format(rpos.keys()))
        for atomname in rpos:
            ra = rpos[atomname] = np.array(rpos[atomname])
            na = ra.shape[0]
            logger.info("  Pair {0}-{0}".format(atomname))
            i,j,delta = pl.pairs_fine(ra, binw*nbin, cellmat, grid, distance=True, raw=True)
            delta = np.floor(delta/binw)
            hist = dict(zip(*np.unique(delta, return_counts=True)))
            rdfname.append((atomname, atomname))
            rdf.append(hist2rdf(hist, volume, (na,), binw, nbin))
        for a, b in it.combinations(rpos, 2):
            ra = rpos[a]
            rb = rpos[b]
            na = ra.shape[0]
            nb = rb.shape[0]
            logger.info("  Pair {0}-{1}".format(a,b))
            i,j,delta = pl.pairs_fine_hetero(ra, rb, binw*nbin, cellmat, grid, distance=True, raw=True)
            delta = np.floor(delta/binw)
            hist = dict(zip(*np.unique(delta, return_counts=True)))
            rdfname.append((a,b))
            rdf.append(hist2rdf(hist, volume, (na,nb), binw, nbin))
        if self.options["json"]:
            D = dict()
            D["r"] = [i*binw for i in range(1,nbin)]
            for i, pair in enumerate(rdfname):
                name = "{0}--{1}".format(*pair)
                D[name] = [x for x in rdf[i]]
            self.output = json.dumps(D, indent=2, sort_keys=True)
        else:
            s = ""
            s += "# r/nm " + "\t".join(["{0}-{1}".format(*name) for name in rdfname]) + "\n"
            for i in range(1,nbin):
                values = [i*binw]+[r[i] for r in rdf]
                s += "\t".join(["{0:.3f}".format(v) for v in values]) + "\n"
            self.output = s
        logger.info("Hook7: end.")
