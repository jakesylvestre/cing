import os
import sys

# Molecule related stuff (former NTmol)
#from constants      import *


cingVersion     = '0.70 alfa'
programName     = 'CING'
programVersion  = cingVersion
header = """
======================================================================================================
|   CING: python NMR/molecule package, version """+cingVersion+""" (c) GWV,AW,JFD 2004-2007    |
======================================================================================================
""" 
footer = """------------------------------------------------------------------------------------------------------
"""
sys.stdout.write( header )

######################################################################################################
# This code is repeated in __init__.py and setup.py please keep it sync-ed
cingPythonCingDir = os.path.split(__file__)[0]
# The path to add to your PYTHONPATH thru the settings script generated by cing.core.setup.py
cingPythonDir = os.path.split(cingPythonCingDir)[0]
# Now a very important variable used through out the code. Even though the
# environment variable CINGROOT is defined the same this is the prefered 
# source for the info within the CING python code.
cingRoot = os.path.split(cingPythonDir)[0]
#printDebug("cingRoot        : " + cingRoot)
######################################################################################################



# dont move these to the top as they become circular.
from cing.Libs.peirceTest import peirceTest
from cing.core.classes import *
from cing.core.database import NTdb
from cing.core.dictionaries import *
from cing.core.importPlugin import importPlugin
from cing.core.molecule import *
from cing.core.parameters import * 