"""
Unit test execute as:
python -u $CINGROOT/python/cing/Libs/test/test_NTutils5.py
"""

from cing.Libs.NTutils import NTcVarianceAverage
from cing.core.sml import NTlist
from unittest import TestCase
import cing
import unittest

class AllChecks(TestCase):

    def testGetKeyWithLargestCount(self):

        testList = [
            [ ('H', 'H', 'H'), 1.0, False, 'H'], # defaults
            [ ('H', 'H', 'S'), 1.0, False,  False], # all need to be the same
            [ ('H', 'H', 'S'), 1.0, True,  'H'], # just taking the most common
            [ ('H', 'H', 'S'), 0.5, False,  'H'], # just taking the most common
]
        for testTuple in testList:
            testList, minFraction, useLargest, testResult = testTuple
#            NTdebug("Testing %s" % `testTuple`)
            testListNT = NTlist()
            testListNT += testList
            self.assertEquals(testListNT.getConsensus(minFraction=minFraction,useLargest=useLargest),testResult)

    def testCircularAverageOfTwoDihdedrals(self):
# VB van cing procheck routines
#A 189 GLN   0.243   0.071   0.164   0.660   0.153   0.362   1.840   6.256  -0.73  -1.05 999.90  -0.89

        lol = [  [  0.243, 0.071, 0.153 ],
                 [  0.164, 0.660, 0.362 ],
                 [ 0.0, 0.0, 0.0], # extremes
                 [ 1.0, 1.0, 1.0], # extremes
                 [ 0.0, 1.0, 0.293], # doesn't really make sense to JFD but here it is.
                  ]

        for cycle in lol:
            cv1, cv2, cav = cycle
            angleList = NTlist()
            angleList.append(cv1)
            angleList.append(cv2)
            circularVariance = NTcVarianceAverage(angleList)
            self.assertAlmostEqual(circularVariance, cav, places = 3)

if __name__ == "__main__":
    cing.verbosity = cing.verbosityDebug
    unittest.main()