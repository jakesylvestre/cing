"""
--------------------------------------------------------------------------------
main.py: command line interface to the cing utilities:
--------------------------------------------------------------------------------

Some examples; all assume a project named 'test':

- To start a new Project using most verbose messaging:
cing --name test --new --verbosity 9

- To start a new Project from a xeasy seq file:
cing --name test --init AD.seq,CYANA

- To start a new Project from a xeasy seq file and load an xeasy prot file:
cing --name test --init AD.seq,CYANA --xeasy AD.seq,AD.prot,CYANA

- To start a new Project from a Ccpn project (new implementation):
cing --name test --initCcpn ccpn_project.xml

- To open an existing Project:
cing --name test

- To open an existing Project and load an xeasy prot file:
cing --name test --xeasy AD.seq,AD.prot,CYANA

- To open an existing Project and start an interactive python interpreter:
cing --name test --ipython

- To open an existing Project and run a script MYSCRIPT.py:
cing --name test --script MYSCRIPT.py

- To test CING without any messages (not even errors):
cing --test --verbose 0

- To test CING without any messages (not even errors):
cing --server [--port 8000]

--------------------------------------------------------------------------------
Some simple script examples:
--------------------------------------------------------------------------------

== merging several prot files ==
project.initResonances()      # removes all resonances from the project
project.importXeasy( 'N15.seq', 'N15.prot', 'CYANA' )
project.importXeasy( 'C15.seq', 'C15.prot', 'CYANA' )
project.importXeasy( 'aro.seq', 'aro.prot', 'CYANA' )
project.mergeResonances( status='reduce'  )

== Generating a peak file from shifts ==
project.listPredefinedExperiments() # list all predefined experiments
peaks = project.generatePeaks('hncaha','HN:HA:N')
format(peaks)

== Print list of parameters:
    formatall( project.molecule.A.residues[0].procheck ) # Adjust for your mols
    formatall( project.molecule.A.VAL171.C )
"""
#==============================================================================
from BaseHTTPServer import HTTPServer
from CGIHTTPServer import CGIHTTPRequestHandler
from cing import cingPythonCingDir
from cing import cingPythonDir
from cing import cingVersion
from cing import header
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTpath
from cing.Libs.NTutils import OptionParser
from cing.Libs.NTutils import findFiles
from cing.Libs.forkoff import ForkOff
from cing.core.classes import Project
from cing.core.molecule import Molecule
from cing.core.parameters import cingPaths
from cing.core.parameters import plugins
from cing.iCing.iCingServer import PORT_CGI
from cing.iCing.iCingServer import PORT_SERVER
from string import join
from cing.iCing.iCingServer import iCingServerHandler
import cing
import os
import sys
import unittest
#from cing.iCing.iCingServer import iCingServerHandler



#------------------------------------------------------------------------------------
# Support routines
#------------------------------------------------------------------------------------

def format( object ):
#    print '>>', object
    if hasattr(object,'format'):
        print object.format()
    else:
        print object
    #end if
#end def

def formatall( object ):
    if isinstance( object, list ):
        i = 0
        for obj in object:
            #printf(">>> [%d] >>> ", i)
            format( obj )
            i += 1
        #end for
    elif isinstance( object, dict ):
        for key,value in object.items():
            NTmessage("%-15s : ", key )
            format(value)
        #end for
    else:
        format( object )
    #end try
#end def

args = []
kwds = {}

def scriptPath( scriptFile ):
    # get path to scriptFile

    if not os.path.exists( scriptFile ):
        NTdebug('Missed in current working directory the script file: %s' % scriptFile)
        scriptsDir  = os.path.join( cingPythonCingDir, cingPaths.scripts)
        scriptFileAbs = os.path.join( scriptsDir, scriptFile)
        if not os.path.exists( scriptFileAbs ):
            NTerror('Missed in current working directory and Scripts directory\n'+
                    '[%s] the script file [%s]' % ( scriptsDir, scriptFile ))
            return None
        return scriptFileAbs
    #end if
    return scriptFile
#end def

def script( scriptFile, *a, **k ):
    # Hack to get arguments to routine as global variables to use in script
    global args
    global kwds
    args = a
    kwds = k

    path = scriptPath( scriptFile )
    if path:
        NTmessage('==> Executing script "%s"', path )
        execfile( path, globals() )
    #end if
#end def


def testOverall():
    # Use silent testing from top level.
#    cing.verbosity = verbosityError
    # Add the ones you don't want to test (perhaps you know they don't work yet)
    excludedModuleList = [ cingPythonDir + "/Cython*",
                           cingPythonDir + "/cyana2cing*",
#                           cingPythonDir + "/cing.PluginCode",
#                           cingPythonDir + "/cing.PluginCode.test.test_Whatif",
#                           cingPythonDir + "/cing.Scripts.test.test_cyana2cing",
#                           cingPythonDir + "/cing.STAR.FileTest",
                          ]
    namepattern, startdir = "test_*.py", cingPythonDir
    nameList = findFiles(namepattern, startdir, exclude=excludedModuleList)
    NTerror('will unit check: ' + `nameList`)
#    nameList = nameList[0:5]
#    namepattern = "*Test.py"
#    nameList2 = findFiles(namepattern, startdir)
#    for name in nameList2:
#      nameList.append(name)
    # translate: '/Users/jd/workspace/cing/python/cing/Libs/test/test_NTplot.py'
    # to: cing.Libs.test.test_NTplot
    lenCingPythonDirStr = len(cingPythonDir)
    for name in nameList:
        tailPathStr = name[lenCingPythonDirStr+1:-3]
        mod_name = join(tailPathStr.split('/'), '.')
#        if mod_name in excludedModuleList:
#            print "Skipping module:  " + mod_name
#            continue
        exec("import %s" % (mod_name)   )
        exec("suite = unittest.defaultTestLoader.loadTestsFromModule(%s)" % (mod_name)   )
        testVerbosity = 2
        unittest.TextTestRunner(verbosity=testVerbosity).run(suite) #@UndefinedVariable
        NTmessage('\n\n\n')

def serve():
    # Now the cgi python code is actually a part of the package.
    # The standard CGI handler assumes it to be in a "cgi-bin" subdir of the current working dir.
    localDir = os.path.join( cingPythonCingDir, "iCing" )
    os.chdir(localDir)
    NTmessage("Starting a server at port %s" % PORT_SERVER )
    httpd = HTTPServer(('', PORT_SERVER), iCingServerHandler )
#    NTmessage("Starting a CGI server at port %s in dir: %s" % ( PORT_CGI, localDir ))
    httpd_cgi = HTTPServer(('', PORT_CGI), CGIHTTPRequestHandler)
    year = 365*24*60*60
    f = ForkOff(
            processes_max           = 2,
            max_time_to_wait        = year, # leave the server up for a year.                
            verbosity               = cing.verbosity )
    job_0       = ( httpd.serve_forever, () )
    job_1       = ( httpd_cgi.serve_forever, () )
    job_list    = [ job_0, job_1 ]    
    done_list   = f.forkoff_start( job_list, delay_between_submitting_jobs=0 )    
    NTmessage("Finished forked ids: %s", done_list)
    
    NTmessage( 'Shutting down server' )        
    try:        
        httpd.socket.close()
        httpd_cgi.socket.close()
    except:
        pass
    try:
        httpd_cgi.socket.close() #@UndefinedVariable
    except:
        pass


project = None # after running main it will be filled.

def main():

    global project

    root,file,_ext  = NTpath( __file__ )
    usage          = "usage: cing [options]       use -h or --help for listing"

    #------------------------------------------------------------------------------------
    # Options
    #------------------------------------------------------------------------------------

    parser = OptionParser(usage=usage, version=cingVersion)
    parser.add_option("--test",
                      action="store_true",
                      dest="test",
                      help="Run set of test routines to verify installations"
                     )
    parser.add_option("--doc",
                      action="store_true",
                      dest="doc",
                      help="Print more documentation to stdout"
                     )
    parser.add_option("--docdoc",
                      action="store_true",
                      dest="docdoc",
                      help="Print full documentation to stdout"
                     )
    parser.add_option("-n", "--name", "--project",
                      dest="name", default=None,
                      help="NAME of the project (required)",
                      metavar="PROJECTNAME"
                     )
    parser.add_option("--gui",
                      action="store_true",
                      dest="gui",
                      help="Start graphical user interface"
                     )
    parser.add_option("--new",
                      action="store_true",
                      dest="new",
                      help="Start new project"
                     )
    parser.add_option("--old",
                      action="store_true",
                      dest="old",
                      help="Open a old project"
                     )
    parser.add_option("--init",
                      dest="init", default=None,
                      help="Initialize from SEQUENCEFILE[,CONVENTION]",
                      metavar="SEQUENCEFILE[,CONVENTION]"
                     )
    parser.add_option("--initPDB",
                      dest="initPDB", default=None,
                      help="Initialize from PDBFILE[,CONVENTION]",
                      metavar="PDBFILE[,CONVENTION]"
                     )
    parser.add_option("--initBMRB",
                      dest="initBMRB", default=None,
                      help="Initialize from edited BMRB file",
                      metavar="BMRBFILE"
                     )
    parser.add_option("--initCcpn",
                      dest="initCcpn", default=None,
                      help="Initialize from CCPNFILE",
                      metavar="CCPNFILE"
                     )
    parser.add_option("--xeasy",
                      dest="xeasy", default=None,
                      help="Import shifts from xeasy SEQFILE,PROTFILE,CONVENTION",
                      metavar="SEQFILE,PROTFILE,CONVENTION"
                     )
    parser.add_option("--xeasyPeaks",
                      dest="xeasyPeaks", default=None,
                      help="Import peaks from xeasy SEQFILE,PROTFILE,PEAKFILE,CONVENTION",
                      metavar="SEQFILE,PROTFILE,PEAKFILE,CONVENTION"
                     )
    parser.add_option("--merge",
                      action="store_true",
                      dest="merge",
                      help="Merge resonances"
                     )
    parser.add_option("--generatePeaks",
                      dest="generatePeaks", default = None,
                      help="Generate EXP_NAME peaks with AXIS_ORDER from the resonance data",
                      metavar="EXP_NAME,AXIS_ORDER"
                     )
    parser.add_option("--molecule",
                      dest="moleculeName", default=None,
                      help="Restore Molecule MOLECULENAME as active molecule",
                      metavar="MOLECULENAME"
                     )
    parser.add_option("--script",
                      dest="script", default=None,
                      help="Run script from SCRIPTFILE",
                      metavar="SCRIPTFILE"
                     )
    parser.add_option("--ipython",
                      action="store_true",
                      dest="ipython",
                      help="Start ipython interpreter"
                     )
    parser.add_option("--validate",
                      action="store_true", dest="validate", default=False,
                      help="Run doValidate.py script [in current or cing directory]"
                     )
    parser.add_option("--shiftx",
                      action="store_true", default=False,
                      dest="shiftx",
                      help="Predict with shiftx"
                     )
    parser.add_option("--ranges",
                      dest="ranges", default=None,
                      help="Ranges for superpose, procheck, validate etc; e.g. 503-547,550-598,800,801",
                      metavar="RANGES"
                     )
    parser.add_option("--superpose",
                      action="store_true", default=False,
                      dest="superpose",
                      help="Do superposition; optionally uses RANGES"
                     )
    parser.add_option( "--nosave",
                      action="store_true",
                      dest="nosave",
                      help="Don't save on exit (default: save)"
                     )
    parser.add_option( "--export", default=False,
                      action="store_true",
                      dest="export",
                      help="Export before exit (default: noexport)"
                     )
    parser.add_option("-v", "--verbosity", type='int',
                      default=cing.verbosityDefault,
                      dest="verbosity", action='store',
                      help="verbosity: [0(nothing)-9(debug)] no/less messages to stdout/stderr (default: 3)"
                     )
    parser.add_option( "--server",
                      action="store_true",
                      dest="server",
                      help="Start a server at port 8000 by default"
                     )

    (options, _args) = parser.parse_args()

    if options.verbosity >= 0 and options.verbosity <= 9:
#        print "In main, setting verbosity to:", options.verbosity
        cing.verbosity = options.verbosity
    else:
        NTerror("set verbosity is outside range [0-9] at: " + options.verbosity)
        NTerror("Ignoring setting")
    # From this point on code may be executed that will go through the appropriate verbosity filtering
    NTmessage(header)

    NTdebug('options: %s', options)
    NTdebug('args: %s', _args)

    # The weird location of this import is because we want it to be verbose.
    from cing.core.importPlugin import importPlugin # This imports all plugins    @UnusedImport

#    root,file,ext  = NTpath( __file__ )

    if options.test:
        testOverall()
        sys.exit(0)

    if options.server:
        serve()
        sys.exit(0)

    #------------------------------------------------------------------------------------
    # Extended documentation
    #------------------------------------------------------------------------------------
    if options.doc:
        parser.print_help(file=sys.stdout)
        print __doc__
        sys.exit(0)
    #end if

    #------------------------------------------------------------------------------------
    # Full documentation
    #------------------------------------------------------------------------------------
    if options.docdoc:
        print '=============================================================================='
        parser.print_help(file=sys.stdout)
        print __doc__

        print Project.__doc__
        for p in plugins.values():
            NTmessage(    '-------------------------------------------------------------------------------' +
                       'Plugin %s\n' +
                       '-------------------------------------------------------------------------------\n%s\n',
                        p.module.__file__, p.module.__doc__
                     )
        #end for

        print Molecule.__doc__
        sys.exit(0)
    #end if

    #------------------------------------------------------------------------------------
    # START
    #------------------------------------------------------------------------------------

    # GUI
    if options.gui:
        import Tkinter
        from cing.core.gui import CingGui

        root = Tkinter.Tk()

        popup = CingGui(root, options=options)
        popup.open()

        root.withdraw()
        root.mainloop()
        exit()
    #end if

    #check for the required name option
    parser.check_required('-n')

#    args = []
    _kwds = {}


    #------------------------------------------------------------------------------------
    # open project
    #------------------------------------------------------------------------------------
    if options.new:
        project = Project.open( options.name, status='new' )
    elif options.old:
        project = Project.open( options.name, status='old' )
    elif options.init:
        init = options.init.split(',')
        if (len(init) == 2):
            project = Project.open( options.name, status='new' )
            project.newMolecule( options.name, sequenceFile=init[0], convention = init[1] )
        else:
            project = Project.open( options.name, status='new' )
            project.newMolecule( options.name, sequenceFile=init[0] )
        #end if
    elif options.initPDB:
        init = options.initPDB.split(',')
        if (len(init) == 2):
            project = Project.open( options.name, status='new' )
            project.initPDB( pdbFile=init[0], convention = init[1] )
        else:
            project = Project.open( options.name, status='new' )
            project.initPDB( pdbFile=init[0] )
    elif options.initBMRB:
        project = Project.open( options.name, status='new' )
        project.initBMRB( bmrbFile = options.initBMRB, moleculeName = project.name )
    elif options.initCcpn:
    ##    init = options.initCcpn.split(',')
        project = Project.open( options.name, status='new' )
        project.initCcpn( ccpnFolder = options.initCcpn )
    else:
        project = Project.open( options.name, status='create' )

    if not project:
        NTdebug("Doing a hard system exit")
        sys.exit(2)
    #end if

    #------------------------------------------------------------------------------------
    # check for alternative molecule
    #------------------------------------------------------------------------------------
    if options.moleculeName:
        if options.moleculeName in project:
            project.molecule = project[options.moleculeName]
        else:
            project.restoreMolecule(options.moleculeName)
        #end if
    #end if

    NTmessage( project.format() )

    # shortcuts
    p   = project
    mol = project.molecule #@UnusedVariable
    m   = project.molecule #@UnusedVariable

#   pr = print
    f  = format #@UnusedVariable
    fa = formatall #@UnusedVariable

    #------------------------------------------------------------------------------------
    # Import xeasy protFile
    #------------------------------------------------------------------------------------
    if options.xeasy:
        xeasy = options.xeasy.split(',')
        if (len(xeasy) != 3):
            NTerror("--xeasy: SEQFILE,PROTFILE,CONVENTION arguments required")
        else:
            project.importXeasy(seqFile=xeasy[0], protFile=xeasy[1], convention=xeasy[2])

    #------------------------------------------------------------------------------------
    # Import xeasy peakFile
    #------------------------------------------------------------------------------------
    if options.xeasyPeaks:
        xeasy = options.xeasy.split(',')
        if (len(xeasy) != 4):
            NTerror("--xeasyPeaks: SEQFILE,PROTFILE,PEAKFILE,CONVENTION arguments required")
        else:
            project.importXeasyPeaks(seqFile=xeasy[0], protFile=xeasy[1], peakFile=xeasy[2],convention=xeasy[3])

    #------------------------------------------------------------------------------------
    # Merge resonances
    #------------------------------------------------------------------------------------
    if (options.merge):
        project.mergeResonances()
    #end if

    #------------------------------------------------------------------------------------
    # Generate peaks
    #------------------------------------------------------------------------------------
    if (options.generatePeaks):
        gp = options.generatePeaks.split(',')
        if len(gp) != 2:
            NTerror("--generatePeaks: EXP_NAME,AXIS_ORDER arguments required")
        else:
            peaks = project.generatePeaks( experimentName = gp[0], axisOrder = gp[1] ) #@UnusedVariable
        #end if
    #end if

    #------------------------------------------------------------------------------------
    # Shiftx
    #------------------------------------------------------------------------------------
    if options.shiftx:
        project.runShiftx()

    #------------------------------------------------------------------------------------
    # Superpose
    #------------------------------------------------------------------------------------
    if options.superpose:
        project.superpose(ranges=options.ranges)

    #------------------------------------------------------------------------------------
    # Validate; just run doValidate script
    #------------------------------------------------------------------------------------
    if options.validate:
        path = scriptPath('doValidate.py')
        if path:
            NTmessage('==> Executing script "%s"', path )
            execfile( path )
    #end if

    #------------------------------------------------------------------------------------
    # Script
    #------------------------------------------------------------------------------------
    if options.script:
        scriptFile = scriptPath( options.script )
        if scriptFile:
            NTmessage('==> Executing script "%s"', scriptFile )
            execfile( scriptFile, globals() )
        #end if
    #end if

    #------------------------------------------------------------------------------------
    # ipython
    #------------------------------------------------------------------------------------
    if options.ipython:
        from IPython.Shell import IPShellEmbed
        ipshell = IPShellEmbed('',  banner   = '--------Dropping to IPython--------',
                                    exit_msg = '--------Leaving IPython--------')
        ipshell()
    #end if

    #------------------------------------------------------------------------------------
    # Optionally export project
    #------------------------------------------------------------------------------------
    if project and  options.export:
        project.export()

    #------------------------------------------------------------------------------------
    # CLose and optionally not save project
    #------------------------------------------------------------------------------------
    if project:
        project.close(save=not options.nosave)
    #------------------------------------------------------------------------------------

if __name__ == '__main__':
    main() # Just to get a name