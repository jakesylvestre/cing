from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.forkoff import do_cmd
from cing.NRG.CasdNmrMassageCcpnProject import * #@UnusedWildImport
from cing.Scripts.validateEntry import * #@UnusedWildImport
from cing.core.constants import * #@UnusedWildImport


def main(entryId, *extraArgList):
    """inputDir may be a directory or a url. A url needs to start with http://.
    """

    fastestTest = 1 # default: False
#    ranges=AUTO_STR # default is None retrieved from DBMS csv files.
    htmlOnly = False # default: False but enable it for faster runs without some actual data.
    doWhatif = True # disables whatif actual run
    doProcheck = True
    doWattos = True
    doTalos = True
    doStoreCheck = True # DEFAULT: True Requires sqlAlchemy
    tgzCing = True # default: True # Create a tgz for the cing project. In case of a CING project input it will be overwritten.
    modelCount = None # default setting is None
    if fastestTest:
        modelCount = 3
        htmlOnly = True
        doWhatif = False
        doProcheck = False
        doWattos = False
        doTalos = False
    FORCE_REDO = True
    FORCE_RETRIEVE_INPUT = True


    NTmessage(header)
    NTmessage(getStartMessage())

    expectedArgumentList = [ 'inputDir', 'outputDir', 'pdbConvention', 'restraintsConvention', 'archiveType', 'projectType' ]
    expectedNumberOfArguments = len(expectedArgumentList)
    if len(extraArgList) != expectedNumberOfArguments:
        NTerror("Got arguments: " + `extraArgList`)
        NTerror("Failed to get expected number of arguments: %d got %d" % (
            expectedNumberOfArguments, len(extraArgList)))
        NTerror("Expected arguments: %s" % expectedArgumentList)
        return True

    entryCodeChar2and3 = entryId[1:3]

    inputDir = extraArgList[0]
    outputDir = os.path.join(extraArgList[1], DATA_STR, entryCodeChar2and3, entryId)
    pdbConvention = extraArgList[2] #@UnusedVariable
    restraintsConvention = extraArgList[3]
    archiveType = extraArgList[4]
    projectType = extraArgList[5]

    if archiveType == ARCHIVE_TYPE_FLAT:
        pass
        # default
    elif archiveType == ARCHIVE_TYPE_BY_ENTRY:
        inputDir = os.path.join(inputDir, entryId)
    elif archiveType == ARCHIVE_TYPE_BY_CH23:
        inputDir = os.path.join(inputDir, entryCodeChar2and3)
    elif archiveType == ARCHIVE_TYPE_BY_CH23_BY_ENTRY:
        inputDir = os.path.join(inputDir, entryCodeChar2and3, entryId)

    targetId = getTargetForFullEntryName(entryId)
    if not targetId:
        NTerror("Failed to getTargetForFullEntryName for entryId: %s" % entryId)
        return True
    ranges = getRangesForTarget(targetId)
    if ranges == None:
        NTerror("Failed to getRangesForTarget for targetId: %s" % targetId)
        return True


    NTdebug("Using:")
    NTdebug("inputDir:             %s" % inputDir)
    NTdebug("outputDir:            %s" % outputDir)
    NTdebug("pdbConvention:        %s" % pdbConvention)
    NTdebug("restraintsConvention: %s" % restraintsConvention)
    NTdebug("archiveType:          %s" % archiveType)
    NTdebug("projectType:          %s" % projectType)
    NTdebug("modelCount:           %s" % modelCount)
    NTdebug("ranges:               %s" % ranges)
    # presume the directory still needs to be created.
    cingEntryDir = entryId + ".cing"

    if os.path.isdir(cingEntryDir):
        if FORCE_REDO:
            NTmessage("Enforcing a redo")
            rmtree(cingEntryDir)
        else:
            mainIndexFile = os.path.join(cingEntryDir, "index.html")
            isDone = os.path.isfile(mainIndexFile)
            if isDone:
                NTmessage("SKIPPING ENTRY ALREADY DONE")
                return
            NTmessage("REDOING BECAUSE VALIDATION CONSIDERED NOT DONE.")
            rmtree(cingEntryDir)
        # end if.
    # end if.

    os.chdir(outputDir)

    project = Project(entryId)
    if project.removeFromDisk():
        NTerror("Failed to remove existing project (if present)")
        return True
    # end if.

#    extension = '.tgz'
    formatFileName = '%s.tgz'
#    fileNameTgz = entryId + '.tgz'
    if projectType == PROJECT_TYPE_CING:
#        fileNameTgz = entryId + '.cing.tgz'
        formatFileName = '%s.cing.tgz'
    elif projectType == PROJECT_TYPE_PDB:
        formatFileName = 'pdb%s.ent.gz'
    fileNameTgz = formatFileName % entryId

#    NTdebug("fileNameTgz: %s" % fileNameTgz)
    # if true will do retrieveTgzFromUrl.
    if inputDir.startswith("http") or inputDir.startswith("file"):
        stillToRetrieve = False
        if os.path.exists(fileNameTgz):
            if FORCE_RETRIEVE_INPUT:
                os.unlink(fileNameTgz)
                stillToRetrieve = True
            # end if
        else:
            stillToRetrieve = True
        # end if
        if stillToRetrieve:
             retrieveTgzFromUrl(entryId, inputDir, archiveType=archiveType, formatFileName=formatFileName)
        # end if
        if not os.path.exists(fileNameTgz):
            NTerror("Tgz should already have been present skipping entry")
            return
        # end if
    # end if.
#            retrieveTgzFromUrl(entryId, inputDir)

    if projectType == PROJECT_TYPE_CING:
        # Needs to be copied because the open method doesn't take a directory argument..
        fullFileNameTgz = os.path.join(inputDir, fileNameTgz)
        shutil.copy(fullFileNameTgz, '.')
        project = Project.open(entryId, status='old')
        if not project:
            NTerror("Failed to init old project")
            return True
    elif projectType == PROJECT_TYPE_CCPN:
        project = Project.open(entryId, status='new')
        if not project.initCcpn(ccpnFolder=fileNameTgz, modelCount=modelCount):
            NTerror("Failed to init project from ccpn")
            return True
    elif projectType == PROJECT_TYPE_PDB:
        project = Project.open(entryId, status='new')
#        pdbFileFormats = [ entryId + ".pdb", "pdb" + entryId + ".ent.gz" ]
#        for pdbFileName in pdbFileFormats:
#        pdbFileName = "pdb" + entryId + ".ent.gz"
#        #    pdbFilePath = os.path.join( inputDir, pdbFileName)
#            pdbFilePath = os.path.join(inputDir, pdbFileName)
#            if os.path.exists(pdbFilePath):
#                break
#        tmpPdbFile = None
#        if pdbFileName.endswith('.gz'):
        pdbFilePath = entryId + ".pdb"
#        tmpPdbFile = pdbFilePath
#        if os.path.exists(pdbFilePath):
#            os.unlink(pdbFilePath)
        gunzip(fileNameTgz, outputFileName=pdbFilePath, removeOriginal=True)
        project.initPDB(pdbFile=pdbFilePath, convention=IUPAC, nmodels=modelCount)
#        if tmpPdbFile:
        if True:
            NTdebug("Removing tmp: %s" % pdbFilePath)
            os.unlink(pdbFilePath)


    elif projectType == PROJECT_TYPE_CYANA:
        project = Project.open(entryId, status='new')
        pdbFileName = entryId + ".pdb"
    #    pdbFilePath = os.path.join( inputDir, pdbFileName)
        pdbFilePath = os.path.join(inputDir, pdbFileName)

        if True:
            pdbConvention = IUPAC
            if entryId.startswith("1YWUcdGMP"):
                pdbConvention = XPLOR
            if entryId.startswith("2hgh"):
                pdbConvention = CYANA
            if entryId.startswith("1tgq"):
                pdbConvention = PDB
        project.initPDB(pdbFile=pdbFilePath, convention=pdbConvention, nmodels=modelCount)
        NTdebug("Reading files from directory: " + inputDir)
        kwds = {'uplFiles': [ entryId ],
                'acoFiles': [ entryId ]
                  }

        if entryId.startswith("1YWUcdGMP"):
            del(kwds['acoFiles'])

        if os.path.exists(os.path.join(inputDir, entryId + ".prot")):
            if os.path.exists(os.path.join(inputDir, entryId + ".seq")):
                kwds['protFile'] = entryId
                kwds['seqFile'] = entryId
            else:
                NTerror("Failed to find the .seq file whereas there was a .prot file.")

        # Skip restraints if absent.
        if os.path.exists(os.path.join(inputDir, entryId + ".upl")):
            project.cyana2cing(cyanaDirectory=inputDir,
                               convention=restraintsConvention,
                               copy2sources=True,
                               nmodels=modelCount,
                               **kwds)

#    if inputDirOrg == inputDirCASD_NMR:
#    if True: # Default is False for this is specific to CASD-NMR
#        NTmessage("Renaming molecule name to entry id: %s" % entryId)
#        project.molecule.name = entryId # insufficient since all data is already initialized to disk.
#        project.updateProject()
#        project.molecule.rename( entryId )

#    project.save()
#    project.molecule.ranges = ranges # JFD: this doesn't seem to be set there exactly.
    project.molecule.superpose(ranges=ranges)
    if True:
        if project.validate(htmlOnly=htmlOnly, ranges=ranges, doProcheck=doProcheck, doWhatif=doWhatif,
                doWattos=doWattos, doTalos=doTalos):
            NTerror("Failed to validate project read")
            return True

#    if True:
#        project.runRpf(
#           doAlised=DEFAULT_CONSIDER_ALIASED_POSITIONS,
#           distThreshold=DEFAULT_DISTANCE_THRESHOLD,
#           prochiralExclusion=DEFAULT_PROCHIRAL_EXCLUSION_SHIFT,
#           diagonalExclusion=DEFAULT_DIAGONAL_EXCLUSION_SHIFT
#    )

    if doStoreCheck:
        if doStoreCING2db( entryId, ARCHIVE_CASD_ID, project=project):
            NTerror("Failed to store CING project's data to DB but continuing.")

    project.save()
    if projectType == PROJECT_TYPE_CCPN:
#        fileNameTgz = entryId + '.tgz'
#        os.unlink(fileNameTgz) # temporary ccpn tgz
        rmdir(entryId) # temporary ccpn dir

    if tgzCing:
        directoryNameCing = entryId + ".cing"
        tgzFileNameCing = directoryNameCing + ".tgz"
        if os.path.exists(tgzFileNameCing):
            NTwarning("Overwriting: " + tgzFileNameCing)
        cmd = "tar -czf %s %s" % (tgzFileNameCing, directoryNameCing)
        do_cmd(cmd)


if __name__ == "__main__":
    cing.verbosity = verbosityDebug

#        sys.exit(1) # can't be used in forkoff api
    try:
        status = main(*sys.argv[1:])
    finally:
        NTmessage(getStopMessage(cing.starttime))
