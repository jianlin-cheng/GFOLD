#!/usr/bin/perl -w

if(@ARGV !=3)
{
	die "The number of parameter is not correct\n";
}
$fastafile = $ARGV[0];
$resfile = $ARGV[1];
$outfile = $ARGV[2];

my %AA3TO1 = qw/ALA A ASN N CYS C GLN Q HIS H LEU L MET M PRO P THR T TYR Y ARG R ASP D GLU E GLY G ILE I LYS K PHE F SER S TRP W VAL V/;
my %CBATOM = qw/A cb N cb C cb Q cb H cb L cb M cb P cb T cb Y cb R cb D cb E cb G ca I cb K cb F cb S cb W cb V cb/;
my %AA1TO3 = reverse %AA3TO1;

%res_list = fasta2residues_hash($fastafile);

open(OUT,">$outfile") || die "Failed to open file $outfile\n";
open(IN,"$resfile") || die "Failed to open file $resfile\n";
while(<IN>)
{
	$line = $_;
	chomp $line;
	
	if(index($line,'assign') !=0)
	{
		next;
	}
	# assign (resid   5 and name O) (resid   9 and name H) 1.99  0.1  0.1 !helix
	$res1 = substr($line,14,3);
	$res1 =~ s/^\s+|\s+$//g;
	if(!exists($res_list{$res1}))
	{
		die "Wrong res id format\n";
	}
	$res1_name = $res_list{$res1};
	if(!exists($AA1TO3{$res1_name}))
	{
		die "Wrong res name format\n";
	}
	$atom1 = uc(substr($line,27,1));
	$res2 = substr($line,37,3);
	$res2 =~ s/^\s+|\s+$//g;
	if(!exists($res_list{$res2}))
	{
		die "Wrong res id format\n";
	}
	$res2_name = $res_list{$res2};
	if(!exists($AA1TO3{$res2_name}))
	{
		die "Wrong res name format\n";
	}
	$atom2 = uc(substr($line,50,1));
	$info = substr($line,52);
	$info =~ s/^\s+|\s+$//g;
	@arr = split(/\s+/,$info);
	$dist = $arr[0];
	$note = $arr[3];
	if($atom2 eq 'H') ## replace with N
	{
		$atom2 = 'N';
	}
	
	print OUT "$res1-$AA1TO3{$res1_name}-$atom1\t$res2-$AA1TO3{$res2_name}-$atom2\tdistance\t$dist\t$note\n";
	
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

