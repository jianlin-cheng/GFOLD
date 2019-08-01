#!/usr/bin/perl -w


my %AA3TO1 = qw/ALA A ASN N CYS C GLN Q HIS H LEU L MET M PRO P THR T TYR Y ARG R ASP D GLU E GLY G ILE I LYS K PHE F SER S TRP W VAL V/;
my %CBATOM = qw/A cb N cb C cb Q cb H cb L cb M cb P cb T cb Y cb R cb D cb E cb G ca I cb K cb F cb S cb W cb V cb/;
my %AA1TO3 = reverse %AA3TO1;

if (@ARGV != 3)
{
	die "need three parameters: option file, sequence file, output dir.\n"; 
}

$fastafile = shift @ARGV;
$distfile = shift @ARGV;
$outputfile = shift @ARGV;

open(IN,"$fastafile") || die "Failed to open directory $fastafile\n";
@content = <IN>;
close IN;
shift @content;
$sequence = shift @content;
chomp $sequence;
open(OUT,">$outputfile") || die "Failed to open directory $outputfile\n";
open(IN,"$distfile") || die "Failed to open directory $distfile\n";
while(<IN>)
{
	$line = $_;
	chomp $line;
	
	@arr = split(/\s+/,$line);
	if(@arr !=3)
	{
		next;
	}else{
		$res1 = $arr[0];
		$res2 = $arr[1];
		$dist = $arr[2];
		
		if(abs($res1 - $res2)<6 or $dist > 16)
		{
			next;
		}
		$type1 = 'CB';
		$type2 = 'CB';
		if(substr($sequence,$res1-1,1) eq 'GLY')
		{
			$type1 = 'CA';
		}
		if(substr($sequence,$res2-1,1) eq 'GLY')
		{
			$type2 = 'CA';
		}
		
		print OUT "$res1-".$AA1TO3{substr($sequence,$res1-1,1)}."-$type1"."\t"."$res2-".$AA1TO3{substr($sequence,$res2-1,1)}."-$type2\tdistance\t$dist\n"
	}
}

close IN;
close OUT;