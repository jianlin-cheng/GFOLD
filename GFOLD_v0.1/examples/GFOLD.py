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

f = open('3BFO-B.fasta', 'r')	
sequence = f.readlines()	
f.close()	
# removing the trailing "\n" and any header lines
sequence = [line.strip() for line in sequence if not '>' in line]
sequence = ''.join( sequence )

# Set up Modeller and build a model from sequence
e = modeller.environ()
e.edat.dynamic_sphere = True
e.libs.topology.read('${LIB}/top_heav.lib')
e.libs.parameters.read('${LIB}/par.lib')
modmodel = modeller.model(e)
modmodel.build_sequence(sequence)


###########################################################################################
# (2) Load the model into IMP Hierarchy
###########################################################################################

# Set up IMP and use the ModelLoader class to load the atom coordinates
# from Modeller into IMP as a new Hierarchy
m1 = IMP.Model()
loader = IMP.modeller.ModelLoader(modmodel)
protein = loader.load_atoms(m1)

# Hierarchies in IMP must have radii
IMP.atom.add_radii(protein)
# Write out the final structure to a PDB file
IMP.atom.write_pdb(protein, '3BFO-B-modeller-init.pdb')
clean_file = "sed -e \'s/\\x00//\' -i " + '3BFO-B-modeller-init.pdb'
os.system(clean_file)
clean_file = "grep CA " + '3BFO-B-modeller-init.pdb' + ' > 3BFO-B-modeller-init-CA.pdb'
os.system(clean_file)


'''
### reload 
e = modeller.environ()
e.edat.dynamic_sphere = True
e.libs.topology.read('${LIB}/top_heav.lib')
e.libs.parameters.read('${LIB}/par.lib')
modmodel = modeller.model(e)
modmodel.read('3BFO-B-modeller-init-CA.pdb')
'''

###########################################################################################
# (3) Load the native structure to achieve restraints
###########################################################################################

# Create an IMP model and add a heavy atom-only protein from a PDB file
m_model = IMP.Model()
# example_protein.pdb is assumed to be just extended chain structure obtained using structure_from_sequence example
prot_model = IMP.atom.read_pdb('3BFO-B-init.pdb', m_model,IMP.atom.CAlphaPDBSelector())  #IMP.atom.NonWaterNonHydrogenPDBSelector()
res = IMP.atom.get_by_type(prot_model, IMP.atom.RESIDUE_TYPE)
atoms = IMP.atom.get_by_type(prot_model, IMP.atom.ATOM_TYPE)
print(atoms)
# update the coordinates of the residue particles so that they cover the atoms
#m.update()

chain = IMP.atom.get_by_type(prot_model, IMP.atom.CHAIN_TYPE)
print("there are", len(chain), "chains in structure.pdb")
print("chain has", len(atoms), "atoms")

##### load the true structure and get restraints 
# Create an IMP model and add a heavy atom-only protein from a PDB file
m_native = IMP.Model()
# example_protein.pdb is assumed to be just extended chain structure obtained using structure_from_sequence example
prot_native = IMP.atom.read_pdb('3BFO-B.chn', m_native,IMP.atom.CAlphaPDBSelector()) 
IMP.atom.add_radii(prot_native)

# Get a list of all atoms in the model, and put it in a container
atoms_model = IMP.atom.get_by_type(prot_model, IMP.atom.ATOM_TYPE)
cont_model = IMP.container.ListSingletonContainer(atoms_model)

# Get a list of all atoms in the protein, and put it in a container
atoms_native = IMP.atom.get_by_type(prot_native, IMP.atom.ATOM_TYPE)
cont_native = IMP.container.ListSingletonContainer(atoms_native)

### check the number of ca atoms in native
ca_in_native=0
for p in cont_native.get_particles():
	if IMP.atom.Atom(p).get_atom_type() == IMP.atom.AtomType("CA"):
		ca_in_native+=1

ca_in_model=0
for p in cont_model.get_particles():
	if IMP.atom.Atom(p).get_atom_type() == IMP.atom.AtomType("CA"):
		ca_in_model+=1

print("Total ",ca_in_native," ca atoms in native structure")
print("Total ",ca_in_model," ca atoms in model structure")


#### check the residue type in model is the same as native
native_dist = {}
index2residue={}
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
	if p1_atom.get_atom_type() != IMP.atom.AtomType("CA"):
		continue
	index2residue[p1_seq_id] = p1_resname
	for j in range(i,len(cont_native.get_particles())):
		p2 = cont_native.get_particles()[j]
		#get atom information
		p2_atom = IMP.atom.Atom(p2)
		p2_coord = IMP.core.XYZ(p2).get_coordinates() #(1.885, 68.105, 54.894)
		p2_atom_name = p2_atom.get_atom_type().get_string() #'N'
		het = p2_atom_name.startswith('HET:')
		if het:
			p2_atom_name = p2_atom_name[4:]
		p2_res = IMP.atom.get_residue(p2_atom) ##1 "SER"
		p2_resname = p2_res.get_name() #'SER'
		p2_seq_id = p2_res.get_index() #1
		if p2_atom.get_atom_type() != IMP.atom.AtomType("CA"):
			continue
	
		if p1_seq_id == p2_seq_id:
			continue
		p1attr = IMP.core.XYZ(p1)
		p2attr = IMP.core.XYZ(p2)
		x1,y1,z1 = [p1attr.get_x(),p1attr.get_y(),p1attr.get_z()]
		x2,y2,z2 = [p2attr.get_x(),p2attr.get_y(),p2attr.get_z()]
		dist = np.linalg.norm([x1-x2,y1-y2,z1-z2])
		
		#print(p1_seq_id, "-", p2_seq_id,": ",p1.get_name(),"-",p2.get_name(), " distacnce: ",dist)
		
		### get distance value for each CA-CA pair
		pair = str(p1_seq_id) + ":"+p1_resname+"-" + str(p2_seq_id)+":"+p2_resname
		native_dist[pair] = dist
		
#for key in native_dist:
#	print(key," ",native_dist[key])


##### add distance restraints to model 

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
	#if p1_atom.get_atom_type() != IMP.atom.AtomType("CA"):
	#	IMP.core.XYZ(p1).set_coordinates_are_optimized(False)
	#	continue
	#else:
	#	IMP.core.XYZ(p1).set_coordinates_are_optimized(True)
	if index2residue[p1_seq_id] != p1_resname:
		print("The residue in model not match as restraints")
		sys.exit(-1)
	for j in range(i,len(cont_model.get_particles())):
		p2 = cont_model.get_particles()[j]
		#get atom information
		p2_atom = IMP.atom.Atom(p2)
		p2_coord = IMP.core.XYZ(p2).get_coordinates() #(1.885, 68.105, 54.894)
		p2_atom_name = p2_atom.get_atom_type().get_string() #'N'
		het = p2_atom_name.startswith('HET:')
		if het:
			p2_atom_name = p2_atom_name[4:]
		p2_res = IMP.atom.get_residue(p2_atom) ##1 "SER"
		p2_resname = p2_res.get_name() #'SER'
		p2_seq_id = p2_res.get_index() #1
		if p2_atom.get_atom_type() != IMP.atom.AtomType("CA"):
			continue
	
		if p1_seq_id == p2_seq_id:
			continue
		
		if index2residue[p2_seq_id] != p2_resname:
			print("The residue in model not match as restraints")
			sys.exit(-1)
		#print(p1_seq_id, "-", p2_seq_id,": ",p1.get_name(),"-",p2.get_name(), " distacnce: ",dist)
		#IMP.core.XYZ(p1).set_coordinates_are_optimized(True)
		#IMP.core.XYZ(p2).set_coordinates_are_optimized(True)
		### get distance value for each CA-CA pair
		pair = str(p1_seq_id) + ":"+p1_resname+"-" + str(p2_seq_id)+":"+p2_resname
		if pair in native_dist.keys():
			if p1_seq_id ==6 and p2_seq_id ==26:
				# Add a simple Modeller distance restraint between the first and last atoms
				#feat = modeller.features.distance(modmodel.atoms[p1_seq_id-1], modmodel.atoms[p2_seq_id-1])
				CA_pos1 = 'CA:'+str(p1_seq_id)
				CA_pos2 = 'CA:'+str(p2_seq_id)
				print(CA_pos1," ",CA_pos2," ",native_dist[pair])
				feat = modeller.features.distance(modmodel.atoms[CA_pos1],modmodel.atoms[CA_pos2])
				r = modeller.forms.gaussian(feature=feat, mean=native_dist[pair], stdev=1.0,
											group=modeller.physical.xy_distance)
				
				
				modmodel.restraints.add(r)



# Generate Modeller stereochemistry
sel = modeller.selection(modmodel)
modmodel.restraints.make(sel, restraint_type='STEREO', spline_on_site=False)
			
# Set up IMP and load the Modeller model in as a new Hierarchy
m = IMP.Model()
loader = IMP.modeller.ModelLoader(modmodel)
protein = loader.load_atoms(m)
IMP.atom.add_radii(protein)

restraints_list=[]


atoms = IMP.atom.get_by_type(protein, IMP.atom.ATOM_TYPE)
cont_model = IMP.container.ListSingletonContainer(atoms)


#restrain all the bonds to have their current length.
IMP.atom.add_bonds(protein)
bds = IMP.atom.get_internal_bonds(protein)
bl = IMP.container.ListSingletonContainer(m, bds)
h = IMP.core.Harmonic(0, 1)
bs = IMP.atom.BondSingletonScore(h)
br = IMP.container.SingletonsRestraint(bs, bl)



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
	#if p1_atom.get_atom_type() != IMP.atom.AtomType("CA"):
	#	IMP.core.XYZ(p1).set_coordinates_are_optimized(False)
	#	continue
	#else:
	#if p1_seq_id == 6 or p1_seq_id == 26:
	if p1_seq_id < 5:
		IMP.core.XYZ(p1).set_coordinates_are_optimized(True)
		print("setting ",p1_atom," ",p1_res, " to true optimize")
	else:
		IMP.core.XYZ(p1).set_coordinates_are_optimized(False)
		
	#else:
	#	IMP.core.XYZ(p1).set_coordinates_are_optimized(False)
	#if num >=0: 
	#	IMP.core.XYZ(p1).set_coordinates_are_optimized(False)
	#else:
	#	IMP.core.XYZ(p1).set_coordinates_are_optimized(True)
	#	print("setting ",p1_atom," ",p1_res, " to true optimize")


# Use the ModellerRestraints class to add all of the Modeller restraints to
# the IMP scoring function
r = IMP.modeller.ModellerRestraints(m, modmodel, atoms)

restraints_list.append(br)
restraints_list.append(r)


###########################################################################################
# Basic Optimization and Chain
###########################################################################################
		
# Optimize the x,y,z coordinates of both particles with conjugate gradients



s= IMP.core.MCCGSampler(m)
#sf = IMP.core.RestraintsScoringFunction([br,r], "scoring function")
sf = IMP.core.RestraintsScoringFunction(restraints_list, "scoring function")
# the box to perform everything
s.set_scoring_function(sf)
s.set_number_of_attempts(2)
# but we do want something to watch
#s.set_log_level(IMP.WARNING)
s.set_log_level(IMP.SILENT)
s.set_check_level(IMP.NONE)
s.set_number_of_monte_carlo_steps(1)
s.set_number_of_conjugate_gradient_steps(1)
# find some configurations which move the particles far apart
configs = s.create_sample()

print("Found ", configs.get_number_of_configurations(), " configurations")

min_energy = 1000000000
min_info = ''
for i in range(0, configs.get_number_of_configurations()):
	configs.load_configuration(i)
	#d=IMP.display.PymolWriter("solution"+str(i)+".py")
	#print("check particles ",cont_model.get_particles())
	#IMP.atom.write_pdb(prot, "solution"+str(i)+".pdb")
	energy = sf.evaluate(False)
	print("Epoch: ",i,": ",energy)
	if energy < min_energy:
		min_energy = energy
		print("Epoch: ",i,": ",min_energy)
		min_info = "Epoch: "+str(i)+": "+str(min_energy)
		IMP.atom.write_pdb(protein, "solution_best.pdb")
		clean_file = "sed -e \'s/\\x00//\' -i " + 'solution_best.pdb'
		os.system(clean_file)
	if i == configs.get_number_of_configurations()-1: 
		break
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

