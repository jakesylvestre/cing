from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.STAR import Utils
from unittest import TestCase
import unittest



class AllChecks(TestCase, Lister):

    os.chdir(cingDirTmp)

    def testTranspose(self):
        m1 = [ [1,2], [3,4] ]
        m2 = [ (1,3), (2,4) ]
        m1t= Utils.transpose(m1)
        self.assertTrue(m1t==m2)
    def testLister(self):
        self.dummy = "dumb"
        NTdebug( "Self is: %r", self )

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
#    cing.verbosity = verbosityError
    unittest.main()
