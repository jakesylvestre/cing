'''
Created on Dec 21, 2010

@author: jd
'''
from cing import cingDirTestsData #@UnusedImport
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode import Ccpn #@UnusedImport Inserted to trigger unit test failure.
from cing.Scripts.FC.utils import getBmrbCsCountsFromFile
from unittest import TestCase
import unittest


class AllChecks(TestCase):

    def testGetBmrbCsCountsFromFile(self):
        useVersion = '2'

        expectedLoL = [
            [ 4020, '1brv', {'1H':  183, '13C':   73}],
            [ 4141, '1nk2', {'1H':  840, '13C':  291, '15N':  100, '31P':   18}], # BMRB 2.1 file reports no 1H in overview
            [15381, '2jsx', {'1H':  443, '13C':  266, '15N':   85}],              # BMRB 2.1 file reports 561 1H instead of the 443 present
#            [16409, '',     {'113Cd':  999}], # absent in PDB.
        ]

        for bmrb_id, pdb_id, expected in expectedLoL:
            NTmessage("Looking at %s %s" % (bmrb_id, pdb_id))
            inputStarFile = os.path.join( cingDirTestsData, 'bmrb','2.1.1','bmr%s.str' )
            if useVersion == '3':
                inputStarFile = os.path.join( cingDirTestsData, 'bmrb','3.0.8.34','bmr%s.str' )
            inputStarFile = inputStarFile % bmrb_id # only in Python ;-)
            assignmentCountMap = getBmrbCsCountsFromFile(inputStarFile)
            self.assertTrue( assignmentCountMap )
            for key in assignmentCountMap.keys():
                value = assignmentCountMap[key]
                if value == 0:
                    continue
                self.assertEqual( value, expected[key])
        # end for
if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()