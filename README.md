# genice-rdf

A [GenIce](https://github.com/vitroid/GenIce) plugin to calculate the radial distribution functions.

## Requirements

* [GenIce](https://github.com/vitroid/GenIce) >=0.16 must be installed.
* [PairList](https://github.com/vitroid/PairList).

## Installation

### System-wide installation

Not supported.

### Private installation

    % make install
or copy the files in genice/formats into your local formats folder of GenIce.

## Usage

	% genice 1c -r 3 3 3 -f _RDF > 1c.rdf

## Test in place

    % make test
