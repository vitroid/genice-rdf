# coding: utf-8
"""
A GenIce format plugin to calculate radial distribution functions.

Usage: 
    % genice 1c -r 3 3 3 -w tip4p -f _RDF > 1c.rdf
    % genice 1c -r 3 3 3 -w tip4p -f _RDF[OW,H=HW1=HW2] > 1c.rdf
    % analice data.gro  -O OW -H HW[12] -w tip3p -f _RDF[OW,HW1=HW2] > data.rdf

Options:
    Atom name
    Atom name and aliases chained with "=".

You can specify the list of atom types to be calculated.

For example, in the following case, TIP4P water has four different atom
types (OW, HW1, HW2, and MW), so all the possible 10 combinations of 
atom types will be examined.

    % genice 1c -r 3 3 3 -w tip4p -f _RDF > 1c.rdf

If you just want the RDF of OW and H, and HW1 and HW2 should be 
abbreviated by H, specify the option string like following.

    % genice 1c -r 3 3 3 -w tip4p -f _RDF[OW,H=HW1=HW2] > 1c.rdf

"""

import itertools as it
import numpy as np
import pairlist as pl
from collections import defaultdict


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
    


def hook7(lattice):
    global options
    atomtypes = options["atomtypes"]
        
    lattice.logger.info("Hook7: Output radial distribution functions.")
    lattice.logger.info("  Total number of atoms: {0}".format(len(lattice.atoms)))
    binw = 0.003
    nbin = 300
    cellmat = lattice.repcell.mat
    rpos = defaultdict(list)
    for atom in lattice.atoms:
        resno, resname, atomname, position, order = atom
        alias = atomname
        if atomtypes is not None:
            if atomname in atomtypes:
                alias = atomtypes[atomname]
            else:
                continue
        rpos[alias].append(lattice.repcell.abs2rel(position))
    rdf = []
    rdfname = []
    volume =  np.linalg.det(lattice.repcell.mat)
    grid = pl.determine_grid(cellmat,binw*nbin)
    lattice.logger.info("  Accelerate using pairlist.")
    for atomname in rpos:
        ra = rpos[atomname] = np.array(rpos[atomname])
        na = ra.shape[0]
        lattice.logger.info("  Pair {0}-{0}".format(atomname))
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
        lattice.logger.info("  Pair {0}-{1}".format(a,b))
        i,j,delta = pl.pairs_fine_hetero(ra, rb, binw*nbin, cellmat, grid, distance=True, raw=True)
        delta = np.floor(delta/binw)
        hist = dict(zip(*np.unique(delta, return_counts=True)))
        rdfname.append((a,b))
        rdf.append(hist2rdf(hist, volume, (na,nb), binw, nbin))
    print("# r/nm ", "\t".join(["{0}-{1}".format(*name) for name in rdfname]))
    for i in range(1,nbin):
        values = [i*binw]+[r[i] for r in rdf]
        print("\t".join(["{0:.3f}".format(v) for v in values]))
    lattice.logger.info("Hook7: end.")


def argparser(lattice, arg):
    global options
    lattice.logger.info("Hook0: Preprocess.")
    options={"atomtypes":None}
    if arg != "":
        atomtypes = dict()
        for a in arg.split(","):
            aliases = a.split("=")
            for alias in aliases:
                atomtypes[alias] = alias[0]
        options["atomtypes"] = atomtypes
    lattice.logger.info("Hook0: end.")
    

hooks = {0:argparser,7:hook7}
