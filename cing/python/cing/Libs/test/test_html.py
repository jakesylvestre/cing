"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_html.py
"""
from cing import cingDirTmp
from cing import verbosityDebug
from cing.Libs import NTplot
from cing.Libs.NTplot import NTplotSet
from cing.Libs.html import HTML_TAG_PRE
from cing.Libs.html import HTML_TAG_PRE2
from cing.Libs.html import HTMLfile
from cing.Libs.html import MakeHtmlTable
from cing.Libs.html import image2DdihedralWidth
from cing.Libs.html import image2Ddihedralheight
from cing.Libs.html import removePreTagLines
from cing.core.classes import Project
from cing.core.molecule import Ensemble
from cing.core.molecule import Molecule
from unittest import TestCase
import cing
import os
import unittest

class AllChecks(TestCase):

    def testRemovePreTagLines(self):
        spuriousSpaceMsg = 'something     with     many spaces'
        msg = '\n'.join([HTML_TAG_PRE, spuriousSpaceMsg, HTML_TAG_PRE2 ])
        self.assertNotEquals(msg, spuriousSpaceMsg)
        self.assertEquals(removePreTagLines(msg), spuriousSpaceMsg)

    def setupSimplestProject(self):
        self.failIf(os.chdir(cingDirTmp),
                     msg="Failed to change to directory for temporary test files: " + cingDirTmp)
        entryId = 'test'
        project = Project(entryId)
        self.failIf(project.removeFromDisk())
        project = Project.open(entryId, status='new')
        molecule = Molecule(name='moleculeName')
        molecule.ensemble = Ensemble(molecule) # Needed for html.
        project.appendMolecule(molecule) # Needed for html.
        c = molecule.addChain('A')
        r1 = c.addResidue('ALA', 1, Nterminal=True)
        if r1:
            r1.addAllAtoms()

        molecule.updateAll()
        project.setupHtml() # Needed for creating the sub dirs.
        return project

    def testMakeHtmlTableWithJavascriptEnabled(self):
#        CSS and Javascript is going to determine much of the formatting.
        project = self.setupSimplestProject()
        h = HTMLfile(project.htmlPath('test.html'), project)
        columnFormats = [ ('col1', {}),
                          ('col2', {}),
                          ('col3', {})
                                 ]

        t = MakeHtmlTable(h.main, classId="testJsTable", id="testJsTableId", columnFormats=columnFormats,
                          bla="0")
        for row in t.rows(range(2)):
            rStr = str(row)
            t.nextColumn()
            t(None, rStr)
            t.nextColumn()
            t('a', rStr + "." + str(2), href='ttt')
            t.nextColumn()  # empty one
            t.nextColumn()
            t(None, rStr + "." + str(4))

        #end for
        h.render()

    def ttttestDihedralComboPlot(self):
        ps = NTplotSet() # closes any previous plots
        ps.hardcopySize = (image2DdihedralWidth, image2Ddihedralheight)
        dihedralName1 = 'PHI'
        dihedralName2 = 'PSI'
        projectName = 'testDihedralComboPlot'
        project     = Project(projectName)
        plotparams1 = project.plotParameters.getdefault(dihedralName1,'dihedralDefault')
        plotparams2 = project.plotParameters.getdefault(dihedralName1,'dihedralDefault')

        plot = NTplot(title=projectName,
          xRange=(plotparams1.min, plotparams1.max),
          xTicks=range(int(plotparams1.min), int(plotparams1.max + 1), plotparams1.ticksize),
          xLabel=dihedralName1,
          yRange=(plotparams2.min, plotparams2.max),
          yTicks=range(int(plotparams2.min), int(plotparams2.max + 1), plotparams2.ticksize),
          yLabel=dihedralName2)

        ps.addPlot(plot)
        ps.hardcopy(projectName, 'png')

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
