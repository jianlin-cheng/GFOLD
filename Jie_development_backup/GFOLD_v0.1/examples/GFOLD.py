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
import time
import modeller
from modeller import *
import IMP.modeller
warnings.filterwarnings("ignore")
modeller.log.none()

import random
#modeller.log.minimal()

#/home/jh7x3/fusion_hybrid/
project_root = '/data/jh7x3/GFOLD_v0.1/examples/GFOLD_pylib'
sys.path.insert(0, project_root)

from GFOLD_lib import *

print('')
print('  ############################################################################')
print('  #																			#')
print('  #		GFOLD : A Distance-based Protein Structure Folding					#')
print('  #																			#')
print('  #	Copyright (C) 2019 -2029	Jie Hou and Jianlin Cheng					#')
print('  #																			#')
print('  ############################################################################')
print('  #																			#')
print('  #	Method to perform distance-based modeling (TS)							#')
print('  #																			#')
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
####################### new added
e.io.hetatm = True
#soft sphere potential
e.edat.dynamic_sphere=False
#lennard-jones potential (more accurate)
e.edat.dynamic_lennard=True
e.edat.contact_shell = 4.0
e.edat.update_dynamic = 0.39
#######################

# To assign 0 weights to restraints whose numerical derivatives
# code does not work (i.e., splines for angles and dihedrals):
# https://salilab.org/modeller/9v8/manual/node251.html
#23.07959        105.20986       363.30685       17.39790        0.19570 0.00000 0.00000 0.00000 39.04685

e.schedule_scale = physical.values(bond= 1, angle= 1, dihedral= 1, improper= 1, xy_distance= 1,lennard_jones=0, coulomb=0, h_bond=1,
                       phi_dihedral=0, psi_dihedral=0, omega_dihedral=0,
                       chi1_dihedral=0, chi2_dihedral=0, chi3_dihedral=0,
                       chi4_dihedral=0, disulfide_angle=0,
                       disulfide_dihedral=0, chi5_dihedral=0)

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

hbond_restraints = []
ssnoe_restraints = []
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
				
				
				hbond_restraints.append(forms.gaussian(group=physical.xy_distance,
				   feature=features.distance(modeller_atoms[res1_pos],
											 modeller_atoms[res2_pos]),
				   mean=2.72, stdev=0.1))
				
				#hbond_restraints.append(forms.gaussian(group=physical.xy_distance,
				#   feature=features.distance(modeller_atoms[res1_pos],
				#							 modeller_atoms[res2_pos]),
				#   mean=float(HR_buff[0]), stdev=float(HR_buff[1])))
				
				#rsr.add(forms.gaussian(group=physical.xy_distance,
				#   feature=features.distance(modeller_atoms[res1_pos],
				#							 modeller_atoms[res2_pos]),
				#   mean=float(HR_buff[0]), stdev=float(HR_buff[1])))
			else:
				print("The following restraint sources not in model: ",res1," and ",res2)
		
		
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
						ssnoe_restraints.append(forms.gaussian(group=physical.xy_distance,
						   feature=features.distance(modeller_atoms[res1_pos],
													 modeller_atoms[res2_pos]),
						   mean=float(AR_buff[0]), stdev=float(AR_buff[1])))
						#rsr.add(forms.gaussian(group=physical.xy_distance,
						#   feature=features.distance(modeller_atoms[res1_pos],
						#							 modeller_atoms[res2_pos]),
						#   mean=float(AR_buff[0]), stdev=float(AR_buff[1])))
					else:
						print("The following restraint sources not in model: ",res1," and ",res2)
		
		
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

alphahelix_restraints = []
if res_helix:
	helix_range = get_ss_range(res_helix.keys())
	for item in helix_range:
		if '-' in str(item):
			print("Setting to helix in range ",item)
			ss_buff = re.split("-",item)
			alphahelix_restraints.append(secondary_structure.alpha(modmodel.residue_range(ss_buff[0], ss_buff[1])))
			#rsr.add(secondary_structure.alpha(modmodel.residue_range(ss_buff[0], ss_buff[1])))
else:
	print("None helix information in structure")

betastrand_restraints = []
if res_strand:
	strand_range = get_ss_range(res_strand.keys())
	for item in strand_range:
		if '-' in str(item):
			print("Setting to strand in range ",item)
			ss_buff = re.split("-",item)
			betastrand_restraints.append(secondary_structure.strand(modmodel.residue_range(ss_buff[0], ss_buff[1])))
			#rsr.add(secondary_structure.strand(modmodel.residue_range(ss_buff[0], ss_buff[1])))

	#	   An anti-parallel sheet composed of the two strands:
	#	   rsr.add(secondary_structure.sheet(at['N:1'], at['O:14'],
	#										  sheet_h_bonds=-5))
	#	   Use the following instead for a *parallel* sheet:
	#	   rsr.add(secondary_structure.sheet(at['N:1'], at['O:9'],
	#										 sheet_h_bonds=5))
else:
	print("None strand information in structure")





###########################################################################################
# (4) load the template structure and get information for all atoms
###########################################################################################

dist_close_restraints = []
dist_short_restraints = []
dist_medium_restraints = []
dist_long_restraints = []
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
		
		if re_value > 24: 
			continue
		
		if res1 in model_particle_index and res2 in model_particle_index and re_type == 'distance':
			# get the particle index in model 
			p1 = cont_model.get_particles()[model_particle_index[res1]]
			p2 = cont_model.get_particles()[model_particle_index[res2]]
			
			p1_buff = re.split("-",res1)
			p2_buff = re.split("-",res2)
			
			#if p1_buff[1] == 'GLY' or p2_buff[1] == 'GLY' :
			#	continue
			
			if int(p2_buff[0])-int(p1_buff[0])< separation:
				continue
			if atom_type_dist == 'all':
				p1_atom_type_dist = p1_buff[2]
				p2_atom_type_dist = p2_buff[2]
				res1_pos = p1_atom_type_dist+':'+str(p1_buff[0])
				res2_pos = p2_atom_type_dist+':'+str(p2_buff[0])
				
				if abs(int(p2_buff[0])-int(p1_buff[0])) <6:
					dist_close_restraints.append(forms.gaussian(group=physical.xy_distance,
					   feature=features.distance(modeller_atoms[res1_pos],
												 modeller_atoms[res2_pos]),
					   mean=re_value, stdev=distdev))
				elif abs(int(p2_buff[0])-int(p1_buff[0])) >=6 and abs(int(p2_buff[0])-int(p1_buff[0])) <12:
					dist_short_restraints.append(forms.gaussian(group=physical.xy_distance,
					   feature=features.distance(modeller_atoms[res1_pos],
												 modeller_atoms[res2_pos]),
					   mean=re_value, stdev=distdev))
				elif abs(int(p2_buff[0])-int(p1_buff[0])) >=12 and abs(int(p2_buff[0])-int(p1_buff[0])) <24:
					dist_medium_restraints.append(forms.gaussian(group=physical.xy_distance,
					   feature=features.distance(modeller_atoms[res1_pos],
												 modeller_atoms[res2_pos]),
					   mean=re_value, stdev=distdev))
				elif abs(int(p2_buff[0])-int(p1_buff[0])) >=24:
					dist_long_restraints.append(forms.gaussian(group=physical.xy_distance,
					   feature=features.distance(modeller_atoms[res1_pos],
												 modeller_atoms[res2_pos]),
					   mean=re_value, stdev=distdev))
				
				#rsr.add(forms.gaussian(group=physical.xy_distance,
				#   feature=features.distance(modeller_atoms[res1_pos],
				#							 modeller_atoms[res2_pos]),
				#   mean=re_value, stdev=distdev))
				content = res1_pos + "\t" + res2_pos + "\t" + str(re_value) + "\t" + str(distdev) + "\t" + str(distdev) + "\t!"+p1_atom_type_dist+"-"+p2_atom_type_dist
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
				
				
				if abs(int(p2_buff[0])-int(p1_buff[0])) <6:
					dist_close_restraints.append(forms.gaussian(group=physical.xy_distance,
					   feature=features.distance(modeller_atoms[res1_pos],
												 modeller_atoms[res2_pos]),
					   mean=re_value, stdev=distdev))
				elif abs(int(p2_buff[0])-int(p1_buff[0])) >=6 and abs(int(p2_buff[0])-int(p1_buff[0])) <12:
					dist_short_restraints.append(forms.gaussian(group=physical.xy_distance,
					   feature=features.distance(modeller_atoms[res1_pos],
												 modeller_atoms[res2_pos]),
					   mean=re_value, stdev=distdev))
				elif abs(int(p2_buff[0])-int(p1_buff[0])) >=12 and abs(int(p2_buff[0])-int(p1_buff[0])) <24:
					dist_medium_restraints.append(forms.gaussian(group=physical.xy_distance,
					   feature=features.distance(modeller_atoms[res1_pos],
												 modeller_atoms[res2_pos]),
					   mean=re_value, stdev=distdev))
				elif abs(int(p2_buff[0])-int(p1_buff[0])) >=24:
					dist_long_restraints.append(forms.gaussian(group=physical.xy_distance,
					   feature=features.distance(modeller_atoms[res1_pos],
												 modeller_atoms[res2_pos]),
					   mean=re_value, stdev=distdev))
				
				
				#rsr.add(forms.gaussian(group=physical.xy_distance,
				#   feature=features.distance(modeller_atoms[res1_pos],
				#							 modeller_atoms[res2_pos]),
				#   mean=re_value, stdev=distdev))
				
				content = res1_pos + "\t" + res2_pos + "\t" + str(re_value) + "\t" + str(distdev) + "\t" + str(distdev) + "\t!"+p1_atom_type_dist+"-"+p2_atom_type_dist
				print2file(work_dir+"/distance.tbl", (content))
			else:
				#if p1_buff[2] == 'CA' and p2_buff[2] == 'CA':
				if p1_buff[2] == 'CA' and p2_buff[2] == 'CA' and atom_type_dist == 'CA':
					#print("Adding restraints for ",res1," and ", res2)
					res1_pos = 'CA:'+str(p1_buff[0])
					res2_pos = 'CA:'+str(p2_buff[0])
					
					if abs(int(p2_buff[0])-int(p1_buff[0])) <6:
						dist_close_restraints.append(forms.gaussian(group=physical.xy_distance,
						   feature=features.distance(modeller_atoms[res1_pos],
													 modeller_atoms[res2_pos]),
						   mean=re_value, stdev=distdev))
					elif abs(int(p2_buff[0])-int(p1_buff[0])) >=6 and abs(int(p2_buff[0])-int(p1_buff[0])) <12:
						dist_short_restraints.append(forms.gaussian(group=physical.xy_distance,
						   feature=features.distance(modeller_atoms[res1_pos],
													 modeller_atoms[res2_pos]),
						   mean=re_value, stdev=distdev))
					elif abs(int(p2_buff[0])-int(p1_buff[0])) >=12 and abs(int(p2_buff[0])-int(p1_buff[0])) <24:
						dist_medium_restraints.append(forms.gaussian(group=physical.xy_distance,
						   feature=features.distance(modeller_atoms[res1_pos],
													 modeller_atoms[res2_pos]),
						   mean=re_value, stdev=distdev))
					elif abs(int(p2_buff[0])-int(p1_buff[0])) >=24:
						dist_long_restraints.append(forms.gaussian(group=physical.xy_distance,
						   feature=features.distance(modeller_atoms[res1_pos],
													 modeller_atoms[res2_pos]),
						   mean=re_value, stdev=distdev))
					
					#rsr.add(forms.gaussian(group=physical.xy_distance,
					#   feature=features.distance(modeller_atoms[res1_pos],
					#							 modeller_atoms[res2_pos]),
					#   mean=re_value, stdev=distdev))
					
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
						
						if abs(int(p2_buff[0])-int(p1_buff[0])) <6:
							dist_close_restraints.append(forms.gaussian(group=physical.xy_distance,
							   feature=features.distance(modeller_atoms[res1_pos],
														 modeller_atoms[res2_pos]),
							   mean=re_value, stdev=distdev))
						elif abs(int(p2_buff[0])-int(p1_buff[0])) >=6 and abs(int(p2_buff[0])-int(p1_buff[0])) <12:
							dist_short_restraints.append(forms.gaussian(group=physical.xy_distance,
							   feature=features.distance(modeller_atoms[res1_pos],
														 modeller_atoms[res2_pos]),
							   mean=re_value, stdev=distdev))
						elif abs(int(p2_buff[0])-int(p1_buff[0])) >=12 and abs(int(p2_buff[0])-int(p1_buff[0])) <24:
							dist_medium_restraints.append(forms.gaussian(group=physical.xy_distance,
							   feature=features.distance(modeller_atoms[res1_pos],
														 modeller_atoms[res2_pos]),
							   mean=re_value, stdev=distdev))
						elif abs(int(p2_buff[0])-int(p1_buff[0])) >=24:
							dist_long_restraints.append(forms.gaussian(group=physical.xy_distance,
							   feature=features.distance(modeller_atoms[res1_pos],
														 modeller_atoms[res2_pos]),
							   mean=re_value, stdev=distdev))
							   
						#rsr.add(forms.gaussian(group=physical.xy_distance,
						#   feature=features.distance(modeller_atoms[res1_pos],
						#							 modeller_atoms[res2_pos]),
						#   mean=re_value, stdev=distdev)) #Standard deviation depends on solvent accessibility, gaps of alignment, and sequence identity: https://salilab.org/modeller/manual/node213.html
						
						content = res1_pos + "\t" + res2_pos + "\t" + str(re_value) + "\t" + str(distdev) + "\t" + str(distdev) + "\t!CB-CB"
						print2file(work_dir+"/distance.tbl", (content))
					if p1_buff[1] == 'GLY' and p1_buff[2] == 'CA' and p2_buff[1] != 'GLY' and  p2_buff[2] == 'CB' :
						#print("Adding restraints for ",res1," and ", res2)
						res1_pos = 'CA:'+str(p1_buff[0])
						res2_pos = 'CB:'+str(p2_buff[0])
						
						
						if abs(int(p2_buff[0])-int(p1_buff[0])) <6:
							dist_close_restraints.append(forms.gaussian(group=physical.xy_distance,
							   feature=features.distance(modeller_atoms[res1_pos],
														 modeller_atoms[res2_pos]),
							   mean=re_value, stdev=distdev))
						elif abs(int(p2_buff[0])-int(p1_buff[0])) >=6 and abs(int(p2_buff[0])-int(p1_buff[0])) <12:
							dist_short_restraints.append(forms.gaussian(group=physical.xy_distance,
							   feature=features.distance(modeller_atoms[res1_pos],
														 modeller_atoms[res2_pos]),
							   mean=re_value, stdev=distdev))
						elif abs(int(p2_buff[0])-int(p1_buff[0])) >=12 and abs(int(p2_buff[0])-int(p1_buff[0])) <24:
							dist_medium_restraints.append(forms.gaussian(group=physical.xy_distance,
							   feature=features.distance(modeller_atoms[res1_pos],
														 modeller_atoms[res2_pos]),
							   mean=re_value, stdev=distdev))
						elif abs(int(p2_buff[0])-int(p1_buff[0])) >=24:
							dist_long_restraints.append(forms.gaussian(group=physical.xy_distance,
							   feature=features.distance(modeller_atoms[res1_pos],
														 modeller_atoms[res2_pos]),
							   mean=re_value, stdev=distdev))
						
						#rsr.add(forms.gaussian(group=physical.xy_distance,
						#   feature=features.distance(modeller_atoms[res1_pos],
						#							 modeller_atoms[res2_pos]),
						#   mean=re_value, stdev=distdev)) #Standard deviation depends on solvent accessibility, gaps of alignment, and sequence identity: https://salilab.org/modeller/manual/node213.html
						
						content = res1_pos + "\t" + res2_pos + "\t" + str(re_value) + "\t" + str(distdev) + "\t" + str(distdev) + "\t!CB-CB"
						print2file(work_dir+"/distance.tbl", (content))
					if p1_buff[1] != 'GLY' and p1_buff[2] == 'CB' and p2_buff[1] == 'GLY' and  p2_buff[2] == 'CA' :
						#print("Adding restraints for ",res1," and ", res2)
						res1_pos = 'CB:'+str(p1_buff[0])
						res2_pos = 'CA:'+str(p2_buff[0])
						
						if abs(int(p2_buff[0])-int(p1_buff[0])) <6:
							dist_close_restraints.append(forms.gaussian(group=physical.xy_distance,
							   feature=features.distance(modeller_atoms[res1_pos],
														 modeller_atoms[res2_pos]),
							   mean=re_value, stdev=distdev))
						elif abs(int(p2_buff[0])-int(p1_buff[0])) >=6 and abs(int(p2_buff[0])-int(p1_buff[0])) <12:
							dist_short_restraints.append(forms.gaussian(group=physical.xy_distance,
							   feature=features.distance(modeller_atoms[res1_pos],
														 modeller_atoms[res2_pos]),
							   mean=re_value, stdev=distdev))
						elif abs(int(p2_buff[0])-int(p1_buff[0])) >=12 and abs(int(p2_buff[0])-int(p1_buff[0])) <24:
							dist_medium_restraints.append(forms.gaussian(group=physical.xy_distance,
							   feature=features.distance(modeller_atoms[res1_pos],
														 modeller_atoms[res2_pos]),
							   mean=re_value, stdev=distdev))
						elif abs(int(p2_buff[0])-int(p1_buff[0])) >=24:
							dist_long_restraints.append(forms.gaussian(group=physical.xy_distance,
							   feature=features.distance(modeller_atoms[res1_pos],
														 modeller_atoms[res2_pos]),
							   mean=re_value, stdev=distdev))
						
						#rsr.add(forms.gaussian(group=physical.xy_distance,
						#   feature=features.distance(modeller_atoms[res1_pos],
						#							 modeller_atoms[res2_pos]),
						#   mean=re_value, stdev=distdev)) #Standard deviation depends on solvent accessibility, gaps of alignment, and sequence identity: https://salilab.org/modeller/manual/node213.html
						
						content = res1_pos + "\t" + res2_pos + "\t" + str(re_value) + "\t" + str(distdev) + "\t" + str(distdev) + "\t!CB-CB"
						print2file(work_dir+"/distance.tbl", (content))
					if p1_buff[1] != 'GLY' and p1_buff[2] == 'CB' and p2_buff[1] != 'GLY' and  p2_buff[2] == 'CB' :
						#print("Adding restraints for ",res1," and ", res2)
						res1_pos = 'CB:'+str(p1_buff[0])
						res2_pos = 'CB:'+str(p2_buff[0])
						
						if abs(int(p2_buff[0])-int(p1_buff[0])) <6:
							dist_close_restraints.append(forms.gaussian(group=physical.xy_distance,
							   feature=features.distance(modeller_atoms[res1_pos],
														 modeller_atoms[res2_pos]),
							   mean=re_value, stdev=distdev))
						elif abs(int(p2_buff[0])-int(p1_buff[0])) >=6 and abs(int(p2_buff[0])-int(p1_buff[0])) <12:
							dist_short_restraints.append(forms.gaussian(group=physical.xy_distance,
							   feature=features.distance(modeller_atoms[res1_pos],
														 modeller_atoms[res2_pos]),
							   mean=re_value, stdev=distdev))
						elif abs(int(p2_buff[0])-int(p1_buff[0])) >=12 and abs(int(p2_buff[0])-int(p1_buff[0])) <24:
							dist_medium_restraints.append(forms.gaussian(group=physical.xy_distance,
							   feature=features.distance(modeller_atoms[res1_pos],
														 modeller_atoms[res2_pos]),
							   mean=re_value, stdev=distdev))
						elif abs(int(p2_buff[0])-int(p1_buff[0])) >=24:
							dist_long_restraints.append(forms.gaussian(group=physical.xy_distance,
							   feature=features.distance(modeller_atoms[res1_pos],
														 modeller_atoms[res2_pos]),
							   mean=re_value, stdev=distdev))
						
						#rsr.add(forms.gaussian(group=physical.xy_distance,
						#   feature=features.distance(modeller_atoms[res1_pos],
						#							 modeller_atoms[res2_pos]),
						#   mean=re_value, stdev=distdev)) #Standard deviation depends on solvent accessibility, gaps of alignment, and sequence identity: https://salilab.org/modeller/manual/node213.html
						
						content = res1_pos + "\t" + res2_pos + "\t" + str(re_value) + "\t" + str(distdev) + "\t" + str(distdev) + "\t!CB-CB"
						print2file(work_dir+"/distance.tbl", (content))
				
				#f = IMP.core.Harmonic(re_value, 0.1)
				#s = IMP.core.DistancePairScore(f)
				#r = IMP.core.PairRestraint(m, s, (p1, p2))
				#restraints_list.append(r)
		#else:
		#	print("The following restraint sources not in model: ",res1," and ",res2)



print('###########################################################################################')
print('# (7) Basic Optimization and Chain')
print('###########################################################################################')


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



if options.eva:
	exit(-1)
out_pdb=''
best_pdb=''


rsr = modmodel.restraints
atmsel = selection(modmodel)
rsr.clear()
rsr.make(atmsel, restraint_type='stereo', spline_on_site=False)
for item in alphahelix_restraints:
	rsr.add(item)
for item in betastrand_restraints:
	rsr.add(item)

for item in dist_short_restraints:
	rsr.add(item)
for item in dist_medium_restraints:
	rsr.add(item)
for item in dist_long_restraints:
	rsr.add(item)

### add stereo can make CA and side-chain atoms optimized together, very important.
r = IMP.modeller.ModellerRestraints(m, modmodel, atoms_model)
restraints_list = []
restraints_list.append(r)
# Optimize the x,y,z coordinates of both particles with conjugate gradients
s = IMP.core.ConjugateGradients(m)
#sf = IMP.core.RestraintsScoringFunction([br,r], "scoring function")
sf = IMP.core.RestraintsScoringFunction(restraints_list, "scoring function")
s.set_scoring_function(sf)
s.optimize(300)

for i in range(1,epoch+1):
	if i == 1:
		min_info = "## GFOLD modeling\n"

		out_energy = work_dir+'/sampling.energy'
		with open(out_energy, 'w') as f1:
			f1.write(min_info)
	
	rsr = modmodel.restraints
	atmsel = selection(modmodel)
	rsr.clear()


	## randomize the helix for refinement
	for mn in range(0,len(cont_model.get_particles())):
		p1 = cont_model.get_particles()[mn]
		#get atom information 
		p1_atom = IMP.atom.Atom(p1)
		p1_res = IMP.atom.get_residue(p1_atom) ##1 "SER"
		p1_resname = p1_res.get_name() #'SER'
		p1_seq_id = p1_res.get_index() #1
		if int(p1_seq_id) in res_helix.keys():
			### randomized the helix for optimization
			p1_coord=IMP.core.XYZ(p1).get_coordinates()
			dx=(2*random.random()-1)*10
			dy=(2*random.random()-1)*10
			dz=(2*random.random()-1)*10 
			p1_coord_new = p1_coord
			p1_coord_new[0] += dx
			p1_coord_new[1] += dy
			p1_coord_new[2] += dz
			IMP.core.XYZ(p1).set_coordinates(p1_coord_new) #placed nearby cen

		
	rsr.clear()
	rsr.make(atmsel, restraint_type='stereo', spline_on_site=False)
	for item in alphahelix_restraints:
		rsr.add(item)
	for item in betastrand_restraints:
		rsr.add(item)

	for item in dist_short_restraints:
		rsr.add(item)
	for item in dist_medium_restraints:
		rsr.add(item)
	for item in dist_long_restraints:
		rsr.add(item)
	
	### add stereo can make CA and side-chain atoms optimized together, very important.
	r = IMP.modeller.ModellerRestraints(m, modmodel, atoms_model)
	restraints_list = []
	restraints_list.append(r)

	### simulated annealing using Molecular Dynamics
	t0 = time.time()
	hot = 1000
	cold = 100
	nc = 4
	dt = (hot-cold)/nc
	for san in range(nc+1):
		t1 = time.time()
		t = hot-dt*san
		s    = IMP.atom.MolecularDynamics(m)
		sf = IMP.core.RestraintsScoringFunction(restraints_list, "scoring function")
		s.set_scoring_function(sf)
		xyzr = cont_model.get_particles()
		md   = IMP.atom.LangevinThermostatOptimizerState(m,xyzr,t,0.1)
		s.add_optimizer_state(md)
		score = s.optimize(100)
		s.remove_optimizer_state(md)
		print("\tMD ",str(cgstep),' steps ',str(san),' done ',str(t1),' score = ',str(score))
		(molpdf, terms) = atmsel.energy(edat=energy_data(dynamic_sphere=True))		

	# Optimize the x,y,z coordinates of both particles with conjugate gradients
	s = IMP.core.ConjugateGradients(m)
	#sf = IMP.core.RestraintsScoringFunction([br,r], "scoring function")
	sf = IMP.core.RestraintsScoringFunction(restraints_list, "scoring function")
	s.set_scoring_function(sf)
	s.optimize(300)
		
		
	(molpdf, terms) = atmsel.energy(edat=energy_data(dynamic_sphere=True))

	# molpdf is the total 'energy', and terms contains the contributions from
	# each physical type. Here we print out the bond length contribution:
	# https://salilab.org/modeller/9.12/manual/node260.html
	print("\n\tBond\tAngle\tdihedral\timproper\th_bond\tca_distance\tphi_dihedral\tpsi_dihedral\txy_distance")
	print("\t%.5f\t%.5f\t%.5f\t%.5f\t%.5f\t%.5f\t%.5f\t%.5f\t%.5f\n" %(terms[physical.bond],terms[physical.angle],terms[physical.dihedral],terms[physical.improper],terms[physical.h_bond],terms[physical.ca_distance],terms[physical.phi_dihedral],terms[physical.psi_dihedral],terms[physical.xy_distance]))

	
	out_pdb = sample_dir+'/'+target+'-epoch'+str(i).zfill(5)+'_beforerefine.pdb'
	modmodel.write(file=out_pdb)
	clean_file = "sed -e \'s/\\x00//\' -i " + out_pdb
	os.system(clean_file)	

		
	energy = sf.evaluate(False)
	print("Epoch: ",i,": ",energy)
	energy_info = "Epoch: "+str(i)+": "+str(energy)+"\n"
	with open(out_energy, 'a') as f1:
		f1.write(energy_info)
	
	
	out_pdb = sample_dir+'/'+target+'-epoch'+str(i).zfill(5)+'.pdb'
	modmodel.write(file=out_pdb)
	clean_file = "sed -e \'s/\\x00//\' -i " + out_pdb
	os.system(clean_file)
	out_eva = sample_dir+'/'+target+'-epoch'+str(i).zfill(5)+'.eva'
	with open(out_eva, 'w') as f1:
		f1.write(min_info)
	# Actually calculate the energy
	## can apply simulated annealing here
	if energy < min_energy:
		min_energy = energy
		best_pdb = sample_dir+'/'+target+'-epoch'+str(i).zfill(5)+'.pdb'
		min_info = "Epoch: "+str(i)+": "+str(min_energy)+"\n"


print("The best model is found in ",min_info) 
cmd = "cp "+best_pdb+" "+ work_dir+"/"+target+"_GFOLD.pdb"
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

