## \example core/simple.py
# Illustration of simple usage of the IMP library from Python.
#

from __future__ import print_function

import IMP
import IMP.algebra
import IMP.core
import sys
import IMP
import IMP.atom
import IMP.container


IMP.setup_from_argv(sys.argv, "simple example")

m = IMP.Model()

# Create two "untyped" particles
p1 = m.add_particle('p1')
p2 = m.add_particle('p2')

# "Decorate" the particles with x,y,z attributes (point-like particles)
d1 = IMP.core.XYZ.setup_particle(m, p1)
d2 = IMP.core.XYZ.setup_particle(m, p2)

# Use some XYZ-specific functionality (set coordinates)
d1.set_coordinates(IMP.algebra.Vector3D(10.0, 10.0, 10.0))
d2.set_coordinates(IMP.algebra.Vector3D(-10.0, -10.0, -10.0))
print(d1, d2)

# Harmonically restrain p1 to be zero distance from the origin
f = IMP.core.Harmonic(0.0, 1.0)
s = IMP.core.DistanceToSingletonScore(f, IMP.algebra.Vector3D(0., 0., 0.))
r1 = IMP.core.SingletonRestraint(m, s, p1)

# Harmonically restrain p1 and p2 to be distance 5.0 apart
f = IMP.core.Harmonic(5.0, 1.0)
s = IMP.core.DistancePairScore(f)
r2 = IMP.core.PairRestraint(m, s, (p1, p2))

# Optimize the x,y,z coordinates of both particles with conjugate gradients
sf = IMP.core.RestraintsScoringFunction([r1, r2], "scoring function")
d1.set_coordinates_are_optimized(True)
d2.set_coordinates_are_optimized(True)
o = IMP.core.ConjugateGradients(m)
o.set_scoring_function(sf)
o.optimize(50)
print(d1, d2)



## Load a protein from a PDB file and then restrain all the bonds to have their
# current length.


m = IMP.Model()
prot = IMP.atom.read_pdb(IMP.atom.get_example_path("example_protein.pdb"), m)
IMP.atom.add_bonds(prot)
bds = IMP.atom.get_internal_bonds(prot)
bl = IMP.container.ListSingletonContainer(m, bds)
h = IMP.core.Harmonic(0, 1)
bs = IMP.atom.BondSingletonScore(h)
br = IMP.container.SingletonsRestraint(bs, bl)
print(br.evaluate(False))


# The script shows how to assess a protein conformation using DOPE.



def create_representation():
    m = IMP.Model()
    mp0 = IMP.atom.read_pdb(IMP.atom.get_example_path(
        'example_protein.pdb'), m, IMP.atom.NonWaterNonHydrogenPDBSelector())
    prot = IMP.atom.get_by_type(mp0, IMP.atom.CHAIN_TYPE)[0]
    return (m, prot)


def add_dope(m, prot):
    ps = IMP.atom.get_by_type(prot, IMP.atom.ATOM_TYPE)
    for p in ps:
        if not IMP.atom.Atom.get_is_setup(p):
            print("Huh?", p)
    dpc = IMP.container.ClosePairContainer(ps, 15.0, 0.0)
# exclude pairs of atoms belonging to the same residue
# for consistency with MODELLER DOPE score
    f = IMP.atom.SameResiduePairFilter()
    dpc.add_pair_filter(f)
    IMP.atom.add_dope_score_data(prot)
    dps = IMP.atom.DopePairScore(15.0)
#    dps= IMP.membrane.DopePairScore(15.0, IMP.membrane.get_data_path("dope_scorehr.lib"))
    d = IMP.container.PairsRestraint(dps, dpc)
    return d

print("creating representation")
(m, prot) = create_representation()

print("creating DOPE score function")
d = add_dope(m, prot)

IMP.set_check_level(IMP.USAGE)
print("DOPE SCORE ::", d.evaluate(False))



# An atomic protein structure is created from primary (amino-acid) sequence.
#

# Use the CHARMM all-atom (i.e. including hydrogens) topology and parameters
topology = IMP.atom.CHARMMTopology(IMP.atom.get_all_atom_CHARMM_parameters())

# Create a single chain of amino acids and apply the standard C- and N-
# termini patches
topology.add_sequence('IACGACKPECPVNIIQGS')
topology.apply_default_patches()

# Make an IMP Hierarchy (atoms, residues, chains) that corresponds to
# this topology
m = IMP.Model()
h = topology.create_hierarchy(m)

# Generate coordinates for all atoms in the Hierarchy, using CHARMM internal
# coordinate information (an extended chain conformation will be produced).
# Since in some cases this information can be incomplete, better results will
# be obtained if the atom types are assigned first and the CHARMM parameters
# file is loaded, as we do here, so missing information can be filled in.
# It will still work without that information, but will approximate the
# coordinates.
topology.add_atom_types(h)
topology.add_coordinates(h)

# Hierarchies in IMP must have radii
IMP.atom.add_radii(h)

# Write out the final structure to a PDB file
IMP.atom.write_pdb(h, 'structure.pdb')
