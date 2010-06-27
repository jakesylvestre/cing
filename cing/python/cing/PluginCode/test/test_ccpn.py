"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_ccpn.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.Ccpn import Ccpn #@UnusedImport needed to throw a ImportWarning so that the test is handled properly.
from cing.Scripts.FC.utils import printSequenceFromCcpnProject
from cing.core.classes import Project
from cing.core.constants import * #@UnusedWildImport
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    entryList = "1brv_cs_pk_2mdl".split() # DEFAULT because it contains many data types and is small/fast to run.
#    entryList = "1brv".split()
#    entryList = "1a4d 1a24 1afp 1ai0 1brv 1bus 1cjg 1hue 1ieh 1iv6 1kr8 2hgh 2k0e SRYBDNA Parvulustat".split()
# Set for creating ccpn projects from cyana pdbs.
#    entryList = "1a4d 1ai0 1brv_1model 1hkt_1model 1i1s 1ka3 1tgq_1model 1tkv 1y4o_1model 2hgh_1model 2hm9 H2_2Ca_53".split()
    def testInitFromAndSaveToCcpn(self):

#        if you have a local copy you can use it; make sure to adjust the path setting below.
        fastestTest = True

        modelCount=99
        redoFromCingProject = True
        htmlOnly = False # default is False but enable it for faster runs without some actual data.
        doWhatif = True # disables whatif actual run
        doProcheck = True
        doWattos = True
        doTalos = True
        useNrgArchive = False
        ranges = None
        if fastestTest:
            modelCount=2
            redoFromCingProject = False
            htmlOnly = True
            doWhatif = False
            doProcheck = False
            doWattos = False
            doTalos = False
        if redoFromCingProject:
            useNrgArchive = False
            doWhatif = False
            doProcheck = False
            doWattos = False
            doTalos = False

        self.failIf(os.chdir(cingDirTmp), msg =
            "Failed to change to directory for temporary test files: " + cingDirTmp)
        for entryId in AllChecks.entryList:

            if redoFromCingProject:
                project = Project.open(entryId, status = 'old')
            else:
                project = Project.open(entryId, status = 'new')
                self.assertTrue(project, 'Failed opening project: ' + entryId)

                if useNrgArchive: # default is False
    #                inputArchiveDir = os.path.join('/Library/WebServer/Documents/NRG-CING/recoordSync', entryId)
                    # Mounted from nmr.cmbi.ru.nl
    #                inputArchiveDir = os.path.join('/Volumes/tera1/Library/WebServer/Documents/NRG-CING/recoordSync', entryId)
                    inputArchiveDir = os.path.join('/Volumes/tera1//Users/jd/ccpn_tmp/data/recoord', entryId)
                else:
                    inputArchiveDir = os.path.join(cingDirTestsData, "ccpn")

                ccpnFile = os.path.join(inputArchiveDir, entryId + ".tgz")
                if not os.path.exists(ccpnFile):
                    ccpnFile = os.path.join(inputArchiveDir, entryId + ".tar.gz")
                    if not os.path.exists(ccpnFile):
                        self.fail("Neither %s or the .tgz exist" % ccpnFile)

                self.assertTrue(project.initCcpn(ccpnFolder = ccpnFile, modelCount=modelCount))
                self.assertTrue(project.save())

            if False:
                ranges = "171-173"
                residueOfInterest = range(171,174)
                for residue in project.molecule.A.allResidues():
                    if residue.resNum not in residueOfInterest:
    #                    NTmessage("Removing residue of no interest")
                        project.molecule.A.removeResidue(residue)
            if False:
                ccpnProject = project.ccpn
                printSequenceFromCcpnProject(ccpnProject)
            if True:
                self.assertFalse(project.validate(htmlOnly = htmlOnly,
                                              ranges=ranges,
                                              doProcheck = doProcheck,
                                              doWhatif = doWhatif,
                                              doWattos=doWattos,
                                              doTalos=doTalos
                                               ))
#            self.assertTrue(project.exportValidation2ccpn())
#            self.assertFalse(project.removeCcpnReferences())
            # Do not leave the old CCPN directory laying around since it might get added to by another test.
#            if os.path.exists(entryId):
#                self.assertFalse(shutil.rmtree(entryId))
            if True:
                self.assertTrue(project.saveCcpn(entryId))
        # end for
    # end def test

    def tttestCreateCcpn(self):
        doRestraints = False
        pdbConvention = IUPAC
        restraintsConvention = CYANA

        self.failIf(os.chdir(cingDirTmp), msg =
            "Failed to change to directory for temporary test files: " + cingDirTmp)
        for entryId in AllChecks.entryList:
            # Allow pdb files to be of different naming systems for this test.
            if entryId.startswith("2hgh"):
                pdbConvention = CYANA
            if entryId.startswith("1tgq"):
                pdbConvention = PDB
            if entryId.startswith("1brv"):
                pdbConvention = IUPAC
            if entryId.startswith("1YWUcdGMP"):
                pdbConvention = XPLOR

            project = Project(entryId)
            self.failIf(project.removeFromDisk())
            project = Project.open(entryId, status = 'new')
            cyanaDirectory = os.path.join(cingDirTestsData, "cyana", entryId)
            pdbFileName = entryId + ".pdb"
            pdbFilePath = os.path.join(cyanaDirectory, pdbFileName)
            project.initPDB(pdbFile = pdbFilePath, convention = pdbConvention)

            if doRestraints:
                NTdebug("Reading files from directory: " + cyanaDirectory)
                kwds = {'uplFiles': [ entryId ],
                        'acoFiles': [ entryId ]
                          }
                if entryId.startswith("1YWUcdGMP"):
                    del(kwds['acoFiles'])

                if os.path.exists(os.path.join(cyanaDirectory, entryId + ".prot")):
                    self.assertTrue(os.path.exists(os.path.join(cyanaDirectory, entryId + ".seq")),
                        "Converter for cyana also needs a seq file before a prot file can be imported")
                    kwds['protFile'] = entryId
                    kwds['seqFile'] = entryId

                # Skip restraints if absent.
                if os.path.exists(os.path.join(cyanaDirectory, entryId + ".upl")):
                    project.cyana2cing(cyanaDirectory = cyanaDirectory, convention = restraintsConvention,
                                copy2sources = True,
                                **kwds)
            # end if
            project.save()
            NTmessage( "Project: %s" % project)
            ccpnFolder = entryId + "New"
            self.assertTrue(project.saveCcpn(ccpnFolder))

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
