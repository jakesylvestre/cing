"""
CING: Common Interface for NMR structure Generation

Directories:

core                    CING API basics
Database                Nomenclature database files
Libs                    Library functionality including fast c code for cython.
PluginCode              Application specific code for e.g. validation programs.
Scripts                 Loose pieces of python CING code.
STAR                    Python API to STAR.
Talos                   Contains the Talos data.

Files:

CONTENTS.txt            File with directory and file description.
localConstants.py       Settings that can be imported from python/cing/__init__.py
                        NB this file is absent from svn. An example can be adapted
                        from: scripts/cing/localSettingsExample.py
main.py                 The CING program.
setupCing.py            Run to set up environment variables and check installation.
valSets.cfg             Validation settings. Might be moved around.

"""
#import sys
#print sys.path

#try:
#    import nose
#except:
#    print "No nose: that's strange, everyone has to semll something"


from cing.Libs.helper import *

programName     = 'CING'
# Version number is a float. Watch out, version 0.100 will be older than 0.99; nope, version 0.100 is long behind us !! (GWV)
cingVersion     = 0.962
cingRevision    = getSvnRevision()



__version__     = cingVersion # for pydoc
#__date__        = '31 January 2011' # TODO: make this live.
__date__        = '17 October 2014'
__copyright_years__ = '2004-' + __date__.split()[-1] # Never have to update this again...

authorList      = [  ('Geerten W. Vuister',          'gv29@le.ac.uk'),
                     ('T. J. Ragan',                 'tjr22@le.ac.uk'),
                     ('Jurgen F. Doreleijers',       'jurgend@cmbi.ru.nl'),
                     ('Alan Wilter Sousa da Silva',  'alanwilter@gmail.com'),
                  ]
__author__      = '' # for pydoc
for _a in authorList:
    __author__ = __author__ + _a[0] + ' (' + _a[1] + ')    '
__copyright__  = "Copyright (c) %s Protein Biophysics (IMM)/CMBI, Radboud University Nijmegen, The Netherlands"
__copyright__  = "Copyright (c) %s Department of Biochemistry, University of Leicester, UK"
__credits__    = """More info at http://nmr.le.ac.uk/

""" + __copyright__ # TODO: misusing credits for pydoc

versionStr = "%s" % cingVersion
cingRevisionUrl = "http://code.google.com/p/cing/source/detail?r="
if cingRevision:
    versionStr += " (r%d)" % cingRevision

header = \
"======================================================================================================\n" +\
"| CING: Common Interface for NMR structure Generation version %-13s AW,JFD,GWV,TJR %s |\n" % (versionStr, __copyright_years__) +\
"======================================================================================================"

issueListUrl = 'http://code.google.com/p/cing/issues/detail?id='

# Verbosity settings: How much text is printed to stdout/stderr streams
# Follows exact same int codes as Wattos.
# Reference to it as cing.verbosity if you want to see non-default behavior
verbosityNothing  = 0 # Even errors will be suppressed
verbosityError    = 1 # show only errors
verbosityWarning  = 2 # show errors and warnings
verbosityOutput   = 3 # and regular output DEFAULT
verbosityDetail   = 4 # show more details
verbosityDebug    = 9 # add debugging info (not recommended for casual user)

verbosityDefault  = verbosityOutput
verbosity         = verbosityDefault
#verbosity         = verbosityDebug # disable when done debugging e.g. importPlugin.py

#- configure local settings:
#    Create a file localConstants parallel to the setupCing.py file and add definitions that
#    get imported from the parallel __init__.py code. Just one setting at the moment.
NaNstring = "." # default if not set in localConstants. @UnusedVariable
# When specified differently it should also be reflected in some dictionaries
# so better not.


osType = getOsType()
ncpus = detectCPUs() # use all if not specified by -c flag to main cing program.

# Can be reset later when internet is up again
internetConnected = isInternetConnected()
#if verbosity >= verbosityOutput:
#  sys.stdout.write(header)

######################################################################################################
# This code is repeated in __init__.py and setupCing.py please keep it sync-ed
cingPythonCingDir = os.path.split(__file__)[0]
# The path to add to your PYTHONPATH thru the settings script generated by cing.core.setupCing.py
cingPythonDir = os.path.split(cingPythonCingDir)[0]
# Now a very important variable used through out the code. Even though the
# environment variable CINGROOT is defined the same this is the preferred
# source for the info within the CING python code. GWV does not understand why. JFD: because it is
# nice to have a cached version instead of having to query the os.
cingRoot = os.path.split(cingPythonDir)[0]
#nTdebug("cingRoot        : " + cingRoot)
######################################################################################################
cingDirTests           = os.path.join(cingRoot,         "Tests")
cingDirMolmolScripts   = os.path.join(cingRoot,         "scripts", "molmol")
cingDirTestsData       = os.path.join(cingDirTests,     "data")
cingDirScripts         = os.path.join(cingPythonCingDir,"Scripts")
cingDirLibs            = os.path.join(cingPythonCingDir,"Libs")
cingDirData            = os.path.join(cingRoot,         "data")
cingDirTmp             = os.path.join("/tmp" , "cing")

# The TMPDIR environment variable will override the default above but not the one that
# might be defined in localConstants.py.
try:
    from cing.localConstants import cingDirTmp #@UnresolvedImport # pylint: disable=E0611
except:
    if os.environ.has_key("TMPDIR"):
        cingDirTmp = os.path.join(os.environ["TMPDIR"] , "cing")
# end if

if not os.path.exists(cingDirTmp):
#    print("DEBUG: Creating a temporary dir for cing: [%s]" % cingDirTmp)
    if os.mkdir(cingDirTmp):
        print("ERROR: Failed to create a temporary dir for cing at: " + cingDirTmp)
        sys.exit(1)

starttime = time.time()

#---------------------------------------------------------------------------------------------
# Define toplevel CING api
# dont move these to the top as they become circular.
# The order within this list is important too. For one thing, pydev extensions code analysis can't
# track imports well if not correct.
#---------------------------------------------------------------------------------------------

from cing.Libs.NTutils      import *
from cing.Libs.AwkLike      import AwkLike

from cing.core.constants    import *

from cing.core.classes      import Project
from cing.core.classes      import Peak,              PeakList
from cing.core.classes      import DistanceRestraint, DistanceRestraintList
from cing.core.classes      import DihedralRestraint, DihedralRestraintList
from cing.core.classes      import RDCRestraint,      RDCRestraintList

#---------------------------------------------------------------------------------------------
# functional imports: Order matters!
#---------------------------------------------------------------------------------------------

# Try a Yasara import
# GV: We could change this by defining yasaradir in the CING setup
try:
    from yasara import yasaradir #@UnresolvedImport # JFD: why not add the functionality from the plugin ?
    if os.path.exists(yasaradir):
        sys.path.append(os.path.join(yasaradir,'pym'))
        sys.path.append(os.path.join(yasaradir,'plg'))
    else:
        nTcodeerror('Yasara directory "%s" as defined in yasara.py module not found', yasaradir)
        exit(1)
except:
    yasaradir = None
#end try

from cing.core.molecule     import *
from cing.core.importPlugin import importPlugin # This imports all plugins
from cing.core.sml          import obj2SML      # This also initializes the SMLhandler methods
from cing.core.sml          import sML2obj      # This also initializes the SMLhandler methods


from cing.core.database     import NTdb #@Reimport
NTdb._restoreFromSML()                          # This initializes the database
