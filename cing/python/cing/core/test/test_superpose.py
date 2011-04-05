"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_pdb.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.core.classes import Project
from cing.core.constants import * #@UnusedWildImport
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    def test_superpose(self):
        pdbConvention = IUPAC
        entryId = "1brv"
#        entryId = "2vb1_simple" # Protein solved by X-ray.

        cingDirTmpTest = os.path.join( cingDirTmp, getCallerName() )
        mkdirs( cingDirTmpTest )
        self.failIf(os.chdir(cingDirTmpTest), msg =
            "Failed to change to test directory for files: " + cingDirTmpTest)

        pdbDirectory = os.path.join(cingDirTestsData,"pdb", entryId)
        pdbFileName = "pdb" + entryId + ".ent"
        pdbFilePath = os.path.join( pdbDirectory, pdbFileName)
        self.failIf( not os.path.exists(pdbFilePath), msg= "Failed to find file: "+pdbFilePath)

        # does it matter to import it just now?
        project = Project( entryId )
        self.failIf( project.removeFromDisk())
        project = Project.open( entryId, status='new' )
        project.initPDB( pdbFile=pdbFilePath, convention = pdbConvention )

        # Compare with molmol on 1brv's 48 models:
#        mean global bb    RMSD:  0.98 +/-  0.40 A  ( 0.10.. 2.19 A)
#        mean global heavy RMSD:  1.75 +/-  0.51 A  ( 0.54.. 3.33 A)
        # Note that in molmol the backbone protein atoms are defined: N, CA, C
        # CING used to include the carbonyl atom

        # using default parameters.
        ens = project.molecule.superpose(backboneOnly=True, includeProtons = False, iterations=2)
        NTdebug( 'ens %s' % ens)
        NTdebug( 'ens.averageModel %s' % ens.averageModel)
        self.assertAlmostEquals( 0.7643199324863148, ens.averageModel.rmsd, 3 )
        # Confirmed to be the 'averaage RMSD to mean: 0.698' in molmol using command
        #    Fit 'to_mean'.
        ens = project.molecule.superpose(backboneOnly=False, includeProtons = False,
                                         iterations=3) # no improvement to do 3 over the default 2 but left in for speed checking.
        NTdebug( 'ens.averageModel %s' % ens.averageModel)
        self.assertAlmostEquals( 0.99383582432002637, ens.averageModel.rmsd, 3 )
        # Confirmed to be the 'averaage RMSD to mean: 1.238' in molmol using command
        #    Fit 'to_mean'. Using 'heavy' atom selection. CING got there much faster.
        # because algorithm in molmol probably does a full list of iterations (47 or so)
        # and CING only 3.

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()

#        1    2    3    4    5    6    7    8    9   10   11   12   13   14   15   16   17   18   19   20   21   22   23   24   25   26   27   28   29   30   31   32   33   34   35   36   37   38   39   40   41   42   43   44   45   46   47   48
#  1       1.53 1.84 1.66 0.49 1.56 1.79 0.76 1.18 1.69 1.12 1.16 1.66 1.21 0.96 0.69 0.81 1.40 0.41 1.36 1.29 1.24 1.70 1.08 0.58 0.95 0.30 1.07 1.29 0.66 0.87 0.76 0.42 1.15 1.05 1.48 1.05 1.21 1.41 0.85 1.66 0.29 0.97 0.48 0.59 1.97 0.67 0.62
#  2  1.99      0.71 0.74 1.72 0.31 0.57 1.00 1.45 1.37 0.71 0.84 0.67 1.13 1.25 1.44 1.50 0.42 1.37 1.22 0.47 1.16 0.74 0.75 1.23 1.44 1.41 0.72 0.44 1.14 1.38 1.35 1.50 1.52 0.66 1.09 0.72 0.80 1.04 0.90 1.01 1.40 1.11 1.26 1.19 0.83 1.79 1.14
#  3  2.62 1.72      0.34 1.90 0.65 0.34 1.20 1.84 1.32 0.92 0.95 0.39 1.06 1.64 1.52 1.53 0.68 1.59 0.97 0.76 1.04 0.28 0.89 1.48 1.43 1.67 0.94 0.87 1.42 1.40 1.42 1.70 1.85 0.97 0.76 0.96 0.82 0.86 1.20 0.63 1.66 1.21 1.48 1.45 0.24 2.06 1.35
#  4  2.74 1.77 1.15      1.68 0.66 0.52 1.05 1.68 1.41 0.77 0.79 0.38 0.83 1.55 1.30 1.30 0.56 1.39 0.77 0.64 0.85 0.18 0.75 1.30 1.23 1.50 0.81 0.80 1.23 1.17 1.20 1.48 1.69 0.87 0.57 0.82 0.65 0.57 1.04 0.44 1.46 1.01 1.29 1.26 0.47 1.85 1.18
#  5  0.83 2.09 2.37 2.49      1.74 1.93 0.91 1.29 1.86 1.24 1.23 1.75 1.16 1.23 0.50 0.67 1.54 0.47 1.26 1.44 1.21 1.75 1.20 0.68 0.84 0.46 1.24 1.48 0.80 0.77 0.61 0.39 1.25 1.22 1.43 1.19 1.27 1.35 1.00 1.62 0.48 0.98 0.58 0.71 2.03 0.67 0.78
#  6  2.06 1.01 1.55 1.54 2.14      0.48 1.03 1.48 1.39 0.78 0.91 0.60 1.16 1.25 1.46 1.51 0.27 1.40 1.20 0.36 1.14 0.65 0.74 1.24 1.46 1.45 0.70 0.35 1.12 1.38 1.37 1.51 1.50 0.77 1.05 0.79 0.80 0.98 0.99 0.98 1.42 1.11 1.29 1.19 0.76 1.78 1.16
#  7  2.50 1.28 1.50 1.31 2.52 1.28      1.16 1.81 1.30 0.88 0.95 0.38 1.14 1.56 1.58 1.58 0.58 1.57 1.11 0.68 1.09 0.44 0.84 1.46 1.47 1.65 0.88 0.74 1.38 1.44 1.49 1.70 1.83 0.92 0.90 0.93 0.87 0.97 1.17 0.81 1.64 1.22 1.46 1.42 0.42 2.04 1.31
#  8  1.50 1.60 1.97 1.93 1.48 1.47 1.77      1.41 1.36 0.49 0.55 1.02 0.69 1.11 0.59 0.67 0.88 0.49 0.82 0.77 0.69 1.08 0.42 0.58 0.63 0.58 0.51 0.85 0.61 0.58 0.54 0.65 1.40 0.46 0.86 0.44 0.62 0.93 0.41 1.04 0.58 0.55 0.37 0.56 1.33 1.19 0.23
#  9  1.91 1.96 2.57 2.62 1.88 2.26 2.67 2.10      1.90 1.45 1.56 1.77 1.61 0.76 1.43 1.59 1.38 1.32 1.76 1.34 1.72 1.75 1.44 1.13 1.72 1.27 1.39 1.22 1.02 1.57 1.43 1.30 0.29 1.37 1.79 1.40 1.46 1.53 1.28 1.80 1.20 1.45 1.31 1.08 1.96 0.98 1.38
# 10  2.63 2.59 2.49 2.59 2.67 2.73 2.37 2.83 3.17      1.34 1.35 1.37 1.50 1.53 1.65 1.66 1.45 1.61 1.50 1.43 1.48 1.38 1.33 1.64 1.59 1.64 1.37 1.44 1.61 1.60 1.62 1.75 1.91 1.29 1.42 1.36 1.39 1.65 1.47 1.49 1.67 1.56 1.54 1.61 1.28 1.99 1.48
# 11  1.71 1.38 1.87 1.85 1.81 0.99 1.52 1.10 2.38 2.69      0.26 0.74 0.54 1.24 0.89 0.91 0.63 0.86 0.73 0.57 0.62 0.78 0.33 0.83 0.85 0.96 0.39 0.71 0.78 0.79 0.80 0.98 1.49 0.24 0.69 0.10 0.45 0.75 0.36 0.78 0.93 0.59 0.75 0.78 1.04 1.43 0.63
# 12  2.09 1.58 1.81 1.49 2.07 1.32 1.34 1.41 2.54 2.64 1.02      0.76 0.48 1.36 0.86 0.84 0.74 0.87 0.65 0.69 0.50 0.80 0.42 0.87 0.75 0.99 0.48 0.87 0.85 0.72 0.77 0.98 1.59 0.43 0.64 0.31 0.50 0.72 0.49 0.74 0.96 0.51 0.76 0.84 1.05 1.46 0.66
# 13  2.29 1.27 1.62 1.27 2.30 1.13 0.93 1.79 2.56 2.37 1.39 1.17      0.91 1.56 1.38 1.35 0.56 1.40 0.83 0.60 0.80 0.33 0.70 1.29 1.24 1.50 0.74 0.78 1.24 1.22 1.28 1.51 1.77 0.82 0.68 0.78 0.71 0.70 1.02 0.55 1.48 1.00 1.29 1.26 0.54 1.89 1.16
# 14  2.52 2.11 1.93 1.43 2.35 1.98 1.51 1.76 2.88 2.51 1.60 1.31 1.64      1.49 0.74 0.65 0.96 0.90 0.45 0.93 0.50 0.86 0.66 0.96 0.63 1.03 0.77 1.10 0.95 0.52 0.66 0.93 1.64 0.71 0.47 0.58 0.61 0.59 0.62 0.67 0.98 0.65 0.82 0.93 1.17 1.45 0.73
# 15  1.86 2.21 2.44 2.65 1.78 2.49 2.63 2.11 1.56 2.41 2.48 2.62 2.62 2.74      1.31 1.44 1.20 1.11 1.60 1.13 1.51 1.57 1.16 0.89 1.55 1.03 1.07 0.99 0.83 1.42 1.31 1.17 0.75 1.08 1.61 1.17 1.21 1.50 1.09 1.68 1.03 1.27 1.09 0.85 1.75 1.02 1.09
# 16  1.79 2.01 2.02 1.85 1.45 1.90 1.99 0.94 2.23 2.93 1.54 1.53 1.98 1.59 2.29      0.34 1.26 0.38 0.85 1.17 0.83 1.36 0.86 0.66 0.47 0.50 0.95 1.26 0.76 0.38 0.19 0.41 1.41 0.92 1.00 0.86 0.91 1.00 0.73 1.22 0.51 0.70 0.41 0.67 1.65 1.03 0.51
# 17  1.95 2.30 2.33 1.89 1.81 1.94 2.04 1.59 2.73 2.71 1.48 1.26 1.73 1.38 2.74 1.31      1.30 0.52 0.78 1.22 0.73 1.35 0.91 0.78 0.33 0.66 0.99 1.35 0.86 0.19 0.36 0.48 1.56 0.99 0.94 0.89 0.96 0.96 0.79 1.18 0.61 0.71 0.52 0.80 1.65 1.13 0.56
# 18  2.11 0.95 1.83 1.47 2.20 0.90 0.93 1.54 2.35 2.54 1.20 1.21 0.86 1.62 2.51 1.86 1.82      1.22 1.02 0.20 0.96 0.59 0.59 1.06 1.27 1.29 0.55 0.31 0.94 1.17 1.17 1.31 1.38 0.66 0.89 0.64 0.63 0.76 0.82 0.85 1.24 0.91 1.11 1.01 0.81 1.60 0.99
# 19  0.54 1.79 2.35 2.52 0.67 1.87 2.32 1.26 1.92 2.63 1.51 1.94 2.10 2.39 1.85 1.56 1.87 1.96      1.03 1.10 0.91 1.44 0.82 0.47 0.59 0.20 0.86 1.16 0.59 0.56 0.43 0.29 1.30 0.84 1.17 0.81 0.96 1.13 0.64 1.36 0.27 0.69 0.18 0.49 1.72 0.87 0.37
# 20  2.30 2.01 1.23 1.22 1.97 1.78 1.59 1.64 2.63 2.45 1.61 1.39 1.56 1.25 2.48 1.39 1.49 1.77 2.07      0.99 0.33 0.80 0.69 1.02 0.68 1.16 0.82 1.17 1.04 0.68 0.75 1.09 1.73 0.86 0.32 0.76 0.61 0.53 0.89 0.51 1.14 0.65 0.95 1.00 1.08 1.55 0.88
# 21  1.67 0.98 1.87 1.82 1.85 0.90 1.52 1.39 1.99 2.66 1.11 1.34 1.15 2.08 2.20 1.83 1.86 0.99 1.52 1.94      0.90 0.67 0.52 0.94 1.19 1.17 0.46 0.31 0.83 1.10 1.08 1.20 1.33 0.58 0.89 0.55 0.60 0.77 0.73 0.88 1.12 0.82 0.99 0.90 0.91 1.50 0.88
# 22  1.65 1.59 1.97 1.84 1.67 1.50 1.44 1.31 2.51 2.35 1.05 1.20 1.18 1.50 2.40 1.53 1.37 1.25 1.45 1.44 1.33      0.87 0.57 0.88 0.59 1.04 0.66 1.10 0.91 0.63 0.74 0.99 1.70 0.75 0.50 0.65 0.60 0.61 0.78 0.65 1.03 0.47 0.81 0.87 1.15 1.45 0.75
# 23  2.58 1.72 0.93 1.02 2.35 1.61 1.32 2.09 2.70 2.17 1.84 1.63 1.40 1.57 2.46 2.11 2.09 1.57 2.36 1.18 1.89 1.75      0.76 1.35 1.27 1.54 0.81 0.83 1.28 1.21 1.26 1.53 1.76 0.88 0.58 0.84 0.66 0.64 1.07 0.47 1.51 1.04 1.33 1.31 0.40 1.92 1.20
# 24  1.60 1.32 1.80 1.93 1.63 1.37 1.55 0.72 2.08 2.72 1.12 1.48 1.68 1.85 2.03 1.34 1.91 1.39 1.32 1.68 1.22 1.26 1.93      0.72 0.84 0.92 0.25 0.62 0.68 0.79 0.79 0.96 1.43 0.35 0.66 0.31 0.35 0.73 0.51 0.78 0.91 0.50 0.70 0.67 1.01 1.37 0.57
# 25  0.90 1.66 2.26 2.43 1.01 1.82 2.09 1.39 1.92 2.56 1.50 1.76 1.92 2.23 1.77 1.67 1.90 1.77 0.82 1.95 1.37 1.28 2.21 1.24      0.84 0.46 0.70 0.98 0.30 0.78 0.65 0.54 1.09 0.76 1.15 0.75 0.82 1.05 0.65 1.29 0.47 0.56 0.42 0.15 1.63 0.74 0.50
# 26  1.53 1.92 2.40 2.19 1.58 1.90 1.82 1.31 2.57 2.60 1.36 1.43 1.64 1.65 2.53 1.33 1.22 1.59 1.40 1.76 1.62 0.87 2.25 1.46 1.37      0.74 0.95 1.33 0.95 0.32 0.45 0.66 1.70 0.93 0.86 0.84 0.93 0.94 0.79 1.09 0.76 0.67 0.58 0.86 1.56 1.29 0.60
# 27  0.66 1.85 2.49 2.62 0.88 2.00 2.31 1.42 2.01 2.52 1.60 1.98 2.13 2.35 1.81 1.66 1.88 1.96 0.64 2.11 1.61 1.46 2.42 1.48 0.78 1.36      0.94 1.20 0.62 0.70 0.56 0.35 1.25 0.89 1.30 0.89 1.05 1.25 0.71 1.48 0.28 0.81 0.30 0.50 1.81 0.81 0.46
# 28  1.38 1.16 1.78 1.95 1.48 1.24 1.51 1.10 2.15 2.40 0.95 1.37 1.42 1.82 1.97 1.55 1.80 1.23 1.15 1.64 1.00 0.93 1.73 0.87 0.96 1.35 1.19      0.59 0.63 0.88 0.87 0.99 1.38 0.38 0.79 0.37 0.40 0.79 0.55 0.88 0.91 0.53 0.74 0.66 1.06 1.34 0.61
# 29  1.69 0.84 1.90 2.00 1.81 1.15 1.62 1.28 1.71 2.77 1.43 1.82 1.64 2.28 1.95 1.85 2.31 1.24 1.48 2.13 0.95 1.64 2.01 0.96 1.44 1.90 1.63 1.12      0.85 1.24 1.19 1.27 1.23 0.65 1.07 0.68 0.74 0.95 0.80 1.06 1.17 0.97 1.06 0.92 1.01 1.49 0.95
# 30  1.12 1.49 2.36 2.39 1.36 1.75 1.96 1.40 1.90 2.54 1.43 1.72 1.87 2.12 1.83 1.76 1.97 1.57 1.09 2.10 1.31 1.32 2.24 1.25 0.84 1.39 1.01 0.95 1.31      0.83 0.75 0.63 0.97 0.73 1.12 0.71 0.79 0.99 0.62 1.25 0.54 0.58 0.51 0.21 1.56 0.74 0.56
# 31  1.85 1.99 2.43 1.94 1.87 1.99 1.72 1.50 2.58 2.56 1.57 1.37 1.58 1.30 2.50 1.43 1.13 1.51 1.79 1.72 1.73 1.12 2.08 1.65 1.68 0.93 1.73 1.56 2.01 1.57      0.34 0.53 1.55 0.89 0.81 0.78 0.83 0.84 0.69 1.05 0.63 0.63 0.50 0.77 1.52 1.18 0.50
# 32  1.80 1.94 1.81 1.63 1.45 1.79 1.94 1.04 2.18 2.77 1.49 1.40 1.88 1.44 2.19 0.64 1.28 1.75 1.61 1.18 1.76 1.48 1.83 1.39 1.64 1.43 1.71 1.51 1.84 1.74 1.45      0.46 1.42 0.84 0.91 0.77 0.82 0.91 0.66 1.11 0.53 0.62 0.41 0.66 1.56 1.07 0.48
# 33  1.38 2.04 2.43 2.17 1.41 1.69 2.13 1.23 2.30 2.87 1.25 1.38 1.84 1.82 2.50 1.28 0.94 1.70 1.38 1.78 1.59 1.33 2.30 1.62 1.47 1.21 1.43 1.52 1.90 1.56 1.29 1.25      1.27 0.99 1.23 0.93 1.05 1.15 0.73 1.42 0.21 0.77 0.32 0.56 1.84 0.76 0.48
# 34  1.96 2.10 2.63 2.54 1.94 2.17 2.57 1.91 0.93 3.27 2.28 2.39 2.47 2.70 1.82 2.02 2.45 2.25 1.98 2.55 1.92 2.43 2.76 1.98 1.95 2.44 2.06 2.16 1.72 1.97 2.38 2.04 2.03      1.41 1.78 1.44 1.46 1.51 1.33 1.80 1.17 1.42 1.29 1.04 1.97 0.89 1.36
# 35  1.37 1.19 1.82 2.11 1.50 1.36 1.69 1.29 2.11 2.37 0.98 1.54 1.63 1.97 1.97 1.76 1.98 1.48 1.16 1.78 1.18 1.21 1.83 1.07 1.06 1.55 1.16 0.59 1.21 1.06 1.82 1.71 1.68 2.21      0.83 0.19 0.49 0.90 0.36 0.91 0.90 0.65 0.73 0.72 1.09 1.38 0.61
# 36  2.57 2.00 1.64 1.25 2.35 1.99 1.30 1.91 2.88 2.24 1.82 1.53 1.52 0.85 2.59 1.75 1.74 1.60 2.39 1.13 2.08 1.46 1.19 1.86 2.20 1.78 2.35 1.74 2.21 2.10 1.46 1.57 2.12 2.80 1.94      0.74 0.55 0.51 0.91 0.38 1.26 0.77 1.06 1.12 0.85 1.70 0.96
# 37  1.74 1.31 1.93 1.88 1.80 1.20 1.48 0.93 2.27 2.78 0.58 1.14 1.48 1.61 2.37 1.37 1.62 1.20 1.51 1.66 1.18 1.07 1.97 0.92 1.46 1.23 1.59 0.94 1.31 1.32 1.52 1.37 1.40 2.20 1.05 1.78      0.46 0.78 0.30 0.84 0.87 0.56 0.69 0.71 1.09 1.36 0.57
# 38  2.01 1.77 1.21 1.41 1.68 1.61 1.81 1.49 2.34 2.45 1.57 1.58 1.70 1.77 2.06 1.45 1.80 1.79 1.72 1.09 1.67 1.60 1.30 1.47 1.75 1.94 1.89 1.37 1.76 1.92 1.97 1.28 1.87 2.36 1.49 1.58 1.63      0.63 0.64 0.62 1.02 0.55 0.84 0.78 0.93 1.44 0.71
# 39  2.25 1.70 1.76 1.29 2.13 1.57 1.44 2.00 2.51 2.37 1.66 1.35 1.02 1.42 2.61 1.95 1.52 1.25 2.14 1.40 1.58 1.36 1.25 1.98 1.94 1.72 2.14 1.67 1.97 1.95 1.48 1.72 1.71 2.42 1.86 1.34 1.82 1.70      0.89 0.49 1.18 0.76 1.05 1.01 1.00 1.52 0.97
# 40  1.25 1.27 2.12 2.13 1.42 1.43 1.78 1.29 1.92 2.58 1.13 1.50 1.64 1.98 2.07 1.72 1.82 1.38 1.14 1.92 1.14 1.26 2.00 1.18 1.10 1.46 1.20 1.00 1.16 1.11 1.58 1.64 1.40 1.90 0.96 2.01 1.19 1.73 1.69      1.03 0.67 0.61 0.54 0.60 1.34 1.18 0.46
# 41  2.60 1.99 1.23 0.88 2.31 1.68 1.62 1.88 2.73 2.58 1.79 1.50 1.38 1.52 2.70 1.69 1.65 1.73 2.35 0.97 1.87 1.72 1.23 1.93 2.31 2.07 2.46 1.89 2.15 2.41 1.94 1.53 2.01 2.60 2.05 1.42 1.90 1.09 1.34 2.12      1.44 0.89 1.25 1.25 0.73 1.82 1.16
# 42  1.26 1.87 2.60 2.37 1.48 1.78 2.10 1.15 2.18 2.91 1.32 1.50 1.91 1.95 2.36 1.32 1.32 1.63 1.29 2.05 1.45 1.35 2.50 1.42 1.27 1.00 1.26 1.38 1.70 1.22 1.21 1.38 0.81 1.95 1.58 2.19 1.24 2.05 1.93 1.33 2.29      0.77 0.28 0.48 1.80 0.74 0.42
# 43  1.42 1.66 2.13 2.17 1.44 1.60 1.83 0.99 2.25 2.82 1.19 1.47 1.75 1.98 2.26 1.30 1.67 1.59 1.15 1.73 1.36 1.08 2.16 0.88 1.08 1.13 1.28 1.00 1.42 1.26 1.52 1.43 1.36 2.13 1.26 2.02 1.06 1.57 1.95 1.32 1.99 1.20      0.57 0.56 1.33 1.14 0.56
# 44  1.08 1.75 2.50 2.44 1.30 1.80 2.04 1.06 2.25 2.70 1.26 1.69 1.93 2.02 2.18 1.48 1.65 1.64 0.97 2.07 1.44 1.12 2.39 1.13 0.99 0.96 0.95 1.05 1.48 0.96 1.33 1.54 1.22 2.15 1.20 2.12 1.14 1.94 2.03 1.18 2.37 0.89 0.94      0.42 1.61 0.90 0.24
# 45  0.89 1.76 2.38 2.60 1.12 1.87 2.25 1.44 1.88 2.73 1.52 1.94 2.11 2.43 1.84 1.81 2.07 1.91 0.83 2.09 1.47 1.45 2.38 1.30 0.58 1.53 0.78 1.10 1.46 0.97 1.87 1.80 1.55 1.96 1.11 2.40 1.49 1.87 2.15 1.10 2.48 1.38 1.12 1.03      1.59 0.73 0.49
# 46  2.90 1.95 0.76 1.13 2.64 1.90 1.58 2.33 2.84 2.30 2.20 1.97 1.71 1.98 2.55 2.32 2.47 1.98 2.65 1.38 2.14 2.17 0.85 2.15 2.54 2.61 2.72 2.05 2.23 2.57 2.50 2.09 2.72 2.95 2.11 1.55 2.25 1.39 1.82 2.39 1.33 2.87 2.44 2.76 2.67      2.19 1.48
# 47  1.26 2.28 3.17 3.02 1.60 2.43 2.76 2.14 1.99 2.83 2.17 2.34 2.40 2.77 2.12 2.36 2.19 2.24 1.50 2.76 1.86 1.93 2.95 2.15 1.34 1.89 1.37 1.90 2.05 1.39 1.93 2.34 1.71 1.95 1.96 2.83 2.20 2.62 2.29 1.63 2.95 1.53 1.91 1.53 1.39 3.33      1.06
# 48  1.20 1.63 2.28 2.17 1.37 1.70 1.78 0.90 2.18 2.55 1.22 1.48 1.77 1.73 2.04 1.34 1.56 1.48 1.12 1.87 1.40 1.05 2.13 0.98 1.08 0.99 1.11 0.98 1.39 1.00 1.11 1.34 1.21 2.06 1.20 1.80 1.11 1.75 1.83 1.05 2.17 0.93 1.01 0.64 1.20 2.52 1.71
#
#mean global bb    RMSD:  0.98 +/-  0.40 A  ( 0.10.. 2.19 A)
#mean global heavy RMSD:  1.75 +/-  0.51 A  ( 0.54.. 3.33 A)


