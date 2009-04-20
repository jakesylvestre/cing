"""
    Whatif Module
    First version: gv June 3, 2007
    Second version by jfd.

    Adapted GWV September 2008: worked around parse error;
"""
# Fix these strings so we can get some automated code checking by pydev extensions.
# Also, we want to put these defs on top before the imports to prevent cycle in
# look up.
from cing import issueListUrl
from cing.Libs.AwkLike import AwkLike
from cing.Libs.NTmoleculePlot import KEY_LIST_STR
from cing.Libs.NTmoleculePlot import MoleculePlotSet
from cing.Libs.NTmoleculePlot import YLABEL_STR
from cing.Libs.NTutils import ExecuteProgram
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTdetail
from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTwarning
from cing.Libs.NTutils import getDeepByKeysOrAttributes
from cing.Libs.NTutils import setDeepByKeys
from cing.Libs.NTutils import sprintf
from cing.Libs.NTutils import val2Str
from cing.PluginCode.required.reqWhatif import ACCLST_STR
from cing.PluginCode.required.reqWhatif import ANGCHK_STR
from cing.PluginCode.required.reqWhatif import BBCCHK_STR
from cing.PluginCode.required.reqWhatif import BMPCHK_STR
from cing.PluginCode.required.reqWhatif import BNDCHK_STR
from cing.PluginCode.required.reqWhatif import C12CHK_STR
from cing.PluginCode.required.reqWhatif import CHECK_ID_STR
from cing.PluginCode.required.reqWhatif import CHICHK_STR
from cing.PluginCode.required.reqWhatif import FLPCHK_STR
from cing.PluginCode.required.reqWhatif import INOCHK_STR
from cing.PluginCode.required.reqWhatif import LEVEL_STR
from cing.PluginCode.required.reqWhatif import LOC_ID_STR
from cing.PluginCode.required.reqWhatif import NQACHK_STR
from cing.PluginCode.required.reqWhatif import OMECHK_STR
from cing.PluginCode.required.reqWhatif import PL2CHK_STR
from cing.PluginCode.required.reqWhatif import PL3CHK_STR
from cing.PluginCode.required.reqWhatif import PLNCHK_STR
from cing.PluginCode.required.reqWhatif import QUACHK_STR
from cing.PluginCode.required.reqWhatif import QUAL_LIST_STR
from cing.PluginCode.required.reqWhatif import RAMCHK_STR
from cing.PluginCode.required.reqWhatif import ROTCHK_STR
from cing.PluginCode.required.reqWhatif import TEXT_STR
from cing.PluginCode.required.reqWhatif import TYPE_STR
from cing.PluginCode.required.reqWhatif import VALUE_LIST_STR
from cing.PluginCode.required.reqWhatif import WHATIF_STR
from cing.PluginCode.required.reqWhatif import wiPlotList
from cing.core.constants import IUPAC
from cing.core.parameters import cingPaths
from cing.setup import PLEASE_ADD_EXECUTABLE_HERE
from glob import glob
from shutil import copy
from string import upper
from cing.PluginCode.required.reqWhatif import HNDCHK_STR
import os
import time

class Whatif( NTdict ):
    """
    Class to use WHAT IF checks.

    Whatif.checks:                  NTlist instance of individual parsed checks
    Whatif.molSpecificChecks:       NTlist instance of those check pertaining to
                                    molecules; i.e Level : MOLECULE. Not implemented in What If yet.
    Whatif.residueSpecificChecks:   NTlist instance of those check pertaining to
                                    residues; i.e Level : RESIDUE.
    Whatif.atomSpecificChecks:      NTlist instance of those check pertaining to
                                    atoms; i.e Level : ATOM.
    Whatif.residues:                NTdict instance with results of all
                                    residueSpecificChecks, sorted by key residue.
    Whatif.atoms:                   NTdict instance with results of all
                                    atomSpecificChecks sorted by key atom.

    Individual checks:
    NTdict instances with keys pointing to NTlist instances;

    All file references relative to rootPath ('.' by default) using the .path()
    method.
    """
    #define some more user friendly names
    # List of defs at:
    # http://www.yasara.org/pdbfinder_file.py.txt
    # http://swift.cmbi.ru.nl/whatif/html/chap23.html
    # All are in text record of file to be parsed so they're kind of redundant.
    # Third element is optional short name suitable for labeling a y-axis.
    nameDefs =[
                ('ACCLST', 'Relative accessibility',                                    'Rel. accessibility'),
                ('ALTATM', 'Amino acids inside ligands check/Attached group check',     'Amino acids inside ligands check/Attached group check'),
                ('ANGCHK', 'Angles',                                                    'Bond angle'),
                ('BA2CHK', 'Hydrogen bond acceptors', 'Hydrogen bond acceptors'),
                ('BBCCHK', 'Backbone normality',                                        'Backbone normality' ),
                ('BH2CHK', 'Hydrogen bond donors', 'Hydrogen bond donors'),
                ('BMPCHK', 'Bumps',                                                     'Summed bumps'),
                ('BNDCHK', 'Bond lengths',                                              'Bond lengths'),
                ('BVALST', 'B-Factors', 'B-Factors'),
                ('C12CHK', 'Chi-1 chi-2',                                               'Chi 1/2. Z'),
                ('CHICHK', 'Torsions',                                                  'Aver. torsions Z.'),
                ('CCOCHK', 'Inter-chain connection check', 'Inter-chain connection check'),
                ('CHICHK', 'Torsion angle check', 'Torsion angle check'),
                ('DUNCHK', 'Duplicate atom names in ligands', 'Duplicate atom names in ligands'),
                ('EXTO2',  'Test for extra OXTs', 'Test for extra OXTs'),
                ('FLPCHK', 'Peptide flip',                                              'Peptide flip'),
                ('H2OCHK',  'Water check', 'Water check'),
                ('H2OHBO',  'Water Hydrogen bond', 'Water Hydrogen bond'),
                ('HNDCHK', 'Chirality', 'Chirality'),
                ('HNQCHK', 'Flip HIS GLN ASN hydrogen-bonds', 'Flip HIS GLN ASN hydrogen-bonds'),
                ('INOCHK', 'Accessibility',                                             'Accessibility Z.'),
                ('MISCHK', 'Missing atoms', 'Missing atoms'),
                ('MO2CHK', 'Missing C-terminal oxygen atoms', 'Missing C-terminal oxygen atoms'),
                ('NAMCHK', 'Atom names', 'Atom names'),
                ('NQACHK', 'Qualities',                                                 'New quality'),
                ('NTCHK',  'Acid group conformation check',                             'COOH check'),
                ('OMECHK', 'Omega angle restraints',                                   'Omega check'),                
                ('PC2CHK', 'Proline puckers', 'Proline puckers'),
                ('PDBLST', 'List of residues', 'List of residues'),
                ('PL2CHK', 'Connections to aromatic rings',                             'Plan. to aromatic'),
                ('PL3CHK', 'Side chain planarity with hydrogens attached',              'NA planarity'),
                ('PLNCHK', 'Protein side chain planarities',                            'Protein SC planarity'),
                ('PRECHK', 'Missing backbone atoms.', 'Missing backbone atoms.'),
                ('PUCCHK', 'Ring puckering in Prolines', 'Ring puckering in Prolines'),
                ('QUACHK', 'Directional Atomic Contact Analysis',                       'Packing quality'),
                ('RAMCHK', 'Ramachandran',                                              'Ramachandr.' ),
                ('ROTCHK', 'Rotamers',                                                  'Rotamer normality'),
                ('SCOLST', 'List of symmetry contacts', 'List of symmetry contacts'),
                ('TO2CHK', 'Missing C-terminal groups', 'Missing C-terminal groups'),
                ('TOPPOS', 'Ligand without know topology', 'Ligand without know topology'),
                ('WGTCHK', 'Atomic occupancy check', 'Atomic occupancy check'),
                ('Hand',   '(Pro-)chirality or handness check'),                                        
                ('AAINLI',   'Unknown check', 'Unknown check'),
                ('ATHYBO',   'Unknown check', 'Unknown check'),
                ('BBAMIS',   'Unknown check', 'Unknown check'),
                ('TORCHK',   'Unknown check', 'Unknown check')
                 ]

#              'Bond max Z',
    DEFAULT_RESIDUE_POOR_SCORES = {}
    DEFAULT_RESIDUE_BAD_SCORES = {}

    DEFAULT_RESIDUE_BAD_SCORES[  RAMCHK_STR ] =  -1.3
    DEFAULT_RESIDUE_POOR_SCORES[ RAMCHK_STR ] =  -1.0 # Guessing on basis of 1ai0, 1brv

    DEFAULT_RESIDUE_BAD_SCORES[  BBCCHK_STR ] =    3.0
    DEFAULT_RESIDUE_POOR_SCORES[ BBCCHK_STR ] =   10.0 # Guessing on basis of 1ai0, 1brv

    DEFAULT_RESIDUE_BAD_SCORES[  C12CHK_STR ] =  -1.2
    DEFAULT_RESIDUE_POOR_SCORES[ C12CHK_STR ] =  -0.9 # Guessing on basis of 1ai0, 1brv

    NUMBER_RESIDUES_PER_SECONDS = 7 # Was 13 before.

    debugCheck = 'BNDCHK'
    # Create a dictionary for fast lookup.
    nameDict = NTdict()
    shortNameDict = NTdict()
    for row in nameDefs:
        n1 = row[0]
        nameDict[n1] = row[1]
        if len(row) >= 3:
            shortNameDict[n1] = row[2]
    nameDict.keysformat()
    recordKeyWordsToIgnore = { # Using a dictionary for fast key checks below.
                              "Bad":None,
                              "Date":None,
                              "DocURL":None,
                              "ID":None,
                              "LText":None,
                              "Poor":None,
                              "Program":None,
                              "Text":None,
                              "Version":None
                              }
#    recordKeyWordsToIgnore.append( "IGNORE" ) # Added by JFD


    scriptBegin = """
# CING generated What If (WI) script
# Set WI options
# Truncating errors in a PDBOUT table
SETWIF 593 100
# Should Q atoms be considered hydrogen atoms?
SETWIF 1505 1
# Read all models
#SETWIF 847 1
# Not adding C-terminal O if missing
SETWIF 1071 1
# We have an NMR structure (curiously set to No here)
SETWIF 1503 0
# IUPAC atom nomenclature
SETWIF 142 1
# Cutoff for reporting in the INP* routines (*100)
SETWIF 143 400
# Skip generation of EPS files in order to speed up this ordeal.
#SETWIF 473 1
# General debug flag
# Should prevent problems such as:
# > 1b9q and many others: broken backbone/ERROR reading DSSP file
# > 1ehj Zero length in torsion calculation
SETWIF 1012 0
"""
    scriptPerModel = """
# Read the one model
%fulchk
$pdb_file
xxx

$mv check.db check_$modelNumberString.db

# Initialize the soup
%inisou

# Keep the line above empty.
"""

    scriptQuit = """
fullstop y
"""
# Run whatif with the script



    def __init__( self, rootPath = '.', molecule = None, **kwds ):
        NTdict.__init__( self, __CLASS__ = WHATIF_STR, **kwds )
        self.checks                = None
        self.molSpecificChecks     = None
        self.residueSpecificChecks = None
        self.atomSpecificChecks    = None
        self.residues              = None
        self.atoms                 = None
        self.molecule              = molecule
        self.rootPath              = rootPath
    #end def

    def path( self, *args ):
        """Return path relative to rootPath """
        return os.path.join( self.rootPath, *args )
    #end def

#    def _dictDictList( self, theDict, name, key ):
#        """
#            Internal routine that returns a NTlist instance for theDict[name][key].
#            Also put in translated key.
#        """
#        d = theDict.setdefault( name, NTdict() )
#        d[self.nameDict[key]] = d.setdefault( key, NTlist() )

    def _processSummary( self, project, fileName='pdbout.txt' ):
        """Parse fileName. Storing the check data according to each model.
           Return None on success or True on error.
           """
        if not os.path.exists(fileName):
            NTerror('Whatif._processSummary: file "%s" not found.', fileName)
            return True

        modelIdx = -1
        for line in AwkLike( fileName, minNF = 2, separator=':' ):
            l = line.dollar[0]
            NTdebug("Read line: "+l)
#            NTdebug("DEBUG: read line dollar 1: [%s]" % line.dollar[1])
#            NTdebug("DEBUG: read line dollar 2: [%s]" % line.dollar[2])
            
            if l.find( 'Summary report for users of a structure') > 0:
                NTdebug('Found summary report and increasing model idx: %d' % modelIdx) 
                modelIdx += 1
                continue
            
            checkId = None
            if l.startswith( '  1st generation packing quality'):
                checkId = QUACHK_STR
            if l.startswith( '  2nd generation packing quality'):
                checkId = QUACHK_STR
            if l.startswith( '  Ramachandran plot appearance'):
                checkId = RAMCHK_STR
            if l.startswith( '  chi-1/chi-2 rotamer normality'):
                checkId = ROTCHK_STR
            if l.startswith( '  Backbone conformation'):
                checkId = BBCCHK_STR
# Second part.                
            if l.startswith( '  Bond lengths'):
                checkId = BNDCHK_STR
            if l.startswith( '  Bond angles'):
                checkId = ANGCHK_STR
            if l.startswith( '  Omega angle restraints'):
                checkId = OMECHK_STR 
            if l.startswith( '  Side chain planarity'):
                checkId = PLNCHK_STR
            if l.startswith( '  Improper dihedral distribution'):
                checkId = HNDCHK_STR
            if l.startswith( '  Inside/Outside distribution'):
                checkId = INOCHK_STR
            
            if not checkId:
#                NTdebug("Failed to find any specific check, continueing to look")
                continue
                        
            valueStringList  = line.dollar[2].strip().split()
            NTdebug("valueStringList: %s" % valueStringList)
            if not valueStringList:
                NTerror("Failed to get valueStringList from line: [%s]"%line)
                return True                    
            value = float(valueStringList[0])
                       
            NTdebug('modelIdx: %d' % modelIdx) 
            if modelIdx < 0:
                NTerror('Failed to have increased model idx at least once')
                return True 
            if modelIdx == 0:
                NTdebug('Setting empty NTlist for first time for check: %s' % checkId) 
                setDeepByKeys( self.molecule, NTlist(), WHATIF_STR, checkId)
            ensembleValueList = getDeepByKeysOrAttributes( self.molecule, WHATIF_STR, checkId)
            if ensembleValueList == None:
                NTerror("Failed to get ensembleValueList for checkId: %s" % checkId)
                return True            
            ensembleValueList.append(value)
            NTdebug('ensembleValueList now: %s' % ensembleValueList)
        # end for line
        
        
        summaryCheckIdList = [ QUACHK_STR, NQACHK_STR, RAMCHK_STR, ROTCHK_STR, BBCCHK_STR, # First part
                               BNDCHK_STR, ANGCHK_STR, OMECHK_STR, PLNCHK_STR, HNDCHK_STR, INOCHK_STR  ] # second part.
        summaryCheckIdMandatoryList = [ BNDCHK_STR, ANGCHK_STR ]
        valueList = [ ]
        qualList = [ ]
        for checkId in summaryCheckIdList:
            ensembleValueList = getDeepByKeysOrAttributes( self.molecule, WHATIF_STR, checkId)
            if not ensembleValueList:
                msg = "empty ensembleValueList for checkId %s" % checkId 
                if checkId in summaryCheckIdMandatoryList:
                    NTwarning(msg)
                else:
                    NTdebug(msg)
                ensembleValueList = NTlist()
            # end if
            ensembleValueList.average()
            valueList.append(ensembleValueList)
            NTdebug('ensembleValueList found: %s' % valueList[-1])
            qualList.append( '' )
            # Add comments like done in What If's pdbout.f:

            if checkId == QUACHK_STR:
                if ensembleValueList.av < -3.0:
                    qualList[-1] = '(bad)'
                elif ensembleValueList.av < -2.0:
                    qualList[-1] = '(poor)'
            if checkId == NQACHK_STR:
                if ensembleValueList.av < -4.0:
                    qualList[-1] = '(bad)'
                elif ensembleValueList.av < -3.0:
                    qualList[-1] = '(poor)'
            if checkId == RAMCHK_STR:
                if ensembleValueList.av < -4.0:
                    qualList[-1] = '(bad)'
                elif ensembleValueList.av < -3.0:
                    qualList[-1] = '(poor)'            
            if checkId == ROTCHK_STR:
                if ensembleValueList.av < -4.0:
                    qualList[-1] = '(bad)'
                elif ensembleValueList.av < -3.0:
                    qualList[-1] = '(poor)'
            if checkId == BBCCHK_STR:
                if ensembleValueList.av < -4.0:
                    qualList[-1] = '(bad)'
                elif ensembleValueList.av < -3.0:
                    qualList[-1] = '(poor)'
            # 2nd part
            if checkId == BNDCHK_STR:
                if ensembleValueList.av < 0.666:
                    qualList[-1] = '(tight)'
                elif ensembleValueList.av > 1.5:
                    qualList[-1] = '(loose)'
            elif checkId == ANGCHK_STR:
                if ensembleValueList.av < 0.666:
                    qualList[-1] = '(tight)'
                elif ensembleValueList.av > 1.5:
                    qualList[-1] = '(loose)'
            elif checkId == OMECHK_STR:
                if ensembleValueList.av > 7.0:
                    qualList[-1] = '(loose)'
                elif ensembleValueList.av < 4.0:
                    qualList[-1] = '(tight)'
            if checkId == PLNCHK_STR:
                if ensembleValueList.av < 0.666:
                    qualList[-1] = '(tight)'
                elif ensembleValueList.av > 2.0:
                    qualList[-1] = '(loose)'
            if checkId == HNDCHK_STR:
                if ensembleValueList.av > 0.0 and ensembleValueList.av > 1.5:
                    qualList[-1] = '(loose)'
            if checkId == INOCHK_STR:
                if ensembleValueList.av > 1.16:
                    qualList[-1] = '(unusual)'
        # end for
        fmt = "%.3f"
        spaceCount = 7
        summary = """
    Summary report for users of a structure
    This is an overall summary of the quality of the structure as
    compared with current reliable structures. This summary is most
    useful for biologists seeking a good structure to use for modelling
    calculations.
    
    The second part of the table mostly gives an impression of how well
    the model conforms to common refinement constraint values. The
    first part of the table shows a number of constraint-independent
    quality indicators.
    
    The standard deviation shows the variation over models in the ensemble
    where appropriate.
     
     Structure Z-scores, positive is better than average:
      1st generation packing quality :  %s +/- %s %s
      2nd generation packing quality :  %s +/- %s %s
      Ramachandran plot appearance   :  %s +/- %s %s
      chi-1/chi-2 rotamer normality  :  %s +/- %s %s
      Backbone conformation          :  %s +/- %s %s

     RMS Z-scores, should be close to 1.0:
      Bond lengths                   :   %s +/- %s %s
      Bond angles                    :   %s +/- %s %s
      Omega angle restraints         :   %s +/- %s %s
      Side chain planarity           :   %s +/- %s %s
      Improper dihedral distribution :   %s +/- %s %s
      Inside/Outside distribution    :   %s +/- %s %s
      
        """ % (val2Str(valueList[0].av,fmt, spaceCount),val2Str(valueList[0].sd,fmt, spaceCount), qualList[0],
               val2Str(valueList[1].av,fmt, spaceCount),val2Str(valueList[1].sd,fmt, spaceCount), qualList[1],
               val2Str(valueList[2].av,fmt, spaceCount),val2Str(valueList[2].sd,fmt, spaceCount), qualList[2],
               val2Str(valueList[3].av,fmt, spaceCount),val2Str(valueList[3].sd,fmt, spaceCount), qualList[3],
               val2Str(valueList[4].av,fmt, spaceCount),val2Str(valueList[4].sd,fmt, spaceCount), qualList[4],
               val2Str(valueList[5].av,fmt, spaceCount),val2Str(valueList[5].sd,fmt, spaceCount), qualList[5],
               val2Str(valueList[6].av,fmt, spaceCount),val2Str(valueList[6].sd,fmt, spaceCount), qualList[6],
               val2Str(valueList[7].av,fmt, spaceCount),val2Str(valueList[7].sd,fmt, spaceCount), qualList[7],
               val2Str(valueList[8].av,fmt, spaceCount),val2Str(valueList[8].sd,fmt, spaceCount), qualList[8],
               val2Str(valueList[9].av,fmt, spaceCount),val2Str(valueList[9].sd,fmt, spaceCount), qualList[9],
               val2Str(valueList[10].av,fmt, spaceCount),val2Str(valueList[10].sd,fmt, spaceCount), qualList[10]
               )
                    
        if setDeepByKeys(self.molecule, summary, 'wiSummary'):# Hacked because should be another wi level in between.
            NTerror( 'Failed to set WI summary' )
            return True
        
        project.whatifStatus.parsed = True
        project.whatifStatus.keysformat()
            
                            
        
    def _parseCheckdb( self, modelCheckDbFileName, model ):
        """Parse check_001.db etc. Generate references to
           all checks. Storing the check data according to residue and atom.
           Return self on success or True on error.

        Example of parsed data structure:
        E.g. check can have attributes like:
        [                                          # checks
            {                                      # curCheck
            "checkID":  "BNDCHK"
            "level":    "RESIDUE"
            "type":     "FLOAT"
            "locId": {                             # curLocDic
                "'A- 189-GLU'"                     # curLocId
                    : {                            # curListDic
                    "valeList": [ 0.009, 0.100 ]
                    "qualList": ["POOR", "GOOD" ]
                    },
                "'A- 188-ILE'": {
                    "valeList": [ 0.01, 0.200 ]
                    "qualList": ["POOR", "GOOD" ]
                    }}},]
           """

        # Parser uses sense of current items as per below.
        curModelId = model
        curCheck   = None # Can be used to skip ahead.
        curLocId   = None
        curLocDic  = None
        curListDic = None
        isTypeFloat= False

        if not self.checks: # This will be called multiple times so don't overwrite.
            self.checks = NTlist()

        if not os.path.exists(modelCheckDbFileName):
            NTdebug('Whatif._parseCheckdb: file "%s" not found.', modelCheckDbFileName)
            return True
        for line in AwkLike( modelCheckDbFileName, minNF = 3 ):
#            NTdebug("DEBUG: read: "+line.dollar[0])
            if line.dollar[2] != ':':
                NTwarning("The line below was unexpectedly not parsed, expected second field to be a semicolon.")
                NTwarning(line.dollar[0])

#            Split a line of the check.db file
            a      = line.dollar[0].split(':')
            key    = a[0].strip()
            value  = a[1].strip()

            if self.recordKeyWordsToIgnore.has_key(key):
                continue

            if key == 'CheckID':
                curCheck = None
                checkID = value # local var within this 'if' statement.
#                NTdebug("found check ID: " + checkID)
                if not self.nameDict.has_key( checkID ):
                    NTwarning("Whatif._parseCheckdb: Skipping an unknown CheckID: "+checkID)
                    continue
#                if self.debugCheck != checkID:
##                    NTdebug("Skipping a check not to be debugged: "+checkID)
#                    continue
                isTypeFloat = False

                if self.has_key( checkID ):
                    curCheck = self.get(checkID)
                else:
                    curCheck = NTdict()
                    self.checks.append( curCheck )
                    curCheck[CHECK_ID_STR] = checkID
                    self[ checkID ] = curCheck
#                    NTdebug("Appended check: "+checkID)
                # Set the curLocDic in case of the first time otherwise get.
                curLocDic = curCheck.setdefault(LOC_ID_STR, NTdict())
                continue
            if not curCheck: # First pick up a check.
                continue

#            NTdebug("found key, value: [" + key + "] , [" + value + "]")
            if key == "Text":
                curCheck[TEXT_STR] = value
                continue
            if key == "Level":
                curCheck[LEVEL_STR] = upper(value) # check Hand has level "Residue" which should be upped.
                continue
            if key == "Type":
                curCheck[TYPE_STR] = value
                if value == "FLOAT":
                    isTypeFloat = True
                continue
            if key == "Name":
                curLocId = value
#                NTdebug("curLocId: "+curLocId )
                curListDic = curLocDic.setdefault(curLocId, NTdict())
                continue

#           Only allow values so lines like:
#            #    Value :  1.000
#            #    Qual  : BAD
            if key == "Value":
                keyWord = VALUE_LIST_STR
            elif  key == "Qual":
                keyWord = QUAL_LIST_STR
            else:
                NTerror( "Whatif._parseCheckdb: Expected key to be Value or Qual but found key, value pair: [%s] [%s]" % ( key, value ))
                return None

            if not curListDic.has_key( keyWord ):
                itemNTlist = NTlist()
                curListDic[ keyWord ] = itemNTlist
                for _dummy in range(self.molecule.modelCount): # Shorter code for these 2 lines please JFD.
                    itemNTlist.append(None)
#                NTdebug("b initialized with Nones: itemNTlist: %r", itemNTlist )
            else:
                itemNTlist = curListDic[ keyWord ]
#            NTdebug("a itemNTlist: "+`itemNTlist` )

            if isTypeFloat:
                itemNTlist[curModelId] = float(value)
            else:
                itemNTlist[curModelId] = value
#            NTdebug("c itemNTlist: "+`itemNTlist` )
#            NTdebug("For key       : "+key)
#            NTdebug("For modelID   : "+`model`)
#            NTdebug("For value     : "+value)
#            NTdebug("For check     : "+`curCheck`)
#            NTdebug("For keyed list: "+`curCheck[key]`)
#            NTdebug("For stored key: "+`curCheck[key][modelId]`)
        #end for each line.

    def _processCheckdb( self   ):
        """
        Put parsed data of all models into CING data model
        Return None for success

        Example of processed data structure attached to say a residue:
            "whatif": {
                "ANGCHK": {
                    "valeList": [ 0.009, 0.100 ],
                    "qualList": ["POOR", "GOOD" ]},
                "BNDCHK": {
                    "valeList": [ 0.009, 0.100 ],
                    }}"""

        NTdetail("==> Processing the WHATIF results into CING data model")
        # Assemble the atom, residue and molecule specific checks
        # set the formats of each check easy printing
#        self.molecule.setAllChildrenByKey( WHATIF_STR, None)
        self.molecule.whatif = self # is self and that's asking for luggage
        # Later

#        self.molSpecificChecks     = NTlist()
        self.residueSpecificChecks = NTlist()
        self.atomSpecificChecks    = NTlist()

#        self.mols     = NTdict(MyName="Mol")
        self.residues = NTdict(MyName="Res")
        self.atoms    = NTdict(MyName="Atom")
#        levelIdList     = ["MOLECULE", "RESIDUE", "ATOM" ]
        levelIdList     = [ "RESIDUE", "ATOM" ]
        selfLevels      = [ self.residues, self.atoms ]
        selfLevelChecks = [ self.residueSpecificChecks, self.atomSpecificChecks ]
        # sorting on mols, residues, and atoms
#        NTmessage("  for self.checks: " + `self.checks`)
        NTdebug("  for self.checks count: " + `len(self.checks)`)
        
        msgBadWiDescriptor = "See also %s%s" % (issueListUrl,10)
        msgBadWiDescriptor += "\n or %s%s" % (issueListUrl,4)
        
        for check in self.checks:
            if LEVEL_STR not in check:
                NTerror("Whatif._processCheckdb: no level attribute in check dictionary: "+check[CHECK_ID_STR])
                NTerror("check dictionary: "+`check`)
                return True
#            NTdebug("attaching check: "+check[CHECK_ID_STR]+" of type: "+check[TYPE_STR] + " to level: "+check[LEVEL_STR])
            idx = levelIdList.index( check[LEVEL_STR] )
            if idx < 0:
                NTerror("Whatif._processCheckdb: Unknown Level ["+check[LEVEL_STR]+"] in check:"+check[CHECK_ID_STR]+' '+check[TEXT_STR])
                return True
            selfLevelChecks[idx].append( check )
            check.keysformat()

        checkIter = iter(selfLevelChecks)
        for _levelEntity in selfLevels:
            levelCheck = checkIter.next()
#            NTdebug("working on levelEntity: " + levelEntity.MyName +"levelCheck: " + `levelCheck`[:80])
            for check in levelCheck:
                checkId = check[CHECK_ID_STR]
#                NTdebug( 'check        : ' + `check`)
#                NTdebug( 'check[CHECK_ID_STR]: ' + checkId)
                if not check.has_key(LOC_ID_STR):
                    NTdebug("Whatif._processCheckdb: There is no %s attribute, skipping check: [%s]" % ( LOC_ID_STR, check ))
                    NTdebug("  check: "+ `check`)
                    continue
                curLocDic = check[LOC_ID_STR]
                if not curLocDic:
#                    NTdebug("Skipping empty locationsDic")
                    continue

                for curLocId in curLocDic.keys():
                    curListDic = curLocDic[curLocId]
#                    NTdebug("Working on curLocId:   " + `curLocId`)
#                    NTdebug("Working on curListDic: " + `curListDic`)

                    nameTuple = self.translateResAtmString( curLocId )
                    if not nameTuple:
                        NTwarning(msgBadWiDescriptor+'\nWhatif._processCheckdb: parsing entity "%s" what if descriptor' % curLocId)
                        continue
                    entity = self.molecule.decodeNameTuple( nameTuple ) # can be a chain, residue or atom level object
                    if not entity:
                        NTwarning(msgBadWiDescriptor+'\nWhatif._processCheckdb: mapping entity "%s" descriptor, tuple %s', curLocId, nameTuple)
                        continue
                    #NTdebug("adding to entity: " + `entity`)
                    entityWhatifDic = entity.setdefault(WHATIF_STR, NTdict())
                    #NTdebug("adding to entityWhatifDic: " + `entityWhatifDic`)

                    keyWordList = [ VALUE_LIST_STR, QUAL_LIST_STR]
#            "locId": {                             # curLocDic
#                "'A- 189-GLU'"                     # curLocId
#                    : {                            # curListDic
#                    "valeList": [ 0.009, 0.100 ]   # curList
#                    "qualList": ["POOR", "GOOD" ]

                    for keyWord in keyWordList:
                        curList = curListDic.getDeepByKeys(keyWord) # just 1 level deep but never set as setdefaults would do.
                        if not curList:
                            continue
                        entityWhatifCheckDic = entityWhatifDic.setdefault(checkId, NTdict())
                        entityWhatifCheckDic[keyWord]=curList
#                    NTdebug("now entityWhatifDic: " + `entityWhatifDic`)
        NTdebug('done with _processCheckdb')
    #end def

    def translateResAtmString( self, string ):
        """Internal routine to split the residue or atom identifier string
            of the check.db file. E.g.:
            A- 187-HIS- CB
            A- 177-GLU
            return None for error
            """
        try:
            a = string.split('-')
            t = ['PDB',a[0].strip(),int(a[1]), None]
            if len(a) == 4: # Is there an atom name too?#                print '>', a
                try:
                    i = int(a[3])    # @TODO this is a whatif bug and should not be possible @UnusedVariable
                except:
                    t[3] = a[3].strip()
            return tuple( t )
        except:
            return None
    #end def

    def report( self ):
        return ''.join( file( self.path( Whatif.reportFile ), 'r').readlines())

#end Class


def createHtmlWhatif(project, ranges=None):
    """ Read out wiPlotList to see what get's created. """

#    wiPlotList.append( ('_01_backbone_chi','QUA/RAM/BBC/C12') )
    # The following object will be responsible for creating a (png/pdf) file with
    # possibly multiple pages
    # Level 1: row
    # Level 2: against main or alternative y-axis
    # Level 3: plot parameters dictionary (extendable).
    keyLoLoL = []
    plotAttributesRowMain = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ WHATIF_STR,          QUACHK_STR,         VALUE_LIST_STR ]
    plotAttributesRowMain[ YLABEL_STR]   = Whatif.shortNameDict[  QUACHK_STR ]
    keyLoLoL.append( [ [plotAttributesRowMain] ] )

    plotAttributesRowMain = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ WHATIF_STR,          RAMCHK_STR,         VALUE_LIST_STR ]
    plotAttributesRowMain[ YLABEL_STR]   = Whatif.shortNameDict[  RAMCHK_STR ]
    keyLoLoL.append( [ [plotAttributesRowMain] ] )

    plotAttributesRowMain = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ WHATIF_STR,          BBCCHK_STR,         VALUE_LIST_STR ]
    plotAttributesRowMain[ YLABEL_STR]   = Whatif.shortNameDict[  BBCCHK_STR ]
    keyLoLoL.append( [ [plotAttributesRowMain] ] )

    plotAttributesRowMain = NTdict()
    plotAttributesRowAlte = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ WHATIF_STR,          C12CHK_STR,         VALUE_LIST_STR ]
    plotAttributesRowAlte[ KEY_LIST_STR] = [ WHATIF_STR,          ROTCHK_STR,         VALUE_LIST_STR ]
    plotAttributesRowMain[ YLABEL_STR]   = Whatif.shortNameDict[  C12CHK_STR ]
    plotAttributesRowAlte[ YLABEL_STR]   = Whatif.shortNameDict[  ROTCHK_STR ]
#        plotAttributesRowMain[ USE_ZERO_FOR_MIN_VALUE_STR]   = True
    keyLoLoL.append( [ [plotAttributesRowMain], [plotAttributesRowAlte] ] )

#    printLink = os.path.join(
#                project.rootPath( project.name )[0],
#                project.molecule.name,
#                project.moleculeDirectories.whatif,
#                project.molecule.name + wiPlotList[-1][0] + ".pdf" )

#gv
    printLink = project.moleculePath( 'whatif', project.molecule.name + wiPlotList[0][0] + ".pdf" )

    moleculePlotSet = MoleculePlotSet(project=project, ranges=ranges, keyLoLoL=keyLoLoL )
    moleculePlotSet.renderMoleculePlotSet( printLink, createPngCopyToo=True  )

#    wiPlotList.append( ('_02_bond_angle','BND/ANG/NQA/PLNCHK') )
    keyLoLoL = []
    plotAttributesRowMain = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ WHATIF_STR,          BNDCHK_STR,         VALUE_LIST_STR ]
    plotAttributesRowMain[ YLABEL_STR]   = Whatif.shortNameDict[  BNDCHK_STR ]
    keyLoLoL.append( [ [plotAttributesRowMain] ] )

    plotAttributesRowMain = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ WHATIF_STR,          ANGCHK_STR,         VALUE_LIST_STR ]
    plotAttributesRowMain[ YLABEL_STR]   = Whatif.shortNameDict[  ANGCHK_STR ]
    keyLoLoL.append( [ [plotAttributesRowMain] ] )

    plotAttributesRowMain = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ WHATIF_STR,          NQACHK_STR,         VALUE_LIST_STR ]
    plotAttributesRowMain[ YLABEL_STR]   = Whatif.shortNameDict[  NQACHK_STR ]
    keyLoLoL.append( [ [plotAttributesRowMain] ] )

    plotAttributesRowMain = NTdict()
    plotAttributesRowAlte = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ WHATIF_STR,          PLNCHK_STR,         VALUE_LIST_STR ]
    plotAttributesRowAlte[ KEY_LIST_STR] = [ WHATIF_STR,          PL2CHK_STR,         VALUE_LIST_STR ]
    plotAttributesRowMain[ YLABEL_STR]   = Whatif.shortNameDict[  PLNCHK_STR ]
    plotAttributesRowAlte[ YLABEL_STR]   = Whatif.shortNameDict[  PL2CHK_STR ]
#        plotAttributesRowMain[ USE_ZERO_FOR_MIN_VALUE_STR]   = True
    keyLoLoL.append( [ [plotAttributesRowMain], [plotAttributesRowAlte] ] )

    plotAttributesRowMain = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ WHATIF_STR,          PL3CHK_STR,         VALUE_LIST_STR ]
    plotAttributesRowMain[ YLABEL_STR]   = Whatif.shortNameDict[  PL3CHK_STR ]
    keyLoLoL.append( [ [plotAttributesRowMain] ] )

#    printLink = os.path.join(
#                project.rootPath( project.name )[0],
#                project.molecule.name,
#                project.moleculeDirectories.whatif,
#                project.molecule.name + wiPlotList[-1][0] + ".pdf" )
#gv
    printLink = project.moleculePath( 'whatif', project.molecule.name + wiPlotList[1][0] + ".pdf" )

    moleculePlotSet = MoleculePlotSet(project=project, ranges=ranges, keyLoLoL=keyLoLoL )
    moleculePlotSet.renderMoleculePlotSet( printLink, createPngCopyToo=True  )


#    wiPlotList.append( ('_03_steric_acc_flip','BMP/ACC/FLP/CHI') )
    keyLoLoL = []
    plotAttributesRowMain = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ WHATIF_STR,          BMPCHK_STR,         VALUE_LIST_STR ]
    plotAttributesRowMain[ YLABEL_STR]   = Whatif.shortNameDict[  BMPCHK_STR ]
    keyLoLoL.append( [ [plotAttributesRowMain] ] )

    plotAttributesRowMain = NTdict()
    plotAttributesRowAlte = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ WHATIF_STR,          ACCLST_STR,         VALUE_LIST_STR ]
    plotAttributesRowAlte[ KEY_LIST_STR] = [ WHATIF_STR,          INOCHK_STR,         VALUE_LIST_STR ]
    plotAttributesRowMain[ YLABEL_STR]   = Whatif.shortNameDict[  ACCLST_STR ]
    plotAttributesRowAlte[ YLABEL_STR]   = Whatif.shortNameDict[  INOCHK_STR ]
#        plotAttributesRowMain[ USE_ZERO_FOR_MIN_VALUE_STR]   = True
    keyLoLoL.append( [ [plotAttributesRowMain], [plotAttributesRowAlte] ] )

    plotAttributesRowMain = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ WHATIF_STR,          FLPCHK_STR,         VALUE_LIST_STR ]
    plotAttributesRowMain[ YLABEL_STR]   = Whatif.shortNameDict[  FLPCHK_STR ]
    keyLoLoL.append( [ [plotAttributesRowMain] ] )

    plotAttributesRowMain = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ WHATIF_STR,          CHICHK_STR,         VALUE_LIST_STR ]
    plotAttributesRowMain[ YLABEL_STR]   = Whatif.shortNameDict[  CHICHK_STR ]
    keyLoLoL.append( [ [plotAttributesRowMain] ] )


#    printLink = os.path.join(
#                project.rootPath( project.name )[0],
#                project.molecule.name,
#                project.moleculeDirectories.whatif,
#                project.molecule.name + wiPlotList[-1][0] + ".pdf" )
#gv
    printLink = project.moleculePath( 'whatif', project.molecule.name + wiPlotList[2][0] + ".pdf" )

    moleculePlotSet = MoleculePlotSet(project=project, ranges=ranges, keyLoLoL=keyLoLoL )
    moleculePlotSet.renderMoleculePlotSet( printLink, createPngCopyToo=True  )
#end def


def runWhatif( project, parseOnly=False ):
    """
        Run and import the whatif results per model.

        All models in the ensemble of the molecule will be checked.
        Set whatif references for Molecule, Chain, Residue and Atom instances
        or None if no whatif results exist

        returns True on error.
    """

    if cingPaths.whatif == None or cingPaths.whatif == PLEASE_ADD_EXECUTABLE_HERE:
        NTmessage("No whatif installed so skipping this step")
        return

    if not project.molecule:
        NTerror("runWhatif: no molecule defined")
        return True

    if project.molecule.modelCount == 0:
        NTwarning('runWhatif: no models for "%s"', project.molecule)
        return

    path = project.moleculePath( 'whatif' )
    if not os.path.exists( path ):
        NTerror('runWhatif: path "%s" does not exist', path)
        return True

    #Specific Whatif requirement : no spaces in path because it will crash
    absPath = os.path.abspath(path)
    if len(absPath.split()) > 1:
        NTerror('runWhatif: absolute path "%s" contains spaces. This will crash Whatif.', absPath)
        return True

    if project.molecule.has_key('whatif'):
        del(project.molecule['whatif'])
    for chain in project.molecule.allChains():
        if chain.has_key('whatif'):
            del(chain['whatif'])
    for res in project.molecule.allResidues():
        if res.has_key('whatif'):
            del(res['whatif'])
    for atm in project.molecule.allAtoms():
        if atm.has_key('whatif'):
            del(atm['whatif'])

    whatif = Whatif( rootPath = path, molecule = project.molecule )
    models = NTlist(*range( project.molecule.modelCount ))

    whatifDir = project.mkdir( project.molecule.name, project.moleculeDirectories.whatif  )
    whatifPath       = os.path.dirname(cingPaths.whatif)
    whatifTopology   = os.path.join(whatifPath, "dbdata","TOPOLOGY.H")
    whatifExecutable = os.path.join(whatifPath, "DO_WHATIF.COM")

    if not parseOnly:
        project.whatifStatus.nonStandardResidues = NTlist()
        project.whatifStatus.path                = path
        project.whatifStatus.models              = models
        project.whatifStatus.completed           = False
        project.whatifStatus.parsed              = False
        project.whatifStatus.time                = None
        project.whatifStatus.exitCode            = None

        for res in project.molecule.allResidues():
            if not (res.hasProperties('protein') or res.hasProperties('nucleic')):
                NTwarning('runWhatif: non-standard residue %s found and will be written out for What If' % `res`)
                project.whatifStatus.nonStandardResidues.append(repr(res))
        #end for

        copy(whatifTopology, os.path.join(whatifDir,"TOPOLOGY.FIL"))

        for model in models:
            fullname =  os.path.join( whatifDir, sprintf('model_%03d.pdb', model) )
            # WI prefers IUPAC like PDB now. In CING the closest is IUPAC?
#            NTdebug('==> Materializing model '+`model`+" to disk" )
            pdbFile = project.molecule.toPDB( model=model, convention = IUPAC )
            if not pdbFile:
                NTerror("runWhatif: Failed to write a temporary file with a model's coordinate")
                return True
            pdbFile.save( fullname   )

        scriptComplete = Whatif.scriptBegin
        for model in models:
            modelNumberString = sprintf('%03d', model)
            modelFileName = 'model_'+modelNumberString+".pdb"
            scriptModel = Whatif.scriptPerModel.replace("$pdb_file", modelFileName)
            scriptModel = scriptModel.replace("$modelNumberString", modelNumberString)
            scriptComplete += scriptModel
        scriptComplete += Whatif.scriptQuit
        # Let's ask the user to be nice and not kill us
        # estimate to do (400/7) residues per minutes as with entry 1bus on dual core intel Mac.
        totalNumberOfResidues = project.molecule.modelCount * len(project.molecule.allResidues())
        timeRunEstimatedInSeconds    = totalNumberOfResidues / Whatif.NUMBER_RESIDUES_PER_SECONDS
        timeRunEstimatedInSecondsStr = sprintf("%.0f",timeRunEstimatedInSeconds)
        NTmessage('==> Running What If checks on '+`totalNumberOfResidues`+
                     " residues for an estimated ("+`Whatif.NUMBER_RESIDUES_PER_SECONDS`+" residues/s): "+timeRunEstimatedInSecondsStr+" seconds; please wait")
        if totalNumberOfResidues < 100:
            NTmessage("It takes much longer per residue for a small molecule/ensemble")

        scriptFileName = "whatif.script"
        scriptFullFileName =  os.path.join( whatifDir, scriptFileName )
        open(scriptFullFileName,"w").write(scriptComplete)
        whatifProgram = ExecuteProgram( whatifExecutable, rootPath = whatifDir,
                                        redirectOutput = True, redirectInputFromDummy = True )
        # The last argument becomes a necessary redirection into fouling What If into
        # thinking it's running interactively.
        now = time.time()
        whatifExitCode = whatifProgram("script", scriptFileName )
        project.whatifStatus.exitCode  = whatifExitCode
        project.whatifStatus.time      = sprintf("%.1f", time.time() - now)
        NTdebug('runWhatif: exitCode %s,  time: %s', project.whatifStatus.exitCode, project.whatifStatus.time)
        project.whatifStatus.keysformat()

        if whatifExitCode:
            NTerror("runWhatif: Failed whatif checks with exit code: " + `whatifExitCode`)
            return True

        removeTempFiles = False # Useful optional block for debugging. Default: True
        if removeTempFiles:
            try:
                removeListLocal = ["DSSPOUT", "TOPOLOGY.FIL", "PDBFILE.PDB", "pdbout.tex"]
                removeList = []
                for fn in removeListLocal:
                    removeList.append( os.path.join(whatifDir, fn) )
    
                for extension in [ "*.eps", "*.pdb", "*.LOG", "*.DAT", "*.SCC", "*.sty", "*.FIG"]:
                    for fn in glob(os.path.join(whatifDir,extension)):
                        removeList.append(fn)
                for fn in removeList:
                    if not os.path.exists(fn):
                        NTdebug("runWhatif: Expected to find a file to be removed but it doesn't exist: " + fn )
                        continue
        #            NTdebug("Removing: " + fn)
                    os.unlink(fn)
            except:
                NTwarning("runWhatif: Failed to remove all temporary what if files that were expected")

        project.whatifStatus.completed = True
    else:
        NTdebug("Skipping actual whatif execution")
        whatifExitCode = 0
    #end if


#    NTmessageNoEOL('Parsing whatif checks ')
    for model in models:
        modelNumberString = sprintf('%03d', model)
#        fullname =  os.path.join( whatifDir, sprintf('model_%03d.pdb', model) )
#        os.unlink( fullname )
        modelCheckDbFileName = "check_"+modelNumberString+".db"
#        NTmessageNoEOL('.')
        modelCheckDbFullFileName =  os.path.join( whatifDir, modelCheckDbFileName )

        if whatif._parseCheckdb( modelCheckDbFullFileName, model ):
            NTerror("\nrunWhatif: Failed to parse check db %s", modelCheckDbFileName)
            return True
    #end if
#    NTmessage(' done')

    if whatif._processCheckdb():
        NTerror("runWhatif: Failed to process check db")
        return True            

    pathPdbOut = os.path.join(path, 'pdbout.txt' )
    if not os.path.exists(pathPdbOut): # Happened for 1ao2 on production machine; not on development...
        NTerror("Path does not exist: %s" % (pathPdbOut))
        return True
    
    if whatif._processSummary(project, pathPdbOut):
        NTerror("runWhatif: Failed to process WI summary file")
        return True
#end def

def restoreWhatif( project, tmp=None ):
    """
    Optionally restore dssp results
    """
    if project.whatifStatus.completed:
        NTmessage('==> restoring whatif results')
        project.runWhatif(parseOnly=True)
#end def


# register the function
methods  = [
            (runWhatif, None),
            (createHtmlWhatif, None),
            ]
#saves    = []
restores = [(restoreWhatif, None)]
#exports  = []

