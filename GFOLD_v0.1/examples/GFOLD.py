#!usr/bin/env python
# python GFOLD.py  --target T0967  --fasta T0967.fasta --alignment T0967.pir  --atomdir ./  --dir  T0967
# python GFOLD.py  --target 3BFO-B  --fasta 3BFO-B.fasta --alignment 3BFO-B.pir  --atomdir ./  --dir  3BFOB




	
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
import optparse
import numpy as np
import sys
import os
import collections
import IMP
import IMP.atom
import IMP.container
import IMP.rotamer
import warnings
import string, re
import math
import modeller
from modeller import *
import IMP.modeller
warnings.filterwarnings("ignore")
modeller.log.none()

import random
#modeller.log.minimal()


#/home/jh7x3/fusion_hybrid/
project_root = '/data/jh7x3/GFOLD_v0.1/'
sys.path.insert(0, project_root)

#from GFOLD_pylib import *
aa_one2index = {'A':0, 'C':1, 'D':2, 'E':3, 'F':4, 'G':5, 'H':6, 'I':7, 'K':8, 'L':9, 'M':10, 'N':11, 'P':12, 'Q':13, 'R':14, 'S':15, 'T':16, 'V':17, 'W':18, 'Y':19}
aa_three2index = {'ALA':0, 'CYS':1, 'ASP':2, 'GLU':3, 'PHE':4, 'GLY':5, 'HIS':6, 'ILE':7, 'LYS':8, 'LEU':9, 'MET':10, 'ASN':11, 'PRO':12, 'GLN':13, 'ARG':14, 'SER':15, 'THR':16, 'VAL':17, 'TRP':18, 'TYR':19}
aa_index2three = {y:x for x,y in aa_three2index.iteritems()}


# Global variables for generating secondary structure restraints
SS_ATOMTYPE = {}
SS_ATOMTYPE['CA'] = 1
SS_ATOMTYPE['N'] = 1
SS_ATOMTYPE['C'] = 1
SS_ATOMTYPE['O'] = 1

SS_SHIFT = {}
SS_SHIFT['0'] = 1
SS_SHIFT['+1'] = 1
SS_SHIFT['-1'] = 1
res_dihe     = {};
res_strnd_OO = {};
res_dist     = {};
res_hbnd     = {};


def get_ss_range(integer_list):
	integer_list = sorted(integer_list)
	pstart = integer_list[0]
	pend = integer_list[-1]

	a = set(integer_list)  # Set a
	b = range(pstart, pend+1)

	# Pick items that are not in range.
	c = set(b) - a  # Set operation b-a

	li = []
	start = 0
	for i in sorted(c):
		end = b.index(i)  # Get end point of the list slicing
		li.append(b[start:end])  # Slice list using values
		start = end + 1  # Increment the start point for next slicing
	li.append(b[start:])  # Add the last series
	range_list =  []
	for sliced_list in li:
		if not sliced_list:
			# list is empty
			continue
		if len(sliced_list) == 1:
			# If only one item found in list
			range_list.append(sliced_list[0])
		else:
			range_list.append("{0}-{1}".format(sliced_list[0], sliced_list[-1]))
	return range_list


def load_ss_restraints(lamda,log_reference):
	# T      Helix or Parallel or anti-parallel or Unknown Strand Type
	# A1_A2  Atom1-Atom2 pair
	# Ref    Hydrogen bonding connector atom (reference hbond connector)
	# N      Neighborhood residue shifting on the hbond connector of R2 side. For example, If R1:N and R2:O have hbond and S = +1, the restraint A1-A2 are for R1 and (R2+1)
	# Note: hbond distances are the distances between Nitrogen and Oxygen
	# Places to verify:
	# http://www.beta-sheet.org/page29/page51/page53/index.html
	# In this model, the HP sheet is composed of identical straight helical chains with phi = -122 degrees, psi = 135 degrees, and a slightly non-linear interchain H-bond angle delta of 170 degrees.
	# http://en.wikipedia.org/wiki/Alpha_helix
	# Residues in alpha-helices typically adopt backbone (phi, psi) dihedral angles around (-60, -45), as shown in the image at right
	# the H to O distance is about 2 A (0.20 nm

	# T A Mean Standard_deviation
	res_dihe["A PSI"] = "136.91 "+str(lamda * 17.39);
	res_dihe["A PHI"] = "-120.89 "+str(lamda * 21.98);
	res_dihe["P PSI"] = "130.96 "+str(lamda * 16.66);
	res_dihe["P PHI"] = "-115.00 "+str(lamda * 20.31);
	res_dihe["U PSI"] = "134.95 "+str(lamda * 17.65);
	res_dihe["U PHI"] = "-118.91 "+str(lamda * 21.73);
	res_dihe["H PSI"] = "-41.51 "+str(lamda * 9.84);
	res_dihe["H PHI"] = "-63.47 "+str(lamda * 9.20);

	#T A1_A2 Ref N Mean Standard_deviation
	res_dist["A O-O O +1"]   = get_dist_neg_pos(7.73, 0.59, lamda);
	res_dist["A O-O O -1"]   = get_dist_neg_pos(4.84, 0.16, lamda);
	res_dist["A O-O O 0"]    = get_dist_neg_pos(3.57, 0.28, lamda);
	res_dist["A O-O H +1"]   = get_dist_neg_pos(7.76, 0.60, lamda);
	res_dist["A O-O H -1"]   = get_dist_neg_pos(4.90, 0.45, lamda);
	res_dist["A O-O H 0"]    = get_dist_neg_pos(3.58, 0.31, lamda);
	res_dist["A C-C O +1"]   = get_dist_neg_pos(7.66, 0.52, lamda);
	res_dist["A C-C O -1"]   = get_dist_neg_pos(4.80, 0.17, lamda);
	res_dist["A C-C O 0"]    = get_dist_neg_pos(4.96, 0.21, lamda);
	res_dist["A C-C H +1"]   = get_dist_neg_pos(7.65, 0.51, lamda);
	res_dist["A C-C H -1"]   = get_dist_neg_pos(4.85, 0.34, lamda);
	res_dist["A C-C H 0"]    = get_dist_neg_pos(4.96, 0.21, lamda);
	res_dist["A N-N O +1"]   = get_dist_neg_pos(5.09, 0.34, lamda);
	res_dist["A N-N O -1"]   = get_dist_neg_pos(6.86, 0.40, lamda);
	res_dist["A N-N O 0"]    = get_dist_neg_pos(4.42, 0.24, lamda);
	res_dist["A N-N H +1"]   = get_dist_neg_pos(5.04, 0.21, lamda);
	res_dist["A N-N H -1"]   = get_dist_neg_pos(6.85, 0.45, lamda);
	res_dist["A N-N H 0"]    = get_dist_neg_pos(4.43, 0.25, lamda);
	res_dist["A CA-CA O +1"] = get_dist_neg_pos(6.43, 0.41, lamda);
	res_dist["A CA-CA O -1"] = get_dist_neg_pos(5.67, 0.28, lamda);
	res_dist["A CA-CA O 0"]  = get_dist_neg_pos(5.26, 0.24, lamda);
	res_dist["A CA-CA H +1"] = get_dist_neg_pos(6.38, 0.36, lamda);
	res_dist["A CA-CA H -1"] = get_dist_neg_pos(5.71, 0.40, lamda);
	res_dist["A CA-CA H 0"]  = get_dist_neg_pos(5.27, 0.25, lamda);
	res_dist["P O-O O +1"]   = get_dist_neg_pos(7.90, 0.61, lamda);
	res_dist["P O-O O -1"]   = get_dist_neg_pos(4.86, 0.16, lamda);
	res_dist["P O-O O 0"]    = get_dist_neg_pos(3.78, 0.34, lamda);
	res_dist["P O-O H +1"]   = get_dist_neg_pos(4.92, 0.40, lamda);
	res_dist["P O-O H -1"]   = get_dist_neg_pos(8.02, 0.60, lamda);
	res_dist["P O-O H 0"]    = get_dist_neg_pos(3.78, 0.32, lamda);
	res_dist["P C-C O +1"]   = get_dist_neg_pos(8.03, 0.51, lamda);
	res_dist["P C-C O -1"]   = get_dist_neg_pos(4.82, 0.17, lamda);
	res_dist["P C-C O 0"]    = get_dist_neg_pos(5.21, 0.25, lamda);
	res_dist["P C-C H +1"]   = get_dist_neg_pos(4.88, 0.34, lamda);
	res_dist["P C-C H -1"]   = get_dist_neg_pos(7.87, 0.44, lamda);
	res_dist["P C-C H 0"]    = get_dist_neg_pos(5.22, 0.22, lamda);
	res_dist["P N-N O +1"]   = get_dist_neg_pos(8.14, 0.35, lamda);
	res_dist["P N-N O -1"]   = get_dist_neg_pos(4.86, 0.40, lamda);
	res_dist["P N-N O 0"]    = get_dist_neg_pos(5.13, 0.32, lamda);
	res_dist["P N-N H +1"]   = get_dist_neg_pos(4.80, 0.18, lamda);
	res_dist["P N-N H -1"]   = get_dist_neg_pos(7.54, 0.69, lamda);
	res_dist["P N-N H 0"]    = get_dist_neg_pos(5.10, 0.28, lamda);
	res_dist["P CA-CA O +1"] = get_dist_neg_pos(8.55, 0.37, lamda);
	res_dist["P CA-CA O -1"] = get_dist_neg_pos(4.90, 0.29, lamda);
	res_dist["P CA-CA O 0"]  = get_dist_neg_pos(6.21, 0.26, lamda);
	res_dist["P CA-CA H +1"] = get_dist_neg_pos(4.90, 0.28, lamda);
	res_dist["P CA-CA H -1"] = get_dist_neg_pos(7.49, 0.60, lamda);
	res_dist["P CA-CA H 0"]  = get_dist_neg_pos(6.24, 0.24, lamda);
	res_dist["H O-O O +1"]   = get_dist_neg_pos(8.40, 0.27, lamda);
	res_dist["H O-O O -1"]   = get_dist_neg_pos(4.99, 0.16, lamda);
	res_dist["H O-O O 0"]    = get_dist_neg_pos(6.12, 0.26, lamda);
	res_dist["H O-O H +1"]   = get_dist_neg_pos(5.03, 0.31, lamda);
	res_dist["H O-O H -1"]   = get_dist_neg_pos(8.43, 0.32, lamda);
	res_dist["H O-O H 0"]    = get_dist_neg_pos(6.12, 0.26, lamda);
	res_dist["H C-C O +1"]   = get_dist_neg_pos(8.16, 0.24, lamda);
	res_dist["H C-C O -1"]   = get_dist_neg_pos(4.87, 0.13, lamda);
	res_dist["H C-C O 0"]    = get_dist_neg_pos(6.09, 0.23, lamda);
	res_dist["H C-C H +1"]   = get_dist_neg_pos(4.89, 0.23, lamda);
	res_dist["H C-C H -1"]   = get_dist_neg_pos(8.17, 0.25, lamda);
	res_dist["H C-C H 0"]    = get_dist_neg_pos(6.09, 0.23, lamda);
	res_dist["H N-N O +1"]   = get_dist_neg_pos(8.07, 0.23, lamda);
	res_dist["H N-N O -1"]   = get_dist_neg_pos(4.84, 0.19, lamda);
	res_dist["H N-N O 0"]    = get_dist_neg_pos(6.10, 0.20, lamda);
	res_dist["H N-N H +1"]   = get_dist_neg_pos(4.81, 0.13, lamda);
	res_dist["H N-N H -1"]   = get_dist_neg_pos(8.08, 0.21, lamda);
	res_dist["H N-N H 0"]    = get_dist_neg_pos(6.10, 0.20, lamda);
	res_dist["H CA-CA O +1"] = get_dist_neg_pos(8.63, 0.28, lamda);
	res_dist["H CA-CA O -1"] = get_dist_neg_pos(5.13, 0.20, lamda);
	res_dist["H CA-CA O 0"]  = get_dist_neg_pos(6.16, 0.26, lamda);
	res_dist["H CA-CA H +1"] = get_dist_neg_pos(5.14, 0.21, lamda);
	res_dist["H CA-CA H -1"] = get_dist_neg_pos(8.64, 0.26, lamda);
	res_dist["H CA-CA H 0"]  = get_dist_neg_pos(6.16, 0.26, lamda);

	# T Mean Standard_deviation
	res_strnd_OO["A"] = get_dist_neg_pos(4.57, 0.30, lamda);
	res_strnd_OO["P"] = get_dist_neg_pos(4.57, 0.29, lamda);
	res_strnd_OO["U"] = get_dist_neg_pos(4.57, 0.30, lamda);

	# T Mean Standard_deviation
	res_hbnd["A"] = get_dist_neg_pos(2.92, 0.16, lamda);
	res_hbnd["P"] = get_dist_neg_pos(2.93, 0.16, lamda);
	res_hbnd["H"] = get_dist_neg_pos(2.99, 0.17, lamda);
	
	if not res_dihe:
		print('Error ! dihe restraints could not be loaded. Exiting application...')
		sys.exit(-1)
	if not res_strnd_OO:
		print('Error ! dstr restraints could not be loaded. Exiting application...')
		sys.exit(-1)
	if not res_dist:
		print('Error ! dist restraints could not be loaded. Exiting application...')
		sys.exit(-1)
	if not res_hbnd:
		print('Error ! hbnd restraints could not be loaded. Exiting application...')
		sys.exit(-1)

	content = "#load_ss_restraints\n";
	with open(log_reference, 'w') as f1:
		f1.write(content)
	
	for item in res_dihe:
		content = item+"\t"+res_dihe[item]+"\n";
		with open(log_reference, 'a') as f1:
			f1.write(content)

	for item in res_strnd_OO:
		content = item+"\t"+res_strnd_OO[item]+"\n";
		with open(log_reference, 'a') as f1:
			f1.write(content)

	for item in res_dist:
		content = item+"\t"+res_dist[item]+"\n";
		with open(log_reference, 'a') as f1:
			f1.write(content)
	
	for item in res_hbnd:
		content = item+"\t"+res_hbnd[item]+"\n";
		with open(log_reference, 'a') as f1:
			f1.write(content)

def get_dist_neg_pos(mean, devi,lamda):
	lamda_devi = round(lamda*devi, 2)
	info = str(mean) + ' ' + str(lamda_devi) + ' ' + str(lamda_devi)
	return info
			
def print2file(file,message):
	if os.path.isfile(file):
		with open(file, 'a') as f1:
			f1.write(message+"\n")
	else:
		with open(file, 'w') as f1:
			f1.write(message+"\n")

print('')
print('  ############################################################################')
print('  #																		  #')
print('  #	  GFOLD : A Distance-based Protein Structure Folding				  #')
print('  #																		  #')
print('  #   Copyright (C) 2019 -2029	Jie Hou and Jianlin Cheng				   #')
print('  #																		  #')
print('  ############################################################################')
print('  #																		  #')
print('  #   Method to perform distance-based modeling (TS)						 #')
print('  #																		  #')
print('  ############################################################################')
print('')


parser = optparse.OptionParser()
parser.add_option('--target', dest='target',
	default = 'test',	# default target name is test
	help = 'name of target protein')
parser.add_option('--fasta', dest = 'fasta',
	default = '',	# default empty!
	help = 'FASTA file containing the protein to sequence to fold')
parser.add_option('--ss', dest = 'ss',
	default = '',	# default empty!
	help = 'Secondary structure file containing the protein to sequence to 3-class secondary structure')
parser.add_option('--restraints', dest = 'restraints',
	default = '',	# default empty!
	help = 'restraints for modeling')
parser.add_option('--hbond', dest = 'hbond',
	default = '',	# default empty!
	help = 'hbond restraints for modeling')
parser.add_option( '--dir', dest = 'dir',
	default = '',	# default empty!
	help = 'root directory for results')
parser.add_option( '--epoch', dest = 'epoch',
	default = '10',	# default empty!
	help = 'number of epochs')
parser.add_option( '--cgstep', dest = 'cgstep',
	default = '100',	# default empty!
	help = 'maximum step for conjugate gradient')
parser.add_option( '--lamda', dest = 'lamda',
	default = '0.4',    # default empty!
	help = 'parameter for ss restraints')
parser.add_option( '--distdev', dest = 'distdev',
	default = '1.0',    # default empty!
	help = 'standard deviation for CA-CA/CB-CB distance')
parser.add_option( '--type', dest = 'type',
	default = 'CB',    # CB/CA
	help = 'atom type for distance restraints')
parser.add_option( '--init', dest = 'initpdb',
	default = '',    # CB/CA
	help = 'initial pdb')
parser.add_option( '--dihedral', dest = 'dihedral',
	default = '',    # CB/CA
	help = 'dihedral restraints')
parser.add_option( '--eva', dest = 'eva',
	default = '',    # CB/CA
	help = 'evaluate restraints')
parser.add_option( '--sep', dest = 'separation',
	default = '1',   
	help = 'sequence separation')

(options,args) = parser.parse_args()

target = options.target
# Sequence file option
sequence = ''
if options.fasta:	
	f = open(options.fasta, 'r')	
	sequence = f.readlines()	
	f.close()	
	# removing the trailing "\n" and any header lines
	sequence = [line.strip() for line in sequence if not '>' in line]
	sequence = ''.join( sequence )
else:
	print('Error ! target protein not defined. Exiting application...')
	sys.exit(1)

residues = {}
for i in range(0, len(sequence)):
	char = sequence[i:i+1]
	residues[i+1] = char

# SS sequence file option
ss_sequence = ''

if options.ss:	
	f = open(options.ss, 'r')	
	ss_sequence = f.readlines()	
	f.close()	
	# removing the trailing "\n" and any header lines
	ss_sequence = [line.strip() for line in ss_sequence if not '>' in line]
	ss_sequence = ''.join( ss_sequence )
else:
	print('Error ! secondary structure not defined. Exiting application...')
	sys.exit(1)

ss_file = options.ss

atom_type_dist = 'CB'
if options.type:
	atom_type_dist = options.type
	
separation = 1
if options.separation:
	separation = int(options.separation)
	
distdev = 1.0
if options.distdev:
	distdev = float(options.distdev)

if atom_type_dist != 'CA' and atom_type_dist != 'CB' and atom_type_dist != 'both' and atom_type_dist != 'all':
	print('Error ! Wrong type of atoms for distance restraints. Exiting application...')
	sys.exit(1)


lamda = 0.4
if options.lamda:
	lamda = float(options.lamda)

epoch= 10
if options.epoch:
	epoch = int(options.epoch)

cgstep = 100
if options.cgstep:
	cgstep = int(options.cgstep)

dir = options.dir
if dir:
	curr_dir = dir
else:
	curr_dir = os.getcwd()


custom_restraints = ''
if options.restraints:
	custom_restraints = options.restraints


work_dir = curr_dir + '/' + target
if not os.path.exists(work_dir):
	os.makedirs(work_dir)


init_dir = work_dir + '/init_structure'
if not os.path.exists(init_dir):
	os.makedirs(init_dir)

sample_dir = work_dir + '/sampled_structure'
if not os.path.exists(sample_dir):
	os.makedirs(sample_dir)


###########################################################################################
# (1) Build extended structure from sequence
###########################################################################################


e = modeller.environ(rand_seed=-4000)
#soft sphere potential
e.edat.dynamic_sphere = False
e.libs.topology.read('${LIB}/top_heav.lib')
e.libs.parameters.read('${LIB}/par.lib')
modmodel = modeller.model(e)
modmodel.build_sequence(sequence)


###########################################################################################
# (2) Load the model into IMP Hierarchy
###########################################################################################
m = IMP.Model()
h = IMP.modeller.ModelLoader(modmodel).load_atoms(m)   ##### can we add secondary structure information to build extend structure, or add secondary structure angle restraints later
IMP.atom.add_radii(h)
init_pdb = init_dir+'/'+target+'-init.pdb'

if options.initpdb:
	print("Loading initial provided structure")
	cmd = "cp " + options.initpdb + " " + init_pdb
	os.system(cmd)
else:
	IMP.atom.write_pdb(h, init_pdb) # Write out the final structure to a PDB file
	print("Writng initial structure to ",init_pdb) 
	clean_file = "sed -e \'s/\\x00//\' -i " + init_pdb
	os.system(clean_file)

###########################################################################################
# (3) Load initial model
###########################################################################################

m = IMP.Model()
#select1 = IMP.atom.OrPDBSelector(IMP.atom.CBetaPDBSelector(),IMP.atom.BackbonePDBSelector())
#select2 = IMP.atom.OrPDBSelector(select1,IMP.atom.HydrogenPDBSelector())
prot = IMP.atom.read_pdb(init_pdb, m)
res_model = IMP.atom.get_by_type(prot, IMP.atom.RESIDUE_TYPE)
atoms_model = IMP.atom.get_by_type(prot, IMP.atom.ATOM_TYPE)
chain_model = IMP.atom.get_by_type(prot, IMP.atom.CHAIN_TYPE)
if len(chain_model) !=1:
	print('Error ! More than one chain in the PDB structure. Exiting application...')
	sys.exit(-1)

print("Chain has", len(atoms_model), "atoms")
cont_model = IMP.container.ListSingletonContainer(atoms_model) # Get a list of all atoms in the model, and put it in a container

#for atom in atoms_model:
#	print(atom)

'''
# Read the original PDB file and copy its sequence to the alignment array:
modmodel = model(e, file=init_pdb)
ali = alignment(e)
ali.append_model(modmodel, atom_files=init_pdb, align_codes=target

)
#get two copies of the sequence.  A modeller trick to get things set up
ali.append_model(modmodel, align_codes=target)

modmodel.read(file=init_pdb)
modmodel.clear_topology()
modmodel.generate_topology(ali[-1])
'''
rsr = modmodel.restraints
atmsel = selection(modmodel)
rsr.make(atmsel, restraint_type='stereo', spline_on_site=False)
#rsr.make(atmsel, restraint_type='bond', spline_on_site=False)
#rsr.make(atmsel, restraint_type='ANGLE', spline_on_site=False)

modeller_atoms = modmodel.chains[0].atoms
modeller_res = modmodel.chains[0].residues


print("modeller_atoms: ",len(modeller_atoms))
print("modeller_res: ",len(modeller_res))
print("atoms_model: ",len(atoms_model))
print("res_model: ",len(res_model))


model_residues = {}
model_particle_index = {}
# Hydrogen or Nitrogen must be present for all atoms, in order to apply hydrogen bond restraints
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
	model_particle_index[info] = i # get particle index of atom in chain 

# In case of Proline, use N atom instead of H
for res_id in model_residues:
	p1_resname = model_residues[res_id]
	if str(res_id)+'-'+p1_resname+'-H' in model_particle_index:
		continue
	if str(res_id)+'-'+p1_resname+'-N' in model_particle_index:
		continue
	print('Error ! Something went wrong with residue ',res_id,':',p1_resname,' must have H or N for each residue!. Exiting application...')
	sys.exit(-1)


# run confold to get helix restraints; start writing to the files hbond.tbl, ssnoe.tbl and dihedral.tbl

load_ss_restraints(lamda, work_dir+"/ssrestraints.log");

# run confold to get strand and/or sheet restraints



###########################################################################################
# (4) load the template structure and get information for all atoms
###########################################################################################
restraints_list = []
if options.restraints:
	print("Loading custom restraints")
	# 2-LYS-CA-1 53-VAL-CA-1 distance 5.1234
	f = open(options.restraints, 'r')	
	restraints_contenst = f.readlines()	
	f.close()	

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
		model_particle_index[info] = i # get particle index of atom in chain 
		#print("Adding ",info)
	
	for line in restraints_contenst:
		if '#' in line:
			continue
		buff = re.split("\t+",line.strip())
		
		res1 = buff[0]
		res2 = buff[1]
		re_type = buff[2]
		re_value = float(buff[3])
		
		if res1 in model_particle_index and res2 in model_particle_index and re_type == 'distance':
			# get the particle index in model 
			p1 = cont_model.get_particles()[model_particle_index[res1]]
			p2 = cont_model.get_particles()[model_particle_index[res2]]
			
			p1_buff = re.split("-",res1)
			p2_buff = re.split("-",res2)
			
			if int(p2_buff[0])-int(p1_buff[0])< separation:
				continue
			if atom_type_dist == 'all':
				p1_atom_type_dist = p1_buff[2]
				p2_atom_type_dist = p2_buff[2]
				res1_pos = p1_atom_type_dist+':'+str(p1_buff[0])
				res2_pos = p2_atom_type_dist+':'+str(p2_buff[0])
				rsr.add(forms.gaussian(group=physical.xy_distance,
				   feature=features.distance(modeller_atoms[res1_pos],
											 modeller_atoms[res2_pos]),
				   mean=re_value, stdev=distdev))
				content = res1_pos + "\t" + res2_pos + "\t" + str(re_value) + "\t" + str(distdev) + "\t" + str(distdev) + "\t!CA-CA"
				print2file(work_dir+"/distance.tbl", (content))	
			elif atom_type_dist == 'both':
				p1_atom_type_dist = p1_buff[2]
				p2_atom_type_dist = p2_buff[2]
				if p1_buff[1] == 'GLY':
					p1_atom_type_dist = 'CA'
				if p2_buff[1] == 'GLY':
					p2_atom_type_dist = 'CA'
				res1_pos = p1_atom_type_dist+':'+str(p1_buff[0])
				res2_pos = p2_atom_type_dist+':'+str(p2_buff[0])
				rsr.add(forms.gaussian(group=physical.xy_distance,
				   feature=features.distance(modeller_atoms[res1_pos],
											 modeller_atoms[res2_pos]),
				   mean=re_value, stdev=distdev))
				content = res1_pos + "\t" + res2_pos + "\t" + str(re_value) + "\t" + str(distdev) + "\t" + str(distdev) + "\t!CA-CA"
				print2file(work_dir+"/distance.tbl", (content))
			else:
				#if p1_buff[2] == 'CA' and p2_buff[2] == 'CA':
				if p1_buff[2] == 'CA' and p2_buff[2] == 'CA' and atom_type_dist == 'CA':
					#print("Adding restraints for ",res1," and ", res2)
					res1_pos = 'CA:'+str(p1_buff[0])
					res2_pos = 'CA:'+str(p2_buff[0])
					rsr.add(forms.gaussian(group=physical.xy_distance,
					   feature=features.distance(modeller_atoms[res1_pos],
												 modeller_atoms[res2_pos]),
					   mean=re_value, stdev=distdev))
					content = res1_pos + "\t" + res2_pos + "\t" + str(re_value) + "\t" + str(distdev) + "\t" + str(distdev) + "\t!CA-CA"
					print2file(work_dir+"/distance.tbl", (content))
					#f = IMP.core.Harmonic(re_value, 0.1)
					#s = IMP.core.DistancePairScore(f)
					#r = IMP.core.PairRestraint(m, s, (p1, p2))
					#restraints_list.append(r)
				
				if atom_type_dist == 'CB':
					res1_pos = 'CB:'+str(p1_buff[0])
					res2_pos = 'CB:'+str(p2_buff[0])
					if p1_buff[1] == 'GLY' and p1_buff[2] == 'CA' and p2_buff[1] == 'GLY' and  p2_buff[2] == 'CA' :
						#print("Adding restraints for ",res1," and ", res2)
						res1_pos = 'CA:'+str(p1_buff[0])
						res2_pos = 'CA:'+str(p2_buff[0])
						rsr.add(forms.gaussian(group=physical.xy_distance,
						   feature=features.distance(modeller_atoms[res1_pos],
													 modeller_atoms[res2_pos]),
						   mean=re_value, stdev=distdev)) #Standard deviation depends on solvent accessibility, gaps of alignment, and sequence identity: https://salilab.org/modeller/manual/node213.html
						content = res1_pos + "\t" + res2_pos + "\t" + str(re_value) + "\t" + str(distdev) + "\t" + str(distdev) + "\t!CB-CB"
						print2file(work_dir+"/distance.tbl", (content))
					if p1_buff[1] == 'GLY' and p1_buff[2] == 'CA' and p2_buff[1] != 'GLY' and  p2_buff[2] == 'CB' :
						#print("Adding restraints for ",res1," and ", res2)
						res1_pos = 'CA:'+str(p1_buff[0])
						res2_pos = 'CB:'+str(p2_buff[0])
						rsr.add(forms.gaussian(group=physical.xy_distance,
						   feature=features.distance(modeller_atoms[res1_pos],
													 modeller_atoms[res2_pos]),
						   mean=re_value, stdev=distdev)) #Standard deviation depends on solvent accessibility, gaps of alignment, and sequence identity: https://salilab.org/modeller/manual/node213.html
						content = res1_pos + "\t" + res2_pos + "\t" + str(re_value) + "\t" + str(distdev) + "\t" + str(distdev) + "\t!CB-CB"
						print2file(work_dir+"/distance.tbl", (content))
					if p1_buff[1] != 'GLY' and p1_buff[2] == 'CB' and p2_buff[1] == 'GLY' and  p2_buff[2] == 'CA' :
						#print("Adding restraints for ",res1," and ", res2)
						res1_pos = 'CB:'+str(p1_buff[0])
						res2_pos = 'CA:'+str(p2_buff[0])
						rsr.add(forms.gaussian(group=physical.xy_distance,
						   feature=features.distance(modeller_atoms[res1_pos],
													 modeller_atoms[res2_pos]),
						   mean=re_value, stdev=distdev)) #Standard deviation depends on solvent accessibility, gaps of alignment, and sequence identity: https://salilab.org/modeller/manual/node213.html
						content = res1_pos + "\t" + res2_pos + "\t" + str(re_value) + "\t" + str(distdev) + "\t" + str(distdev) + "\t!CB-CB"
						print2file(work_dir+"/distance.tbl", (content))
					if p1_buff[1] != 'GLY' and p1_buff[2] == 'CB' and p2_buff[1] != 'GLY' and  p2_buff[2] == 'CB' :
						#print("Adding restraints for ",res1," and ", res2)
						res1_pos = 'CB:'+str(p1_buff[0])
						res2_pos = 'CB:'+str(p2_buff[0])
						rsr.add(forms.gaussian(group=physical.xy_distance,
						   feature=features.distance(modeller_atoms[res1_pos],
													 modeller_atoms[res2_pos]),
						   mean=re_value, stdev=distdev)) #Standard deviation depends on solvent accessibility, gaps of alignment, and sequence identity: https://salilab.org/modeller/manual/node213.html
						content = res1_pos + "\t" + res2_pos + "\t" + str(re_value) + "\t" + str(distdev) + "\t" + str(distdev) + "\t!CB-CB"
						print2file(work_dir+"/distance.tbl", (content))
				
				#f = IMP.core.Harmonic(re_value, 0.1)
				#s = IMP.core.DistancePairScore(f)
				#r = IMP.core.PairRestraint(m, s, (p1, p2))
				#restraints_list.append(r)
		#else:
		#	print("The following restraint sources not in model: ",res1," and ",res2)

if options.hbond:
	print("Loading hbond restraints")
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
		model_particle_index[info] = i # get particle index of atom in chain 
	
	
	#print_helix_restraints:
	res_sec = {}
	for i in range(0, len(ss_sequence)):
		ss_char = ss_sequence[i:i+1]
		if ss_char == 'H':
			res_sec[i+1] = ss_char
	
	if res_sec:
		'''
		print("Loading dihedral restraints")
		print2file(work_dir+"/ssrestraints.log", "write helix tbl restraints");
		### haven't figure out how to add angle in IMP, using modeller's restraints instead https://salilab.org/modeller/9v8/manual/node102.html
		for i in sorted(res_sec.keys()):
			PHI_buff = re.split(" +",res_dihe["H PHI"])
			PSI_buff = re.split(" +",res_dihe["H PSI"])
			if len(PHI_buff) != 2:
				print("The PHI_buff value is strange: ",PHI_buff)
				sys.exit(-1)
			if len(PSI_buff) != 2:
				print("The PSI_buff value is strange: ",PSI_buff)
				sys.exit(-1)
			# 9/1/2014: If phi angle is removed from the pre-first residue, the first residue cannot form helix most of the times. Checked in 4/5 proteins and 2 dozen helices.
			# So, adding the pre-first phi angle as well (by removing the condition for  res_sec{$i-1} to exist)
			
			
			if (i-1) in residues:
				C1 = str(i-1)+'-'+aa_index2three[aa_one2index[residues[i-1]]]+'-C'
				N2 = str(i)+'-'+aa_index2three[aa_one2index[residues[i]]]+'-N'
				CA2 = str(i)+'-'+aa_index2three[aa_one2index[residues[i]]]+'-CA'
				C2 = str(i)+'-'+aa_index2three[aa_one2index[residues[i]]]+'-C'
				content = C1 + "\t" + N2 + "\t" + CA2 + "\t" + C2 + "\t"  + str(5.0) + "\t" + str(PHI_buff[0]) + "\t" + str(PHI_buff[1]) + "\t" +  str(2) + "\t!helix phi"
				print2file(work_dir+"/dihedral.tbl", content)
				res1_pos = 'C:'+str(i-1)
				res2_pos = 'N:'+str(i)
				res3_pos = 'CA:'+str(i)
				res4_pos = 'C:'+str(i)
				rsr.add(forms.gaussian(group=physical.dihedral, ## Table 6.1 in https://salilab.org/modeller/9v8/manual/node251.html#tab:physrsrtypes
				   feature=features.dihedral(modeller_atoms[res1_pos],
											 modeller_atoms[res2_pos],
											 modeller_atoms[res3_pos],
											 modeller_atoms[res4_pos]),
				   mean=float(PHI_buff[0]), stdev=float(PHI_buff[1])))
			# 9/1/2014: Even if we don't have PSI for the last residue, the last residue form helix, almost in all cases.
			# 9/2/2014: In some cases like target Tc767, only 106 helix residues were formed while the input is 111. And all of it is because of the psi angle at the end.
			# So, adding the post-last psi angle as well (by removing the condition for res_sec{$i+1} to exist)
			if (i+1) in residues:
				N1 = str(i)+'-'+aa_index2three[aa_one2index[residues[i]]]+'-N'
				CA1 = str(i)+'-'+aa_index2three[aa_one2index[residues[i]]]+'-CA'
				C1 = str(i)+'-'+aa_index2three[aa_one2index[residues[i]]]+'-C'
				N2 = str(i+1)+'-'+aa_index2three[aa_one2index[residues[i+1]]]+'-N'
				content = N1 + "\t" + CA1 + "\t" + C1 + "\t" + N2 + "\t"  + str(5.0) + "\t" + str(PSI_buff[0]) + "\t" + str(PSI_buff[1]) + "\t" +  str(2) + "\t!helix psi"
				print2file(work_dir+"/dihedral.tbl", content)		
				res1_pos = 'N:'+str(i)
				res2_pos = 'CA:'+str(i)
				res3_pos = 'C:'+str(i)
				res4_pos = 'N:'+str(i+1)
				rsr.add(forms.gaussian(group=physical.dihedral,
				   feature=features.dihedral(modeller_atoms[res1_pos],
											 modeller_atoms[res2_pos],
											 modeller_atoms[res3_pos],
											 modeller_atoms[res4_pos]),
				   mean=float(PSI_buff[0]), stdev=float(PSI_buff[1])))		
		
		'''
		
		## adding hbond will improve optimization, 
		for i in sorted(res_sec.keys()):
			if (i+1) not in res_sec:
				continue
			if (i+2) not in res_sec:
				continue
			if (i+3) not in res_sec:
				continue
			if (i+4) not in res_sec:
				continue
			HR_buff = re.split(" +",res_hbnd["H"])
			HR_buff[0] = float(HR_buff[0])
			if len(HR_buff) != 3:
				print("The HR_buff value is strange: ",HR_buff)
				sys.exit(-1)
			# In case of Proline, use N atom instead of H
			#HATOM = "H";
			#HR_buff[0] -= 1.0
			#if residues[i+4] == "P":
			#	HR_buff[0] += 1.0;
			#	HATOM  = "N";
			HATOM  = "N" # set to N, the optimal distance between O and N in alpha helix is 2.72
			# check https://www.nature.com/articles/srep38341, 
			O1 = str(i)+'-'+aa_index2three[aa_one2index[residues[i]]]+'-O'
			N4 = str(i+4)+'-'+aa_index2three[aa_one2index[residues[i+4]]]+'-' + HATOM
			content = O1 + "\t" + N4 + "\t" + str(HR_buff[0]) + "\t" + str(HR_buff[1]) + "\t" + str(HR_buff[2]) + "\t!helix"
			print2file(work_dir+"/hbond.tbl", (content))
			
			buff = re.split("\t+",content.strip())
			
			res1 = buff[0]
			res2 = buff[1]
			#re_value = float(buff[2]) # confold use 2.99, the optimization will stuck at 9 epoch with high energy, the reason might be the score function. If use harmoic, the number should be very accurate, which is different from the mean and deviation
			re_value = 2.72 #if harmonic funciton, need use this. the optimal distance between O and N in alpha helix is 2.72, the number should be very accurate for optimization, can keep being optimzed until 100 epoch
			content = O1 + "\t" + N4 + "\t" + str(re_value) + "\t!helix-harmonic"
			print2file(work_dir+"/hbond2.tbl", (content))
			if res1 in model_particle_index and res2 in model_particle_index:
				# get the particle index in model 
				#p1 = cont_model.get_particles()[model_particle_index[res1]]
				#p2 = cont_model.get_particles()[model_particle_index[res2]]
				#print(res1,"-",res2,": ",re_value)
				#f = IMP.core.Harmonic(re_value, 1)
				#s = IMP.core.DistancePairScore(f)
				#r = IMP.core.PairRestraint(m, s, (p1, p2))
				#restraints_list.append(r)
				
				res1_pos = 'O:'+str(i)
				res2_pos = 'N:'+str(i+4)
				rsr.add(forms.gaussian(group=physical.xy_distance,
				   feature=features.distance(modeller_atoms[res1_pos],
											 modeller_atoms[res2_pos]),
				   mean=float(HR_buff[0]), stdev=float(HR_buff[1])))
			else:
				print("The following restraint sources not in model: ",res1," and ",res2)
		
		'''
		#conclusion: score function is important, if using harmonic, the optimal distance should be very correct, otherwise, the optimization will stuck.
		#adding this won't improve optimization using harmonic function, will stuck at 19 epoch, i gutss the reason is that confold use mean and standard deviation, but here use harmoic, the number is not exact correct for optimization
		# after using gaussian function, the optimization is great., but still worse than only hbond
		print("Loading ssnoe restraints")
		for i in sorted(res_sec.keys()):
			if (i+1) not in res_sec:
				continue
			if (i+2) not in res_sec:
				continue
			if (i+3) not in res_sec:
				continue
			if (i+4) not in res_sec:
				continue
			for A in sorted(SS_ATOMTYPE.keys()):
				for SH in sorted(SS_SHIFT.keys()):
					AR_buff = re.split(" +",res_dist["H "+A+"-"+A+" O "+SH])
					if len(AR_buff) != 3:
						print("The AR_buff value is strange: ",AR_buff)
						sys.exit(-1)
					# found restraints even for non-helix SS
					if (i+4+int(SH)) not in res_sec:
						continue
					#confess ":(" if not defined ($i and $A and ($i+4+$SH) and $AR[0] and $AR[1] and $AR[2]);
					
					A1 = str(i)+'-'+aa_index2three[aa_one2index[residues[i]]]+'-'+str(A)
					A5 = str(i+4+int(SH))+'-'+aa_index2three[aa_one2index[residues[i+4+int(SH)]]]+'-'+str(A)
					content = A1 + "\t" + A5 + "\t" + str(AR_buff[0]) + "\t" + str(AR_buff[1]) + "\t" + str(AR_buff[2]) + "\t!helix"
					print2file(work_dir+"/ssnoe.tbl", (content))
					
					buff = re.split("\t+",content.strip())
			
					res1 = buff[0]
					res2 = buff[1]
					re_value = float(buff[2])
					
					if res1 in model_particle_index and res2 in model_particle_index:
						# get the particle index in model 
						#p1 = cont_model.get_particles()[model_particle_index[res1]]
						#p2 = cont_model.get_particles()[model_particle_index[res2]]
						#f = IMP.core.Harmonic(re_value, 1)
						#s = IMP.core.DistancePairScore(f)
						#r = IMP.core.PairRestraint(m, s, (p1, p2))
						#restraints_list.append(r)
				
						res1_pos = str(A)+':'+str(i)
						res2_pos = str(A)+':'+str(i+4+int(SH))
						rsr.add(forms.gaussian(group=physical.xy_distance,
						   feature=features.distance(modeller_atoms[res1_pos],
													 modeller_atoms[res2_pos]),
						   mean=float(AR_buff[0]), stdev=float(AR_buff[1])))
					else:
						print("The following restraint sources not in model: ",res1," and ",res2)
		
		'''
	else:
		print2file(work_dir+"/ssrestraints.log", "no helix predictions!");
	

if options.dihedral:
	print("Loading dihedral restraints")
	# 2-LYS-CA-1 53-VAL-CA-1 distance 5.1234
	f = open(options.dihedral, 'r')	
	restraints_contenst = f.readlines()	
	f.close()	

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
		model_particle_index[info] = i # get particle index of atom in chain 
	
	for line in restraints_contenst:
		if '#' in line:
			continue
		buff = re.split("\t+",line.strip())
		
		res1 = buff[0]
		res2 = buff[1]
		res3 = buff[2]
		res4 = buff[3]
		re_type = buff[4]
		re_value = float(buff[5])
		deviation = float(buff[6])
		
		p1_buff = re.split("-",res1)
		p2_buff = re.split("-",res2)
		p3_buff = re.split("-",res3)
		p4_buff = re.split("-",res4)
			
		res1_pos = p1_buff[2]+':'+str(p1_buff[0])
		res2_pos = p2_buff[2]+':'+str(p2_buff[0])
		res3_pos = p3_buff[2]+':'+str(p3_buff[0])
		res4_pos = p4_buff[2]+':'+str(p4_buff[0])
		rsr.add(forms.gaussian(group=physical.dihedral,
		   feature=features.dihedral(modeller_atoms[res1_pos],
									 modeller_atoms[res2_pos],
									 modeller_atoms[res3_pos],
									 modeller_atoms[res4_pos]),
		   mean=float(re_value), stdev=float(deviation)))
		''' not working in imp		   
		if res1 in model_particle_index and res2 in model_particle_index and res3 in model_particle_index and res4 in model_particle_index and re_type == 'dihedral':
			# get the particle index in model 
			p1 = cont_model.get_particles()[model_particle_index[res1]]
			p2 = cont_model.get_particles()[model_particle_index[res2]]
			p3 = cont_model.get_particles()[model_particle_index[res3]]
			p4 = cont_model.get_particles()[model_particle_index[res4]]
			
			anglemin = re_value  - deviation
			anglemax = re_value + deviation
			ts = IMP.core.HarmonicWell(
                     (math.pi * anglemin / 180.0,
                      math.pi * anglemax / 180.0), 10)
			#ts = IMP.core.HarmonicWell(
            #         (self.pi * anglemin / 180.0,
            #          self.pi * anglemax / 180.0), 10)
			r = IMP.core.DihedralRestraint(m,ts,p1,p2,p3,p4)
			
			restraints_list.append(r)
		else:
			print("The following restraint sources not in model: ",res1," and ",res2)
		'''
#else:
#	print('Error ! No restrains are provided. Exiting application...')
#	sys.exit(-1)
	
#### check using the predicted distance	
#### use predicted CB-CB distance,  
#### add secondary structure bond
#### in future, we can add predicted dihedral angles, predicted CA-CA	

###########################################################################################
# (6) Charmm forcefield
###########################################################################################

### add secondary structure, this is not enough to make perfect alpha helix, need custom hbond restraints above
#The example on this page
#http://www.salilab.org/modeller/wiki/Make%20alpha%20helix
#will not give you a "perfect" or ideal helix, but the minimization
#step should give you something reasonably stable to start from.

f = open(ss_file, 'r')	
ss_seq = f.readlines()	
f.close()	
# removing the trailing "\n" and any header lines
ss_seq = [line.strip() for line in ss_seq if not '>' in line]
ss_seq = ''.join( ss_seq )
res_strand = {}
res_helix = {}
for i in range(0, len(ss_sequence)):
	ss_char = ss_sequence[i:i+1]
	if ss_char == 'H':
		res_helix[i+1] = ss_char
	if ss_char == 'E':
		res_strand[i+1] = ss_char

print("Loading modeller's secondary structure restraints")
if res_helix:
	helix_range = get_ss_range(res_helix.keys())
	for item in helix_range:
		if '-' in str(item):
			print("Setting to helix in range ",item)
			ss_buff = re.split("-",item)
			rsr.add(secondary_structure.alpha(modmodel.residue_range(ss_buff[0], ss_buff[1])))
else:
	print("None helix information in structure")
	
if res_strand:
	strand_range = get_ss_range(res_strand.keys())
	for item in strand_range:
		if '-' in str(item):
			print("Setting to strand in range ",item)
			ss_buff = re.split("-",item)
			rsr.add(secondary_structure.strand(modmodel.residue_range(ss_buff[0], ss_buff[1])))

	#	   An anti-parallel sheet composed of the two strands:
	#	   rsr.add(secondary_structure.sheet(at['N:1'], at['O:14'],
	#										  sheet_h_bonds=-5))
	#	   Use the following instead for a *parallel* sheet:
	#	   rsr.add(secondary_structure.sheet(at['N:1'], at['O:9'],
	#										 sheet_h_bonds=5))
else:
	print("None strand information in structure")


### add stereo can make CA and side-chain atoms optimized together, very important.
r = IMP.modeller.ModellerRestraints(m, modmodel, atoms_model)
modeller_rsr = work_dir+'/modeller.rsr'
rsr.write(modeller_rsr)
restraints_list.append(r)

print('###########################################################################################')
print('# (7) Basic Optimization and Chain')
print('###########################################################################################')

# Optimize the x,y,z coordinates of both particles with conjugate gradients
s = IMP.core.ConjugateGradients(m)
#sf = IMP.core.RestraintsScoringFunction([br,r], "scoring function")
sf = IMP.core.RestraintsScoringFunction(restraints_list, "scoring function")

# the box to perform everything
s.set_scoring_function(sf)
#IMP.set_log_level(IMP.TERSE)

rotamer_lib='/data/commons/tools/IMP_tools/rotamer/ALL.bbdep.rotamers.lib'
rl = IMP.rotamer.RotamerLibrary()
rl.read_library_file(rotamer_lib)
rc = IMP.rotamer.RotamerCalculator(rl)

min_energy = 100000000000000
min_info = ''

out_pdb = sample_dir+'/'+target+'-epoch'+str(0).zfill(5)+'.pdb'
IMP.atom.write_pdb(prot, out_pdb)
clean_file = "sed -e \'s/\\x00//\' -i " + out_pdb
os.system(clean_file)


energy = sf.evaluate(False)
min_info = "Epoch: "+str(0)+": "+str(energy)+"\n"

out_energy = work_dir+'/sampling.energy'
with open(out_energy, 'w') as f1:
	f1.write(min_info)

out_eva = sample_dir+'/'+target+'-epoch'+str(0).zfill(5)+'.eva'
with open(out_eva, 'w') as f1:
	f1.write(min_info)


(molpdf, terms) = atmsel.energy(edat=energy_data(dynamic_sphere=True))

# molpdf is the total 'energy', and terms contains the contributions from
# each physical type. Here we print out the bond length contribution:
# https://salilab.org/modeller/9.12/manual/node260.html
print('initial energy')
print("Bond\tAngle\tdihedral\timproper\th_bond\tca_distance\tphi_dihedral\tpsi_dihedral\txy_distance\n")

print("%.5f\t%.5f\t%.5f\t%.5f\t%.5f\t%.5f\t%.5f\t%.5f\t%.5f\n\n" %(terms[physical.bond],terms[physical.angle],terms[physical.dihedral],terms[physical.improper],terms[physical.h_bond],terms[physical.ca_distance],terms[physical.phi_dihedral],terms[physical.psi_dihedral],terms[physical.xy_distance]))

if options.eva:
	exit(-1)
out_pdb=''
for i in range(1,epoch+1):
	s.optimize(cgstep)
	
	energy = sf.evaluate(False)
	## can apply simulated annealing here
	if energy < min_energy:
		min_energy = energy
		print("Epoch: ",i,": ",min_energy)
		## 
		min_info = "Epoch: "+str(i)+": "+str(min_energy)+"\n"
		with open(out_energy, 'a') as f1:
			f1.write(min_info)
		# Actually calculate the energy
		(molpdf, terms) = atmsel.energy(edat=energy_data(dynamic_sphere=True))

		# molpdf is the total 'energy', and terms contains the contributions from
		# each physical type. Here we print out the bond length contribution:
		# https://salilab.org/modeller/9.12/manual/node260.html
		print("%.5f\t%.5f\t%.5f\t%.5f\t%.5f\t%.5f\t%.5f\t%.5f\t%.5f\n" %(terms[physical.bond],terms[physical.angle],terms[physical.dihedral],terms[physical.improper],terms[physical.h_bond],terms[physical.ca_distance],terms[physical.phi_dihedral],terms[physical.psi_dihedral],terms[physical.xy_distance]))

		'''
		print("before rotamer: ",sf.evaluate(False))
		IMP.atom.write_pdb(prot, '3BFO-B-epoch'+str(i)+'-noRotamer.pdb')
		
		## add backbone-dependent rotamer library
		mh = IMP.atom.get_by_type(prot, IMP.atom.RESIDUE_TYPE)
		# get the most probable rotamers
		rotamers = list()
		for h in mh:
			rd = IMP.atom.Residue(h)
			rr = rc.get_rotamer(rd, 0.01)
			rotamers.append((rd, rr))
		
		# now set the coordinates of all atoms in the residues to the rotated
		# coordinates
		for rd, rr in rotamers:
			for h in IMP.atom.get_by_type(rd, IMP.atom.ATOM_TYPE):
				at = IMP.atom.Atom(h)
				at_t = at.get_atom_type()
				if rr.get_atom_exists(at_t):
					# some atoms might not be rotated
					idx = min(rr.get_number_of_cases(at_t) - 1, 1)
					v = rr.get_coordinates(idx, at_t)
					xyz = IMP.core.XYZ(at)
					xyz.set_coordinates(v)
		
		print("after rotamer: ",sf.evaluate(False))
		## question, why rotamer increase the energy?
		IMP.atom.write_pdb(prot, '3BFO-B-epoch'+str(i)+'-withRotamer.pdb')
		'''
		out_pdb = sample_dir+'/'+target+'-epoch'+str(i).zfill(5)+'.pdb'
		IMP.atom.write_pdb(prot, out_pdb)
		clean_file = "sed -e \'s/\\x00//\' -i " + out_pdb
		os.system(clean_file)
		
		out_eva = sample_dir+'/'+target+'-epoch'+str(i).zfill(5)+'.eva'
		with open(out_eva, 'w') as f1:
			f1.write(min_info)
		#pulchra_cmd = '/data/jh7x3/multicom_github/multicom/tools/pulchra304/pulchra 3BFO-B-epoch'+str(i)+'.pdb'
		#os.system(pulchra_cmd)
	
print(min_info) 
cmd = "cp "+out_pdb+" "+ work_dir+"/"+target+"_GFOLD.pdb"
os.system(cmd)



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

