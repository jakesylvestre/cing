"""
Takes a file with dihedral angles values and converts them to a python pickle file
with histograms for (combined) residue and sec. struct. types.

Unlike convertD1D2_2Db this script collects the data into a different data structure.

Because of the symmetry between the x/y axes in the d1d2 plot the axes can be compiled
together per residue type vs residue type pair (e.g. Pro (i-1)/Gly(i) and then convoluted  with
another; e.g. Gly(i)/Ala(i+1) to get the d1d2 plot for a triple Pro (i-1)/Gly(i)/Ala(i+1)
Run:
python $CINGROOT/python/cing/Scripts/convertD1D2_2Db2.py
"""

from cing import cingDirData
from cing import cingDirTmp
from cing import verbosityDebug
from cing import verbosityOutput
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTsort
from cing.Libs.NTutils import NTwarning
from cing.Libs.NTutils import appendDeepByKeys
from cing.Libs.NTutils import floatParse
from cing.Libs.NTutils import getDeepByKeys
from cing.Libs.NTutils import getEnsembleAverageAndSigmaFromHistogram
from cing.Libs.NTutils import gunzip
from cing.Libs.NTutils import setDeepByKeys
from cing.Libs.fpconst import isNaN
from cing.PluginCode.required.reqDssp import to3StateUpper
from cing.Scripts.getPhiPsiWrapper import BFACTOR_COLUMN
from cing.Scripts.getPhiPsiWrapper import DEFAULT_BFACTOR_PERCENTAGE_FILTER
from cing.Scripts.getPhiPsiWrapper import DEFAULT_MAX_BFACTOR
from cing.Scripts.getPhiPsiWrapper import IDX_COLUMN
from cing.core.database import NTdb
from cing.core.molecule import common20AAList
from cing.core.validate import binCount
from cing.core.validate import bins360
from cing.core.validate import plotparams360
from cing.core.validate import xGrid360
from cing.core.validate import yGrid360
from matplotlib.pyplot import hist
from numpy.ma.core import multiply
from numpy.matrixlib.defmatrix import mat
import cPickle
import cing
import csv
import os



file_name_base = 'cb4ncb4c_wi_db'
#file_name_base2 = 'cb4ncb4c_wi_db2'
# .gz extension is appended in the code.
cvs_file_name = file_name_base + '.csv'
dbase_file_name = file_name_base + '.dat'
dir_name = os.path.join(cingDirData, 'PluginCode', 'WhatIf')
cvs_file_abs_name = os.path.join(dir_name, cvs_file_name)
dbase_file_abs_name = os.path.join(dir_name, dbase_file_name)

plotparams1 = plotparams360
plotparams2 = plotparams360
xRange = (plotparams1.min, plotparams1.max)
yRange = (plotparams2.min, plotparams2.max)
isRange360=True
xGrid,yGrid = xGrid360,yGrid360
bins = bins360

os.chdir(cingDirTmp)

lineCountMax = 1000 * 1000 * 100 # in fact only 1 M lines
#lineCountMax = 2 # testing order

def main():
    cvs_file_abs_name_gz = os.path.join(cingDirData, 'PluginCode', 'Whatif', cvs_file_abs_name + '.gz')
    gunzip(cvs_file_abs_name_gz)
    reader = csv.reader(open(cvs_file_abs_name, "rb"), quoting=csv.QUOTE_NONE)
    valueBySsAndResTypes = {}
    valueByResTypes = {}
    valueBySs = {}
    histd1CtupleBySsAndResTypes = {}
    value = [] # NB is an array without being keyed.

    histd1BySsAndResTypes = {}
    histd1ByResTypes = {}
    histd1BySs = {}


    linesByEntry = {}
    lineCount = 0
    for row in reader:
        lineCount += 1
        if lineCount > lineCountMax:
            break
        entryId = row[0]
        if not linesByEntry.has_key(entryId):
            linesByEntry[ entryId ] = []
        linesByEntry[ entryId ].append( row )

    skippedResTypes = []
    entryIdList = linesByEntry.keys()
    entryIdList.sort()

    # Do some pre filtering.
    for entryId2 in entryIdList:
        lineList = linesByEntry[ entryId2 ]
        for idx,line in enumerate(lineList):
            line.append(idx)
        lineListSorted = NTsort(lineList,BFACTOR_COLUMN,inplace=False)
        # Now throw away the worst 10 % of residues.
        n = len(lineListSorted)
        bad_count = int(round((n * DEFAULT_BFACTOR_PERCENTAGE_FILTER) / 100.))
        to_remove_count = n-bad_count
        NTmessage("Removing at least %d from %d residues" % (bad_count,n))
        badIdxList = [lineItem[IDX_COLUMN] for lineItem in lineListSorted[to_remove_count:n]]
        iList = range(n)
        iList.reverse()
        for i in iList:
            lineItem = lineList[i]
            max_bfactor = float(lineItem[BFACTOR_COLUMN])
            if max_bfactor > DEFAULT_MAX_BFACTOR:
                NTdebug('Skipping because max bfactor of atoms in dihedral %.3f is above %.3f %s' % (max_bfactor, DEFAULT_MAX_BFACTOR, lineItem))
                del lineList[i] # TODO: check if indexing is still right or we shoot in the foot.
                continue
            if i in badIdxList:
                NTdebug('Skipping because bfactor worst %.3f %s' % (max_bfactor, lineItem))
                del lineList[i]
                continue
        removed_count = n - len(lineList)
        NTdebug("Reduced list by %d" % removed_count)
        if removed_count < bad_count:
            NTwarning("Failed to remove at least %d residues" % bad_count)

    for entryId2 in entryIdList:
        prevChainId = None
        prevResType = None
        prevResNum = None
        for row in linesByEntry[ entryId2 ]:
    #1zzk,A,GLN ,  17,E, 205.2, 193.6
    #1zzk,A,VAL ,  18,E, 193.6, 223.2
    #1zzk,A,THR ,  19,E, 223.2, 190.1
            (entryId, chainId, resType, resNum, ssType, d1, _d2, _max_bfactor, _idx) = row
            resNum = int(resNum)
            ssType = to3StateUpper(ssType)[0]
            resType = resType.strip()
            db = NTdb.getResidueDefByName( resType )
            if not db:
                NTerror("resType not in db: %s" % resType)
                return
            resType = db.nameDict['IUPAC']
            d1 = d1.strip()
            d1 = floatParse(d1)
            if isNaN(d1):
                NTdebug("d1 %s is a NaN on row: %s" % (d1,row))
                continue
            if not inRange(d1):
                NTerror("d1 not in range for row: %s" % `row`)
                return

            if not (resType in common20AAList):
    #            NTmessage("Skipping uncommon residue: %s" % resType)
                if not ( resType in skippedResTypes):
                    skippedResTypes.append( resType )
                continue
            if isSibling(chainId, resNum, prevChainId, prevResNum):
                appendDeepByKeys(valueBySsAndResTypes, d1, ssType, resType, prevResType)
                appendDeepByKeys(valueByResTypes, d1, resType, prevResType)
                appendDeepByKeys(valueBySs, d1, ssType)
                value.append( d1 )
            prevResType = resType
            prevResNum = resNum
            prevChainId = chainId

    os.unlink(cvs_file_abs_name)
    NTmessage("Skipped skippedResTypes: %r" % skippedResTypes )
    NTmessage("Got count of values: %r" % len(value) )
    # fill FOUR types of hist.
    # TODO: filter differently for pro/gly
    keyListSorted1 = valueBySsAndResTypes.keys();
    keyListSorted1.sort()
    for ssType in keyListSorted1:
        d1List = valueBySs[ssType]
        if not d1List:
            NTerror("Expected d1List from valueBySs[%s]" % (ssType))
            continue
        hist1d, _bins, _patches = hist(d1List, bins=binCount, range=xRange)
        NTmessage("Count %6d in valueBySs[%s]" % (sum(hist1d), ssType))
        setDeepByKeys(histd1BySs, hist1d, ssType)

        keyListSorted2 = valueBySsAndResTypes[ssType].keys();
        keyListSorted2.sort()
        for resType in keyListSorted2:
            NTmessage("Working on valueBySsAndResTypes for [%s][%s]" % (ssType, resType)) # nice for balancing output verbosity.
            keyListSorted3 = valueBySsAndResTypes[ssType][resType].keys();
            keyListSorted3.sort()
            for prevResType in keyListSorted3:
#                NTmessage("Working on valueBySsAndResTypes[%s][%s][%s]" % (ssType, resType, prevResType))
                d1List = valueBySsAndResTypes[ssType][resType][prevResType]
                if not d1List:
                    NTerror("Expected d1List from valueBySsAndResTypes[%s][%s][%s]" % (ssType, resType, prevResType))
                    continue
                hist1d, _bins, _patches = hist(d1List, bins=binCount, range=xRange)
#                NTmessage("Count %6d in valueBySsAndResTypes[%s][%s][%s]" % (sum(hist1d), ssType, resType, prevResType))
                setDeepByKeys(histd1BySsAndResTypes, hist1d, ssType, resType, prevResType)
        # Now that they are all in we can redo this.
        for resType in keyListSorted2:
            NTmessage("Working on valueBySsAndResTypes for [%s][%s]" % (ssType, resType)) # nice for balancing output verbosity.
            keyListSorted3 = valueBySsAndResTypes[ssType][resType].keys();
            keyListSorted3.sort()
            for resTypePrev in keyListSorted3:
                keyListSorted4 = keyListSorted3[:] # take a copy
                for resTypeNext in keyListSorted4:
                    hist1 = getDeepByKeys(histd1BySsAndResTypes, ssType, resType, resTypePrev)
                    hist2 = getDeepByKeys(histd1BySsAndResTypes, ssType, resTypeNext, resType)
                    if hist1 == None:
                        NTdebug('skipping for hist1 is empty for [%s] [%s] [%s]' % (ssType, resTypePrev, resType))
                        continue
                    if hist2 == None:
                        NTdebug('skipping for hist2 is empty for [%s] [%s] [%s]' % (ssType, resType, resTypeNext))
                        continue
                    m1 = mat(hist1,dtype='float')
                    m2 = mat(hist2,dtype='float')
                    m2 = m2.transpose()
                    hist2d = multiply(m1,m2)

                    cTuple = getEnsembleAverageAndSigmaFromHistogram( hist2d )
                    (c_av, c_sd) = cTuple
                    NTdebug("For ssType %s residue type %s found (c_av, c_sd) %8.3f %s" %(ssType,resType,c_av,`c_sd`))
                    if c_sd == None:
                        NTdebug('Failed to get c_sd when testing not all residues are present in smaller sets.')
                        continue
                    if c_sd == 0.:
                        NTdebug('Got zero c_sd, ignoring histogram. This should only occur in smaller sets. Not setting values.')
                        continue
                    setDeepByKeys( histd1CtupleBySsAndResTypes, cTuple, ssType, resType, resTypePrev, resTypeNext)

    keyListSorted1 = valueByResTypes.keys();
    keyListSorted1.sort()
    for resType in keyListSorted1:
        keyListSorted2 = valueByResTypes[resType].keys();
        keyListSorted2.sort()
        for prevResType in keyListSorted2:
            d1List = valueByResTypes[resType][prevResType]
            if not d1List:
                NTerror("Expected d1List from valueByResTypes[%s][%s]" % (resType, prevResType))
                continue
            hist1d, _bins, _patches = hist(d1List, bins=binCount, range=xRange)
#            NTmessage("Count %6d in valueByResTypes[%s][%s]" % (sum(hist1d), resType, prevResType))
            setDeepByKeys(histd1ByResTypes, hist1d, resType, prevResType)

    histd1, _bins, _patches = hist(value, bins=binCount, range=xRange)
    NTmessage("Count %6d in value" % sum(histd1))
#    setDeepByKeys(histd1, hist1d, resType, prevResType)

    if os.path.exists(dbase_file_abs_name):
        os.unlink(dbase_file_abs_name)
    output = open(dbase_file_abs_name, 'wb')
    dbase = {}
    dbase[ 'histd1BySsAndResTypes' ] = histd1BySsAndResTypes # 92 kb uncompressed in the case of ~1000 lines only
    dbase[ 'histd1CtupleBySsAndResTypes' ] = histd1CtupleBySsAndResTypes
    dbase[ 'histd1ByResTypes' ] = histd1ByResTypes # 56 kb
    dbase[ 'histd1BySs' ] = histd1BySs # 4 kb
    dbase[ 'histd1' ] = histd1 #  4 kb

    cPickle.dump(dbase, output, -1)
    output.close()


def inRange(a):
    if a < plotparams1.min or a > plotparams1.max:
        return False
    return True

def isSibling(chainId, resNum, prevChainId, prevResNum):
    if prevResNum == None:
        return False
    if prevChainId == None:
        return False
    if resNum != prevResNum + 1:
        return False
    if chainId != prevChainId:
        return False
    return True

if __name__ == '__main__':
    cing.verbosity = verbosityOutput
    cing.verbosity = verbosityDebug
    main()
#    testEntry()