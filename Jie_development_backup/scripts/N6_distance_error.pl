#!/usr/bin/perl -w

if(@ARGV !=2)
{
	die "The number of parameter is not correct\n";
}
$distfile1 = $ARGV[0];
$distfile2 = $ARGV[1];

open(IN,"$distfile1") || die "Failed to open file $distfile1\n";
%dist_hash = {};
while(<IN>)
{
	$line = $_;
	chomp $line;
	
	if(index($line,'distance') <0)
	{
		next;
	}
	
	@tmp = split(/\t/,$line);
	
	$pos1 = $tmp[0];
	$pos2 = $tmp[1];
	$dist = $tmp[3];
	
	$dist_hash{"$pos1-$pos2"} = $dist;
	
}
close IN;


$error_avg = 0;
$error_avg_num = 0;
open(IN,"$distfile2") || die "Failed to open file $distfile2\n";
while(<IN>)
{
	$line = $_;
	chomp $line;
	
	if(index($line,'distance') <0)
	{
		next;
	}
	
	@tmp = split(/\t/,$line);
	
	$pos1 = $tmp[0];
	$pos2 = $tmp[1];
	$dist = $tmp[3];
	
	if(!exists($dist_hash{"$pos1-$pos2"}))
	{
		print "Error: failed to find $pos1-$pos2\n";
	}else{
		$error = abs($dist_hash{"$pos1-$pos2"} - $dist);
		if($error > 0.1)
		{
			print "Checking large error pair $line with error $error\n";
		}
		$error_avg += $error;
		$error_avg_num += 1;
		
	}
	
}
close IN;

$error_avg /= $error_avg_num;

print "absolute error: $error_avg\n\n";