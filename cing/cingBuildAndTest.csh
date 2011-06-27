#!/bin/tcsh -e
# Run with absolut path e.g.:
#
#        $CINGROOT/cingBuildAndTest.csh
#
# Used by Jenkins to build and test CING installation automatically on various platforms. 
# Important to use shell setup from user; hence the above no -f option.

cd $0:h

echo "DEBUG: PATH       1: $PATH"
echo "DEBUG: PYTHONPATH 1: $PYTHONPATH"
echo "DEBUG: CLASSPATH  1: $CLASSPATH"

setenv CINGROOT $cwd

# Unset inherited environment
# Alternatively we could use env for this as in:
# env -i PATH=$PATH HOME=$HOME USER=$USER /Users/jd/workspace/xplor-nih-2.27/bin/xplor  
#unsetenv PYTHONPATH
unsetenv CYTHON
unsetenv PYMOL_PATH
unsetenv YASARA_PATH
unsetenv CING_VARS

if ( $?CCPNMR_TOP_DIR ) then
    echo "DEBUG: CCPNMR_TOP_DIR 1: $CCPNMR_TOP_DIR"
else
    echo "DEBUG: CCPNMR_TOP_DIR 1: undefined"
endif

echo "DEBUG: PYTHONPATH 2: $PYTHONPATH"

make clean
make install
source cing.csh
make build_cython

echo "DEBUG: PATH       3  : $PATH"
echo "DEBUG: PYTHONPATH 3  : $PYTHONPATH"
echo "DEBUG: CINGROOT   3  : $CINGROOT"

# Comment out the next line after done testing for it's a security issue.
setenv | sort

#make test

# Just see if it can return a zero status code on starting
cing --noProject

# Just count Source Lines Of Code.
make sloccount
# Still fails on some deps. So listing last in line.
make nose
# Still fails 
make pylint



echo "Done"
