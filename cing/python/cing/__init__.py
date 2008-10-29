"""
CING: Common Interface for NMR structure Generation

(c) AW,JFD,GWV 2004-2008

"""
import time
import os
import sys
# Version number is a float. Watch out, version 0.100 will be older than 0.99; nope, version 0.100 is long behind us !! (GWV)
cingVersion     = 0.82
programName     = 'CING'
header = """
======================================================================================================
| CING: Common Interface for NMR structure Generation version %-17s AW,JFD,GWV 2004-2008 |
======================================================================================================
""" % (cingVersion)
footer = """------------------------------------------------------------------------------------------------------
"""
usage          = "usage: cing [options]       use -h or --help for listing"

authorList = [  ('Geerten W. Vuister',          'g.vuister@science.ru.nl'),
                ('Jurgen F. Doreleijers',       'jurgend@cmbi.ru.nl'),
                ('Alan Wilter Sousa da Silva',  'alanwilter@gmail.com'),
                ]

verbosityNothing  = 0 # Even errors will be suppressed
verbosityError    = 1 # show only errors
verbosityWarning  = 2 # show errors and warnings
verbosityOutput   = 3 # and regular output DEFAULT
verbosityDetail   = 4 # show more details
verbosityDebug    = 9 # add debugging info (not recommended for casual user)

verbosityDefault  = verbosityOutput
"""How much text is printed to stdout/sstderr streams
Reference to it as cing.verbosity if you want to see non-default behavior
"""
verbosity = verbosityDefault
prefixError     = "ERROR: "
prefixWarning   = "WARNING: "
prefixDetail    = ""
prefixDebug     = "DEBUG: "

#- configure local settings:
#    Create a file localConstants parallel to the setup.py file and add definitions that
#    get imported from the parallel __init__.py code. Just one setting at the moment.
NaNstring = "." # default if not set in localConstants. @UnusedVariable
# When specified differently it should also be reflected in some dictionaries
# so better not.

#try:
#    from localConstants import criteriaDict #@UnresolvedImport
#except:
#    criteriaDict = criteriaDict


CHARS_PER_LINE_OF_PROGRESS = 100
#if verbosity >= verbosityOutput:
#  sys.stdout.write(header)

######################################################################################################
# This code is repeated in __init__.py and setup.py please keep it sync-ed
cingPythonCingDir = os.path.split(__file__)[0]
# The path to add to your PYTHONPATH thru the settings script generated by cing.core.setup.py
cingPythonDir = os.path.split(cingPythonCingDir)[0]
# Now a very important variable used through out the code. Even though the
# environment variable CINGROOT is defined the same this is the preferred
# source for the info within the CING python code.
cingRoot = os.path.split(cingPythonDir)[0]
#NTdebug("cingRoot        : " + cingRoot)
######################################################################################################
cingDirTests           = os.path.join(cingRoot,         "Tests")
cingDirMolmolScripts   = os.path.join(cingRoot,         "scripts", "molmol")
cingDirTestsData       = os.path.join(cingDirTests,     "data")
cingDirScripts         = os.path.join(cingPythonCingDir,"Scripts")
cingDirData            = os.path.join(cingRoot,         "data")
cingDirTmp             = os.path.join("/tmp" , "cing")

try:
    from localConstants import cingDirTmp #@UnresolvedImport
except:
    pass # cingDirTmp was set above already.

if not os.path.exists(cingDirTmp):
    print("Creating a temporary dir for cing: [%s]" % cingDirTmp)
    if os.mkdir(cingDirTmp):
        print("ERROR: Failed to create a temporary dir for cing at: " + cingDirTmp)
        sys.exit(1)

starttime = time.time()

# Define some we are used to use from the toplevel Cing api
# dont move these to the top as they become circular.
# The order within this list is important too. For one thing, pydev extensions code analysis can't
# track imports well if not correct.
#from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils      import NTmessage, NTwarning, NTerror, printf, fprintf, sprintf, NTdict, NTlist, NTvalue, NTpath
from cing.Libs.AwkLike      import AwkLike
from cing.Libs.fpconst      import NaN

from cing.core.constants    import *
from cing.core.classes      import Project
from cing.core.classes      import Peak,              PeakList
from cing.core.classes      import DistanceRestraint, DistanceRestraintList
from cing.core.classes      import DihedralRestraint, DihedralRestraintList
#from cing.core.parameters import *
from cing.core.database     import NTdb
#from cing.core.dictionaries import *
from cing.core.molecule     import Molecule, Chain, Residue, Atom, Coordinate, Resonance, mapMolecules
from cing.core.importPlugin import importPlugin # This imports all plugins
from cing.core.sml          import obj2SML    # This also initializes the SMLhandler methods
from cing.core.sml          import SML2obj    # This also initializes the SMLhandler methods
#from cing.Libs.peirceTest import peirceTest
#from cing.Libs.TypeChecking import *
