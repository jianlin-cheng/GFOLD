#!/usr/bin/perl -w
 use FileHandle; # use FileHandles instead of open(),close()
 use Cwd;
 use Cwd 'abs_path';

 # perl /home/jh7x3/GFOLD_v1.1/setup_database.pl
 
######################## !!! customize settings here !!! ############################
#																					#
# Set directory of GFOLD databases and tools								        #

$GFOLD_db_tools_dir = "/data/jh7x3/GFOLD/GFOLD_database_tools/";							        
						        

######################## !!! End of customize settings !!! ##########################

######################## !!! Don't Change the code below##############

$install_dir = getcwd;
$install_dir=abs_path($install_dir);


if(!-s $install_dir)
{
	die "The GFOLD directory ($install_dir) is not existing, please revise the customize settings part inside the configure.pl, set the path as  your unzipped GFOLD directory\n";
}

if ( substr($install_dir, length($install_dir) - 1, 1) ne "/" )
{
        $install_dir .= "/";
}


print "checking whether the configuration file run in the installation folder ...";
$cur_dir = `pwd`;
chomp $cur_dir;
$configure_file = "$cur_dir/configure.pl";
if (! -f $configure_file || $install_dir ne "$cur_dir/")
{
        die "\nPlease check the installation directory setting and run the configure program under the main directory of GFOLD.\n";
}
print " OK!\n";


if(!-d $GFOLD_db_tools_dir)
{
	$status = system("mkdir $GFOLD_db_tools_dir");
	if($status)
	{
		die "Failed to create folder $GFOLD_db_tools_dir\n";
	}
}
$GFOLD_db_tools_dir=abs_path($GFOLD_db_tools_dir);



if ( substr($GFOLD_db_tools_dir, length($GFOLD_db_tools_dir) - 1, 1) ne "/" )
{
        $GFOLD_db_tools_dir .= "/";
}

=pod
if (prompt_yn("GFOLD database will be installed into <$GFOLD_db_tools_dir> ")){

}else{
	die "The installation is cancelled!\n";
}
=cut

print "Start install GFOLD into <$GFOLD_db_tools_dir>\n"; 



chdir($GFOLD_db_tools_dir);

$database_dir = "$GFOLD_db_tools_dir/databases";
$tools_dir = "$GFOLD_db_tools_dir/tools";


if(!-d $database_dir)
{
	$status = system("mkdir $database_dir");
	if($status)
	{
		die "Failed to create folder ($database_dir), check permission or folder path\n";
	}
	`chmod -R 755 $database_dir`;
}
if(!-d $tools_dir)
{ 
	$status = system("mkdir $tools_dir");
	if($status)
	{
		die "Failed to create folder ($tools_dir), check permission or folder path\n";
	}
	`chmod -R 755 $tools_dir`;
}

####### tools compilation 
`mkdir -p $install_dir/installation/GFOLD_manually_install_files`;
if(-e "$install_dir/installation/GFOLD_manually_install_files/P1_install_boost.sh")
{
	`rm $install_dir/installation/GFOLD_manually_install_files/*sh`;
}

##### check gcc version
$check_gcc = system("gcc -dumpversion");
if($check_gcc)
{
	print "Failed to find gcc in system, please check gcc version";
	exit;
}

$gcc_v = `gcc -dumpversion`;
chomp $gcc_v;
@gcc_version = split(/\./,$gcc_v);
if($gcc_version[0] != 4)
{
	print "!!!! Warning: gcc 4.X.X is recommended for boost installation, currently is $gcc_v\n\n";
	sleep(2);
	
}


if($gcc_version[0] ==4 and $gcc_version[1]<6) #gcc 4.6
{
	print "\nGCC $gcc_v is used, install boost-1.38.00\n\n";
	### install boost-1.38 
	open(OUT,">$install_dir/installation/GFOLD_manually_install_files/P1_install_boost.sh") || die "Failed to open file $install_dir/installation/GFOLD_manually_install_files/P1_install_boost.sh\n";
	print OUT "#!/bin/bash -e\n\n";
	print OUT "echo \" Start compile boost (will take ~20 min)\"\n\n";
	print OUT "cd $GFOLD_db_tools_dir/tools\n\n";
	print OUT "cd boost_1_38_0\n\n";
	print OUT "./configure  --prefix=$GFOLD_db_tools_dir/tools/boost_1_38_0\n\n";
	print OUT "make\n\n";
	print OUT "make install\n\n";
	print OUT "echo \"installed\" > $GFOLD_db_tools_dir/tools/boost_1_38_0/install.done\n\n";
	close OUT;


}else{
	print "\nGCC $gcc_v is used, install boost-1.55.00\n\n";
	### install boost-1.55 
	open(OUT,">$install_dir/installation/GFOLD_manually_install_files/P1_install_boost.sh") || die "Failed to open file $install_dir/installation/GFOLD_manually_install_files/P1_install_boost.sh\n";
	print OUT "#!/bin/bash -e\n\n";
	print OUT "echo \" Start compile boost (will take ~20 min)\"\n\n";
	print OUT "cd $GFOLD_db_tools_dir/tools\n\n";
	print OUT "cd boost_1_55_0\n\n";
	print OUT "./bootstrap.sh  --prefix=$GFOLD_db_tools_dir/tools/boost_1_55_0\n\n";
	print OUT "./b2\n\n";
	print OUT "./b2 install\n\n";
	print OUT "echo \"installed\" > $GFOLD_db_tools_dir/tools/boost_1_55_0/install.done\n\n";
	close OUT;	
}


#### install OpenBlas
open(OUT,">$install_dir/installation/GFOLD_manually_install_files/P2_install_OpenBlas.sh") || die "Failed to open file $install_dir/installation/GFOLD_manually_install_files/P2_install_OpenBlas.sh\n";
print OUT "#!/bin/bash -e\n\n";
print OUT "echo \" Start compile OpenBlas (will take ~5 min)\"\n\n";
print OUT "cd $GFOLD_db_tools_dir/tools\n\n";
print OUT "cd OpenBLAS\n\n";
print OUT "#make clean\n\n";
print OUT "make\n\n";
print OUT "make PREFIX=$GFOLD_db_tools_dir/tools/OpenBLAS install\n\n";
print OUT "echo \"installed\" > $GFOLD_db_tools_dir/tools/OpenBLAS/install.done\n\n";
close OUT;



#### install scwrl4

open(OUT,">$install_dir/installation/GFOLD_manually_install_files/P2_install_scwrl4.sh") || die "Failed to open file $install_dir/installation/GFOLD_manually_install_files/P2_install_scwrl4.sh\n";
print OUT "#!/bin/bash -e\n\n";
print OUT "echo \" Start compile freecontact (will take ~1 min)\"\n\n";
print OUT "echo \" \"\n\n";
print OUT "echo \" \"\n\n";
print OUT "echo \" !!!!!!!! Please copy and set the installation path of scwrl to <${GFOLD_db_tools_dir}tools/scwrl4> !!!!!!!! \"\n\n";
print OUT "echo \" \"\n\n";
print OUT "cd $GFOLD_db_tools_dir/tools\n\n";
print OUT "cd scwrl4\n\n";
print OUT "./install_Scwrl4_Linux\n\n";
close OUT;


#### install cmake-2.8.12.2

open(OUT,">$install_dir/installation/GFOLD_manually_install_files/P3_install_cmake_2.8.sh") || die "Failed to open file $install_dir/installation/GFOLD_manually_install_files/P3_install_cmake_2.8.sh\n";
print OUT "#!/bin/bash -e\n\n";
print OUT "echo \" Start compile cmake-2.8 (will take ~5 min)\"\n\n";
print OUT "cd $GFOLD_db_tools_dir/tools\n\n";
print OUT "cd cmake-2.8.12.2/\n\n";
print OUT "./bootstrap --prefix=$GFOLD_db_tools_dir/tools/cmake-2.8.12.2/\n\n";
print OUT "gmake\n\n";
print OUT "make DESTDIR=$GFOLD_db_tools_dir/cmake-2.8.12.2/ install\n\n";
print OUT "echo \"installed\" > $GFOLD_db_tools_dir/tools/cmake-2.8.12.2//install.done\n\n";
close OUT;

#### install cmake3.5.2

open(OUT,">$install_dir/installation/GFOLD_manually_install_files/P4_install_cmake_3.5.sh") || die "Failed to open file $install_dir/installation/GFOLD_manually_install_files/P4_install_cmake_3.5.sh\n";
print OUT "#!/bin/bash -e\n\n";
print OUT "echo \" Start compile cmake-3.5.2 (will take ~5 min)\"\n\n";
print OUT "cd $GFOLD_db_tools_dir/tools\n\n";
print OUT "cd cmake-3.5.2\n\n";
print OUT "./bootstrap --prefix=$GFOLD_db_tools_dir/tools/cmake-3.5.2/\n\n";
print OUT "gmake\n\n";
print OUT "make DESTDIR=$GFOLD_db_tools_dir/cmake-3.5.2/ install\n\n";
print OUT "echo \"installed\" > $GFOLD_db_tools_dir/tools/cmake-3.5.2/install.done\n\n";
close OUT;

#### install blas-3.6.0

open(OUT,">$install_dir/installation/GFOLD_manually_install_files/P5_install_blas-3.6.0.sh") || die "Failed to open file $install_dir/installation/GFOLD_manually_install_files/P5_install_blas-3.6.0.sh\n";
print OUT "#!/bin/bash -e\n\n";
print OUT "echo \" Start compile blas-3.6.0 (will take ~1 min)\"\n\n";
print OUT "cd $GFOLD_db_tools_dir/tools\n\n";
print OUT "cd blas-3.6.0\n\n";
print OUT "make\n\n";
print OUT "mv blas_LINUX.a libblas.a\n\n";
print OUT "echo \"installed\" > $GFOLD_db_tools_dir/tools/blas-3.6.0/install.done\n\n";
close OUT;

#### install lapack-3.4.1

open(OUT,">$install_dir/installation/GFOLD_manually_install_files/P6_install_lapack-3.4.1.sh") || die "Failed to open file $install_dir/installation/GFOLD_manually_install_files/P6_install_blas-lapack-3.4.1.sh\n";
print OUT "#!/bin/bash -e\n\n";
print OUT "echo \" Start compile lapack-3.4.1 (will take ~1 min)\"\n\n";
print OUT "cd $GFOLD_db_tools_dir/tools\n\n";
print OUT "cd lapack-3.4.1\n\n";
print OUT "cp make.inc.example make.inc\n\n";
print OUT "make blaslib  # To generate the Reference BLAS Library\n\n";
print OUT "make\n\n";
print OUT "echo \"installed\" > $GFOLD_db_tools_dir/tools/lapack-3.4.1/install.done\n\n";
close OUT;


#### install zlib-1.2.8

open(OUT,">$install_dir/installation/GFOLD_manually_install_files/P7_install_zlib-1.2.8.sh") || die "Failed to open file $install_dir/installation/GFOLD_manually_install_files/P7_install_blas-zlib-1.2.8.sh\n";
print OUT "#!/bin/bash -e\n\n";
print OUT "echo \" Start compile zlib-1.2.8 (will take ~1 min)\"\n\n";
print OUT "cd $GFOLD_db_tools_dir/tools\n\n";
print OUT "cd zlib-1.2.8\n\n";
print OUT "./configure  --prefix=$GFOLD_db_tools_dir/tools/zlib-1.2.8\n\n";
print OUT "make\n\n";
print OUT "make install\n\n";
print OUT "echo \"installed\" > $GFOLD_db_tools_dir/tools/zlib-1.2.8/install.done\n\n";
close OUT;


#### install hdf5-1.8.16

open(OUT,">$install_dir/installation/GFOLD_manually_install_files/P8_install_hdf5-1.8.16.sh") || die "Failed to open file $install_dir/installation/GFOLD_manually_install_files/P8_install_hdf5-hdf5-1.8.16.sh\n";
print OUT "#!/bin/bash -e\n\n";
print OUT "echo \" Start compile hdf5-1.8.16 (will take ~1 min)\"\n\n";
print OUT "cd $GFOLD_db_tools_dir/tools\n\n";
print OUT "cd hdf5-1.8.16\n\n";
print OUT "./configure --with-zlib=$GFOLD_db_tools_dir/tools/zlib-1.2.8\n\n";
print OUT "make\n\n";
print OUT "make install\n\n";
print OUT "echo \"installed\" > $GFOLD_db_tools_dir/tools/hdf5-1.8.16/install.done\n\n";
close OUT;



#### install gsl-2.1

open(OUT,">$install_dir/installation/GFOLD_manually_install_files/P9_install_gsl-2.1.sh") || die "Failed to open file $install_dir/installation/GFOLD_manually_install_files/P9_install_gsl-gsl-2.1.sh\n";
print OUT "#!/bin/bash -e\n\n";
print OUT "echo \" Start compile gsl-2.1 (will take ~1 min)\"\n\n";
print OUT "cd $GFOLD_db_tools_dir/tools\n\n";
print OUT "cd gsl-2.1\n\n";
print OUT "./configure --prefix=$GFOLD_db_tools_dir/tools/gsl-2.1\n\n";
print OUT "make\n\n";
print OUT "make install\n\n";
print OUT "echo \"installed\" > $GFOLD_db_tools_dir/tools/gsl-2.1/install.done\n\n";
close OUT;



#### install gmp-4.3.2

open(OUT,">$install_dir/installation/GFOLD_manually_install_files/P9_install_gmp-4.3.2.sh") || die "Failed to open file $install_dir/installation/GFOLD_manually_install_files/P9_install_gsl-gmp-4.3.2.sh\n";
print OUT "#!/bin/bash -e\n\n";
print OUT "echo \" Start compile gmp-4.3.2 (will take ~1 min)\"\n\n";
print OUT "cd $GFOLD_db_tools_dir/tools\n\n";
print OUT "cd gmp-4.3.2\n\n";
print OUT "./configure --prefix=$GFOLD_db_tools_dir/tools/gmp-4.3.2\n\n";
print OUT "make\n\n";
print OUT "make install\n\n";
print OUT "echo \"installed\" > $GFOLD_db_tools_dir/tools/gmp-4.3.2/install.done\n\n";
close OUT;




=pod
#### create python virtual environment

open(OUT,">$install_dir/installation/GFOLD_manually_install_files/P4_python_virtual.sh") || die "Failed to open file $install_dir/installation/GFOLD_manually_install_files/P4_python_virtual.sh\n";
print OUT "#!/bin/bash -e\n\n";
print OUT "echo \" Start install python virtual environment (will take ~1 min)\"\n\n";
print OUT "cd $GFOLD_db_tools_dir/tools\n\n";
print OUT "rm -rf python_virtualenv\n\n";
print OUT "virtualenv python_virtualenv\n\n";
print OUT "source $GFOLD_db_tools_dir/tools/python_virtualenv/bin/activate\n\n";
print OUT "pip install --upgrade pip\n\n";
print OUT "pip install --upgrade numpy==1.12.1\n\n";
print OUT "pip install --upgrade theano\n\n";
print OUT "pip install --upgrade h5py\n\n";
print OUT "pip install --upgrade matplotlib\n\n";
print OUT "pip install --upgrade pillow\n\n";
print OUT "NOW=\$(date +\"%m-%d-%Y\")\n\n";
print OUT "echo \"installed\" > $GFOLD_db_tools_dir/tools/python_virtualenv/install.done\n\n";
close OUT;

=cut

=pod
#### (1) Download basic databases
print("#### (1) Download basic databases\n\n");
chdir($database_dir);
$basic_db_list = "";
@basic_db = split(';',$basic_db_list);
foreach $db (@basic_db)
{
	$dbname = substr($db,0,index($db,'.tar.gz'));
	if(-e "$database_dir/$dbname/download.done")
	{
		print "\t$dbname is done!\n";
		next;
	}
	if(-e $db)
	{
		`rm $db`;
	}
	`wget http://sysbio.rnet.missouri.edu/multicom_db_tools/databases/$db`;
	
	if(-e "$db")
	{
		print "\t$db is found, start extracting files......\n\n";
		`tar -zxf $db`;
		`echo 'done' > $dbname/download.done`;
		`rm $db`;
		`chmod -R 755 $dbname`;
	}else{
		die "Failed to download $db from http://sysbio.rnet.missouri.edu/multicom_db_tools/databases, please contact chengji\@missouri.edu\n";
	}
}
=cut
#### (2) Download basic tools
print("\n#### (2) Download basic tools\n\n");

chdir($tools_dir);
$basic_tools_list = "modeller-9.16.tar.gz;boost_1_38_0.tar.gz;boost_1_55_0.tar.gz;OpenBLAS.tar.gz;scwrl4.tar.gz;SCRATCH-1D_1.1.tar.gz;TMscore.tar.gz;cmake-2.8.12.2.tar.gz;cmake-3.5.2.tar.gz;Mocapy++-1.07.tar.gz;blas-3.6.0.tar.gz;lapack-3.4.1.tar.gz;zlib-1.2.8.tar.gz;hdf5-1.8.16.tar.gz;gsl-2.1.tar.gz;gmp-4.3.2.tar.gz;mpfr-2.4.2.tar.gz;CGAL-4.8.1.tar.gz";
@basic_tools = split(';',$basic_tools_list);
foreach $tool (@basic_tools)
{
	$toolname = substr($tool,0,index($tool,'.tar.gz'));
	if(-d "$tools_dir/$toolname")
	{
		if(-e "$tools_dir/$toolname/download.done")
		{
			print "\t$toolname is done!\n";
			next;
		}
	}elsif(-f "$tools_dir/$toolname")
	{
			print "\t$toolname is done!\n";
			next;
	}				
	if(-e $tool)
	{
		`rm $tool`;
	}
	`wget http://sysbio.rnet.missouri.edu/multicom_db_tools/tools/$tool`;
	if(-e "$tool")
	{
		print "\n\t$tool is found, start extracting files......\n\n";
		`tar -zxf $tool`;
		`echo 'done' > $toolname/download.done`;
		`rm $tool`;
		`chmod -R 755 $toolname`;
	}else{
		die "Failed to download $tool from http://sysbio.rnet.missouri.edu/multicom_db_tools/tools, please contact chengji\@missouri.edu\n";
	}
}

=pod
print "#########  (2) Configuring tools\n";

$option_list = "$install_dir/installation/GFOLD_configure_files/GFOLD_tools_list";

if (! -f $option_list)
{
        die "\nOption file $option_list not exists.\n";
}
configure_tools($option_list,'tools',$GFOLD_db_tools_dir);

print "#########  Configuring tools, done\n\n\n";
=cut


$tooldir = $GFOLD_db_tools_dir.'/tools/SCRATCH-1D_1.1/';
if(-d $tooldir)
{
	print "\n#########  Setting up SCRATCH \n";
	chdir $tooldir;
	if(-f 'install.pl')
	{
		$status = system("perl install.pl");
		if($status){
			die "Failed to run perl install.pl \n";
			exit(-1);
		}
	}else{
		die "The configure.pl file for $tooldir doesn't exist, please contact us(Jie Hou: jh7x3\@mail.missouri.edu)\n";
	}
}


my($addr_mod9v16) = $GFOLD_db_tools_dir."/tools/modeller-9.16/bin/mod9.16";
if(-e $addr_mod9v16)
{
	print "\n#########  Setting up MODELLER 9v16 \n";
	if (!-s $addr_mod9v16) {
		die "Please check $addr_mod9v16, you can download the modeller and install it by yourself if the current one in the tool folder is not working well, the key is MODELIRANJE.  please install it to the folder tools/modeller-9.16, with the file mod9v7 in the bin directory\n";
	}

	my($deep_mod9v16) = $GFOLD_db_tools_dir."/tools/modeller-9.16/bin/modeller9v16local";
	$OUT = new FileHandle ">$deep_mod9v16";
	$IN=new FileHandle "$addr_mod9v16";
	while(defined($line=<$IN>))
	{
			chomp($line);
			@ttt = split(/\=/,$line);

			if(@ttt>1 && $ttt[0] eq "MODINSTALL9v16")
			{
					print $OUT "MODINSTALL9v16=\"$GFOLD_db_tools_dir/tools/modeller-9.16\"\n";
			}
			else
			{
					print $OUT $line."\n";
			}
	}
	$IN->close();
	$OUT->close();
	#system("chmod 777 $deep_mod9v16");
	$modeller_conf = $GFOLD_db_tools_dir."/tools/modeller-9.16/modlib/modeller/config.py";
	$OUT = new FileHandle ">$modeller_conf";
	print $OUT "install_dir = r\'$GFOLD_db_tools_dir/tools/modeller-9.16/\'\n";
	print $OUT "license = \'MODELIRANJE\'";
	$OUT->close();
	#system("chmod 777 $modeller_conf");
	system("cp $deep_mod9v16 $addr_mod9v16");
	print "Done\n";
}

####### update prc database 
$prc_db = "$GFOLD_db_tools_dir/databases/prc_db/";
if(-d $prc_db)
{
	opendir(PRCDIR,"$prc_db") || die "Failed to open directory $prc_db\n";
	@prcfiles = readdir(PRCDIR);
	closedir(PRCDIR);
	open(PRCLIB,">$prc_db/prcdb.lib")  || die "Failed to write $prc_db/prcdb.lib\n";
	foreach $prcfile (@prcfiles)
	{
		if($prcfile eq '.' or $prcfile eq '..' or substr($prcfile,length($prcfile)-4) ne '.mod')
		{
			next;
		}
		print PRCLIB "$prc_db/$prcfile\n";
		
	}
	close PRCLIB;
}


$addr_scwrl4 = $GFOLD_db_tools_dir."/tools/scwrl4";
if(-d $addr_scwrl4)
{
	print "\n#########  Setting up scwrl4 \n";
	$addr_scwrl_orig = $addr_scwrl4."/"."Scwrl4.ini";
	$addr_scwrl_back = $addr_scwrl4."/"."Scwrl4.ini.back";
	system("cp $addr_scwrl_orig $addr_scwrl_back");
	@ttt = ();
	$OUT = new FileHandle ">$addr_scwrl_orig";
	$IN=new FileHandle "$addr_scwrl_back";
	while(defined($line=<$IN>))
	{
		chomp($line);
		@ttt = split(/\s+/,$line);
		
		if(@ttt>1 && $ttt[1] eq "FilePath")
		{
			print $OUT "\tFilePath\t=\t$addr_scwrl4/bbDepRotLib.bin\n"; 
		}
		else
		{
			print $OUT $line."\n";
		}
	}
	$IN->close();
	$OUT->close();
	print "Done\n";
}


print "\n#########  Start install tools in folder 'installation/GFOLD_manually_install_files/'\n\n";
### install boost-1.55 
chdir("$install_dir/installation/GFOLD_manually_install_files/");
if($gcc_version[0] ==4 and $gcc_version[1]<6) #gcc 4.6
{
	if(! -e "$GFOLD_db_tools_dir/tools/boost_1_38_0/install.done")
	{
		print "\nStart install boost_1.38, may take ~20 min (sh P1_install_boost.sh &> P1_install_boost.log)\n\n";
		print "\n\t\t\tLog is saved in $install_dir/installation/GFOLD_manually_install_files/P1_install_boost.log\n\n";
		`sh P1_install_boost.sh &> P1_install_boost.log`;
		if(-d "$GFOLD_db_tools_dir/tools/boost_1_55_0")
		{
			`mv $GFOLD_db_tools_dir/tools/boost_1_55_0 $GFOLD_db_tools_dir/tools/boost_1_55_0_original`;
			`ln -s $GFOLD_db_tools_dir/tools/boost_1_38_0 $GFOLD_db_tools_dir/tools/boost_1_55_0`;
		}
	}else{
		print "\nboost-1.38 is installed!\n\n";
	}
}else{
	if(! -e "$GFOLD_db_tools_dir/tools/boost_1_55_0/install.done")
	{
		print "\nStart install boost_1.55, may take ~20 min (sh P1_install_boost.sh &> P1_install_boost.log)\n\n";
		print "\n\t\t\tLog is saved in $install_dir/installation/GFOLD_manually_install_files/P1_install_boost.log\n\n";
		`sh P1_install_boost.sh &> P1_install_boost.log`;
	}else{
		print "\nboost-1.55 is installed!\n\n";
	}
}

#### install OpenBlas

if(! -e "$GFOLD_db_tools_dir/tools/OpenBLAS/install.done")
{
	print "\nStart install OpenBlas, may take ~1 min (sh P2_install_OpenBlas.sh &> P2_install_OpenBlas.log)\n\n";
	print "\n\t\t\tLog is saved in $install_dir/installation/GFOLD_manually_install_files/P2_install_OpenBlas.log\n\n";
	`sh P2_install_OpenBlas.sh &> P2_install_OpenBlas.log`;
}else{
	print "\nOpenBLAS is installed!\n\n";
}

#### install cmake-2.8

if(! -e "$GFOLD_db_tools_dir/tools/cmake-2.8.12.2/install.done")
{
	print "\nStart install cmake-2.8.12.2, may take ~1 min (sh P3_install_cmake_2.8.sh &> P3_install_cmake_2.8.sh.log)\n\n";
	print "\n\t\t\tLog is saved in $install_dir/installation/GFOLD_manually_install_files/P3_install_cmake_2.8.log\n\n";
	`sh P3_install_cmake_2.8.sh &> P3_install_cmake_2.8.log`;
}else{
	print "\ncmake-2.8 is installed!\n\n";
}


#### install cmake_3.5

if(! -e "$GFOLD_db_tools_dir/tools/cmake-3.5.2/install.done")
{
	print "\nStart install cmake-3.5.2, may take ~1 min (sh P4_install_cmake_3.5.sh &> P4_install_cmake_3.5.log)\n\n";
	print "\n\t\t\tLog is saved in $install_dir/installation/GFOLD_manually_install_files/P4_install_cmake_3.5.log\n\n";
	`sh P4_install_cmake_3.5.sh &> P4_install_cmake_3.5.log`;
}else{
	print "\ncmake-3.5 is installed!\n\n";
}


#### install blas-3.6.0

if(! -e "$GFOLD_db_tools_dir/tools/blas-3.6.0/install.done")
{
	print "\nStart install blas-3.6.0, may take ~1 min (sh P5_install_blas-3.6.0.sh &> P5_install_blas-3.6.0.log)\n\n";
	print "\n\t\t\tLog is saved in $install_dir/installation/GFOLD_manually_install_files/P4_install_blas-3.6.0.log\n\n";
	`sh P5_install_blas-3.6.0.sh &> P5_install_blas-3.6.0.log`;
}else{
	print "\nblas-3.6.0 is installed!\n\n";
} 


#### install lapack-3.4.1

if(! -e "$GFOLD_db_tools_dir/tools/lapack-3.4.1/install.done")
{
	print "\nStart install lapack-3.4.1, may take ~1 min (sh P6_install_lapack-3.4.1.sh &> P6_install_lapack-3.4.1.log)\n\n";
	print "\n\t\t\tLog is saved in $install_dir/installation/GFOLD_manually_install_files/P6_install_lapack-3.4.1.log\n\n";
	`sh P6_install_lapack-3.4.1.sh &> P6_install_lapack-3.4.1.log`;
}else{
	print "\nlapack-3.4.1 is installed!\n\n";
} 

#### install zlib-1.2.8

if(! -e "$GFOLD_db_tools_dir/tools/zlib-1.2.8/install.done")
{
	print "\nStart install zlib-1.2.8, may take ~1 min (sh P7_install_zlib-1.2.8.sh &> P7_install_zlib-1.2.8.log)\n\n";
	print "\n\t\t\tLog is saved in $install_dir/installation/GFOLD_manually_install_files/P7_install_zlib-1.2.8.log\n\n";
	`sh P7_install_zlib-1.2.8.sh &> P7_install_zlib-1.2.8.log`;
}else{
	print "\nzlib-1.2.8 is installed!\n\n";
} 

#### install hdf5-1.8.16

if(! -e "$GFOLD_db_tools_dir/tools/hdf5-1.8.16/install.done")
{
	print "\nStart install hdf5-1.8.16, may take ~1 min (sh P8_install_hdf5-1.8.16.sh &> P8_install_hdf5-1.8.16.log)\n\n";
	print "\n\t\t\tLog is saved in $install_dir/installation/GFOLD_manually_install_files/P8_install_hdf5-1.8.16.log\n\n";
	`sh P8_install_hdf5-1.8.16.sh &> P8_install_hdf5-1.8.16.log`;
}else{
	print "\nhdf5-1.8.16 is installed!\n\n";
} 

#### install gsl-2.1

if(! -e "$GFOLD_db_tools_dir/tools/gsl-2.1/install.done")
{
	print "\nStart install gsl-2.1, may take ~1 min (sh P9_install_gsl-2.1.sh &> P9_install_gsl-2.1.log)\n\n";
	print "\n\t\t\tLog is saved in $install_dir/installation/GFOLD_manually_install_files/P9_install_gsl-2.1.log\n\n";
	`sh P9_install_gsl-2.1.sh &> P9_install_gsl-2.1.log`;
}else{
	print "\ngsl-2.1 is installed!\n\n";
} 

#### install gmp-4.3.2

if(! -e "$GFOLD_db_tools_dir/tools/gmp-4.3.2/install.done")
{
	print "\nStart install gmp-4.3.2, may take ~1 min (sh P9_install_gmp-4.3.2.sh &> P9_install_gmp-4.3.2.log)\n\n";
	print "\n\t\t\tLog is saved in $install_dir/installation/GFOLD_manually_install_files/P9_install_gmp-4.3.2.log\n\n";
	`sh P9_install_gmp-4.3.2.sh &> P9_install_gmp-4.3.2.log`;
}else{
	print "\ngmp-4.3.2 is installed!\n\n";
} 



### change permission of SCRATCH, will write tmp file 
if(-d "$GFOLD_db_tools_dir/tools/SCRATCH-1D_1.1")
{
	`chmod -R 777 $GFOLD_db_tools_dir/tools/SCRATCH-1D_1.1`;
}


sub prompt_yn {
  my ($query) = @_;
  my $answer = prompt("$query (Y/N): ");
  return lc($answer) eq 'y';
}
sub prompt {
  my ($query) = @_; # take a prompt string as argument
  local $| = 1; # activate autoflush to immediately show the prompt
  print $query;
  chomp(my $answer = <STDIN>);
  return $answer;
}




sub configure_file{
	my ($option_list,$prefix) = @_;
	open(IN,$option_list) || die "Failed to open file $option_list\n";
	$file_indx=0;
	while(<IN>)
	{
		$file = $_;
		chomp $file;
		if ($file =~ /^$prefix/)
		{
			$option_default = $install_dir.$file.'.default';
			$option_new = $install_dir.$file;
			$file_indx++;
			print "$file_indx: Configuring $option_new\n";
			if (! -f $option_default)
			{
					die "\nOption file $option_default not exists.\n";
			}	
			
			open(IN1,$option_default) || die "Failed to open file $option_default\n";
			open(OUT1,">$option_new") || die "Failed to open file $option_new\n";
			while(<IN1>)
			{
				$line = $_;
				chomp $line;

				if(index($line,'SOFTWARE_PATH')>=0)
				{
					$line =~ s/SOFTWARE_PATH/$install_dir/g;
					$line =~ s/\/\//\//g;
					print OUT1 $line."\n";
				}else{
					print OUT1 $line."\n";
				}
			}
			close IN1;
			close OUT1;
		}
	}
	close IN;
}


sub configure_tools{
	my ($option_list,$prefix,$DBtool_path) = @_;
	open(IN,$option_list) || die "Failed to open file $option_list\n";
	$file_indx=0;
	while(<IN>)
	{
		$file = $_;
		chomp $file;
		if ($file =~ /^$prefix/)
		{
			$option_default = $DBtool_path.$file.'.default';
			$option_new = $DBtool_path.$file;
			$file_indx++;
			print "$file_indx: Configuring $option_new\n";
			if (! -f $option_default)
			{
					next;
					#die "\nOption file $option_default not exists.\n";
			}	
			
			open(IN1,$option_default) || die "Failed to open file $option_default\n";
			open(OUT1,">$option_new") || die "Failed to open file $option_new\n";
			while(<IN1>)
			{
				$line = $_;
				chomp $line;

				if(index($line,'SOFTWARE_PATH')>=0)
				{
					$line =~ s/SOFTWARE_PATH/$DBtool_path/g;
					$line =~ s/\/\//\//g;
					print OUT1 $line."\n";
				}else{
					print OUT1 $line."\n";
				}
			}
			close IN1;
			close OUT1;
		}
	}
	close IN;
}



sub configure_file2{
	my ($option_list,$prefix) = @_;
	open(IN,$option_list) || die "Failed to open file $option_list\n";
	$file_indx=0;
	while(<IN>)
	{
		$file = $_;
		chomp $file;
		if ($file =~ /^$prefix/)
		{
			@tmparr = split('/',$file);
			$filename = pop @tmparr;
			chomp $filename;
			$filepath = join('/',@tmparr);
			$option_default = $install_dir.$filepath.'/.'.$filename.'.default';
			$option_new = $install_dir.$file;
			$file_indx++;
			print "$file_indx: Configuring $option_new\n";
			if (! -f $option_default)
			{
					die "\nOption file $option_default not exists.\n";
			}	
			
			open(IN1,$option_default) || die "Failed to open file $option_default\n";
			open(OUT1,">$option_new") || die "Failed to open file $option_new\n";
			while(<IN1>)
			{
				$line = $_;
				chomp $line;

				if(index($line,'SOFTWARE_PATH')>=0)
				{
					$line =~ s/SOFTWARE_PATH/$install_dir/g;
					$line =~ s/\/\//\//g;
					print OUT1 $line."\n";
				}else{
					print OUT1 $line."\n";
				}
			}
			close IN1;
			close OUT1;
		}
	}
	close IN;
}


