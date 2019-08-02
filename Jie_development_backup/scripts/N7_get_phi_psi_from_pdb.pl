#!/usr/bin/perl -w

if(@ARGV !=4)
{
	die "The number of parameter is not correct\n";
}
$fastafile = $ARGV[0];
$pdbfile = $ARGV[1];
$dssp = $ARGV[2];
$outfile = $ARGV[3];


open(OUT,">$outfile") || die "Failed to open file $outfile\n";
my %AA3TO1 = qw/ALA A ASN N CYS C GLN Q HIS H LEU L MET M PRO P THR T TYR Y ARG R ASP D GLU E GLY G ILE I LYS K PHE F SER S TRP W VAL V/;
my %CBATOM = qw/A cb N cb C cb Q cb H cb L cb M cb P cb T cb Y cb R cb D cb E cb G ca I cb K cb F cb S cb W cb V cb/;
my %AA1TO3 = reverse %AA3TO1;

@dssp_info = `$dssp $pdbfile`;
%res_list = fasta2residues_hash($fastafile);

$sequence = seq_fasta($fastafile);
chomp $sequence;
$flag = 0;

%pos2res={};
%pos2res_phi={};
%pos2res_psi={};
foreach $line (@dssp_info)
{
	chomp $line;
	
	if ($line =~ /\#([\ ]+)RESIDUE([\000-\256]*)/) {
		$flag = 1;
		next;
	}
	if($flag == 0)
	{
		next;
	}
	
	#print("$line\n");
	$aa=substr($line,13,1); 
	#Seriours bug fix: lower case is for Cysteine in disulfide bond
	#$aa =~ y/a-z/A-Z/;
	$aa =~ y/a-z/C/;
	################################################################
	$temp_string = $line;
	@separate_vec = split(/\s+/, $temp_string);
	$pdb_position = $separate_vec[2]; 
	
	#  106  106   D              0   0  211     -2,-0.2    -1,-0.1    -3,-0.1   -24,-0.0   0.244 360.0 360.0
	#   51   51   G        -     0   0   50     -2,-0.4     2,-0.1     1,-0.4     3,-0.1  -0.021  56.5 -21.3-110.3
	$phi = substr($line,103,6);
	$psi = substr($line,109,6);
	@divided=split(/\s+/,$line);
	$phi =~ s/^\s+|\s+$//g;
	$psi =~ s/^\s+|\s+$//g;
	$x=$divided[$#divided-2];
	$y=$divided[$#divided-1];
	$z=$divided[$#divided];
	
	
	#print "$pdb_position\t$aa\t$phi\t$psi\t$x\t$y\t$z\n";
	
	if(!exists($res_list{$pdb_position}))
	{
		die "Wrong res id format\n";
	}
	$res_name = $res_list{$pdb_position};
	if(!exists($AA1TO3{$res_name}))
	{
		die "Wrong res name format\n";
	}
	
	if($res_list{$pdb_position} ne $aa)
	{
		die "Mismatch amino acid in $pdb_position\n\n";
	}
	
	$pos2res{$pdb_position} = $res_name;
	$pos2res_phi{$pdb_position} = $phi;
	$pos2res_psi{$pdb_position} = $psi;
}


foreach $pdb_position (sort { $a <=> $b } keys %res_list)
{
	$res_name = $res_list{$pdb_position};
	if(!exists($AA1TO3{$res_name}))
	{
		die "Wrong res name format\n";
	}
	
	if($pdb_position == 1)
	{
		$res1_pos = $pdb_position;
		$res2_pos = $pdb_position+1;
		$res1_name = $res_list{$res1_pos};
		$res2_name = $res_list{$res2_pos};
		
		$res1_namefull = $AA1TO3{$res1_name};
		$res2_namefull = $AA1TO3{$res2_name};
		
		#print psi for res 1
		print OUT "$res1_pos-$AA1TO3{$res1_name}-N\t$res1_pos-$AA1TO3{$res1_name}-CA\t$res1_pos-$AA1TO3{$res1_name}-C\t$res2_pos-$AA1TO3{$res2_name}-N\tdihedral\t$pos2res_psi{$res1_pos}\t0.1\t!! psi\n";
	}elsif($pdb_position == length($sequence))
	{
		$res1_pos = $pdb_position-1;
		$res2_pos = $pdb_position;
		$res1_name = $res_list{$res1_pos};
		$res2_name = $res_list{$res2_pos};
		
		$res1_namefull = $AA1TO3{$res1_name};
		$res2_namefull = $AA1TO3{$res2_name};
		
		#print phi for res
		print OUT "$res1_pos-$AA1TO3{$res1_name}-C\t$res2_pos-$AA1TO3{$res2_name}-N\t$res2_pos-$AA1TO3{$res2_name}-CA\t$res2_pos-$AA1TO3{$res2_name}-C\tdihedral\t$pos2res_phi{$res1_pos}\t0.1\t!! phi\n";
	}else{
		$res1_pos = $pdb_position-1;
		$res2_pos = $pdb_position;
		$res3_pos = $pdb_position+1;
		$res1_name = $res_list{$res1_pos};
		$res2_name = $res_list{$res2_pos};
		$res3_name = $res_list{$res3_pos};
		
		$res1_namefull = $AA1TO3{$res1_name};
		$res2_namefull = $AA1TO3{$res2_name};
		$res3_namefull = $AA1TO3{$res3_name};
		
		if(!exists($pos2res_phi{$res1_pos}))
		{
			die "Failed to find phi angle for $res1_pos\n";
		}
		if(!exists($pos2res_phi{$res2_pos}))
		{
			die "Failed to find phi angle for $res2_pos\n";
		}
		if(!exists($pos2res_phi{$res3_pos}))
		{
			die "Failed to find phi angle for $res3_pos\n";
		}
		
		if(!exists($pos2res_psi{$res1_pos}))
		{
			die "Failed to find psi angle for $res1_pos\n";
		}
		if(!exists($pos2res_psi{$res2_pos}))
		{
			die "Failed to find psi angle for $res2_pos\n";
		}
		if(!exists($pos2res_psi{$res3_pos}))
		{
			die "Failed to find psi angle for $res3_pos\n";
		}
		#print phi for res
		print OUT "$res1_pos-$AA1TO3{$res1_name}-C\t$res2_pos-$AA1TO3{$res2_name}-N\t$res2_pos-$AA1TO3{$res2_name}-CA\t$res2_pos-$AA1TO3{$res2_name}-C\tdihedral\t$pos2res_phi{$res1_pos}\t0.1\t!! phi\n";
		#print psi for res
		print OUT "$res2_pos-$AA1TO3{$res2_name}-N\t$res2_pos-$AA1TO3{$res2_name}-CA\t$res2_pos-$AA1TO3{$res2_name}-C\t$res3_pos-$AA1TO3{$res3_name}-N\tdihedral\t$pos2res_psi{$res2_pos}\t0.1\t!! psi\n";
	
	}
}
close OUT;


sub fasta2residues_hash{
	my $file_fasta = shift;
	die "ERROR! Fasta file $file_fasta does not exist!" if not -f $file_fasta;
	my $seq = seq_fasta($file_fasta);
	my %res = ();
	foreach (my $i = 0; $i < length($seq); $i++){
		$res{$i+1} = substr $seq, $i, 1;
	}
	return %res;
}


sub seq_fasta{
	my $file_fasta = shift;
	die "ERROR! Fasta file $file_fasta does not exist!" if not -f $file_fasta;
	my $seq = "";
	open FASTA, $file_fasta or die $!;
	while (<FASTA>){
		next if (substr($_,0,1) eq ">"); 
		chomp $_;
		$_ =~ tr/\r//d; # chomp does not remove \r
		$seq .= $_;
	}
	close FASTA;
	return $seq;
}
