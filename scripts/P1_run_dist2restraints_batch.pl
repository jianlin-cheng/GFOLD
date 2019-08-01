#!/usr/bin/perl -w

if (@ARGV != 3)
{
	die "need three parameters: option file, sequence file, output dir.\n"; 
}

$fasta_dir = shift @ARGV;
$pdb_dir = shift @ARGV;
$work_dir = shift @ARGV;


opendir(DIR,"$fasta_dir") || die "Failed to open directory $fasta_dir\n";
@files = readdir(DIR);
closedir(DIR);

foreach $file (@files)
{
	if($file eq '.' or $file eq '..')
	{
		next;
	}
	$pdbname = substr($file,0,index($file,'.fasta'));
	if($pdbname eq 'T0999')
	{
		next;
	}
	$pdbfile = "$pdb_dir/$pdbname.pdb";
	if(!(-e $pdbfile))
	{
		print "Failed to find $pdbfile\n";
		next;
	}
	
	if(-e "$work_dir/$pdbname.restraints")
	{
		next;
	}
	
	
	print "python /data/jh7x3/GFOLD_v0.1/examples/GFOLD_pdb2dist.py --pdb  $pdbfile --out  $work_dir/$pdbname.restraints\n";
	`python /data/jh7x3/GFOLD_v0.1/examples/GFOLD_pdb2dist.py --pdb  $pdbfile --out  $work_dir/$pdbname.restraints`;
}
