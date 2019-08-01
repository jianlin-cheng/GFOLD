$num = @ARGV;
if($num <2)
{
  die "The number of parameter is not correct!\n";
}

$pdb_dir = $ARGV[0];
$native_file = $ARGV[1];
$native_image = $ARGV[2];
$native_info = $ARGV[3];

-e $native_file || die "Failed to find $native_file\n";
opendir(DIR,"$pdb_dir") || die "Failed to open directory $pdb_dir\n";
@files = readdir(DIR);
closedir(DIR);


foreach $file (sort @files)
{


	if($file eq '.' or $file eq '..' or substr($file,length($file)-4) ne '.pdb')
	{
		next;
	}
	chomp $file ;
	$pdb_file = "$pdb_dir/$file";
	if(!(-e $pdb_file))
	{
		next;
	}


	$filename = substr($file,0,index($file,'.pdb'));
	$filename =~ s/\./\-/g;

	if(-e "${filename}.png" and -e "${filename}.eva")
	{
		next;
	}

	chdir($pdb_dir);
	`perl /data/jh7x3/GFOLD_v0.1/examples/scripts/N3_superimpose_two_pdb.pl $pdb_file $native_file /data/jh7x3/GFOLD_v0.1/examples/TMalign ${filename}_superimpose.pdb`;
	`/data/jh7x3/multicom_github/multicom/tools/pulchra304/pulchra ${filename}_superimpose.pdb`;
	`/data/jh7x3/multicom_github/multicom/tools/scwrl4/Scwrl4 -i ${filename}_superimpose.rebuilt.pdb  -o ${filename}_superimpose_rebuilt_scwrl.pdb`;
	`python /data/jh7x3/GFOLD_v0.1/examples/scripts/pdb_to_png.py ${filename}_superimpose_rebuilt_scwrl.pdb`;
	open(TMP, ">tmp") || die("Couldn't open file tmp\n");
	my $command1="/data/commons/tools/TMscore ${filename}_superimpose_rebuilt_scwrl.pdb $native_file";
	print "Run $command1 \n";
	my @arr1=`$command1`;

	$tmscore=0;
	$maxscore=0;
	$gdttsscore=0;
	$rmsd=0;

	foreach $ln2 (@arr1){
			chomp($ln2);
			if ("RMSD of  the common residues" eq substr($ln2,0,28)){
					$s1=substr($ln2,index($ln2,"=")+1);
					while (substr($s1,0,1) eq " ") {
							$s1=substr($s1,1);
					}
					$rmsd=1*$s1;
			}
			if ("TM-score" eq substr($ln2,0,8)){
					$s1=substr($ln2,index($ln2,"=")+2);
					$s1=substr($s1,0,index($s1," "));
					$tmscore=1*$s1;
			}
			if ("MaxSub-score" eq substr($ln2,0,12)){
					$s1=substr($ln2,index($ln2,"=")+2);
					$s1=substr($s1,0,index($s1," "));
					$maxscore=1*$s1;
			}
			if ("GDT-TS-score" eq substr($ln2,0,12)){
					$s1=substr($ln2,index($ln2,"=")+2);
					$s1=substr($s1,0,index($s1," "));
					$gdttsscore=1*$s1;
			}
	}

	open(OUT,">>${filename}.eva") || die "Failed to open ${filename}.eva\n";
	print OUT "TM-score: $tmscore\n";
	print OUT "GDT-TS: $gdttsscore\n";
	print OUT "RMSD: $rmsd\n";
	close OUT;
	
	if(defined($native_image) and defined($native_info))
        {
        	`Rscript /data/jh7x3/GFOLD_v0.1/examples/scripts/add_info_in_image.R $native_image $native_info ${filename}_superimpose_rebuilt_scwrl.png ${filename}.eva ${filename}.png`;
        	`rm ${filename}_superimpose_rebuilt_scwrl.png`;
	}else{
                `mv ${filename}_superimpose_rebuilt_scwrl.png ${filename}.png`;
        }
	`rm ${filename}_superimpose.rebuilt.pdb`;
	`rm ${filename}_superimpose.pdb`;
	`rm ${filename}_superimpose_rebuilt_scwrl.pdb`;



	print "Saved in ${filename}.png, (TM-score: $tmscore   GDT-TS: $gdttsscore  RMSD: $rmsd)\n\n";

}
