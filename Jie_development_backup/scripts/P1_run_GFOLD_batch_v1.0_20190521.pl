#!/usr/bin/perl -w

if (@ARGV != 6)
{
	die "need three parameters: option file, sequence file, output dir.\n"; 
}

$fasta_dir = shift @ARGV;
$ss_dir = shift @ARGV;
$pdb_dir = shift @ARGV;
$restraints_dir = shift @ARGV;
$work_dir = shift @ARGV;
$filelist = shift @ARGV;

if(!(-d $work_dir))
{
	`mkdir $work_dir`;
}

open(FILE,"$filelist") || die "Failed to open directory $filelist\n";
@files = <FILE>;
close FILE;

foreach $file (sort @files)
{
	chomp $file;
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
	$ssfile = "$ss_dir/$pdbname.ss";
	if(!(-e $ssfile))
	{
		print "Failed to find $ssfile\n";
		next;
	}
	$restraintsfile = "$restraints_dir/$pdbname.restraints";
	if(!(-e $restraintsfile))
	{
		print "Failed to find $restraintsfile\n";
		next;
	}
	
	if(!(-e $pdbfile) and !(-e $ssfile)  and !(-e $restraintsfile) )
	{
		print "Failed to find $pdbfile or $ssfile or $restraintsfile\n";
		next;
	}
	$outdir = "$work_dir/$pdbname";
	if(!(-d $outdir))
	{
		`mkdir $outdir`;
	}

	if(-e "$outdir/$pdbname/${pdbname}_GFOLD.pdb")
	{
		print "$outdir/$pdbname/${pdbname}_GFOLD.pdb already generated\n";
		#next;
	}
	
	$start_run = time();
	
	print "python /data/jh7x3/GFOLD_v0.1/examples/Sucessed_cases_codes_backup/GFOLD_v0.9_1BYR-A.py.20190521_v3 --target $pdbname  --fasta $fasta_dir/$file --ss $ssfile  --hbond 1 --restraints $restraintsfile --type CB --distdev 0.1  --epoch 10  --cgstep 100  --dir  $outdir --sep 1\n";
	system("python /data/jh7x3/GFOLD_v0.1/examples/Sucessed_cases_codes_backup/GFOLD_v0.9_1BYR-A.py.20190521_v3  --target $pdbname  --fasta $fasta_dir/$file --ss $ssfile  --hbond 1 --restraints $restraintsfile --type CB --distdev 0.1 --epoch 10  --cgstep 100  --dir  $outdir --sep 1");
	
	$end_run = time();
	$run_time = $end_run - $start_run;
	

	if(-e "$outdir/$pdbname/${pdbname}_GFOLD.pdb")
	{
		print "$outdir/$pdbname/${pdbname}_GFOLD.pdb already generated\n";
		`echo $run_time > $outdir/folding.done`;
	}else{
		print "$outdir/$pdbname/${pdbname}_GFOLD.pdb failed to be generated\n";
	}
	
}
