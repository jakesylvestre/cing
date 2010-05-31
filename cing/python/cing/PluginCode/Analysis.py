from cing import __author__
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.required.reqAnalysis import ANALYSIS_STR
from traceback import format_exc

__author__ += 'Tim Stevens '

if True: # for easy blocking of data, preventing the code to be resorted with imports above.
    switchOutput(False)
    try:
        from ccpnmr.analysis.Version import version #@UnusedImport
        from ccpnmr.analysis.core.ExperimentBasic import getThroughSpacePeakLists
        from cing.Scripts.Analysis.PyRPF import calcRPF
        from cing.Scripts.Analysis.PyRPF import DEFAULT_DISTANCE_THRESHOLD
        from cing.Scripts.Analysis.PyRPF import DEFAULT_PROCHIRAL_EXCLUSION_SHIFT
        from cing.Scripts.Analysis.PyRPF import DEFAULT_DIAGONAL_EXCLUSION_SHIFT
        from cing.Scripts.Analysis.PyRPF import getEnsembles
        from cing.Scripts.Analysis.PyRPF import getNoeTolerances
        from cing.PluginCode.required.reqCcpn import CCPN_LOWERCASE_STR
    except:
        switchOutput(True)
        raise ImportWarning(ANALYSIS_STR)
    finally: # finally fails in python below 2.5
        switchOutput(True)
#    NTdebug('Imported plugin Analysis version %s' % version)
"""
    Adds Analysis functionality.
"""

class Analysis:
    def __init__(self, project):
        self.project = project

    def runRpf(self,
               doAlised=False,
               distThreshold=DEFAULT_DISTANCE_THRESHOLD,
               prochiralExclusion=DEFAULT_PROCHIRAL_EXCLUSION_SHIFT,
               diagonalExclusion=DEFAULT_DIAGONAL_EXCLUSION_SHIFT
               ):
        """
        Return None on error.
        It's not an error to have no peak list.
        """

        NTmessage("Starting cing.PluginCode.Analysis#runRpf")

        if not hasattr(self.project, CCPN_LOWERCASE_STR):
            NTerror("Failed to find ccpn attribute project. Happens when no CCPN project was read first.") # TODO: change when cing to ccpn code works.
            return

        self.ccpnProject = self.project[ CCPN_LOWERCASE_STR ]
        ccpnProject = self.ccpnProject
        if not ccpnProject:
            NTmessage("Failed to find ccpn project.")
            return

        # Find and print this peakList in the CCPN data model.
        peakLists = getThroughSpacePeakLists(ccpnProject)
        if not peakLists:
            NTwarning("No peak list found; skipping runRpf")
            return
        NTmessage( 'Peaklists: [%s]' % peakLists )

#        peakLists = [pl for pl in self.peakListTable.objectList if pl.rpfUse]
#        ensembles = [e for e in self.ensembleTable.objectList if e.rpfUse]
        ensembles = getEnsembles(ccpnProject)
        if not ensembles:
            NTwarning("No ensemble found; skipping runRpf")
            return

        for ensemble in ensembles:
            NTdebug("Using ensemble: %s " % str(ensemble))
            ensemble.rpfUse = True # set the selection automatically.
        # end for

        tolerances = []
        for peakList in peakLists:
            tolerance = getNoeTolerances(peakList)
            tolerances.append(tolerance)
            NTdebug("Using peakList.dataSource.name: %s with tolerance: %s" % (peakList.dataSource.name,str(tolerance)))
#            peakList[RPF_USE] = True # set the selection automatically.
            peakList.rpfUse = True # set the selection automatically.
        # end for

        #Instead of polluting the RPF code simply prevent it from crashing CING by wrapping the functionality in a try block.
        validResultStores = None
        try:
            validResultStores = calcRPF(ensembles, peakLists,
                                      tolerances,
                                      distThreshold,
                                      prochiralExclusion,
                                      diagonalExclusion,
                                      doAlised)
#            self.updateResultsTable()
            NTdebug("validResultStores: %s" % str(validResultStores))
        except:
            NTexception(format_exc())
        # end try
        return validResultStores
    # end def
# end class

def runRpf(project):
    '''Descrn:
       Inputs:
    '''
    analysis = Analysis(project=project)
    if not analysis.runRpf():
        NTerror("Analysis: Failed runRpf")
        return None
    return project


# register the function
methods = [ (runRpf, None),
           ]