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
		print OUT "$line\n";
		next;
	}else{
		$res1 = $arr[0];
		$res2 = $arr[1];
		$dist = $arr[2];
		
		if(abs($res1 - $res2)<6 or $dist > 16)
		{
			next;
		}
		
		if($dist ==0)
		{
			$weight = 0;
		}else{
			$weight = sprintf("%.5f",1/$dist);
		}
		
		print OUT "$res1 $res2 0 $dist $weight\n";
		
	}
}

close IN;
close OUT;