from cing import __author__
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.required.reqCcpn import CCPN_LOWERCASE_STR

__author__ += 'Wim Vranken '

class NmrStar():
    def __init__(self, project):
        self.project = project
        self.ccpnProject = None

    def _nullCcpnAndCingProject(self):
        del( self.ccpnProject ) # hopefull forces GC.
        del( self.project ) # hopefull forces GC.
        self.ccpnProject = None
        self.project = None

    def toNmrStarFile(self, fileName):
        """Return None on error"""

#        NTdebug("starting toNmrStarFile")

        if not hasattr(self.project, CCPN_LOWERCASE_STR):
            NTdebug("Failed to find ccpn attribute project. Happens when no CCPN project was read first.")
#            cwd = os.getcwd()
#            ccpnFolder = os.path.join(cwd, self.project.name + '.tgz')
#            if os.path.exists(ccpnFolder):
#                NTdebug("Found parallel parked tgz with ccpn project.")
#                self.project.ccpnFolder = ccpnFolder
#            else:
#                NTmessage("No parallel parked directory or tgz with ccpn project found.")
            return

        self.ccpnProject = self.project[ CCPN_LOWERCASE_STR ]
        if not self.ccpnProject:
            NTmessage("Failed to find ccpn project. This is normal if CING project didn't contain one previously generated.")
            return

        ccpnFolder = self.project.ccpnFolder
        if ccpnFolder.endswith(".tgz") or ccpnFolder.endswith(".tar.gz"):
            head, tail = os.path.split(ccpnFolder)
            print head, tail
            baseNameList = tail.split('.')
            print "baseNameList %s" % baseNameList
            baseName = baseNameList[0]
            ccpnFolder = os.path.join(head, baseName)
        if not ccpnFolder:
            NTerror("No CCPN project folder defined thus no NmrStar export possible.")
            return

        if not os.path.exists(ccpnFolder):
            NTerror("No CCPN project folder available at [%s] thus no NmrStar export possible." % ccpnFolder)
            return

        inputDir, projectName = os.path.split(ccpnFolder)
        if inputDir == '':
            inputDir = '.'
        if projectName == '':
            NTerror("Failed to get ccpnProjectName from: ccpnProject.ccpnFolder [%s]" % self.ccpnProject.ccpnFolder)
            return

        if os.path.exists(fileName):
            os.unlink(fileName)

        if not fileName.endswith('.str'):
            NTerror("Failed to get a descent str file name from: [%s]" % fileName)
            return

        outputDir, tail = os.path.split(fileName)
        if outputDir == '':
            outputDir = '.'
        if tail == '':
            NTerror("Failed to get a descent str file name from: [%s]" % fileName)
            return

        scriptFileName = "$CINGROOT/python/cing/Scripts/FC/convertCcpn2Nmrstar.py"
        logFileName = tail.replace(".str", "")
        logFileName += "_convertCcpn2Nmrstar.log"
        convertProgram = ExecuteProgram("python -u %s" % scriptFileName,
                rootPath = outputDir, redirectOutputToFile = logFileName)
        NTmessage("==> Running Wim Vranken's FormatConverter from script %s" % scriptFileName )
        exitCode = convertProgram("%s %s %s" % (projectName, inputDir, fileName))
        if exitCode:
            NTerror("Failed convertProgram with exit code: " + `exitCode`)
            return
        if not os.path.exists(fileName):
            NTerror("Failed to find result file [%s]" % fileName)
            return
        NTmessage("==> NMR-STAR project written at %s" % fileName)

        try:
            self._nullCcpnAndCingProject()
        except:
            NTcodeerror( "Failed to nullCcpnProject()" )

        return True # Just to be explicit.