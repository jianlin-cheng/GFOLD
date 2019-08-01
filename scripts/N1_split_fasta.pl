#!/usr/bin/perl -w

if (@ARGV != 2)
{
	die "need three parameters: option file, sequence file, output dir.\n"; 
}

$fasta_seq = shift @ARGV;
$out_dir = shift @ARGV;

if(!(-d $out_dir))
{
	`mkdir $out_dir`;
}
$c=0;
open(IN,"$fasta_seq") || die "Failed to open $fasta_seq\n";
while(<IN>)
{
	$line=$_;
	chomp $line;
	if(substr($line,0,1) eq '>')
	{
		$c++;
		if($c>1)
		{
			print OUT "\n";
			close OUT;
		}
		$name = substr($line,1);
		open(OUT,">$out_dir/$name.ss") || die "Failed to open $out_dir/$name.ss\n";
		print OUT "$line\n";
	}else{
		print OUT "$line\n";
	}

}
close IN;
close OUT;