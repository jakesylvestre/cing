from ConfigParser import ConfigParser
from cing import authorList
from cing import cingPythonCingDir
from cing import cingRoot
from cing import cingVersion
from cing import programName
from cing.Libs.Geometry import violationAngle
from cing.Libs.NTutils import NTaverage
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTvalue
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTfill
from cing.Libs.NTutils import NTindent
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTdetail
from cing.Libs.NTutils import NTpath
from cing.Libs.NTutils import NTsort
from cing.Libs.NTutils import NTtoXML
from cing.Libs.NTutils import NTwarning
from cing.Libs.NTutils import ROGscore
from cing.Libs.NTutils import XML2obj
from cing.Libs.NTutils import XMLhandler
from cing.Libs.NTutils import fprintf
from cing.Libs.NTutils import obj2XML
from cing.Libs.NTutils import removedir
from cing.Libs.NTutils import sprintf
from cing.Libs.NTutils import val2Str
from cing.Libs.fpconst import NaN
from cing.Libs.fpconst import isNaN
from cing.core.constants import COLOR_ORANGE
from cing.core.constants import COLOR_RED
from cing.core.constants import LOOSE
from cing.core.constants import NOSHIFT
from cing.core.constants import CYANA
from cing.core.molecule import Atom
from cing.core.molecule import Molecule
from cing.core.molecule import NTdihedralOpt
from cing.core.molecule import NTdistanceOpt
from cing.core.molecule import dots
from cing.core.parameters import cingPaths
from cing.core.parameters import directories
from cing.core.parameters import moleculeDirectories
from cing.core.parameters import parameters
from cing.core.parameters import plotParameters
from cing.core.parameters import plugins
#from cing.core.sml import SMLhandler
from shutil import rmtree
import math
import os
import sys
import time

import cing


projects = NTlist()

#-----------------------------------------------------------------------------
# Cing classes and routines
#-----------------------------------------------------------------------------

class Project( NTdict ):

    """
-------------------------------------------------------------------------------
Project: Top level Cing project class
-------------------------------------------------------------------------------

                                   ccpnResidue
                                        ^
                         ccpnChain      |     ccpnAtom
                             ^          |        ^
             ccpnMolecule    |          |        |  Coordinate
                 ^           |          |        |  ^
                 |           |          |        |  |
                 v           v          v        v  v
  Project ->  Molecule <-> Chain <-> Residue <-> Atom <-> Resonance <- Peak
     ^                                  |          |
     |                                  v          v
     v                    NTdb <-> ResidueDef <-> AtomDef
  ccpnProject

  Project.ccpn     = ccpnProject    (Molecule.ccpn      =  ccpnMolecule and so on)
  ccpnProject.cing = Project        (ccpnMolecule.cing  =  Molecule and so on)

  ccpnProject :: (memops.Implementation.Project)
  ccpnMolecule = ccpnProject.molSystems[0]   :: (ccp.molecule.MolSystem.MolSystem)
  ccpnChain   in ccpnMolecule.sortedChains() :: (ccp.molecule.MolSystem.Chain)
  ccpnResidue in ccpnChain.sortedResidues()  :: (ccp.molecule.MolSystem.Residue)
  ccpnAtom    in ccpnResidue.sortedAtoms()   :: (ccp.molecule.MolSystem.Atom)

  Project  -> molecules[Molecule-1, Molecule-2, ...] # Molecules name list
           -> molecule <-> ... (See Molecule)        # 'Current' molecule

           -> peakLists[<Peaklist [<Peak>, ...]>]
          <-> distances[<DistanceRestraintList[<DistanceRestraint>, ...]>]
          <-> dihedrals[<DihedralRestraintList[<DihedralRestraint>, ...]>]

           -> parameters
           -> directories
           -> cingPaths
           -> plotParameters
           -> plugins
  _____________________________________________________________________________

    Methods:

    to open a project:
        project = Project.open( name, status = 'old' )    Open an existing project
        project = Project.open( name, status = 'new' )    Open a new project
        project = Project.open( name, status = 'create' ) Open an existing project
                                                          if it exists or new project
                                                          otherwise

    to initialize a Molecule:
        project.initializeMolecule( name, sequenceFile, convention )

                                    convention = CYANA, CYANA2, INTERNAL, LOOSE

    to save a project:
        project.save()

    to export:
        project.export()

    to export and save:
        project.close()

    to initialize the resonance lists:
        project.initResonances()

    to merge the resonance lists:
        project.mergeResonances( order=None, status='reduce' )
                                status='reduce' results in reducing the resonances
                                list to one merged entry

    to define and add a new PeakList to project:
        peakList = project.newPeakList( name, status='keep' ):

    to define and add a new DistanceRestraintList to project:
        distanceRestraintList = project.distances.new( name, status='keep' ):

    """

#    project.valSets.OMEGA_MAXALL_POOR = 15. # Normally 15 but may be set low for testing 1brv to
#    OMEGA_MAXALL_BAD  = 20. # Normally 20 

    def __init__( self, name ):

        root, name = Project.rootPath( name )

        NTdict.__init__(   self,
                           __CLASS__                = 'Project',

                           version                  =  cingVersion,

                           root                     =  root,
                           name                     =  name.strip(),
                           created                  =  time.asctime(),

                           molecule                 =  None,        # Current Molecule instance

                           moleculeNames            =  NTlist(),    # list to store molecule names for save and restore
                           peakListNames            =  NTlist(),    # list to store peaklist names for save and restore
                           distanceListNames        =  NTlist(),    # list to store distancelist names names for save and restore
                           dihedralListNames        =  NTlist(),    # list to store dihedrallist names for save and restore
                           rdcListNames             =  NTlist(),    # list to store rdclist names for save and restore

                           reports                  =  NTlist(),    # list with validation reports names

                           history                  =  History(),

                           contentIsRestored        =  False,       # True if Project.restore() has been called
                           storedInCcpnFormat       =  False,       #


                         # store a reference to te global things we might need
                           gui                      =  None,        # Reference to CingGui instance
                           parameters               =  parameters,
                           directories              =  directories,
                           moleculeDirectories      =  moleculeDirectories,
                           cingPaths                =  cingPaths,
                           plotParameters           =  plotParameters,
                           plugins                  =  plugins
                         )

        # These Project lists are dynamic and will be filled  on restoring a project
        # They also maintain some internal settings
        # new( name ), append( instance), save(), restore() and path( name ) comprise core functionality
        self.molecules  =  _ProjectList( project     = self,
                                         classDef    = Molecule,
                                         nameListKey = 'moleculeNames',
                                         basePath    = directories.molecules + '/%s.molecule'
                                       )
        self.peaks      =  _ProjectList( project     = self,
                                         classDef    = PeakList,
                                         nameListKey = 'peakListNames',
                                         basePath    = directories.peaklists + '/%s.peaks'
                                       )
        self.distances  =  _ProjectList( project     = self,
                                         classDef    = DistanceRestraintList,
                                         nameListKey = 'distanceListNames',
                                         basePath    = directories.restraints + '/%s.distances'
                                       )
        self.dihedrals  =  _ProjectList( project     = self,
                                         classDef    = DihedralRestraintList,
                                         nameListKey = 'dihedralListNames',
                                         basePath    = directories.restraints + '/%s.dihedrals'
                                       )
        self.rdcs       =  _ProjectList( project     = self,
                                         classDef    = RDCRestraintList,
                                         nameListKey = 'rdcListNames',
                                         basePath    = directories.restraints + '/%s.rdcs'
                                       )

        # store reference to self
        self[name] = self
        self.objectPath = self.path( cingPaths.project )
#        self.makeObjectPaths() # generates the objectPaths dict from the nameLists


        self.rogScore   = ROGscore()
        self.valSets = NTdict()
        self.readValidationSettings(fn=None)
        

        self.saveXML( 'version',
                      'name',  'created',
                      'moleculeNames',
                      'peakListNames','distanceListNames','dihedralListNames','rdcListNames',
                      'storedInCcpnFormat',
                      'reports',
                      'history'
                    )
    #end def


    def readValidationSettings(self, fn=None):
        if fn:
            validationConfigurationFile = fn
        else:
            validationConfigurationFile = os.path.join(cingPythonCingDir, 'valSets.cfg')
        config = ConfigParser()
        config.readfp(open(validationConfigurationFile))
        for item in config.items('DEFAULT'):
            key = item[0].upper()  # upper only.
            value = float(item[1])
            self.valSets[key] = value # name value pairs.

    def criticize(self):
        # funny things not in what if.
        for res in self.molecule.allResidues():
            dihed = 'OMEGA'
            if dihed in res and res[dihed]:
                d = res[dihed] # NTlist object
                if d == None:
                    continue
                modelId = 0
                for value in d:
                    v = violationAngle(value=value, lowerBound=180., upperBound=180)
                    if v > 90.: # Never mind a cis
                        v = violationAngle(value=value, lowerBound=-180., upperBound=-180)
#                    NTdebug('found residue %s model %d omega to violate from square trans/cis: %8.3f' % (
#                            res, modelId, v) )
                    if v >= self.valSets.OMEGA_MAXALL_BAD:
                        res.rogScore.setMaxColor( COLOR_RED, ROGscore.ROG_COMMENT_BAD_OMEGA )
#                        res.rogScore.setMaxColor( COLOR_RED, ROGscore.ROG_COMMENT_BAD_OMEGA + ' double on purpose; TODO: REMOVE')
                        NTdebug('Set to red')
                    elif v >= self.valSets.OMEGA_MAXALL_POOR:
                        res.rogScore.setMaxColor( COLOR_ORANGE, ROGscore.ROG_COMMENT_BAD_OMEGA )
                        NTdebug('Set to orange (perhaps)')
                    modelId += 1

        # distance and dihedral restraints
        for drl in self.distances + self.dihedrals:
            drl.criticize(self)

    #-------------------------------------------------------------------------
    # Path stuff
    #-------------------------------------------------------------------------

    def path( self, *args ):
        """Return joined args as path relative to root of project
        """
        return os.path.join( self.root, *args )
    #end def

    def rootPath( name ):
        """Static method returning Root,name of project from name

        name can be:
            simple_name_string
            directory.cing
            directory.cing/
            directory.cing/project.xml

        GWV  6 Dec 2007: to allow for relative paths.
        JFD 17 Apr 2008: fixed bugs caused by returning 2 values.
        """
        root,name,ext = NTpath(name)
        if name == '' or name == 'project': # indicate we had a full path
            root,name,ext = NTpath( root )
        #end if
        if (len(ext)>0 and ext != '.cing'):
            NTerror('FATAL ERROR: unable to parse "%s"\n', name )
#            exit(1) # no more hard exits for we might call this from GUI or so wrappers
            return None

        rootp = os.path.join(root, name + '.cing')
        #print '>>',rootp,name

        return rootp, name

    rootPath = staticmethod( rootPath )

    def mkdir( self, *args ):
        """Make a directory relative to to root of project from joined args.
           Check for presence.
           Return the result
        """
        dir = self.path( *args )
        if not os.path.exists( dir ):
#            NTdebug( "project.mkdir: %s" % dir )
            os.makedirs(  dir )
        return dir
    #end def

    def moleculePath(self, subdir=None, *args ):
        """ Path relative to molecule.
        Return path or None in case of error.
        """
        if not self.molecule:
            return None
        if subdir == None:
            return self.path( self.molecule.name )

        return self.path( self.molecule.name, moleculeDirectories[subdir], *args )

    def htmlPath(self, *args ):
        """ Path relative to molecule's html directory.
        Return path or None in case of error.
        """
        return self.moleculePath( 'html', *args )
    #end def

#    def makeObjectPaths(self):
#        """
#        Generate paths for all the currently defined names in the project
#        """
#        self.objectPaths = NTdict()
#        for name in self.moleculeNames:
##            self.objectPaths[name] = self.path(directories.molecules, name+'.molecule')
#            self.objectPaths[name] = self.molecules.path(name)
#        for name in self.peakListNames:
#            self.objectPaths[name] = self.peaks.path(name)
#        for name in self.distanceListNames:
#            self.objectPaths[name] = self.distances.path(name)
#        for name in self.dihedralListNames:
#            self.objectPaths[name] = self.dihedrals.path(name)
#        for name in self.rdcListNames:
#            self.objectPaths[name] = self.rdcs.path(name)
#
#        self.objectPaths.keysformat()
#        NTdebug('objectPaths: %s', self.objectPaths.format())
#    #end def

    def decodeNameTuple(self, nameTuple):
        """
        Decode the 7-element nameTuple:
        (objectName, chainName, resNum, atomName, modelIndex, resonanceIndex, convention)

        Return Object or None on error.

@TODO Now works for Molecule; Also implement for other project list object like PeakList, DistanceRestraintList, etc
        """
        if nameTuple == None or not self.has_key(nameTuple[0]):
            return None
        return self[nameTuple[0]].decodeNameTuple(nameTuple)

    #-------------------------------------------------------------------------
    # actions exists/open/restore/save/close/export/updateProject
    #-------------------------------------------------------------------------

    def exists( name ):
        """Static method exists check for presence of Project directory derived from name
            returns True or False
        """
        rootp, _n = Project.rootPath( name )
        if os.path.exists( rootp ):
            return True
        return False
    #end def
    exists = staticmethod( exists )


    def open( name, status = 'create', restore=True ):
        """Static method open returns a new/existing Project instance depending on status.

           status == 'new': open a new project 'name'
           status == 'old: open existing project 'name'
                      project data is restored when restore == True.
           status == 'create': if project name if exists open as old, open as new otherwise.

           Returns Project instance or None on error.
        """
        global projects

        #print '>>', name, status

        if (status == 'new'):
            root,dummy = Project.rootPath( name )
            if os.path.exists( root ):
                removedir( root )
            #end if
            os.mkdir( root )
            pr = Project( name )
            pr.addHistory( 'New project'  )
            # Save the project data
            obj2XML( pr, path = pr.objectPath )

        elif (status == 'create'):
            root,dummy = Project.rootPath( name )
            if os.path.exists( root ):
                return Project.open( name, 'old')
            else:
                return Project.open( name, 'new')
            #end if

        elif (status == 'old'):
            root,newName = Project.rootPath( name )
            if not os.path.exists( root ):
                NTerror('Project.open: unable to open Project "%s"\n', name )
                return None
            #end if

            # Restore Project info from xml-file
            pfile = os.path.join( root, cingPaths.project )
            if not os.path.exists( pfile ):
                NTerror('Project.open: missing Project file "%s"\n', pfile )
                return None
            #end if
            pr = XML2obj( pfile )
            if pr == None:
                NTerror('Project.open: error parsing Project file "%s"\n', pfile )
                return None
            #end if
            # This allows renaming/relative addressing at the shell level
            pr.root = root
            pr.name = newName
            pr.objectPath = pfile

            pr.contentIsRestored = False

            try:
                # <= 0.75 version have string
                pr.version = float(pr.version.split()[0])
            except:
                pass

            if pr.version <= 0.75:
                NTmessage('Project.Open: converting from version %s', pr.version)

                # 0.75 version had moleculeNames stored in molecules attribute
                # >=0.76 version molecules is a ProjectList instance
                pr.moleculeNames = pr.molecules
                # store the xmlFile and reopen to have correct settings
                if obj2XML(pr, path=pfile) != pr:
                    NTerror('Molecule.Open: conversion from version %s failed on write', pr.version)
                    return None
                pr = XML2obj( pfile )
                if pr == None:
                    NTerror('Molecule.Open: conversion from version %s failed on read', pr.version)
                    return None

                for molName in pr.moleculeNames:
                    path = pr.path( directories.molecules, molName ) # old reference
                    mol = Molecule._open075( path )
                    if not mol:
                        NTerror('Molecule.Open: conversion from version %s failed on molecule %s', pr.version, molName)
                        return None
                    removedir(path)
                    # Save molecule to new format
                    mol.save( pr.molecules.path(molName) )
                #end for

                # restore
                pr.restore()
                # Save to consolidate
                pr.save()
            #end if

            # Optionally restore the content
            if restore and not pr.contentIsRestored:
                pr.restore()
            #end if

        else:
            NTerror('ERROR Project.open: invalid status option "%s"\n', status )
            return None
        #end if

        # Check the subdirectories
        tmpdir = pr.path( directories.tmp )
        # have to use cing.verbosity to work?
        if os.path.exists(tmpdir) and cing.verbosity != cing.verbosityDebug:
            removedir(tmpdir)
        for dir in directories.values():
            pr.mkdir( dir )
        #end for

        projects.append( pr )
        return pr
    #end def
    open = staticmethod( open )

    def close( self, save=True ):
        """
        Save project data and close project.
        TODO: Call destructor on self and its elements
        """
        global projects
        #self.export()
        if save: self.save()
        # remove the tmpdir
        tmpdir = self.path( directories.tmp )
        # have to use cing.verbosity to work?
        #print '>>', cing.verbosity, cing.verbosityDebug
        if os.path.exists(tmpdir) and cing.verbosity != cing.verbosityDebug:
            removedir(tmpdir)

        projects.remove(self)
        return None
    #end def

    def save( self):
        """
        Save project data
        """
        NTmessage('' + dots*5 +'' )
        NTmessage(   '==> Saving %s', self )

        # Save the molecules
        for mol in self.molecules:
            mol.save( mol.objectPath)

        # Save the molecules and lists
        for pl in [self.peaks, self.distances, self.dihedrals, self.rdcs]:
            self[pl.nameListKey] = pl.save() # Save returns a list of name; store these in project
            # Patch for XML bug
            self.saveXML( pl.nameListKey )
        #end for

        # Call Plugin registered functions
        for p in self.plugins.values():
            for f,o in p.saves:
                f( self, o )
            #end for
        #end for

        # Update version number since it is now saved with this cingVersion
        self.version = cingVersion
        # Save the project data to xml file
        if obj2XML( self, path = self.objectPath) != self:
            NTerror('Project.save: writing Project file "%s" failed', self.objectPath)
        #end if

        self.addHistory( 'Saved project' )
    #end def

    def restore(self ):
        """
        Restore the project: molecules and lists
        """
        NTmessage('==> Restoring %s ... ', self )

        # Molecules
        for molName in self.moleculeNames:
            path = self.molecules.path( molName )
            mol = Molecule.open( path )
            if mol:
                mol.status = 'keep'
                self.appendMolecule(mol)
            #end if
        #end for

        # restore the lists
        for pl in [self.peaks, self.distances, self.dihedrals, self.rdcs]:
             pl.restore()
        #end for

        # Plugin registered functions
        for p in self.plugins.values():
            for f,o in p.restores:
                f( self, o )
            #end for
        #end for

        self.contentIsRestored = True

        self.updateProject()
    #end def

    def export( self):
        """Call export routines from the plugins to export the project
        """
        NTmessage('' + dots*5 +'' )
        NTmessage(   '==> Exporting %s', self )

        for p in self.plugins.values():
            for f,o in p.exports:
                f( self, o )
            #end for
        #end for
    #end def

    def updateProject( self ):
        """Do all administrative things after actions
        """
        if self.molecule: self[self.molecule.name] = self.molecule
    #end def

    #-------------------------------------------------------------------------
    # actions Molecule
    #-------------------------------------------------------------------------
    def appendMolecule( self, molecule ):
        if not molecule: return None

        # generate the required directories for export and HTML data
        for dir in moleculeDirectories.values():
            self.mkdir( molecule.name, dir )
        #end for

        # Store names and references and append
        self.molecule = molecule
        self.molecules.append( molecule )
# GV 21 Jun 08: do not know why we would need a save here
#        self.molecule.save( path = self.molecule.objectPath )
        return self.molecule
    #end def

    def newMolecule( self, name, sequenceFile, convention = LOOSE ):
        """Return Molecule instance or None on error
        """
        uname = self.uniqueKey(name)
        molecule = Molecule.initialize( uname,
                                        path = sequenceFile,
                                        convention=convention,
                                        status='keep'
                                      )
        if not molecule:
            return None
        self.appendMolecule( molecule )

        self.addHistory( sprintf('Initialized molecule "%s" from "%s"', uname, sequenceFile ) )
        return molecule
    #end def
    initializeMolecule = newMolecule # keep old name


    #-------------------------------------------------------------------------
    # Resonances stuff
    #-------------------------------------------------------------------------

    def mergeResonances( self, order=None, selection=None, status='reduce' ):

        """ Merge resonances for all the atoms
            check all the resonances in the list, optionally using selection
            and take the first one which has a assigned value,
            append or reduce the resonances list to this entry depending on status.

        """

        if not self.molecule:
            NTerror('Project.mergeResonances: No molecule defined\n')
            return
        #end if

        for atom in self.molecule.allAtoms():
            if ( len(atom.resonances) == 0 ):
                NTerror('mergeResonances: zero length resonance list for atom "%s"\n',
                         atom
                       )
                return
            else:
                rm = None
                if (selection == None or atom.name in selection):
                    for res in atom.resonances:
                        if not isNaN(res.value):
                            rm=res
                            break
                        #end if
                    #end for
                #end if
            #end if

            if (rm):
                atom.resonances.append(rm)
            else:
                rm = atom.resonances[0]
                atom.resonances.append(rm)
            #end if

            # Optionally reduce the list
            if (status == 'reduce'):
                atom.resonances = NTlist( atom.resonances() )
                self.molecule.resonanceCount = 1
            else:
                self.molecule.resonanceCount = len( atom.resonances )
        NTmessage("==> Merged resonances")

    def initResonances( self ):

        """ Initialize resonances for all the atoms
        """
        if not self.molecule:
            NTerror('Project.initResonances: No molecule defined\n')
            return
        self.molecule.initResonances()

    #-------------------------------------------------------------------------
    # actions other
    #-------------------------------------------------------------------------

    def addHistory( self, line, timeStamp = True ):
        self.history( line, timeStamp )
    #end def

    def newPeakList( self, name, status='keep'):
        """Dummy for compatibility
        """
        return self.peaks.new( name = name, status=status)
    #end def

    def appendPeakList( self, peaklist):
        """Append peaklist; dummy for compatibility
        """
        self.peaks.append( peaklist )
        return peaklist
    #end def

    def header( self, dots = '---------'  ):
        """Subclass header to generate using __CLASS__, name and dots.
        """
        return sprintf('%s %s: %s %s', dots, self.__CLASS__, self.name, dots)
    #end def

    def __str__( self ):
        return sprintf('<Project %s>', self.name )
    #end def

    def __repr__(self):
        return str(self)

    def format( self ):
        dots =              '-----------'
        self.__FORMAT__   =  self.header( dots ) + '\n' + \
                            'created:    %(created)s\n' +\
                            'molecules:  %(molecules)s\n' +\
                            'peaks:      %(peaks)s\n' +\
                            'distances:  %(distances)s\n' +\
                            'dihedrals:  %(dihedrals)s\n' +\
                            'rdcs:       %(rdcs)s\n' +\
                            'reports:    %(reports)s\n' +\
                             self.footer( dots )
        return NTdict.format( self )
    #end def

    def removeFromDisk(self):
        """Removes True on error. If no cing project is found on disk None (Success) will
        still be returned. Note that you should set the nosave option on the project
        before exiting."""
        pathString, _name = self.rootPath(self.name)
        if not os.path.exists(pathString):
            NTwarning("No cing project is found at: " + pathString)
            return None
        NTmessage("Removing existing cing project")
        if rmtree( pathString ):
            NTerror("Failed to remove existing cing project")
            return True

#end class

#-----------------------------------------------------------------------------

class XMLProjectHandler( XMLhandler ):
    """Project handler class"""
    def __init__( self ):
        XMLhandler.__init__( self, name='Project')
    #end def

    def handle( self, node ):
        attrs = self.handleDictElements( node )
        if attrs == None: return None
        result = Project( name = attrs['name'] )

        # update the attrs values
        result.update( attrs )

        return result
    #end def
#end class

#register this handler
projecthandler = XMLProjectHandler()

#
#-----------------------------------------------------------------------------
class _ProjectList( NTlist ):
    """Generic Project list class; only to be used internally
       Creates classDef instance when calling the new() method
    """
    def __init__( self, project, classDef, nameListKey, basePath ):
        """
        nameList is key of project identifying list of names.
        This is done because of the update done in the Project.restore()
        method.
        """
        NTlist.__init__( self )
        self.project  = project
        self.classDef = classDef
        self.nameListKey = nameListKey
        self.basePath = basePath # project(self.basePath % name) yields valid path
#        self.savePath = savePath
#        self.extention = extention
    #end def

    def path(self, name):
        #print '>>', self.basePath % name
        return self.project.path(self.basePath % name)

    def append( self, instance ):
        """Append instance to self, storing instance.name in project
        """
        #print '>>',instance, self.project
        instance.name = self.project.uniqueKey( instance.name )
        NTlist.append( self, instance )
        # add reference in project
        self.project[instance.name] = instance
        instance.objectPath = self.path(instance.name)
    #end def

    def new( self, name,*args, **kwds ):
        """Create a new classDef instance, append to self
        """
        uname = self.project.uniqueKey(name)
        instance = self.classDef( name = uname, *args, **kwds )
        self.append ( instance )
        s = sprintf('New "%s" instance named "%s"', self.className(), uname )
        self.project.history( s )
        NTdebug( s )
        #end if
        return instance
    #end def

    def save(self):
        """
        Save the lists of self to savePath/name.extention
        savePath relative to project

        Use SML methods

        Return a list of names
        """
        saved = NTlist()
        for l in self:
            if l.status == 'keep':
                NTdetail('==> Saving %s to %s', l, l.objectPath)
                if self.classDef.SMLhandler.toFile( l, l.objectPath ) == l:
                    saved.append(l.name)
            #end if
        #end for
        self.project[self.nameListKey] = saved
        # patch XML bug
        self.project.saveXML( self.nameListKey )
        return saved
    #end def

    def restore(self, names=None ):
        """
        Use the SMLhandler instance of classDef to restore the list.
        if names=None;
            derive the list from the project[nameListKey]
        else:
            names is a list instance containing the names to of the lists to restore.
        """
        if not names:
            names = self.project[self.nameListKey]
        for name in names:
            path = self.path(name)
            l = self.classDef.SMLhandler.fromFile( path, self.project) # Lists get append to project by SML routines
            if l != None:
                NTdetail('==> Restored %s from %s', l, path)
                l.objectPath = path
            #end if
        #end for
    #end def

    def names(self):
        "Return a list of name of self"
        names = NTlist()
        for l in self:
            names.append(l.name)
        return names

    def className(self):
        """Return a string describing the class of lists of this project list
        """
        # eg. to extract from <class 'cing.classes.PeakList'>
        return str(self.classDef)[8:-2].split(".")[-1:][0]
    #end def
#end class ProjectList

#
#
PeakIndex = 0
class Peak( NTdict ):
    """Peak class:
       Peaks point to resonances
       Resonances point to atoms
       by GV 2007 07 23: added hasHeight, hasVolume attributes to the class
          GV 2007 28 09: Moved from molecule.py to project.py
          GV 19 Jun 08: PeakIndex starts at 0
          GV 19 Jun 08: change height, volume to NTvalue clasess
          GV 19 Jun 08: changed hasHeight and hasVolume to methods
    """

    HEIGHT_VOLUME_FORMAT  = '%9.2e +- %8.1e'

    def __init__( self,
                  dimension,
                  positions=None,
                  height=NaN, heightError = NaN,
                  volume=NaN, volumeError = NaN,
                  resonances=None,
                  **kwds
                ):

        NTdict.__init__( self, __CLASS__  = 'Peak', **kwds )
#       several external programs need an index
        global PeakIndex
        self.peakIndex = PeakIndex
        PeakIndex += 1

        self.__FORMAT__ =  self.header(dots) + '\n' +\
                           'dimension:  %(dimension)dD\n' +\
                           'positions:  %(positions)s\n' +\
                           'height:     %(height)s\n'   +\
                           'volume:     %(volume)s\n' +\
                           'resonances: %(resonances)s\n' +\
                           self.footer(dots)

        self.dimension=dimension

        # Copy the poistions and resonances argumnet to assure they become
        # NTlist objects
        if resonances:
            self.resonances = NTlist( *resonances )
        else:
            self.resonances = NTfill( None, dimension )
        #end if

        if positions:
            self.positions = NTlist( *positions )
        else:
            self.positions = NTfill( NaN, dimension )
        #end if

        self.height = NTvalue(height, heightError, Peak.HEIGHT_VOLUME_FORMAT)
        self.volume = NTvalue(volume, volumeError, Peak.HEIGHT_VOLUME_FORMAT)
    #end def

    def isAssigned( self, axis ):
        if (axis >= self.dimension): return False
        if (axis >= len(self.resonances) ): return False
        if (self.resonances[axis] == None): return False
        if (self.resonances[axis].atom == None): return False
        return True
    #end def

    def getAssignment( self, axis):
        """Return atom instances in case of an assignment or None
        """
        if (self.isAssigned( axis ) ):
            return self.resonances[axis].atom
        #end if
        return None
    #end def

    def hasHeight(self):
        return not isNaN(self.height.value)

    def hasVolume(self):
        return not isNaN(self.volume.value)

    def __str__( self ):
        #print '>>', self.resonances.zap('atom')
        return sprintf( 'Peak %4d (%dD)  [%s]   height: %s   volume: %s    Assiged to: %s',
                         self.peakIndex, self.dimension,
                         self.positions.format('%8.2f'),
                         self.height, self.volume,
                         self.resonances.zap('atom').format('%-20s')
                       )
    #end def

    def header( self, dots = '---------'  ):
        """Subclass header to generate using __CLASS__, peakIndex and dots.
        """
        return sprintf('%s %s: %d %s', dots, self.__CLASS__, self.peakIndex, dots)
    #end def
#end class


#-----------------------------------------------------------------------------
class PeakList( NTlist ):

    def __init__( self, name, status='keep' ):
        NTlist.__init__( self )
        self.name = name
        self.status = status
        self.listIndex = -1 # list is not appended to anything yet
    #end def

    def peakFromAtoms( self, atoms, onlyAssigned=True ):
        """Append a new Peak based on atoms list
           Return Peak instance, or None
        """
        if (None not in atoms):     # None value in atoms indicates atom not present
            if (onlyAssigned and (False in map( Atom.isAssigned, atoms ))):
                pass                # Check atom assignments, if only assigned and not all assignments
                                    # present we skip it
            else:                   # all other cases we add a peak
                s = []
                r = []
                for a in atoms:
                    s.append( a.shift() )
                    r.append( a.resonances() )
                #end for
                peak = Peak( dimension = len(atoms),
                             positions = s,
                             resonances = r
                           )
                self.append( peak )
                return peak
            #end if
        #end if
        return None
    #end def

    def __str__( self ):
        return sprintf( '<PeakList "%s" (%s,%d)>',self.name,self.status,len(self) )
    #end def

    def __repr__(self):
        return str(self)
    #end def

    def format( self ):
        s = sprintf( '%s PeakList "%s" (%s,%d) %s\n', dots, self.name,self.status,len(self), dots )
        for peak in self:
            s = s + str(peak) + '\n'
        #end for
        return s
    #end def

    def save(self,path=None):
        """
        Create a SML file
        Return self or None on error
        """
        if not path: path = self.objectPath
        if self.SMLhandler.toFile(self, path) != self:
            NTerror('PeakList.save: failed creating "%s"', path)
            return None
        #end if

        NTdetail('==> Saved %s to "%s"', self, path)
        return self
    #end def
#end class


def getAtomsFromAtomPairs(atomPairs):
    result = []
    for atomPair in atomPairs:
        for atom in atomPair:
            for real_atm in atom.realAtoms():
                result.append( real_atm )
    return result

#-----------------------------------------------------------------------------
class DistanceRestraint( NTdict ):
    """DistanceRestraint class:
       atomPairs: list of (atom_1,atom_2) tuples,
       lower and upper bounds
    """

    def __init__( self, atomPairs=[], lower=0.0, upper=0.0, **kwds ):

        NTdict.__init__(self,__CLASS__  = 'DistanceRestraint',
                               atomPairs  = NTlist(),
                               lower      = lower,
                               upper      = upper,
                               **kwds
                        )
        self.id         = -1       # Undefined index number

        self.distances  = None     # list with distances for each model; None: not yet defined
        self.av         = 0.0      # Average distance
        self.sd         = 0.0      # sd on distance
        self.min        = 0.0      # Minimum distance
        self.max        = 0.0      # Max distance
        self.violations = None     # list with violations for each model; None: not yet defined
        self.violCount1 = 0        # Number of violations over 0.1A
        self.violCount3 = 0        # Number of violations over 0.3A
        self.violCount5 = 0        # Number of violations over 0.5A
        self.violMax    = 0.0      # Maximum violation
        self.violAv     = 0.0      # Average violation
        self.violSd     = 0.0      # Sd of violations
        self.error      = False    # Indicates if an error was encountered when analyzing restraint
        self.rogScore   = ROGscore()

        for pair in atomPairs:
            self.appendPair( pair )
        #end for
    #end def

    def criticize(self, project):
        """Only the self violations,violMax and violSd needs to be set before calling this routine"""
#        NTdebug( '%s' % self )
        if self.violMax >= project.valSets.DR_MAXALL_POOR:
            comment = '[crit.1] violMax: %8.3f' % self.violMax
            NTdebug(comment)
            self.rogScore.setMaxColor( COLOR_ORANGE, comment )
        if self.violMax >= project.valSets.DR_MAXALL_BAD:
            comment = '[crit.2] violMax: %8.3f' % self.violMax
            NTdebug(comment)
            self.rogScore.setMaxColor( COLOR_RED, comment )
        fractionAbove = getFractionAbove( self.violations, project.valSets.DR_THRESHOLD_OVER_POOR )
        if fractionAbove >= project.valSets.DR_THRESHOLD_FRAC_POOR:
            comment = '[crit.3b]: fractionAbove: %8.3f' % fractionAbove
            NTdebug(comment)
            self.rogScore.setMaxColor( COLOR_ORANGE, comment )
        fractionAbove = getFractionAbove( self.violations, project.valSets.DR_THRESHOLD_OVER_BAD )
        if fractionAbove >= project.valSets.DR_THRESHOLD_FRAC_BAD:
            comment = '[crit.3]: fractionAbove: %8.3f' % fractionAbove
            NTdebug(comment)
            self.rogScore.setMaxColor( COLOR_RED, comment )
        if self.violSd >= project.valSets.DR_RMSALL_BAD:
            comment = '[crit.4] violSd: %8.3f' % self.violSd
            NTdebug(comment)
            self.rogScore.setMaxColor( COLOR_RED, comment )

    def appendPair( self, pair ):
        # check if atom already present, keep order
        # otherwise: keep atom with lower residue index first
        a0 = self.atomPairs.zap(0)
        a1 = self.atomPairs.zap(1)
        if (pair[0] in a0 or pair[1] in a1):
            self.atomPairs.append( pair )
        elif (pair[0] in a1 or pair[1] in a0):
            self.atomPairs.append( (pair[1],pair[0]) )
        elif (pair[0].residue.resNum > pair[1].residue.resNum):
            self.atomPairs.append( (pair[1],pair[0]) )
        else:
            self.atomPairs.append( pair )
    #end def

    def calculateAverage(self):
        """
        Calculate R-6 average distance and violation
        for each model.
        return (av,sd,min,max) tuple, or (None, None, None, None) on error
        Important to set the violations to 0.0 if no violations were found.
        In that case the s.d. may remain None to indicate undefined.
        """

        modelCount = 0
        if len(self.atomPairs) :
            modelCount = self.atomPairs[0][0].residue.chain.molecule.modelCount
        #end if

        if modelCount == 0:
            NTerror('Error DistanceRestraint.calculateAverage: No structure models (%s)\n', self)
            return (None, None, None, None)
        #end if

        self.distances  = NTlist() # list with distances for each model
        self.av         = 0.0      # Average distance
        self.sd         = 0.0      # sd on distance
        self.min        = 0.0      # Minimum distance
        self.max        = 0.0      # Max distance
        self.violations = NTlist() # list with violations for each model INCLUDING non violating models!
        self.violCount1 = 0        # Number of violations over 0.1A
        self.violCount3 = 0        # Number of violations over 0.3A
        self.violCount5 = 0        # Number of violations over 0.5A
        self.violMax    = 0.0      # Maximum violation
        self.violAv     = 0.0      # Average violation
        self.violSd     = None     # Sd of violations
        self.error      = False    # Indicates if an error was encountered when analyzing restraint

        if modelCount:
            for i in range( modelCount):
                d = 0.0
                for atm1,atm2 in self.atomPairs:
                    #expand pseudoatoms
                    atms1 = atm1.realAtoms()
                    atms2 = atm2.realAtoms()
                    for a1 in atms1:
                        #print '>>>', a1.format()
                        if (len( a1.coordinates ) > i ):
                            for a2 in atms2:
                                if (len(a2.coordinates) > i ):
                                    tmp = NTdistanceOpt( a1.coordinates[i], a2.coordinates[i] )
                                    d += math.pow( tmp, -6.0 )
                                else:
                                    self.error = True
                                #end if
                            #end for
                        else:
                            self.error = True
                        #end if
                    #end for
                #end for
                try:
                    self.distances.append( math.pow(d, -0.166666666666666667) )
                except:
                    self.error = True
                    msg = "AtomPair (%s,%s) without coordinates" % (atm1.toString(), atm2.toString())
                    NTdebug(msg)
                    self.rogScore.setMaxColor( COLOR_RED, msg )
                    return (None, None, None, None)
                #end try
            #end for

            self.av, self.sd, self.n = NTaverage( self.distances )
            self.min = min( self.distances )
            self.max = max( self.distances )

            # calculate violations
            for d in self.distances:
                if (d < self.lower):
                    self.violations.append( d-self.lower )
                elif (d > self.upper):
                    self.violations.append( d-self.upper )
                else:
                    self.violations.append( 0.0 )
                #end if
            #end for

            # analyze violations
            for d in self.violations:
                dabs = math.fabs(d)
#               print '>>', d,dabs
                if ( dabs > 0.1):
                    self.violCount1 += 1
                if ( dabs > 0.3):
                    self.violCount3 += 1
                if ( dabs > 0.5):
                    self.violCount5 += 1
            #end for
            if self.violations:
                # JFD doesn't understand why the values need to be mapped to floats.
                self.violAv, self.violSd, _n = NTaverage( map(math.fabs,self.violations) )
                self.violMax = max( map(math.fabs,self.violations) )
        #end if

        return (self.av,self.sd,self.min,self.max )

    #end def

    def listViolatingModels(self, cutoff = 0.3 ):
        """
        Examine for violations larger then cutoff, return list of violating models or None on error
        Requires violations attribute (obtained with calculateAverage method.
        """
        if not self.has_key('violations'):
            return None

        violatingModels = NTlist()
        #TODO: check if the below self.violations was meant when JFD changed from just 'violations'
        for i in range( len(self.violations) ):
            if (math.fabs( self.violations[i]) > cutoff):
                violatingModels.append( i )
            #end if
        #end for

        return violatingModels
    #end def

    def _names(self):
        """
        Internal routine: generate string from atomPairs
        """
        s = ''
        for p in self.atomPairs:
            s = s + sprintf('(%-11s - %11s)   ', p[0]._Cname(1), p[1]._Cname(1))
        #end for
        return s.strip()
    #end def

    def __str__(self):
        return sprintf('<DistanceRestraint %d>', self.id )
    #end def

    def format( self ):
        return  \
            sprintf('%-25s (Target: %4.1f %4.1f)  (Models: av %4s sd %4s min %4.1f max %4.1f)'+\
                    '(Violations: av %6s max %6.1f counts %2d,%2d,%2d) %s',
                        str(self),
                        self.lower, self.upper,
                val2Str(self.av,         "%6.1f", 6),
                val2Str(self.sd,         "%7.3f", 7),
                self.min, self.max,
                val2Str(self.violAv,     "%4.1f", 4),
                self.violMax, self.violCount1, self.violCount3, self.violCount5,
                self._names())
    #end def
#end class


#-----------------------------------------------------------------------------
class DistanceRestraintList( NTlist ):
    """
    Class based on NTlist that holds distanceRestraints.
    Also manages the "id's".
    Sort  by item of DistanceRestraint Class
    """
    def __init__( self, name, status='keep' ):
        NTlist.__init__( self )
        self.name   = name        # Name of the list
        self.status = status      # Status of the list; 'keep' indicates storage required
        self.Hbond  = False       # Hbond: fix to keep information about Hbond restraints from CCPN
        self.currentId  = 0       # Id for each element of list

        self.rmsd       = None    # rmsd per model, None indicate no analysis done
        self.rmsdAv     = 0.0
        self.rmsdSd     = 0.0
        self.violCount1 = 0       # Total violations over 0.1 A
        self.violCount3 = 0       # Total violations over 0.3 A
        self.violCount5 = 0       # Total violations over 0.5 A
        self.rogScore   = ROGscore()
    #end def

    def criticize(self, project):
        for dr in self:
            dr.criticize(project)
            self.rogScore.setMaxColor( dr.rogScore.colorLabel, comment='Cascaded from: %s'%`dr` )

    def append( self, distanceRestraint ):
        distanceRestraint.id = self.currentId
        NTlist.append( self, distanceRestraint )
        self.currentId += 1
    #end def

    def analyze( self ):
        """
        Calculate averages for every restraint.
        Return <rmsd>, sd and total violations over 0.1, 0.3, 0.5 A as tuple
        or (None, None, None, None, None) on error
        """

        if (len( self ) == 0):
            NTerror('ERROR DistanceRestraintList.analyze: "%s" empty list', self.name )
            return (None, None, None, None, None)
        #end if

        modelCount = 0
        if len(self[0].atomPairs):
            modelCount = self[0].atomPairs[0][0].residue.chain.molecule.modelCount
        #end if

        if modelCount == 0:
            NTerror('DistanceRestraintList.analyze: "%s" modelCount 0', self.name )
            return (None, None, None, None, None)
        #end if

        self.rmsd  = NTfill( 0.0, modelCount )
        self.violCount1 =  0
        self.violCount3 =  0
        self.violCount5 =  0
        count = 0
        self.errors = NTlist() # Store reference to restraints with calc problems
        for dr in self:
            dr.calculateAverage()
            if dr.error:
                self.errors.append( dr )
            else:
                self.violCount1 += dr.violCount1
                self.violCount3 += dr.violCount3
                self.violCount5 += dr.violCount5
                for i in range(0, modelCount):
                    self.rmsd[i] += dr.violations[i]*dr.violations[i]
                #end for
                count += 1
            #end if
        #end for

        for i in range(0, modelCount):
            self.rmsd[i] = math.sqrt(self.rmsd[i]/count)
        #end for

        self.rmsdAv, self.rmsdSd, _n = NTaverage( self.rmsd )
        return (self.rmsdAv, self.rmsdSd, self.violCount1, self.violCount3, self.violCount5)
    #end def

    def sort(self, byItem ):
        """
        Sort the list byItem
        """
        NTsort( self, byItem, inplace=True)
        return self
    #end def

    def __str__( self ):
        return sprintf( '<DistanceRestraintList "%s" (%s,%d)>',self.name,self.status,len(self) )
    #end def

    def format( self ):
        return sprintf( '%s DistanceRestraintList "%s" (%s,%d) %s\n'+\
                        'rmsd: %7s %6s        Violations > 0.1,0.3,0.5: %d, %d, %d\n',
                      dots, self.name,self.status,len(self), dots,
                      val2Str(self.rmsdAv,         "%7.3f", 7),
                      val2Str(self.rmsdSd,         "%6.3f", 6),
                      self.violCount1, self.violCount3, self.violCount5)

    #end def

    def save(self,path=None):
        """
        Create a SML file
        Return self or None on error
        """
        if not path: path = self.objectPath
        if self.SMLhandler.toFile(self, path) != self:
            NTerror('DistanceRestraintList.save: failed creating "%s"', path)
            return None
        #end if

        NTdetail('==> Saved %s to "%s"', self, path)
        return self
    #end def
#end class


#-----------------------------------------------------------------------------
class DihedralRestraint( NTdict ):
    """
        DihedralRestraint class:

       GV 2 Oct 2007: removed residue and angle attributes.
       If the 4 atoms consitute a known dihedral angle, this can
       be retrieved with the retrieveDefinition method

       GV&AWSS: 10 Oct 2007, upper-limit adjustment
    """

#    project.valSets.DR_MAXALL_POOR = 3. # Normally 0.3 but set low for testing 1brv to
#    DR_MAXALL_BAD  = 5. # Normally 0.5 but set low for testing 1brv to
#    DR_THRESHOLD_OVER_BAD  = 0.3 # degrees.
#    DR_THRESHOLD_FRAC_BAD  = 0.5
#    DR_RMSALL_BAD  = 0.3 # Angstrom rms violations. # Normally 0.3 but set low for testing 1brv to

    def __init__( self, atoms, lower, upper, **kwds ):

        if upper<lower:
            upper+=360.0
        NTdict.__init__(self, __CLASS__  = 'DihedralRestraint',
                              atoms      = NTlist( *atoms ),
                              lower      = lower,
                              upper      = upper,
                              **kwds
                       )
        self.id         = -1       # Undefined index number
        self.dihedrals  = None     # list with dihedral values for each model, None indicates no analysis done
        self.cav        = 0.0      # Average dihedral value
        self.cv         = 0.0      # cv on dihedral
#        self.min        = 0.0      # Minimum dihedral
#        self.max        = 0.0      # Max dihedral
        self.violations = None     # list with violations for each model, None indicates no alalysis done
        self.violCount1 = 0        # Number of violations over 1 degree
        self.violCount3 = 0        # Number of violations over 3 degrees
        self.violCount5 = 0        # Number of violations over 5 degrees
        self.violMax    = 0.0      # Maximum violation
        self.violAv     = 0.0      # Average violation
        self.violSd     = 0.0      # Sd of violations
        self.rogScore   = ROGscore()
    #end def

    def criticize(self, project):
        """Only the self violations,violMax and violSd needs to be set before calling this routine"""
#        NTdebug( '%s (dih)' % self )
        if self.violMax >= project.valSets.AC_MAXALL_POOR:
            comment = '[crit.1] violMax: %8.3f' % self.violMax
            NTdebug(comment)
            self.rogScore.setMaxColor( COLOR_ORANGE, comment )
        if self.violMax >= project.valSets.AC_MAXALL_BAD:
            comment = '[crit.2] violMax: %8.3f' % self.violMax
            NTdebug(comment)
            self.rogScore.setMaxColor( COLOR_RED, comment )
        fractionAbove = getFractionAbove( self.violations, project.valSets.AC_THRESHOLD_OVER_POOR )
        if fractionAbove >= project.valSets.AC_THRESHOLD_FRAC_POOR:
            comment = '[crit.3a]: fractionAbove: %8.3f' % fractionAbove
            NTdebug(comment)
            self.rogScore.setMaxColor( COLOR_ORANGE, comment )
        fractionAbove = getFractionAbove( self.violations, project.valSets.AC_THRESHOLD_OVER_BAD )
        if fractionAbove >= project.valSets.AC_THRESHOLD_FRAC_BAD:
            comment = '[crit.3]: fractionAbove: %8.3f' % fractionAbove
            NTdebug(comment)
            self.rogScore.setMaxColor( COLOR_RED, comment )
        if self.violSd >= project.valSets.AC_RMSALL_BAD:
            comment = '[crit.4] violSd: %8.3f' % self.violSd
            NTdebug(comment)
            self.rogScore.setMaxColor( COLOR_RED, comment )



    def calculateAverage(self):
        """Calculate the values and violations for each model
        return cav and cv tuple or (None, None) tuple on error
        """

        modelCount = 0
        if len(self.atoms):
            modelCount = self.atoms[0].residue.chain.molecule.modelCount
        #end if

        if (modelCount == 0):
            NTerror('Error DihedralRestraint: no structure models\n' )
            return (None,None)
        #end if

        if len(self.atoms) != 4 or (None in self.atoms):
            NTerror('Error DihedralRestraint: invalid dihedral definition %s\n', self.atoms )
            return (None,None)
        #end if

        if None in self.atoms.zap('meanCoordinate'):
            NTerror('Error DihedralRestraint: atom without coordinates %s\n', self.atoms )
            return (None,None)
        #end if

        #set the default values
        self.dihedrals  = NTlist() # list with dihedral values for each model
        self.cav        = 0.0      # Average dihedral value
        self.cv         = 0.0      # cv on dihedral
#        self.min        = 0.0      # Minimum dihedral
#        self.max        = 0.0      # Max dihedral
        self.violations = NTlist() # list with violations for each model
        self.violCount1 = 0        # Number of violations over 1 degree
        self.violCount3 = 0        # Number of violations over 3 degrees
        self.violCount5 = 0        # Number of violations over 5 degrees
        self.violMax    = 0.0      # Maximum violation
        self.violAv     = 0.0      # Average violation
        self.violSd     = 0.0      # Sd of violations

        for i in range(modelCount):
            d = NTdihedralOpt(
                            self.atoms[0].coordinates[i],
                            self.atoms[1].coordinates[i],
                            self.atoms[2].coordinates[i],
                            self.atoms[3].coordinates[i]
                          )
            self.dihedrals.append( d )
        #end for

        #find the range to store these dihedral values
        #limit = 0.0
        #if limit > self.lower: limit = -180.0
        #self.dihedrals.limit(limit, limit+360.0)

        plotpars =plotParameters.getdefault( self.retrieveDefinition()[1],
                                             'dihedralDefault' )

        self.dihedrals.limit(plotpars.min, plotpars.max)

        # Analyze violations, account for periodicity
        for d in self.dihedrals:
            v = violationAngle(value=d, lowerBound=self.lower, upperBound=self.upper)
            fv = math.fabs(v)
            self.violations.append( v )
            if fv > 1.0: self.violCount1 += 1
            if fv > 3.0: self.violCount3 += 1
            if fv > 5.0: self.violCount5 += 1
            if fv > self.violMax: self.violMax = fv
            #end if
        #end for
        self.violAv,self.violSd,_n = self.violations.average()

        self.cav,self.cv,_n = self.dihedrals.cAverage(plotpars.min, plotpars.max)
        return( self.cav, self.cv )
    #end def

    def listViolatingModels(self, cutoff = 3.0 ):
        """
        Examine for violations larger then cutoff, return list of violating models or None on error
        Requires violations attribute (obtained with calculateAverage method).
        """
        if not self.has_key('violations'):
            return None

        violatingModels = NTlist()
        for i in range(0, len(self.violations) ):
            if (math.fabs( self.violations[i]) > cutoff):
                violatingModels.append( i )
            #end if
        #end for

        return violatingModels
    #end def

    def retrieveDefinition(self):
        """
        Retrieve a (<Residue>, angleName, <AngleDef>) tuple from
        the molecule.dihedralDict
        or
        (None,None,None) on error
        """
        if (not self.atoms or (None in self.atoms)):
            return (None,None,None)
        #end if
        mol = self.atoms[0].residue.chain.molecule

        if mol.dihedralDict.has_key(tuple(self.atoms)):
            return mol.dihedralDict[tuple(self.atoms)]
        else:
            return (None,None,None)
        #end if
    #end def

    def __str__(self):
        return sprintf('<DihedralRestraint %d>', self.id )
    #end def

    def format( self ):
        return  \
            sprintf('%-25s (Target: %6.1f %6.1f)  (Models: cav %6s cv %4s)  '+\
                    '(Violations: av %4s max %4.1f counts %2d,%2d,%2d) %s',
                        self, self.lower, self.upper,
                val2Str(self.cav,         "%6.1f", 6),
                val2Str(self.cv,          "%4.1f", 4),
                val2Str(self.violAv,      "%4.1f", 4),
                self.violMax, self.violCount1, self.violCount3, self.violCount5,
                        self.atoms.format('%-11s ')
                       )

    #end def
#end class


class DihedralRestraintList( NTlist ):

    def __init__( self, name, status='keep' ):
        NTlist.__init__( self )
        self.name       = name
        self.status     = status
        self.currentId  = 0       # Id for each element of list

        self.rmsd       = None    # rmsd per model, None indicate no analysis done
        self.rmsdAv     = 0.0
        self.rmsdSd     = 0.0
        self.violCount1 = 0       # Total violations over 1 degree
        self.violCount3 = 0       # Total violations over 3 degrees
        self.violCount5 = 0       # Total violations over 5 degrees
        self.rogScore   = ROGscore()
    #end def

    def criticize(self, project):
        for dr in self:
            dr.criticize(project)
            self.rogScore.setMaxColor( dr.rogScore.colorLabel, comment='Cascaded from: %s'%`dr` )

    def append( self, dihedralRestraint ):
        dihedralRestraint.id = self.currentId
        NTlist.append( self, dihedralRestraint )
        self.currentId += 1
    #end def

    def analyze( self, calculateFirst = True ):
        """
        Calculate averages for every restraint.
        Return <rmsd>, sd and total violations over 1, 3, and 5 degrees as tuple
        or (None, None, None, None, None) on error
        """
        if not len( self ):
            NTerror('DihedralRestraintList.analyze: "%s" empty list', self.name )
            return (None, None, None, None, None)
        #end if

        modelCount = 0
        if (len(self[0].atoms) > 0):
            modelCount = self[0].atoms[0].residue.chain.molecule.modelCount
        #end if

        if (modelCount == 0):
            NTerror('DihedralRestraintList.analyze: "%s" modelCount 0', self.name )
            return (None, None, None, None, None)
        #end if

        self.rmsd  = NTfill( 0.0, modelCount )
        self.violCount1 =  0
        self.violCount3 =  0
        self.violCount5 =  0
        for dr in self:
            if calculateFirst:
                (cav, _cv) = dr.calculateAverage()
                if not cav:
                    NTdebug("Failed to calculate average for: "+self.format())
            self.violCount1 += dr.violCount1
            self.violCount3 += dr.violCount3
            self.violCount5 += dr.violCount5
            for i in range(0, modelCount):
                self.rmsd[i] += dr.violations[i]*dr.violations[i]
            #end for
        #end for

        for i in range(0, modelCount):
            self.rmsd[i] = math.sqrt(self.rmsd[i]/len(self))
        #end for

        self.rmsdAv, self.rmsdSd, _n = NTaverage( self.rmsd )
        return (self.rmsdAv, self.rmsdSd, self.violCount1, self.violCount3, self.violCount5)
    #end def

    def sort(self, byItem ):
        """
        Sort the list byItem
        """
        NTsort( self, byItem, inplace=True)
        return self
    #end def

    def __str__( self ):
        return sprintf( '<DihedralRestraintList "%s" (%s,%d)>', self.name, self.status, len(self) )
    #end def

    def format( self ):
        return sprintf( '%s DihedralRestraintList "%s" (%s,%d) %s\n'+\
                        'rmsd: %7s %6s        Violations > 1,3,5 degree: %d, %d, %d\n',
                      dots, self.name,self.status,len(self), dots,
                      val2Str(self.rmsdAv,         "%7.3f", 7),
                      val2Str(self.rmsdSd,         "%6.3f", 6),
                      self.violCount1, self.violCount3, self.violCount5)
    #end def

    def save(self,path=None):
        """
        Create a SML file
        Return self or None on error
        """
        if not path: path = self.objectPath
        if self.SMLhandler.toFile(self, path) != self:
            NTerror('DihedralRestraintList.save: failed creating "%s"', path)
            return None
        #end if

        NTdetail('==> Saved %s to "%s"', self, path)
        return self
    #end def
#end class


class RDCRestraint( NTdict ):
    """RDCRestraint class:
    """
    def __init__( self, atomPairs=[], lower=0.0, upper=0.0, **kwds ):

        NTdict.__init__(self, __CLASS__  = 'RDCRestraint',
                              atomPairs  = NTlist(),
                              lower      = lower,
                              upper      = upper,
                              **kwds
                       )
        self.id         = -1       # Undefined index number
        self.rdcs        = None     # list with backcalculated rdc values for each model, None indicates no analysis done
        self.rogScore   = ROGscore()

        for pair in atomPairs:
            self.appendPair( pair )
        #end for

    #end def

    def appendPair( self, pair ):
        # check if atom already present, keep order
        # otherwise: keep atom with lower residue index first
        a0 = self.atomPairs.zap(0)
        a1 = self.atomPairs.zap(1)
        if (pair[0] in a0 or pair[1] in a1):
            self.atomPairs.append( pair )
        elif (pair[0] in a1 or pair[1] in a0):
            self.atomPairs.append( (pair[1],pair[0]) )
        elif (pair[0].residue.resNum > pair[1].residue.resNum):
            self.atomPairs.append( (pair[1],pair[0]) )
        else:
            self.atomPairs.append( pair )
    #end def

    def calculateAverage(self):
        """Calculate the values and violations for each model
        """

        modelCount = 0
        if (len(self.atoms) > 0):
            modelCount = self.atoms[0].residue.chain.molecule.modelCount
        #end if

        if (modelCount == 0):
            NTerror('Error RDCRestraint: no structure models\n' )
            return (None,None)
        #end if

        if len(self.atoms) != 2 or None in self.atoms:
            NTerror('Error RDCRestraint: invalid rdc definition %s\n', self.atoms )
            return (None,None)
        #end if

        if None in self.atoms.zap('meanCoordinate'):
            NTerror('Error RDCRestraint: atom without coordinates %s\n', self.atoms )
            return (None,None)
        #end if

        #set the default values

        return( None, None )
    #end def

    def listViolatingModels(self, cutoff = 3.0 ):
        """
        Examine for violations larger then cutoff, return list of violating models or None on error
        Requires violations attribute (obtained with calculateAverage method).
        """
        if not self.has_key('violations'):
            return None

        violatingModels = NTlist()
        for i in range(0, len(self.violations) ):
            if (math.fabs( self.violations[i]) > cutoff):
                violatingModels.append( i )
            #end if
        #end for

        return violatingModels
    #end def

    def _names(self):
        """
        Internal routine: generate string from atomPairs
        """
        s = ''
        for p in self.atomPairs:
            s = s + sprintf('(%-11s - %11s)   ', p[0]._Cname(1), p[1]._Cname(1))
        #end for
        return s.strip()
    #end def

    def __str__(self):
        return sprintf('<RDCRestraint %d>', self.id )
    #end def

    def format( self ):
#        s = '('
#        for p in self.atoms:
#            s = s + sprintf('%-11s ', p._Cname(1) )
#        #end for
#        s = s.strip() + ')'
        return  sprintf('%-25s (Target: %6.1f %6.1f) %s',
                        str(self), self.lower, self.upper,
                        self._names()
                       )

    #end def
#end class


class RDCRestraintList( NTlist ):

    def __init__( self, name, status='keep' ):
        NTlist.__init__( self )
        self.name       = name
        self.status     = status
        self.currentId  = 0       # Id for each element of list

        self.rmsd       = None    # rmsd per model, None indicate no analysis done
        self.rmsdAv     = 0.0
        self.rmsdSd     = 0.0
        self.rogScore   = ROGscore()
    #end def

    def append( self, RDCRestraint ):
        RDCRestraint.id = self.currentId
        NTlist.append( self, RDCRestraint )
        self.currentId += 1
    #end def

    def analyze( self, calculateFirst = True ):
        """
        Calculate averages for every restraint.

        """
        if (len( self ) == 0):
            NTerror('RDCRestraintList.analyze: "%s" empty list', self.name )
            return (None, None, None, None, None)
        #end if

        modelCount = 0
        if (len(self[0].atoms) > 0):
            modelCount = self[0].atoms[0].residue.chain.molecule.modelCount
        #end if

        if (modelCount == 0):
            NTerror('RDCRestraintList.analyze: "%s" modelCount 0', self.name )
            return (None, None, None, None, None)
        #end if

        self.rmsd  = NTfill( 0.0, modelCount )
        self.violCount1 =  0
        self.violCount3 =  0
        self.violCount5 =  0
        for dr in self:
            if calculateFirst: dr.calculateAverage()
            self.violCount1 += dr.violCount1
            self.violCount3 += dr.violCount3
            self.violCount5 += dr.violCount5
            for i in range(0, modelCount):
                self.rmsd[i] += dr.violations[i]*dr.violations[i]
            #end for
        #end for

        for i in range(0, modelCount):
            self.rmsd[i] = math.sqrt(self.rmsd[i]/len(self))
        #end for

        self.rmsdAv, self.rmsdSd, dummy_n = NTaverage( self.rmsd )
        return (self.rmsdAv, self.rmsdSd, self.violCount1, self.violCount3, self.violCount5)
    #end def

    def sort(self, byItem ):
        """
        Sort the list byItem
        """
        NTsort( self, byItem, inplace=True)
        return self
    #end def

    def __str__( self ):
        return sprintf( '<RDCRestraintList "%s" (%s,%d)>', self.name, self.status, len(self) )
    #end def

    def format( self ):
        s = sprintf( '%s RDCRestraintList "%s" (%s,%d) %s\n' +\
                     'rmsd: %7.3f %6.3f\n',
                      dots, self.name,self.status,len(self), dots,
                      self.rmsdAv, self.rmsdSd )
        return s
    #end def

    def save(self,path=None):
        """
        Create a SML file
        Return self or None on error
        """
        if not path: path = self.objectPath
        if self.SMLhandler.toFile(self, path) != self:
            NTerror('RDCRestraintList.save: failed creating "%s"', path)
            return None
        #end if

        NTdetail('==> Saved %s to "%s"', self, path)
        return self
    #end def
#end class


class History( NTlist ):
    """Cing history storage class
    """

    def __call__( self, line, timeStamp = True ):
        if timeStamp:
            self.append( (time.asctime(), line) )
        else:
            self.append( (None, line) )
        #end if
    #end def

    def __str__( self ):
        s = sprintf('%s History %s\n', dots, dots )
        for timeStamp,line in self:
            if timeStamp:
                s = s + sprintf('%s: %s\n', timeStamp, line )
            else:
                s = s + line + '\n'
            #end if
        #end for
        return s
    #end def

    format = __str__

    def toXML( self, depth=0, stream=sys.stdout, indent='\t', lineEnd='\n' ):
        NTindent( depth, stream, indent )
        fprintf( stream, "<History>")
        fprintf( stream, lineEnd )

        for a in self:
            NTtoXML( a, depth+1, stream, indent, lineEnd )
        #end for
        NTindent( depth, stream, indent )
        fprintf( stream, "</History>")
        fprintf( stream, lineEnd )
    #end def
#end class


class XMLHistoryHandler( XMLhandler ):
    """History handler class"""
    def __init__( self ):
        XMLhandler.__init__( self, name='History')
    #end def

    def handle( self, node ):
        items = self.handleMultipleElements( node )
        if items == None: return None
        result = History()
        for item in items:
            result.append( item )
        return result
    #end def
#end class

#register this handler
historyhandler = XMLHistoryHandler()


htmlObjects = NTlist() # A list of all htmlobject for rendering purposes

class HTMLfile:
    '''Description: Class to create a Html file; to be used with cing.css layout.
       Inputs: file name, title
       Output: a Html file.
    '''
    # A list of all htmlobject for rendering purposes
    #htmlObjects = NTlist() # Local track-keeping list

    def __init__( self, fileName, title = None ):
        '''Description: __init__ for HTMLfile class.
           Inputs: file name, title
           Output: an instanciated HTMLfile obj.

           The file is immidiately tested by a quick open for writing and closing.
        '''

        self.fileName = os.path.normpath( fileName )
        self.stream = open( self.fileName, 'w' )
        self.stream.close()

        # definition of content-less  tags
        self.noContent = [ 'base','basefont','br','col','frame','hr','img',
                           'input','link','meta','ccsrule', 'script' ]

        self.title = title
        self.indent = 0

        self._header    = NTlist()
        self._call      = NTlist()
        self._main      = NTlist()
        self._left      = NTlist()
        self._right     = NTlist()
        self._footer    = NTlist()

        htmlObjects.append( self )
    #end def

    # Having a del method might upset the gc.
#    def __del__(self):
#        print '>>deleting>', self.title, self.fileName
#        print self
#        if self in htmlObjects:
#            htmlObjects.remove(self)
#        del( self )
#    #end def

    def killHtmlObjects():  # note there is no 'self', it's going to be a static method!
        """ Remove all objects from the htmlObjects list
            """
        while htmlObjects.pop():
            pass # I think this should work to clear the list

    killHtmlObjects = staticmethod( killHtmlObjects)

    def _appendTag( self, htmlList, tag, *args, **kwds ):
        '''Description: core routine for generating Tags.
           Inputs: HTMLfile obj, list, tag, openTag, closeTag, *args, **kwds.
           Output: list.
        '''
        self.indent += 1
        htmlList.append( self._generateTag( tag, *args, **kwds ) )
        self.indent -= 1
    #end def

    def _generateTag( self, tag, *args, **kwds ):
        '''Description: core routine for generating Tags.
           Inputs: HTMLfile obj, tag, openTag, closeTag,
                   newLine, *args, **kwds.
           Output: list.
        '''

        #self.indent += 1

        if kwds.has_key('openTag'):
            openTag = kwds['openTag']
            del kwds['openTag']
        else:
            openTag = True

        if kwds.has_key('closeTag'):
            closeTag = kwds['closeTag']
            del kwds['closeTag']
        else:
            closeTag = True

        if kwds.has_key('newLine'):
            newLine = kwds['newLine']
            del kwds['newLine']
        else:
            newLine = True
        v = { True: None, False: -1 }

        #print '****', htmlList,'*',tag,'*', openTag,'*', closeTag, '*', args

        if openTag and closeTag:
            s = ( self.openTag( tag, *args, **kwds )[:-1] +
                  self.closeTag(tag)[self.indent:v[newLine]] )
        elif openTag:
            s = ( self.openTag( tag, *args, **kwds ) )
        elif closeTag:
            s = ( self.closeTag( tag, *args, **kwds ) )
        #end if
        #self.indent -=1

        return s
    #end def

    def header( self, tag, *args, **kwds ):
        self.indent +=1
        self._appendTag( self._header, tag, *args, **kwds )
        self.indent -=1
    #end def

    def __call__( self, tag, *args, **kwds ):
        "Write openTag, content, closeTag (if appropriate)"
        self.indent +=1
        self._appendTag( self._call, tag, *args, **kwds )
        self.indent -=1
    #end def

    def main( self, tag, *args, **kwds ):
        self.indent +=1
        self._appendTag( self._main, tag, *args, **kwds )
        self.indent -=1
    #end def

    def left( self, tag, *args, **kwds ):
        self.indent +=1
        self._appendTag( self._left, tag, *args, **kwds )
        self.indent -=1
    #end def

    def right( self, tag, *args, **kwds ):
        self.indent +=1
        self._appendTag( self._right, tag, *args, **kwds )
        self.indent -=1
    #end def

    def footer( self, tag, *args, **kwds ):
        self._appendTag( self._footer, tag, *args, **kwds )
    #end def

    def render(self):
        '''Description: write container to file Html.
           Inputs: a HTMLfile obj.
           Output: written lines and close file.

           JFD notes it is simpler to code this as constructing the whole content
           first and then writing. It would be just as fast for the size
           of html files we render.
        '''

        self.stream = open( self.fileName, 'w' )
#        NTdebug('writing to file: %s' % self.fileName)
        self.indent = 0
        # JFD proposes to drop the below tags because they hinder javascript beyond my knowledge.
#        self.stream.write(self.openTag('!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"'))
        self.stream.write(self.openTag('html'))
        self.stream.write(self.openTag('head'))
        if self.title:
            self.stream.write( self._generateTag( 'title', self.title ))

        relativePath = self.relativePath()
        cssLink = os.path.join(relativePath, cingPaths.css)
        jsMultiLineLink = os.path.join(relativePath, cingPaths.jsMultiLine)
        self.stream.write(self._generateTag( 'link',
            rel="stylesheet", type="text/css", media="screen", href=cssLink))
        self.stream.write(self._generateTag( 'script', # Not needed for all but always nice.
            type="text/javascript", src=jsMultiLineLink))

        self.stream.write(self.closeTag('head'))
        self.stream.write(self.openTag('body'))
        self.stream.write(self.openTag('div', id="container"))
        self.indent += 1

        self.stream.write( self.openTag('div', id = 'header') )
        self.stream.writelines(self._header)
        self.stream.write(self.closeTag('div', '<!-- end header -->'))

        self.stream.write( self.openTag('div', id = 'main') )
        self.stream.writelines(self._call + self._main)

        for divId, htmlList in [ ('left', self._left), ('right', self._right) ]:

            if htmlList:
                self.indent += 1

                self.stream.write( self.openTag('div', id = divId) )
                self.stream.writelines(htmlList)
                self.stream.write(self.closeTag('div',sprintf('<!-- end %s -->',
                                                              divId)))
                self.indent -= 1
        self.stream.write(self.closeTag('div', '<!-- end main -->'))
        self.stream.write(self._generateTag( 'br', style="clear: both;" ))

        self.indent = 0

        self.stream.write(self.closeTag('div', '<!-- end container -->'))

        self.stream.write(self.openTag('div', id = 'footer'))
        #self.defaultFooter()
        self.stream.writelines(self._footer)
        msg = programName + ' ' + cingVersion + ' '
        i=0
        n=len(authorList)
        for author in authorList:
            i+=1
            msg +=  '<a href="mailto:%s">%s</a>' % ( author[1],author[0])
            if i==(n-1):
                msg += ' and '
            elif i<n:
                msg += ', '
        self.stream.write(self._generateTag( 'p', msg))
        self.stream.write(self.closeTag('div', '<!-- end footer -->'))

        self.stream.write(self.closeTag('body'))
        self.stream.write(self.closeTag('html'))

        self.stream.close()

    def tag( self, tag, *args, **kwds ):
        "Return (openingTag, content, closingTag) triple"

        #print '*****', tag, [args], (kwds)
        openTag = sprintf('<%s',tag)
        for key,value in kwds.iteritems():
            openTag = openTag + sprintf(' %s="%s"', key, value)
        #end for

        if (tag in self.noContent):
            openTag = openTag +  '/>'
        else:
            openTag = openTag +  '>'
        #end if

        content = ''.join(args)
        if (tag in self.noContent):
            closeTag = ''
        else:
            closeTag = sprintf('</%s>',tag)
        #end if
        return (openTag,content,closeTag)
    #end def

    def openTag( self, tag, *args, **kwds ):
        "Write openTag, content; NO closeTag"
        openTag, content, dummyCloseTag = self.tag( tag, *args, **kwds )
        return sprintf( '%s%s%s\n', '' + '\t' * self.indent, openTag, content )
    #end def

    def closeTag( self, tag, *args, **kwds ):
        "Write closeTag *args"
        dummyOpenTag, content, closeTag = self.tag( tag, *args, **kwds )
        return sprintf( '%s%s%s\n', '' + '\t' * self.indent, closeTag, content )
    #end def

    def relativePath(self):
        ''' Description: return relative path between htmlObj and project
            directory.
            Inputs: htmlObj
            Output: relative path to project root
            Example: htmlObj molecule: Ccpn_1brv
                     project.molecule.html.fileName (1brvV1.cing/Ccpn_1brv/HTML/index.html)
                     returns: '../../'
        '''
        fileName = self.fileName
        sep = os.path.sep
        #pardir = os.path.pardir
        pardirSep = '../' #pardir + sep # '../' is standard for html, no matter if Windows OS.
        countSep = fileName.count(sep)
        return (countSep - 1) * pardirSep

    def findHtmlLocation(self, source, destination, id=None ):
        '''Description: given 2 Cing objects returns the relative path between them.
           Inputs: Cing objects souce, destination
           Output: string path or None or error

           E.g. input: source.htmlLocation[0]     : test_HTMLfile.cing/index.html
                       destination.htmlLocation[0]: test_HTMLfile.cing/moleculeName/HTML/indexMolecule.html
                output                            : moleculeName/HTML/indexMolecule.html
        '''
        # Debugger perspecitive put at source (me)
        # Destination is the target.
        for item in [source, destination]:
            if not hasattr(item,'htmlLocation'):
                NTerror('No htmlLocation attribute associated to obj %s\n', item)
                return None

        # Strip leading dot for rest of algorithm.
        # Normalize path, eliminating double slashes, etc.
        sourcePath = os.path.normpath(     source.htmlLocation[0])
        destPath   = os.path.normpath(destination.htmlLocation[0])
        # Get default id.
        destId     = destination.htmlLocation[1]
        # Or override.
        if id:
            destId = '#' + id

        listSourcePath = sourcePath.split('/')
        listDestPath   = destPath.split('/')

        # JFD next code is disabled because the comparison might shortcircuit
        # when identical names are matched 'by accident'.
#        for index in range(lenSP):
#            if listSourcePath[index] != listDestPath[index]:
#                #location = index * ['..'] + listDestPath
#                break
#        i = lenSP - 1 - index
#        locationList = (index + i) * ['..'] + listDestPath
#        loc = ''
#        for item in location:
#            loc = os.path.join(loc,item)
#        loc = os.path.join( *locationList )

        # How far away (in dir changes) am I from the first (left/cing) dir?
        # The list will look like:  list: ['test_HTMLfile.cing', 'index.html']
        # One jump is one directory.
        # E.g. 1brv/1brv/index.html has 2 jumps.

        toLeftNumberOfJumpsSource = len(listSourcePath) - 1
        toLeftNumberOfJumpsDest   = len(listDestPath)   - 1

        # Any same leading directories may be ommited.
        # using the fact that they are rooted in the same starting dir (curdir)
        toLeftNumberOfJumpsSourceNew = toLeftNumberOfJumpsSource
        i = 0
        while i < toLeftNumberOfJumpsDest and i < toLeftNumberOfJumpsSource:
            if listSourcePath[i] == listDestPath[i]:
                toLeftNumberOfJumpsSourceNew -= 1
            else:
                break
            i += 1
        jumpsToRemove = toLeftNumberOfJumpsSource - toLeftNumberOfJumpsSourceNew
        listDestPathNew = listDestPath[jumpsToRemove:]
        locationList = toLeftNumberOfJumpsSourceNew * ['..']
        locationList += listDestPathNew
        loc = os.path.join( *locationList )
        loc = os.path.normpath(loc) # I don't think it's needed anymore but can't hurt either.
        return loc + destId

    def insertHtmlLink( self, section, source, destination, text=None, id=None ):
        '''Description: create the html command for linking Cing objects.
           Inputs: section (main, header, left etc.), source obj., destination
                   obj., html text, id.
           Output: <a class="red" href="link">text</a> inside section

           Example call: project.html.insertHtmlLink( main, project, item, text=item.name )

           And the funny thing is that if the destination has an attribute:
               'rogScore.colorLabel' then it will be used to define an html class with
               which through the cing.css can be used for defining coloring
               schemes.
        '''

        if not section:
            NTerror("No HTML section defined here\n")
            return None

        if not source:
            NTerror("No Cing object source defined here\n")
            return None

        if not destination:
            NTerror("No Cing object destination defined here\n")
            return None

        link = self.findHtmlLocation( source, destination, id )
#        NTdebug('From source: [%s] to destination [%s] id [%s] using relative link: %s' % (source, destination, id,link))


        kw = {'href':link}
        #if not destination.has_key('colorLabel'):
        if hasattr(destination, 'rogScore'):
#            destination.colorLabel = COLOR_GREEN
            if destination.rogScore.isCritiqued():
                # solution for avoiding python 'class' command with html syntax
                kw['class'] = destination.rogScore.colorLabel
                destination.rogScore.addHTMLkeywords( kw )
        section('a', text, **kw)
    #end def

    def insertHtmlLinkInTag( self, tag, section, source, destination, text=None,
                             id=None):
        '''Description: create the html command for linking Cing objs inside a tag.
           Inputs: tag, section (main, header, left etc.), source obj.,
                   destination obj., html text, id.
           Output: <h1><a class="red" href="link">text</a></h1> inside section

        Example call:
                    project.html.insertHtmlLinkInTag( 'li', main, project, item, text=item.name )

        '''

        section(tag, closeTag=False)
        self.insertHtmlLink(section, source, destination, text=text, id=id)
        section(tag, openTag=False)

#end class

def path( *args ):
    """
    Return a path from arguments relative to cing root
    """
    return os.path.join( cingRoot, *args )
#end def

def shift( atm ):
    return atm.shift()
#end def


def getFractionAbove( valueList, threshold ):
    """Return the fraction that is above the threshold. Return .0 if
    list contains no values.
    """
    if not valueList:
        return .0
    n = 0.0 # enforce float arithmics for below division.
    for v in valueList:
        if not v: # catch None and pure zero
            continue
        if v > threshold:
            n += 1.
    return n / len(valueList)

#-----------------------------------------------------------------------------
class AtomList( NTlist ):
    """
    Class based on NTlist that holds atoms.
    Also manages the "id's".
    Sort by item of Atom Class.

    NB this list is only instantiated for the validate plugin. It has very little
    functionality. Most functionality should be in Residue, Chains, etc.
    """
    def __init__( self, project, status='keep' ):
        NTlist.__init__( self )
        self.name       = 'Atom List'
        self.status     = status      # Status of the list; 'keep' indicates storage required
        self.currentId  = 0       # Id for each element of list
        self.rogScore = ROGscore()
        self.appendFromMolecule( project.molecule )
        self.criticize()
    #end def

    def criticize(self):
        for atom in self:
#            atom.criticize()
            self.rogScore.setMaxColor( atom.rogScore.colorLabel, comment='Cascaded from: %s'%atom.toString() )

    def append( self, o ):
        o.id = self.currentId
        NTlist.append( self, o )
        self.currentId += 1

    def appendFromMolecule( self, molecule ):
        for atom in molecule.allAtoms():
            self.append( atom )

    def __str__( self ):
        return sprintf( '<AtomList "%s" (%s,%d)>',self.name,self.status,len(self) )
    #end def

    def format( self ):
        return sprintf( '%s AtomList "%s" (%s,%d) %s\n',
                      dots, self.name,self.status,len(self), dots)
