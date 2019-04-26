
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
  return 0;
}

