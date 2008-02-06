"""
--------------------------------------------------------------------------------
main.py: command line interface to the cing utilities:
--------------------------------------------------------------------------------

Some examples; all assume a project named 'test':

- To start a new Project:
cing --name test --new

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

"""
#==============================================================================
from cing import programVersion
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTpath
from cing.Libs.NTutils import OptionParser
from cing.Libs.NTutils import printDebug
from cing.Libs.NTutils import printMessage
from cing.Libs.NTutils import printf
from cing.core.classes import Project
from cing.core.molecule import Molecule
from cing.core.parameters import cingPaths
from cing.core.parameters import plugins
from cing.test.test_All import testOverall
import cing #@UnusedImport
import os 
import sys



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
            printf("%-15s : ", key )
            format(value)
        #end for
    else:
        format( object )
    #end try
#end def

def script( scriptFile, *a, **k ):
    global args
    global kwds
    args = a
    kwds = k
    if os.path.exists( scriptFile ):
        printMessage('==> Executing script '+ scriptFile )
        execfile( scriptFile, globals() )
    else:
        scriptFile2 = os.path.join( root, cingPaths.scripts, scriptFile)        
        if os.path.exists( scriptFile2 ):
            printMessage('==> Executing script "%s"\n', scriptFile2 )
            #end if
            execfile( scriptFile2, globals() )
        else:
            NTerror('ERROR script: file "%s" not found\n', scriptFile)
        #end if
    #end if
#end def

if __name__ == '__main__':
    
    root,file,ext  = NTpath( __file__ )
    usage          = "usage: cing [options]       use -h or --help for listing"
    
    #------------------------------------------------------------------------------------
    # Options
    #------------------------------------------------------------------------------------
    
    parser = OptionParser(usage=usage, version=programVersion)
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
    parser.add_option("-n", "--name", 
                      dest="name", default=None,
                      help="NAME of the project (required)", 
                      metavar="PROJECTNAME"
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
                      help="Initialise from SEQUENCEFILE[,CONVENTION]", 
                      metavar="SEQUENCEFILE[,CONVENTION]"
                     )
    parser.add_option("--initPDB", 
                      dest="initPDB", default=None,
                      help="Initialise from PDBFILE[,CONVENTION]", 
                      metavar="PDBFILE[,CONVENTION]"
                     )
    parser.add_option("--initBMRB", 
                      dest="initBMRB", default=None,
                      help="Initialise from edited BMRB file", 
                      metavar="BMRBFILE"
                     )
    parser.add_option("--initCcpn", 
                      dest="initCcpn", default=None,
                      help="Initialise from CCPNFILE", 
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
                      action="store_true", default=False, 
                      dest="validate", 
                      help="Do validation"
                     )
    parser.add_option("-q", "--quiet",
                      action="store_true", 
                      dest="quiet", 
                      help="quiet: no/less messages to stdout (default: not quiet)"
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
    
    (options, args) = parser.parse_args()
    
#    parameters.verbose.set( not options.quiet )

    if options.test:
        testOverall()
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
            printf(    '-------------------------------------------------------------------------------\n' +
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
    
    #check for the required name option  
    parser.check_required('-n')

    args = []
    kwds = {}
    
     
    #------------------------------------------------------------------------------------
    # open project
    #------------------------------------------------------------------------------------
    if (options.new):    
        project = Project.open( options.name, status='new' )
    elif (options.old):    
        project = Project.open( options.name, status='old' )
    elif (options.init):    
        init = options.init.split(',')
        if (len(init) == 2):
            project = Project.open( options.name, status='new' )
            project.newMolecule( options.name, sequenceFile=init[0], convention = init[1] )
        else:
            project = Project.open( options.name, status='new' )
            project.newMolecule( options.name, sequenceFile=init[0] )
        #end if
    elif (options.initPDB):
        init = options.initPDB.split(',')
        if (len(init) == 2):
            project = Project.open( options.name, status='new' )
            project.initPDB( pdbFile=init[0], convention = init[1] )
        else:
            project = Project.open( options.name, status='new' )
            project.initPDB( pdbFile=init[0] )
        #end if
    elif (options.initBMRB):
        project = Project.open( options.name, status='new' )
        project.initBMRB( bmrbFile = options.initBMRB, moleculeName = project.name )
    elif (options.initCcpn):
    ##    init = options.initCcpn.split(',')
        project = Project.open( options.name, status='new' )
        project.initCcpn( ccpnFile = options.initCcpn )
        #end if
    else:
        project = Project.open( options.name, status='create' )
    #end if
    
    if not project:
        printDebug("Doing a hard system exit")
        sys.exit(2)
    #end if
    
    #------------------------------------------------------------------------------------
    # Import xeasy protFile
    #------------------------------------------------------------------------------------
    if (options.xeasy):
        xeasy = options.xeasy.split(',')
        if (len(xeasy) != 3):
            NTerror("--xeasy: SEQFILE,PROTFILE,CONVENTION arguments required\n")
        else:
            project.importXeasy(seqFile=xeasy[0], protFile=xeasy[1], convention=xeasy[2])
        #end if
    #end if
    
    #------------------------------------------------------------------------------------
    # Import xeasy peakFile
    #------------------------------------------------------------------------------------
    if (options.xeasyPeaks):
        xeasy = options.xeasy.split(',')
        if (len(xeasy) != 4):
            NTerror("--xeasyPEaks: SEQFILE,PROTFILE,PEAKFILE,CONVENTION arguments required\n")
        else:
            project.importXeasyPeaks(seqFile=xeasy[0], protFile=xeasy[1], peakFile=xeasy[2],convention=xeasy[3])
        #end if
    #end if
    
    #------------------------------------------------------------------------------------
    # Merge resonances
    #------------------------------------------------------------------------------------
    if options.merge:
        project.mergeResonances()
    #end if
    
    #------------------------------------------------------------------------------------
    # Generate peaks
    #------------------------------------------------------------------------------------
    if options.generatePeaks:
        gp = options.generatePeaks.split(',')
        if (len(gp) != 2):
            NTerror("--generatePeaks: EXP_NAME,AXIS_ORDER arguments required\n")
        else:
            peaks = project.generatePeaks( experimentName = gp[0], axisOrder = gp[1] )
        #end if
    #end if
    
    #------------------------------------------------------------------------------------
    # Script
    #------------------------------------------------------------------------------------
    if options.script:
        script( options.script )
    
    #------------------------------------------------------------------------------------
    # Validate
    #------------------------------------------------------------------------------------
    if options.validate:
        project.validate()
    #end if
    
    #------------------------------------------------------------------------------------
    # ipython
    #------------------------------------------------------------------------------------
    if options.ipython:
         # JFD The below gets flagged as unfound by pydev extensions code analysis but
         # if you move the conflicting Shell class down in the PYTHONPATH it's ok.
        from IPython.Shell import IPShellEmbed
        ipshell = IPShellEmbed('',  banner   = '--------Dropping to IPython--------',
                                    exit_msg = '--------Leaving IPython--------')
        ipshell()
    #end if
     
    #------------------------------------------------------------------------------------
    # Optionally export project 
    #------------------------------------------------------------------------------------
    if project and options.export: 
        project.export()
    
    #------------------------------------------------------------------------------------
    # CLose and optionally not save project
    #------------------------------------------------------------------------------------
    if project and not options.nosave: 
        project.close()
    #------------------------------------------------------------------------------------

