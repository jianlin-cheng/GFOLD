#!/usr/bin/perl -w

if (@ARGV != 3)
{
	die "need three parameters: option file, sequence file, output dir.\n"; 
}

$fasta_dir = shift @ARGV;
$dist_dir = shift @ARGV;
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
	$distfile = "$dist_dir/$pdbname.predict.distmap.rr";
	if(!(-e $distfile))
	{
		print "Failed to find $distfile\n";
		next;
	}
	
	if(-e "$work_dir/$pdbname.restraints")
	{
		next;
	}
	
	
	print "perl /data/jh7x3/GFOLD_v0.1/examples/scripts/N5_format_distmap2distrr.pl  $fasta_dir/$file  $distfile  $work_dir/$pdbname.dist.rr\n";
	`perl /data/jh7x3/GFOLD_v0.1/examples/scripts/N5_format_distmap2distrr.pl  $fasta_dir/$file  $distfile  $work_dir/$pdbname.dist.rr`;
}
