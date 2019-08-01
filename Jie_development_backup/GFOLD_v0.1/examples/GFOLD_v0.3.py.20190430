#!usr/bin/env python
############################################################################
#
#	 GFOLD : A Distance-based Protein Structure Folding
#
#	 Copyright (C) 2019 -2029	Jie Hou and Jianlin Cheng
#
############################################################################
#
#	 Method to perform distance-based modeling (TS)
#
############################################################################

from __future__ import print_function
import modeller
import IMP
import IMP.modeller
import IMP.atom
import IMP.container
import optparse
import IMP.atom
import IMP.example
import IMP.statistics
import IMP.display
import numpy as np
import sys
import os
import collections
import IMP.rotamer


#/home/jh7x3/fusion_hybrid/
project_root = '/data/jh7x3/GFOLD_v0.1/'
sys.path.insert(0, project_root)

#from GFOLD_pylib import *

print('')
print('  ############################################################################')
print('  #                                                                          #')
print('  #      GFOLD : A Distance-based Protein Structure Folding                  #')
print('  #                                                                          #')
print('  #   Copyright (C) 2019 -2029	Jie Hou and Jianlin Cheng                   #')
print('  #                                                                          #')
print('  ############################################################################')
print('  #                                                                          #')
print('  #   Method to perform distance-based modeling (TS)                         #')
print('  #                                                                          #')
print('  ############################################################################')
print('')


###########################################################################################
# (1) Build extended structure from sequence
###########################################################################################

# Use the CHARMM all-atom (i.e. including hydrogens) topology and parameters
topology = IMP.atom.CHARMMTopology(IMP.atom.get_all_atom_CHARMM_parameters())
# Create a single chain of amino acids and apply the standard C- and N-
# termini patches
f = open('3BFO-B.fasta', 'r')	
sequence = f.readlines()	
f.close()	
# removing the trailing "\n" and any header lines
sequence = [line.strip() for line in sequence if not '>' in line]
sequence = ''.join( sequence )
	
topology.add_sequence(sequence)
topology.apply_default_patches()



###########################################################################################
# (2) Load the model into IMP Hierarchy
###########################################################################################

# Make an IMP Hierarchy (atoms, residues, chains) that corresponds to
# this topology
m = IMP.Model()
h = topology.create_hierarchy(m)   ##### can we add secondary structure information to build extend structure, or add secondary structure angle restraints later
topology.add_atom_types(h)
topology.add_coordinates(h)

# Hierarchies in IMP must have radii
IMP.atom.add_radii(h)
# Write out the final structure to a PDB file
IMP.atom.write_pdb(h, '3BFO-B-init.pdb')

###########################################################################################
# Charmm forcefield
###########################################################################################

# Create an IMP model and add a heavy atom-only protein from a PDB file
m = IMP.Model()
# example_protein.pdb is assumed to be just extended chain structure obtained using structure_from_sequence example
#prot = IMP.atom.read_pdb('3BFO-B-init.pdb',m,IMP.atom.BackbonePDBSelector())  #IMP.atom.NonWaterNonHydrogenPDBSelector()
#prot = IMP.atom.read_pdb('3BFO-B-init.pdb', m,IMP.atom.CAlphaPDBSelector())  #IMP.atom.NonWaterNonHydrogenPDBSelector()
#prot = IMP.atom.read_pdb('3BFO-B.chn', m,IMP.atom.CAlphaPDBSelector())  #IMP.atom.NonWaterNonHydrogenPDBSelector()
#prot = IMP.atom.read_pdb('3BFO-B.chn', m,IMP.atom.BackbonePDBSelector())  #IMP.atom.NonWaterNonHydrogenPDBSelector()
#prot = IMP.atom.read_pdb('3BFO-B.chn', m,IMP.atom.OrPDBSelector(IMP.atom.CBetaPDBSelector(),IMP.atom.BackbonePDBSelector()))  #IMP.atom.NonWaterNonHydrogenPDBSelector()
prot = IMP.atom.read_pdb('3BFO-B-init.pdb', m,IMP.atom.OrPDBSelector(IMP.atom.CBetaPDBSelector(),IMP.atom.BackbonePDBSelector()))  #IMP.atom.NonWaterNonHydrogenPDBSelector()

'''
79 :  Atom N of residue 79
79 :  Atom CA of residue 79
79 :  Atom C of residue 79
79 :  Atom O of residue 79
79 :  Atom CB of residue 79
'''
res_model = IMP.atom.get_by_type(prot, IMP.atom.RESIDUE_TYPE)
atoms_model = IMP.atom.get_by_type(prot, IMP.atom.ATOM_TYPE)
chain_model = IMP.atom.get_by_type(prot, IMP.atom.CHAIN_TYPE)
print("there are", len(chain_model), "chains in structure.pdb")
print("chain has", len(atoms_model), "atoms")

# Get a list of all atoms in the model, and put it in a container
cont_model = IMP.container.ListSingletonContainer(atoms_model)

########################

#### load the true structure and get restraints 
# Create an IMP model and add a heavy atom-only protein from a PDB file
m_native = IMP.Model()
# example_protein.pdb is assumed to be just extended chain structure obtained using structure_from_sequence example
prot_native = IMP.atom.read_pdb('3BFO-B.chn', m_native) 
# Get a list of all atoms in the protein, and put it in a container
atoms_native = IMP.atom.get_by_type(prot_native, IMP.atom.ATOM_TYPE)
cont_native = IMP.container.ListSingletonContainer(atoms_native)



#### get information for N,CA,C,O,CB from native structure

native_dist = {}
index2ResidueName={}
index2AtomCoord={}
for i in range(0,len(cont_native.get_particles())):
	p1 = cont_native.get_particles()[i]
	#get atom information
	p1_atom = IMP.atom.Atom(p1)
	p1_coord = IMP.core.XYZ(p1).get_coordinates() #(1.885, 68.105, 54.894)
	p1_atom_name = p1_atom.get_atom_type().get_string() #'N'
	het = p1_atom_name.startswith('HET:')
	if het:
		p1_atom_name = p1_atom_name[4:]
	p1_res = IMP.atom.get_residue(p1_atom) ##1 "SER"
	p1_resname = p1_res.get_name() #'SER'
	p1_seq_id = p1_res.get_index() #1
	if p1_atom.get_atom_type() == IMP.atom.AtomType("CA"):
		index2ResidueName[p1_seq_id] = p1_resname
	
	index2AtomCoord[str(p1_seq_id)+'-'+p1_resname+'-'+p1_atom_name] = IMP.core.XYZ(p1)


#for key in index2ResidueName:
#	print(key," ",index2ResidueName[key])


#oindex2AtomCoord = collections.OrderedDict(sorted(index2AtomCoord.items()))
#for key in sorted(oindex2AtomCoord):
#	print(key,": ",oindex2AtomCoord[key])


print("there are", len(index2ResidueName.keys()), "residues in native structure")



#### get distance restraints for N-CA, CA-C, C-O, CA-CB, CA-CA, CB-CB
model_residues = {}
model_particle_index = {}
for i in range(0,len(cont_model.get_particles())):
	p1 = cont_model.get_particles()[i]
	#get atom information
	p1_atom = IMP.atom.Atom(p1)
	p1_coord = IMP.core.XYZ(p1).get_coordinates() #(1.885, 68.105, 54.894)
	p1_atom_name = p1_atom.get_atom_type().get_string() #'N'
	het = p1_atom_name.startswith('HET:')
	if het:
		p1_atom_name = p1_atom_name[4:]
	p1_res = IMP.atom.get_residue(p1_atom) ##1 "SER"
	p1_resname = p1_res.get_name() #'SER'
	p1_seq_id = p1_res.get_index() #1
	IMP.core.XYZ(p1).set_coordinates_are_optimized(True)
	if p1_atom.get_atom_type() == IMP.atom.AtomType("CA"):
		model_residues[p1_seq_id] = p1_resname
	
	info = str(p1_seq_id)+'-'+p1_resname+'-'+p1_atom_name
	model_particle_index[info] = i
	if  info not in index2AtomCoord.keys():
		print("The atom information in model not match in restraints: ",info)
		sys.exit(-1)

residue_array = sorted(model_residues.keys())
restraints_list = []
for i in range(0,len(residue_array)):
	# get N-CA, CA-C, C-O, CA-CB
	res1_indx = residue_array[i]
	res1_name = model_residues[res1_indx]
	
	res1_N_atom = str(res1_indx)+'-'+res1_name+'-N'
	res1_CA_atom = str(res1_indx)+'-'+res1_name+'-CA'
	res1_C_atom = str(res1_indx)+'-'+res1_name+'-C'
	res1_O_atom = str(res1_indx)+'-'+res1_name+'-O'
	res1_CB_atom = str(res1_indx)+'-'+res1_name+'-CB'
	
	# get native coordinates, suppose the template structure is provided
	'''
	this part is not needed, which can be replaced by stereo restraints
	# get N-CA
	if res1_N_atom in index2AtomCoord.keys() and res1_CA_atom in index2AtomCoord.keys():
		res1_N_atom_coord = index2AtomCoord[res1_N_atom]
		res1_CA_atom_coord = index2AtomCoord[res1_CA_atom]
		x1,y1,z1 = [res1_N_atom_coord.get_x(),res1_N_atom_coord.get_y(),res1_N_atom_coord.get_z()]
		x2,y2,z2 = [res1_CA_atom_coord.get_x(),res1_CA_atom_coord.get_y(),res1_CA_atom_coord.get_z()]
		dist = np.linalg.norm([x1-x2,y1-y2,z1-z2])
		
		# get the particle index in model 
		p1 = cont_model.get_particles()[model_particle_index[res1_N_atom]]
		p2 = cont_model.get_particles()[model_particle_index[res1_CA_atom]]
		f = IMP.core.Harmonic(dist, 1.0)
		s = IMP.core.DistancePairScore(f)
		r = IMP.core.PairRestraint(m, s, (p1, p2))
		restraints_list.append(r)
		
	# get CA-C
	if res1_CA_atom in index2AtomCoord.keys() and res1_C_atom in index2AtomCoord.keys():
		res1_CA_atom_coord = index2AtomCoord[res1_CA_atom]
		res1_C_atom_coord = index2AtomCoord[res1_C_atom]
		x1,y1,z1 = [res1_CA_atom_coord.get_x(),res1_CA_atom_coord.get_y(),res1_CA_atom_coord.get_z()]
		x2,y2,z2 = [res1_C_atom_coord.get_x(),res1_C_atom_coord.get_y(),res1_C_atom_coord.get_z()]
		dist = np.linalg.norm([x1-x2,y1-y2,z1-z2])
		
		# get the particle index in model 
		p1 = cont_model.get_particles()[model_particle_index[res1_CA_atom]]
		p2 = cont_model.get_particles()[model_particle_index[res1_C_atom]]
		f = IMP.core.Harmonic(dist, 1.0)
		s = IMP.core.DistancePairScore(f)
		r = IMP.core.PairRestraint(m, s, (p1, p2))
		restraints_list.append(r)
	
	# get C-O
	if res1_C_atom in index2AtomCoord.keys() and res1_O_atom in index2AtomCoord.keys():
		res1_C_atom_coord = index2AtomCoord[res1_C_atom]
		res1_O_atom_coord = index2AtomCoord[res1_O_atom]
		x1,y1,z1 = [res1_C_atom_coord.get_x(),res1_C_atom_coord.get_y(),res1_C_atom_coord.get_z()]
		x2,y2,z2 = [res1_O_atom_coord.get_x(),res1_O_atom_coord.get_y(),res1_O_atom_coord.get_z()]
		dist = np.linalg.norm([x1-x2,y1-y2,z1-z2])
		
		# get the particle index in model 
		p1 = cont_model.get_particles()[model_particle_index[res1_C_atom]]
		p2 = cont_model.get_particles()[model_particle_index[res1_O_atom]]
		f = IMP.core.Harmonic(dist, 1.0)
		s = IMP.core.DistancePairScore(f)
		r = IMP.core.PairRestraint(m, s, (p1, p2))
		restraints_list.append(r)
	
	# get CA-CB, Glycine not have CB
	if res1_CA_atom in index2AtomCoord.keys() and res1_CB_atom in index2AtomCoord.keys():
		res1_CA_atom_coord = index2AtomCoord[res1_CA_atom]
		res1_CB_atom_coord = index2AtomCoord[res1_CB_atom]
		x1,y1,z1 = [res1_CA_atom_coord.get_x(),res1_CA_atom_coord.get_y(),res1_CA_atom_coord.get_z()]
		x2,y2,z2 = [res1_CB_atom_coord.get_x(),res1_CB_atom_coord.get_y(),res1_CB_atom_coord.get_z()]
		dist = np.linalg.norm([x1-x2,y1-y2,z1-z2])
		
		# get the particle index in model 
		p1 = cont_model.get_particles()[model_particle_index[res1_CA_atom]]
		p2 = cont_model.get_particles()[model_particle_index[res1_CB_atom]]
		f = IMP.core.Harmonic(dist, 1.0)
		s = IMP.core.DistancePairScore(f)
		r = IMP.core.PairRestraint(m, s, (p1, p2))
		restraints_list.append(r)
	
	## Need add angle restraints
	## https://integrativemodeling.org/2.4.0/doc/html/stereochemistry_8py_source.html
	'''
	
	for j in range(i+1,len(residue_array)):
		res2_indx = residue_array[j]
		res2_name = model_residues[res2_indx]
		
		res2_CA_atom = str(res2_indx)+'-'+res2_name+'-CA'
		res2_CB_atom = str(res2_indx)+'-'+res2_name+'-CB'
		res2_O_atom = str(res2_indx)+'-'+res2_name+'-O'
		# get CA-CA
		if res1_CA_atom in index2AtomCoord.keys() and res2_CA_atom in index2AtomCoord.keys():
			res1_CA_atom_coord = index2AtomCoord[res1_CA_atom]
			res2_CA_atom_coord = index2AtomCoord[res2_CA_atom]
			x1,y1,z1 = [res1_CA_atom_coord.get_x(),res1_CA_atom_coord.get_y(),res1_CA_atom_coord.get_z()]
			x2,y2,z2 = [res2_CA_atom_coord.get_x(),res2_CA_atom_coord.get_y(),res2_CA_atom_coord.get_z()]
			dist = np.linalg.norm([x1-x2,y1-y2,z1-z2])
			
			# get the particle index in model 
			p1 = cont_model.get_particles()[model_particle_index[res1_CA_atom]]
			p2 = cont_model.get_particles()[model_particle_index[res2_CA_atom]]
			f = IMP.core.Harmonic(dist, 1.0)
			s = IMP.core.DistancePairScore(f)
			r = IMP.core.PairRestraint(m, s, (p1, p2))
			restraints_list.append(r)
		
		# get CB-CB
		if res1_CB_atom in index2AtomCoord.keys() and res2_CB_atom in index2AtomCoord.keys():
			res1_CB_atom_coord = index2AtomCoord[res1_CB_atom]
			res2_CB_atom_coord = index2AtomCoord[res2_CB_atom]
			x1,y1,z1 = [res1_CB_atom_coord.get_x(),res1_CB_atom_coord.get_y(),res1_CB_atom_coord.get_z()]
			x2,y2,z2 = [res2_CB_atom_coord.get_x(),res2_CB_atom_coord.get_y(),res2_CB_atom_coord.get_z()]
			dist = np.linalg.norm([x1-x2,y1-y2,z1-z2])
			
			# get the particle index in model 
			p1 = cont_model.get_particles()[model_particle_index[res1_CB_atom]]
			p2 = cont_model.get_particles()[model_particle_index[res2_CB_atom]]
			f = IMP.core.Harmonic(dist, 1.0)
			s = IMP.core.DistancePairScore(f)
			r = IMP.core.PairRestraint(m, s, (p1, p2))
			restraints_list.append(r)
		
		
		# this is very useful for secondary structure folding. get N-O to get hydrogen bond, check confold how to add all N-O. pulchar also does post-hydrogen bond optimization.  We don't need all N-O which will cause large energy, we only need small part N-O, check confold
		if res1_N_atom in index2AtomCoord.keys() and res2_O_atom in index2AtomCoord.keys():
			res1_N_atom_coord = index2AtomCoord[res1_N_atom]
			res2_O_atom_coord = index2AtomCoord[res2_O_atom]
			x1,y1,z1 = [res1_N_atom_coord.get_x(),res1_N_atom_coord.get_y(),res1_N_atom_coord.get_z()]
			x2,y2,z2 = [res2_O_atom_coord.get_x(),res2_O_atom_coord.get_y(),res2_O_atom_coord.get_z()]
			dist = np.linalg.norm([x1-x2,y1-y2,z1-z2])
			
			# get the particle index in model 
			p1 = cont_model.get_particles()[model_particle_index[res1_N_atom]]
			p2 = cont_model.get_particles()[model_particle_index[res2_O_atom]]
			f = IMP.core.Harmonic(dist, 1.0)
			s = IMP.core.DistancePairScore(f)
			r = IMP.core.PairRestraint(m, s, (p1, p2))
			restraints_list.append(r)
			

#### check using the predicted distance	
#### use predicted CB-CB distance,  
#### add secondary structure bond
#### in future, we can add predicted dihedral angles, predicted CA-CA	



# Read in the CHARMM heavy atom topology and parameter files
ff = IMP.atom.get_heavy_atom_CHARMM_parameters()

# Using the CHARMM libraries, determine the ideal topology (atoms and their
# connectivity) for the PDB file's primary sequence
topology = ff.create_topology(prot)

# Typically this modifies the C and N termini of each chain in the protein by
# applying the CHARMM CTER and NTER patches. Patches can also be manually
# applied at this point, e.g. to add disulfide bridges.
topology.apply_default_patches()

# Make the PDB file conform with the topology; i.e. if it contains extra
# atoms that are not in the CHARMM topology file, remove them; if it is
# missing atoms (e.g. sidechains, hydrogens) that are in the CHARMM topology,
# add them and construct their Cartesian coordinates from internal coordinate
# information.
topology.setup_hierarchy(prot)

# Set up and evaluate the stereochemical part (bonds, angles, dihedrals,
# impropers) of the CHARMM forcefield
# or check atom/charmm_forcefield_verbose.py for customization
r1 = IMP.atom.CHARMMStereochemistryRestraint(prot, topology)
#m.add_restraint(r)

# Add non-bonded interaction (in this case, Lennard-Jones). This needs to
# know the radii and well depths for each atom, so add them from the forcefield
# (they can also be assigned manually using the XYZR or LennardJones
# decorators):
ff.add_radii(prot)
ff.add_well_depths(prot)



restraints_list.append(r1)

###########################################################################################
# Basic Optimization and Chain
###########################################################################################

# Optimize the x,y,z coordinates of both particles with conjugate gradients
s = IMP.core.ConjugateGradients(m)
#sf = IMP.core.RestraintsScoringFunction([br,r], "scoring function")
sf = IMP.core.RestraintsScoringFunction(restraints_list, "scoring function")

# the box to perform everything
s.set_scoring_function(sf)
#IMP.set_log_level(IMP.TERSE)

min_energy = 1000000000
min_info = ''
for i in range(0,10):
	s.optimize(100)
	
	energy = sf.evaluate(False)
	## can apply simulated annealing here
	if energy < min_energy:
		min_energy = energy
		print("Epoch: ",i,": ",min_energy)
		min_info = "Epoch: "+str(i)+": "+str(min_energy)
		## add side-chain by rotamer
		
		### question: why output has side-chain atoms. Based on the visualization, the side-chain atoms don't conform to backbone atoms
		IMP.atom.write_pdb(prot, '3BFO-B-init-after'+str(i)+'.pdb')
		#pulchra_cmd = '/data/jh7x3/multicom_github/multicom/tools/pulchra304/pulchra 3BFO-B-init-after'+str(i)+'.pdb'
		#os.system(pulchra_cmd)
	
print(min_info)


'''


m = IMP.Model()

#prot = IMP.atom.read_pdb(IMP.atom.get_example_path("example_protein.pdb"), m)

#####  build extend structure 


##### load true bond length, angle, residue distance 

##### load modeller restarints, steric, van der waasls, refer to /data/commons/tools/IMP_tools/IMP2.6/doc/examples/modeller/load_modeller_model.py 


##### add modeller restrants into imp 

##### add our dihedral, angular and distance restraints into imp
#modmodel.restraints.make(sel, restraint_type='STEREO', spline_on_site=False)
#https://salilab.org/modeller/9v7/manual/node196.html
#https://salilab.org/modeller/9.21/examples/automodel/model-addrsr.py


## the idea to convert secondary structure to dihedral constraints 
## (1) first load secodnary structure into dihedral  using https://salilab.org/modeller/9.21/examples/automodel/model-addrsr.py
## (2) get dihedral constratins using  modmodel.restraints.make(sel, restraint_type='dehidral', spline_on_site=False)


##### optimize 


##### write pdb
'''

'''
IMP.atom.add_bonds(prot)
bds = IMP.atom.get_internal_bonds(prot)
bl = IMP.container.ListSingletonContainer(m, bds)
h = IMP.core.Harmonic(0, 1)
bs = IMP.atom.BondSingletonScore(h)
br = IMP.container.SingletonsRestraint(bs, bl)
print(br.evaluate(False))



# Optimize the x,y,z coordinates of both particles with conjugate gradients
sf = IMP.core.RestraintsScoringFunction([br], "scoring function")
prot.set_coordinates_are_optimized(True)
o = IMP.core.ConjugateGradients(m)
o.set_scoring_function(sf)
o.optimize(50)

IMP.atom.write_pdb(prot, 'structurenew.pdb')
'''

