
/** \example core/simple.cpp
    Simple example of using the IMP C++ library.
    This should be equivalent to the first part of the Python example simple.py.
*/

////  Define header
#include <IMP.h>
#include <boost/program_options.hpp>
#include "boost/filesystem.hpp" 
namespace po = boost::program_options;

#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>

struct stat st = {0};

#include <fstream>
//#include <IMP/kernel.h>
#include <IMP/algebra.h>
#include <IMP/core.h>
#include <IMP/Model.h>
#include <IMP/Particle.h>
#include <IMP/core/Harmonic.h>
#include <IMP/Optimizer.h>
#include <IMP/SingletonScore.h>
#include <IMP/AttributeOptimizer.h>
int main() {
  //IMP_NEW(IMP::kernel::Model, m, ());
  IMP_NEW(IMP::Model, m, ());
  // Create two "untyped" kernel::Particles
  //IMP_NEW(IMP::kernel::Particle, p1, (m));
  IMP_NEW(IMP::Particle, p1, (m));
  //IMP_NEW(IMP::kernel::Particle, p2, (m));
  IMP_NEW(IMP::Particle, p2, (m));
  // "Decorate" the kernel::Particles with x,y,z attributes (point-like
  // particles)
  IMP::core::XYZ d1 = IMP::core::XYZ::setup_particle(p1);
  IMP::core::XYZ d2 = IMP::core::XYZ::setup_particle(p2);
  // Use some XYZ-specific functionality (set coordinates)
  d1.set_coordinates(IMP::algebra::Vector3D(10.0, 10.0, 10.0));
  d2.set_coordinates(IMP::algebra::Vector3D(-10.0, -10.0, -10.0));
  std::cout << d1 << " " << d2 << std::endl;
  
  
  // Harmonically restrain p1 to be zero distance from the origin 
  // the type of variable can be refered in python by (type(f))
  IMP_NEW(IMP::core::Harmonic, f,(0.0,1.0));
  
  IMP_NEW(IMP::core::DistanceToSingletonScore,s,(f, IMP::algebra::Vector3D(0.0, 0.0, 0.0)));  
  
  IMP_NEW(IMP::core::SingletonRestraint,r1,(s, p1));


  // Harmonically restrain p1 and p2 to be distance 5.0 apart
  IMP_NEW(IMP::core::Harmonic, f2,(5.0,1.0));
  std::string restr2 = "Restraint 2";
  IMP_NEW(IMP::core::DistancePairScore,s2,(f2,restr2));
  IMP_NEW(IMP::core::PairRestraint,r2,(s2,IMP::ParticlePair(p1,p2)));

  // Optimize the x,y,z coordinates of both particles with conjugate gradients
  IMP::RestraintsAdaptor restraints_list;
  restraints_list.push_back(r1);
  restraints_list.push_back(r2);
  IMP_NEW(IMP::core::RestraintsScoringFunction,sf,(restraints_list, "scoring function"));
  bool set_true = true;
  d1.set_coordinates_are_optimized(set_true);
  d2.set_coordinates_are_optimized(set_true);
  
  IMP_NEW(IMP::core::ConjugateGradients, o, (m));
  //IMP::core::ConjugateGradients* o = new IMP::core::ConjugateGradients(m);
  o->set_scoring_function(sf);
  o->optimize(50);
  std::cout << d1 << " " << d2 << std::endl;
  return 0;
}

