use Cwd 'abs_path';
$num = @ARGV;
if($num != 3)
{
  die "The number of parameter is not correct!\n";
}

$atom_file = $ARGV[0];
$filepath = abs_path($ARGV[1]);
$native_file = abs_path($ARGV[2]);

$pdb_file = "$filepath/$atom_file";
-e $pdb_file || die "Failed to find $pdb_file\n";
-e $native_file || die "Failed to find $native_file\n";

$filename = substr($atom_file,0,index($atom_file,'.pdb'));
$filename =~ s/\./\-/g;

chdir($filepath);
`perl /data/jh7x3/GFOLD_v0.1/examples/N3_superimpose_two_pdb.pl $pdb_file $native_file /data/jh7x3/GFOLD_v0.1/examples/TMalign ${filename}_superimpose.pdb`;
`/data/jh7x3/multicom_github/multicom/tools/pulchra304/pulchra ${filename}_superimpose.pdb`;
`/data/jh7x3/multicom_github/multicom/tools/scwrl4/Scwrl4 -i ${filename}_superimpose.rebuilt.pdb  -o ${filename}_superimpose_rebuilt_scwrl.pdb`;
`python /data/jh7x3/GFOLD_v0.1/examples/pdb_to_png.py ${filename}_superimpose_rebuilt_scwrl.pdb`;
`mv ${filename}_superimpose_rebuilt_scwrl.png ${filename}.png`;



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

open(OUT,">${filename}.eva") || die "Failed to open ${filename}.eva\n";
print OUT "TM-score: $tmscore\n";
print OUT "GDT-TS: $gdttsscore\n";
print OUT "RMSD: $rmsd\n";
close OUT;

`rm ${filename}_superimpose.rebuilt.pdb`;
`rm ${filename}_superimpose.pdb`;
`rm ${filename}_superimpose_rebuilt_scwrl.pdb`;



print "Saved in ${filename}.png, (TM-score: $tmscore   GDT-TS: $gdttsscore  RMSD: $rmsd)\n\n";

