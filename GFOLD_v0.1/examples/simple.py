## \example core/simple.py
# Illustration of simple usage of the IMP library from Python.
#

import IMP
import IMP.algebra
import IMP.core
import sys

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
