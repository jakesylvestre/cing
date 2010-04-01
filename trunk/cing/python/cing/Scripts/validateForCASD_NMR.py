# python -u $CINGROOT/python/cing/Scripts/validateForENmrWorkshop.py
from cing import cingDirScripts
from cing.NRG import CASD_NMR_BASE_NAME
from cing.NRG.PDBEntryLists import writeEntryListToFile
from cing.Scripts.doScriptOnEntryList import doScriptOnEntryList
from cing.Scripts.validateEntry import ARCHIVE_TYPE_BY_CH23_BY_ENTRY
from cing.Scripts.validateEntry import PROJECT_TYPE_CCPN
import cing
import os

cing.verbosity = cing.verbosityDebug
#cing.verbosity = cing.verbosityDefault

# parameters for doScriptOnEntryList
startDir = '/Library/WebServer/Documents/%s' % CASD_NMR_BASE_NAME
pythonScriptFileName = os.path.join(cingDirScripts, 'validateEntry.py')
#entryListFileName = os.path.join(startDir, 'entry_list_108d.csv')
#entryListFileName = os.path.join(startDir, 'list', 'entry_list.csv')
entryListFileName = os.path.join(startDir, 'list', 'entry_list_single.csv')
#entryListFileName = os.path.join('/Users/jd', 'entryCodeList.csv')
#entryListFileName = os.path.join('/Users/jd', 'entryCodeList-Oceans14.csv')

# parameters for validateEntry
#inputDir              = '/Users/jd/wattosTestingPlatform/nozip/data/structures/all/pdb'
#inputDir = 'file://Library/WebServer/Documents/NRG-CING/recoordSync'

inputDirCASD_NMR = 'file:///Users/jd/%s/dataDivided' % CASD_NMR_BASE_NAME
#inputDir = 'http://restraintsgrid.bmrb.wisc.edu/servlet_data/NRG_ccpn_tmp'
outputDir = startDir

extraArgList = (inputDirCASD_NMR, outputDir, '.', '.', ARCHIVE_TYPE_BY_CH23_BY_ENTRY, PROJECT_TYPE_CCPN)

# disable next line for regular run.
writeEntryListToFile(entryListFileName, ['NeR103AParis'])

doScriptOnEntryList(pythonScriptFileName,
                    entryListFileName,
                    startDir,
                    processes_max = 3,
                    delay_between_submitting_jobs = 5, # why is this so long? because of time outs at tang?
                    max_time_to_wait = 3600, # 1y4o took more than 600. This is one of the optional arguments.
                    # 1ai0 took over 20 min; let's set this to 1 hour
                    START_ENTRY_ID = 0,
                    MAX_ENTRIES_TODO = 1,
                    expectPdbEntryList = False,
                    extraArgList = extraArgList)