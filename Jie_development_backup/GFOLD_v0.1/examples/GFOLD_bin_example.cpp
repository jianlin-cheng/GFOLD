
/** \example core/simple.cpp
    Simple example of using the IMP C++ library.
    This should be equivalent to the first part of the Python example simple.py.
*/

////  Define header
#include <IMP.h>
#include <boost/program_options.hpp>
#include "boost/filesystem.hpp" 

#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <map>

#include <fstream>
//#include <IMP/kernel.h>
#include <IMP/atom.h>
#include <IMP/algebra.h>
#include <IMP/core.h>
#include <IMP/Model.h>
#include <IMP/Particle.h>
#include <IMP/core/Harmonic.h>
#include <IMP/Optimizer.h>
#include <IMP/SingletonScore.h>
#include <IMP/AttributeOptimizer.h>
#include <IMP/atom/ForceFieldParameters.h>
#include <IMP/atom/charmm_topology.h>


struct stat st = {0};
namespace po = boost::program_options;
using namespace std;

void loadFasta(char *filename, string &sequence);

int main() {
	
	//###########################################################################################
	//# (1) Build extended structure from sequence
	//###########################################################################################
	
	const IMP::atom::CHARMMParameters *force_field = IMP::atom::get_all_atom_CHARMM_parameters();
	IMP_NEW(IMP::atom::CHARMMTopology, topology0, (force_field));
	
	// load amino acid
	char *faFile = "3BFO-B.fasta";
    string sequence;
    loadFasta(faFile, sequence);
	cout << "Loading sequence: " << sequence << endl;
	
	topology0->add_sequence(sequence);
	topology0->apply_default_patches();
	

	//###########################################################################################
	//# (2) Load the model into IMP Hierarchy
	//###########################################################################################

	IMP_NEW(IMP::Model,m,());
	IMP::atom::Hierarchy h;
	h = topology0->create_hierarchy(m);
	topology0->add_atom_types(h);
	topology0->add_coordinates(h);

	// Hierarchies in IMP must have radii
	IMP::atom::add_radii(h);
	// Write out the final structure to a PDB file
	char *initFile = "3BFO-B-init2.pdb";
	IMP::atom::write_pdb(h, initFile);
	
	destroy(h);
	
	//###########################################################################################
	//# (3) Load initial model
	//###########################################################################################
	
	
	//# Create an IMP model and add a heavy atom-only protein from a PDB file
	//# example_protein.pdb is assumed to be just extended chain structure obtained using structure_from_sequence example
	IMP::atom::Hierarchy prot;
	IMP_NEW(IMP::atom::CBetaPDBSelector,cbSelect,());
	IMP_NEW(IMP::atom::BackbonePDBSelector,backboneSelect,());
	IMP_NEW(IMP::atom::OrPDBSelector,pdbSelect,(cbSelect,backboneSelect));
	prot = IMP::atom::read_pdb(initFile, m,pdbSelect);
	
	/*
	79 :  Atom N of residue 79
	79 :  Atom CA of residue 79
	79 :  Atom C of residue 79
	79 :  Atom O of residue 79
	79 :  Atom CB of residue 79
	*/
	
	IMP::atom::Hierarchies res_model = IMP::atom::get_by_type(prot, IMP::atom::RESIDUE_TYPE);
	IMP::atom::Hierarchies atoms_model = IMP::atom::get_by_type(prot, IMP::atom::ATOM_TYPE);
	IMP::atom::Hierarchies chain_model = IMP::atom::get_by_type(prot, IMP::atom::CHAIN_TYPE);
	
	cout << "There are " << chain_model.size() << " chains in structure" << endl;
	cout << "chain has " << atoms_model.size() << " atoms in structure" << endl;
	
	//# Get a list of all atoms in the model, and put it in a container
	IMP_NEW(IMP::container::ListSingletonContainer,cont_model,(atoms_model));
	
	//###########################################################################################
	//# (4) load the true structure and get information for all atoms
	//###########################################################################################
	
	IMP_NEW(IMP::Model,m_native,());
	IMP::atom::Hierarchy prot_native;
	char *nativeFile = "3BFO-B.chn";
	prot_native = IMP::atom::read_pdb(nativeFile, m);
	IMP::atom::Hierarchies atoms_native = IMP::atom::get_by_type(prot_native, IMP::atom::ATOM_TYPE);
	IMP_NEW(IMP::container::ListSingletonContainer,cont_native,(atoms_native));

	
	//#### get information for N,CA,C,O,CB from native structure
	map<int,string> index2ResidueName;
	map<string,IMP::core::XYZ> index2AtomCoord;
	
	//index2ResidueName.erase('1'); // erase
	//index2ResidueName.clear();; // clear
	//index2ResidueName["1"]="Gly";
    //cout<<index2ResidueName["1"]<<endl;
	
	for(int i=0;i<cont_native->get_particles().size();i++)
	{
		IMP::atom::Atom p1_atom = IMP::atom::Atom(cont_native->get_particles()[i]);
		IMP::algebra::Vector3D p1_coord = IMP::core::XYZ(cont_native->get_particles()[i]).get_coordinates(); //(1.885, 68.105, 54.894)
		string p1_atom_name = p1_atom.get_atom_type().get_string(); //#'N'
		string HET ("HET:");
		if(p1_atom_name.compare(0, HET.length(), HET)==0) {
			p1_atom_name = p1_atom_name.substr(4,p1_atom_name.length()-4);
		}
		IMP::atom::Residue p1_res = IMP::atom::get_residue(p1_atom);//#1 "SER"
		string p1_resname = p1_res->get_name(); // #'SER'
		int p1_seq_id = p1_res.get_index(); // #1
		if(p1_atom.get_atom_type() == IMP::atom::AtomType("CA"))
		{
			index2ResidueName[p1_seq_id] = p1_resname;
		}
		char key_info[1000];
		//cout<<p1_res<<" "<< p1_seq_id<< " " <<p1_resname<< " " << IMP::core::XYZ(cont_native->get_particles()[i]) <<endl;
		sprintf(key_info, "%i-%s-%s",p1_seq_id,p1_resname.c_str(),p1_atom_name.c_str());
		
		index2AtomCoord[key_info] = IMP::core::XYZ(cont_native->get_particles()[i]);
		
	}
	cout << "size: " << cont_native->get_particles().size() << endl;
	
	// use const_iterator to walk through elements of index2AtomCoord
	//for ( std::map<string,IMP::core::XYZ>::const_iterator iter = index2AtomCoord.begin();
	//	iter != index2AtomCoord.end(); ++iter )
	//	cout << iter->first << '\t' << iter->second << '\n';	
	
	
	//###########################################################################################
	//# (5) get distance restraints for N-CA, CA-C, C-O, CA-CB, CA-CA, CB-CB
	//###########################################################################################
	map<int,string> model_residues;
	map<string,int> model_particle_index;
	vector<int> residue_array;
	for(int i=0;i<cont_model->get_particles().size();i++)
	{
		IMP::atom::Atom p1_atom = IMP::atom::Atom(cont_model->get_particles()[i]);
		IMP::algebra::Vector3D p1_coord = IMP::core::XYZ(cont_model->get_particles()[i]).get_coordinates(); //(1.885, 68.105, 54.894)
		string p1_atom_name = p1_atom.get_atom_type().get_string(); //#'N'
		string HET ("HET:");
		if(p1_atom_name.compare(0, HET.length(), HET)==0) {
			p1_atom_name = p1_atom_name.substr(4,p1_atom_name.length()-4);
		}
		IMP::atom::Residue p1_res = IMP::atom::get_residue(p1_atom);//#1 "SER"
		string p1_resname = p1_res->get_name(); // #'SER'
		int p1_seq_id = p1_res.get_index(); // #1
		bool set_true = true;
		IMP::core::XYZ(cont_model->get_particles()[i]).set_coordinates_are_optimized(set_true);
		if(p1_atom.get_atom_type() == IMP::atom::AtomType("CA"))
		{
			model_residues[p1_seq_id] = p1_resname;
			residue_array.push_back(p1_seq_id);
		}	
		char key_info[100];
		sprintf(key_info, "%i-%s-%s",p1_seq_id,p1_resname.c_str(),p1_atom_name.c_str());
		model_particle_index[key_info] = i;
	}
	
	IMP::RestraintsAdaptor restraints_list;
	for(int i=0;i<residue_array.size();i++)
	{
		//# get N-CA, CA-C, C-O, CA-CB
		int res1_indx = residue_array[i];
		string res1_name = model_residues[res1_indx];
		
		char res1_N_atom[100];
		sprintf(res1_N_atom, "%i-%s-N",res1_indx,res1_name.c_str());
		
		char res1_CA_atom[100];
		sprintf(res1_CA_atom, "%i-%s-CA",res1_indx,res1_name.c_str());
		
		char res1_C_atom[100];
		sprintf(res1_C_atom, "%i-%s-C",res1_indx,res1_name.c_str());
		
		char res1_O_atom[100];
		sprintf(res1_O_atom, "%i-%s-O",res1_indx,res1_name.c_str());
		
		char res1_CB_atom[100];
		sprintf(res1_CB_atom, "%i-%s-CB",res1_indx,res1_name.c_str());
		
		//# get native coordinates, suppose the template structure is provided
		for(int j=i+1;j<residue_array.size();j++)
		{
			int res2_indx = residue_array[j];
			string res2_name = model_residues[res2_indx];
			
			char res2_CA_atom[100];
			sprintf(res2_CA_atom, "%i-%s-CA",res2_indx,res2_name.c_str());
			
			char res2_CB_atom[100];
			sprintf(res2_CB_atom, "%i-%s-CB",res2_indx,res2_name.c_str());
			
			char res2_O_atom[100];
			sprintf(res2_O_atom, "%i-%s-O",res2_indx,res2_name.c_str());
		
			char res2_N_atom[100];
			sprintf(res2_N_atom, "%i-%s-N",res2_indx,res2_name.c_str());
			
			//# get CA-CA
			
			if ( index2AtomCoord.find(res1_CA_atom) != index2AtomCoord.end() and index2AtomCoord.find(res2_CA_atom) != index2AtomCoord.end()) 
			{
			  // found
				IMP::core::XYZ res1_CA_atom_coord = index2AtomCoord[res1_CA_atom];
				IMP::core::XYZ res2_CA_atom_coord = index2AtomCoord[res2_CA_atom];
				double x1 = res1_CA_atom_coord.get_x();
				double y1 = res1_CA_atom_coord.get_y();
				double z1 = res1_CA_atom_coord.get_z();
				
				double x2 = res2_CA_atom_coord.get_x();
				double y2 = res2_CA_atom_coord.get_y();
				double z2 = res2_CA_atom_coord.get_z();
				double dist = sqrt((x1-x2) * (x1-x2) + (y1-y2) * (y1-y2) + (z1-z2) * (z1-z2));
				
				//# get the particle index in model 
				int res1_pindex = model_particle_index[res1_CA_atom];
				int res2_pindex = model_particle_index[res2_CA_atom];
				// Harmonically restrain p1 and p2 to be distance apart
				IMP_NEW(IMP::core::Harmonic, f2,(dist,1.0));
				char restr[100];
				sprintf(restr, "Distance Restraint <%s-%s>",res1_name.c_str(),res2_name.c_str());
				IMP_NEW(IMP::core::DistancePairScore,s,(f2,restr));
				IMP_NEW(IMP::core::PairRestraint,r,(s,IMP::ParticlePair(cont_model->get_particles()[res1_pindex],cont_model->get_particles()[res2_pindex])));
				restraints_list.push_back(r);
				
				//cout << "Adding restraints <"<< res1_name << ","<<res2_name<<">"<< endl;
				
			}
			
			//# get CB-CB
			
			if ( index2AtomCoord.find(res1_CB_atom) != index2AtomCoord.end() and index2AtomCoord.find(res2_CB_atom) != index2AtomCoord.end()) 
			{
			  // found
				IMP::core::XYZ res1_CB_atom_coord = index2AtomCoord[res1_CB_atom];
				IMP::core::XYZ res2_CB_atom_coord = index2AtomCoord[res2_CB_atom];
				double x1 = res1_CB_atom_coord.get_x();
				double y1 = res1_CB_atom_coord.get_y();
				double z1 = res1_CB_atom_coord.get_z();
				
				double x2 = res2_CB_atom_coord.get_x();
				double y2 = res2_CB_atom_coord.get_y();
				double z2 = res2_CB_atom_coord.get_z();
				double dist = sqrt((x1-x2) * (x1-x2) + (y1-y2) * (y1-y2) + (z1-z2) * (z1-z2));
				
				//# get the particle index in model 
				int res1_pindex = model_particle_index[res1_CB_atom];
				int res2_pindex = model_particle_index[res2_CB_atom];
				// Harmonically restrain p1 and p2 to be distance apart
				IMP_NEW(IMP::core::Harmonic, f2,(dist,1.0));
				char restr[100];
				sprintf(restr, "Distance Restraint <%s-%s>",res1_name.c_str(),res2_name.c_str());
				IMP_NEW(IMP::core::DistancePairScore,s,(f2,restr));
				IMP_NEW(IMP::core::PairRestraint,r,(s,IMP::ParticlePair(cont_model->get_particles()[res1_pindex],cont_model->get_particles()[res2_pindex])));
				restraints_list.push_back(r);
				
				//cout << "Adding restraints <"<< res1_name << ","<<res2_name<<">"<< endl;
				
			}
			
			//# this is very useful for secondary structure folding. get N-O to get hydrogen bond, 
			//#check confold how to add all N-O. pulchar also does post-hydrogen bond optimization.  
			//#We don't need all N-O which will cause large energy, we only need small part N-O, check confold
			
			//# get N-O
			
			if ( index2AtomCoord.find(res1_N_atom) != index2AtomCoord.end() and index2AtomCoord.find(res2_O_atom) != index2AtomCoord.end()) 
			{
			  // found
				IMP::core::XYZ res1_N_atom_coord = index2AtomCoord[res1_N_atom];
				IMP::core::XYZ res2_O_atom_coord = index2AtomCoord[res2_O_atom];
				double x1 = res1_N_atom_coord.get_x();
				double y1 = res1_N_atom_coord.get_y();
				double z1 = res1_N_atom_coord.get_z();
				
				double x2 = res2_O_atom_coord.get_x();
				double y2 = res2_O_atom_coord.get_y();
				double z2 = res2_O_atom_coord.get_z();
				double dist = sqrt((x1-x2) * (x1-x2) + (y1-y2) * (y1-y2) + (z1-z2) * (z1-z2));
				
				//# get the particle index in model 
				int res1_pindex = model_particle_index[res1_N_atom];
				int res2_pindex = model_particle_index[res2_O_atom];
				// Harmonically restrain p1 and p2 to be distance apart
				IMP_NEW(IMP::core::Harmonic, f2,(dist,1.0));
				char restr[100];
				sprintf(restr, "Distance Restraint <%s-%s>",res1_name.c_str(),res2_name.c_str());
				IMP_NEW(IMP::core::DistancePairScore,s,(f2,restr));
				IMP_NEW(IMP::core::PairRestraint,r,(s,IMP::ParticlePair(cont_model->get_particles()[res1_pindex],cont_model->get_particles()[res2_pindex])));
				restraints_list.push_back(r);
				
				//cout << "Adding restraints <"<< res1_name << ","<<res2_name<<">"<< endl;
				
			}
			
			//# get O-N
			
			if ( index2AtomCoord.find(res1_O_atom) != index2AtomCoord.end() and index2AtomCoord.find(res2_N_atom) != index2AtomCoord.end()) 
			{
			  // found
				IMP::core::XYZ res1_O_atom_coord = index2AtomCoord[res1_O_atom];
				IMP::core::XYZ res2_N_atom_coord = index2AtomCoord[res2_N_atom];
				double x1 = res1_O_atom_coord.get_x();
				double y1 = res1_O_atom_coord.get_y();
				double z1 = res1_O_atom_coord.get_z();
				
				double x2 = res2_N_atom_coord.get_x();
				double y2 = res2_N_atom_coord.get_y();
				double z2 = res2_N_atom_coord.get_z();
				double dist = sqrt((x1-x2) * (x1-x2) + (y1-y2) * (y1-y2) + (z1-z2) * (z1-z2));
				
				//# get the particle index in model 
				int res1_pindex = model_particle_index[res1_O_atom];
				int res2_pindex = model_particle_index[res2_N_atom];
				// Harmonically restrain p1 and p2 to be distance apart
				IMP_NEW(IMP::core::Harmonic, f2,(dist,1.0));
				char restr[100];
				sprintf(restr, "Distance Restraint <%s-%s>",res1_name.c_str(),res2_name.c_str());
				IMP_NEW(IMP::core::DistancePairScore,s,(f2,restr));
				IMP_NEW(IMP::core::PairRestraint,r,(s,IMP::ParticlePair(cont_model->get_particles()[res1_pindex],cont_model->get_particles()[res2_pindex])));
				restraints_list.push_back(r);
				
				//cout << "Adding restraints <"<< res1_name << ","<<res2_name<<">"<< endl;
				
			}

		}
		
		
	}
	
	//###########################################################################################
	//# (6) Charmm forcefield
	//###########################################################################################
	const IMP::atom::CHARMMParameters *ff = IMP::atom::get_heavy_atom_CHARMM_parameters();
	IMP::atom::CHARMMTopology *topology = ff->create_topology(prot);
	topology->apply_default_patches();
	topology->setup_hierarchy(prot);
	
	IMP_NEW(IMP::atom::CHARMMStereochemistryRestraint,r_stereo,(prot, topology));
	
	ff->add_radii(prot);
	ff->add_well_depths(prot);
	restraints_list.push_back(r_stereo);
	
	//###########################################################################################
	//# (7) Basic Optimization and Chain
	//###########################################################################################

	
	//# Optimize the x,y,z coordinates of both particles with conjugate gradients
	IMP_NEW(IMP::core::ConjugateGradients,s,(m));
	IMP_NEW(IMP::core::RestraintsScoringFunction,sf,(restraints_list,"scoring function"));
	s->set_scoring_function(sf);
	//IMP.set_log_level(IMP.TERSE);
	bool set_false = false;
	char sampleFile[100];
	for(int i=0; i<10;i++)
	{
		s->optimize(100);
		double energy = sf->evaluate(set_false);
		cout << "Epoch " << i << ": " << energy << endl;
		sprintf(sampleFile,"3BFO-B-bin-epoch-%i.pdb",i);
		IMP::atom::write_pdb(prot, sampleFile);
	}

  return 0;
}


/*************************************************************************
 * Name        : loadFasta
 * Purpose     : loads a fasta file into a vector of int object
 * Arguments   : char *filename, vector<int> &aa
 * Return Type : void
 *************************************************************************/
void loadFasta(char *filename, string &sequence) {
    string line, str;
    string header (">");
    ifstream fin (filename);
    if (fin.is_open()) {
        while ( fin.good() ) {
            getline(fin, line);
            line.erase(std::remove(line.begin(), line.end(), '\n'), line.end());
            if(line.length() != 0 && line.compare(0, header.length(), header) != 0) {
                for (int i = 0; i < line.length(); i++) {
					sequence.append(line.substr(i,1).c_str());
                }
            }
        }
        fin.close();
    }
    else {
        cout << "Error! fasta file can not open " << filename << endl;
        exit(0);
    }
}


	
	
	


