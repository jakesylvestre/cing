'''
Created on Mar 25, 2010

This class thinks of a bunch of CSV files (such as created by Mac Numbers in iWork) as a database
much like the code in Wattos.Database.DBMS.
@author: jd
'''
from StringIO import StringIO
from cing.Libs.NTutils import * #@UnusedWildImport
import csv
import urllib

DEFAULT_COLUMN_LABEL = 'COLUMN_' # a number will be added.
ROW_WITHOUT_COLUMNS_STRING   = "No columns present"
NULL_STRING = '' # may be modified

class Relation():

    def __init__(self, name, dbms, columnList=None):
        # Name for the column. Only place where order of columns is defined and matters.*/
        self.columnOrder = []
        self.name = name
        # Other objects that should all be native arrays with using parallel indices as the above.
        self.attr = {}
        self.dbms = dbms
        self.dbms.tables[self.name] = self
        if columnList:
            for col in columnList:
                self.insertColumn(label=col)


    def insertColumn(self, index=-1, label=None, foreignKeyConstr=None):
        """Insert a column for a certain variable type; before the given position.
         label Column name; has to be unique.
        """
#        if ( hasColumn( label )  ) {
#            General.showWarning("in insertColumn label already present for label: [" +
#                label + "] and type: [" + dataTypeList[dataType] + "]. So didn't add another column with this label.");
#            return false;
#        }

#        if ( index > sizeColumns() ) {
#            General.showWarning("in insertColumn the given index for the new column ("+index+") is larger than the current size: [" +
#                sizeColumns() + "] that's impossible. No column added.");
#            return false;
#        }

        if index == -1:
            index = self.sizeColumns()
        if label == None: # label may be empty string or a zero of some sort except None
            label = DEFAULT_COLUMN_LABEL + `index`


        self.columnOrder.insert(index, label)
        self.attr[label] = []

    def sizeColumns(self):
        return len(self.columnOrder)

    def sizeRows(self):
        firstColumn = self.attr[ self.columnOrder[0] ]
        return len(firstColumn)

    def getColumnByIdx(self, idx):
        label = self.columnOrder[idx]
        return self.attr[label]

    def getColumn(self, label):
        if label not in self.columnOrder:
            NTerror("Requested column label is absent in table: %s" % self.name)
            return None
        return self.attr[label]

    def readCsvFile(self, file_name, containsHeaderRow, dtd_file_name=None):
        """
     *If containsHeaderRow is false then the default labels will be used.
     *dtd file if not existing defaults to all elements being STRING.
     *If it does exist,  it should be formatted as a csv file with the first two
     *columns having the column name and the column data type as strings.
        """
#        //General.showDebug("Reading from file    : " + file_name);
#        //General.showDebug(" with header         : " + containsHeaderRow);
#        //General.showDebug(" and dtd             : " + dtd_file_name);

        url_links = 'file://' + file_name
#        NTdebug("Reading from %s" % (url_links))
        try:
            resource = urllib.urlopen(url_links)
            reader = csv.reader(resource)
        except IOError:
            NTtracebackError()
            NTerror("Couldn't open url for reader: " + url_links)
            return True

        ncols = -1
        try:
            if containsHeaderRow:
                row = reader.next()
#                NTdebug("read header: %s" % row)
                ncols = len(row)
                for c in range(ncols):
                    self.insertColumn(label=row[c])
            for row in reader:
                if ncols == -1: # Without a header the table columns will have default labels.
                    ncols = len(row)
                    for c in range(ncols):
                        self.insertColumn()
                if len(row) != ncols:
                    NTerror("Failed to read correct number of columns on line: %s" % row)
                    return True
                for c in range(ncols):
                    label = self.columnOrder[c]
                    l = self.attr[label]
                    l.append(row[c])
        # Never know when the connection is finally empty.
        except IOError:
            pass
        NTdebug("Read %8d rows %2d cols to relation %s" % (self.sizeRows(), self.sizeColumns(), self.name))


    def writeCsvFile(self, file_name=None, doHeader=True):
        """Returns True on error.
        File name will be derived from table name if omitted.
        """

        txt = ''
        if doHeader:
            txt += ','.join(self.columnOrder)
            txt += '\n'
        firstColumn = self.getColumnByIdx(0)
        nrows = len(firstColumn)
        ncols = len(self.columnOrder)
        dataAsMatrix = []
        for c in range(ncols):
            dataAsMatrix.append(self.getColumnByIdx(c))

        rowStrList = []
        for r in range(nrows):
            colStrList = []
            for c in range(ncols):
                colStrList.append( str(dataAsMatrix[c][r]) )
            # end for c
            rowStr = ','.join(colStrList)
#            NTdebug("Adding rowStr: %s" % rowStr)
            rowStrList.append( rowStr )
        # end for r
        resultStr = txt + '\n'.join(rowStrList)

        if not file_name:
            file_name = self.name + '.csv'
        NTmessage("Will write %s nrows and %s ncols to %s" % (nrows,ncols,file_name))
        if writeTextToFile(file_name, resultStr):
            NTerror("Failed to write string to file: %s" % file_name)
            return True

    def getHash(self, keyColumnLabel = None, ignoreDuplicateKeyWithoutWarning = False):
        """Takes a DMBS table and turns it into a hash on the keyColumnLabel with
        values a list of all columns.
        If the keyColumnLabel is None then the first column will be used.
        One warning will be issued if the column contains multiple keys. The code
        will skip consecutive occurrences.

        Returns False on error.
        """

        dic = {}

        if keyColumnLabel == None:
            keyColumn = self.getColumnByIdx(0)
        else:
            keyColumn = self.getColumn(keyColumnLabel)
        if keyColumn == None:
            return
        columnList = [ self.getColumnByIdx(i) for i in range(self.sizeColumns())]

        duplicateKeyFound = False
        for idx, k in enumerate(keyColumn):
            if dic.has_key(k):
                duplicateKeyFound = 'Last duplicate key found was for row idx: %s with key: %s' % ( idx, k )
                continue
            columnValues = [ columnList[i][idx] for i in range(self.sizeColumns())]
            dic[k] = columnValues

        if duplicateKeyFound:
            if ignoreDuplicateKeyWithoutWarning:
                NTdebug(duplicateKeyFound)
            else:
                NTwarning(duplicateKeyFound)
        return dic

    def isValidColumnIdx( self, columnIdx ):
        'Just checking'
        if ( ( columnIdx < 0 ) or ( columnIdx > (self.sizeColumns()-1))):
            return False
        return True

    def getColumnLabel( self, index ):
        'Return False on error'
        if not self.isValidColumnIdx(index):
            NTerror("in getColumnLabel: given index is not valid for columns: %s" % index);
            return
        label = self.columnOrder[index]
        return label

    def __str__( self, show_header = True,
#         show_data_types= True,
#         show_fkcs= True,
#         show_indices= True,
         show_rows= True):
        """
        This will create a string representation. The code in here should not
        need to be optimized because it is never intended to use this for millions of
        rows in an efficient way.
        Returns None in case of error.
        """

        sizeColumns = self.sizeColumns()
        sizeRows = self.sizeRows()
        if sizeColumns < 1:
            return    "---  Relation        : " + self.name + " has NO columns ---\n"

        file_str = StringIO()
#        // Header
        if show_header:
#            boolean containsForeignKeyConstraints = false;
#            boolean containsindices               = false;
            file_str.write("---  Relation        : " + self.name + " ---\n");
            file_str.write("---  Column Labels   : ");
            for i in range(sizeColumns):
                label = self.getColumnLabel(i);
                file_str.write( label );
#                ForeignKeyConstr fkc = dbms.foreignKeyConstrSet.getForeignKeyConstrFrom(name,label);
#                if ( fkc != null ) {
#                    containsForeignKeyConstraints = true;
#                }
#                if ( indices.containsKey( label ) ) {
#                    containsindices = true;
#                }
                if i < ( sizeColumns - 1 ):
                    file_str.write(",")
                else:
                    file_str.write(" ---\n");

#            // Datatypes
#            if (show_data_types) {
#                file_str.write("---  Data Types      : ");
#                for (int i=0;i<sizeColumns;i++) {
#                    String label = getColumnLabel(i);
#                    int dataType = getColumnDataType(label);
#                    file_str.write(dataTypeList[dataType]);
#                    //file_str.write("("+dataType+")");
#                    if ( i < ( sizeColumns - 1 ) )
#                        file_str.write(",");
#                    else
#                        file_str.write(" ---\n");
#                }
#            }
#            // Foreign Key Constraints
#            if ( containsForeignKeyConstraints && show_fkcs ) {
#                file_str.write("---  Foreign Key Constraints   :\n");
#                for (int i=0;i<sizeColumns;i++) {
#                    String label = getColumnLabel(i);
#                    ForeignKeyConstr fkc = dbms.foreignKeyConstrSet.getForeignKeyConstrFrom(name,label);
#                    if ( fkc != null ) {
#                        file_str.write( "\t" );
#                        file_str.write( fkc.toString() );
#                        file_str.write( General.eol );
#                    }
#                }
#            }
#            // indices
#            if ( containsindices && show_indices ) {
#                file_str.write("---  indices                   :\n");
#                for (int i=0;i<sizeColumns;i++) {
#                    String label = getColumnLabel(i);
#                    if ( indices.containsKey( label )) {
#                        // Check all elements in array to see if there is such an index
#                        Index[] al = (Index[]) indices.get( label );
#                        for (int j=0;j<Index.INDEX_TYPE_COUNT;j++) {
#                            Index index = al[j];
#                            if ( index == null ) { // will skip zero-th element
#                                continue;
#                            }
#                            file_str.write( "\tColumn " );
#                            file_str.write( label );
#                            file_str.write( " has index. " );
#                            file_str.write( index.toString() );
#                            file_str.write( General.eol );
#                        }
#                    }
#                }
#            }
#        }

        if show_rows:
            if sizeRows < 1 :
                file_str.write("---  Empty Relation (%s columns but no rows) ---\n" % sizeColumns);
                return file_str.getvalue()
            for r in range(sizeRows):
                rowString = self.toStringRow( r )
                if rowString == None:
                    NTerror("Failed to get row as a string for row %s from relation %s" % (r,self.name))
                    return None
                file_str.write( rowString ) # Get the row representation.
                file_str.write('\n')

        return file_str.getvalue()


    def toStringRow(self, row, showColumnLabels=False):
        """Still need to program correct quote styles for csv format if that becomes important.
         Returns ROW_WITHOUT_COLUMNS_STRING
         if there are no columns in the table.
         Return None on error.
         """
        if self.sizeColumns() == 0:
            return ROW_WITHOUT_COLUMNS_STRING

        file_str = StringIO()
        sizeColumns = self.sizeColumns()
        sizeColumnsMinusOne = sizeColumns - 1
        if showColumnLabels:
            file_str.write( "[Header] " )
            for c in range(sizeColumns):
                file_str.write( self.getColumnLabel(c) )
                if c < sizeColumnsMinusOne:
                    file_str.write(',')
            file_str.write('\n')
        file_str.write( "[%s] " % row )
        for c in range(sizeColumns):
            valueString = self.getValueString(row,c)
            if valueString == None:
                NTerror("Failed to get value as a string for row %s, column %s from relation %s" % (row,c,self.name))
                return None
            file_str.write( self.getValueString(row,c) )
            if c < sizeColumnsMinusOne:
                file_str.write(',')
        return file_str.getvalue()

    def getValueString( self, row, column):
        """
        Returns None on error.
        Returns module variable NULL_STRING for None values. Modify if needed.
        """
        label = self.getColumnLabel(column);
#        // Sanity checks
        if label == False:
            NTerror("Failed to Relation.getValueString for column idx %s. Existing column labels:" % (
                column, str(self.columnOrder)))
            return None
        column = self.getColumnByIdx(column)
        sizeRows = self.sizeRows()
        if row < 0 or row >= self.sizeRows():
            NTerror("Failed to Relation.getValueString for row idx %s is not in range of (0,%s) for column %s." % (
                row, label, sizeRows))
            return None

        value = column[row]
        if value == None:
            return NULL_STRING
        return str(value)


class DBMS():
    def __init__(self):
        self.tables = {}

    def readCsvRelationList(self, relationNames, csvFileDir='.',
            csvDtdFileDir=None, checkConsistency=False, showChecks=False, containsHeaderRow=True):
        csvFilesRead = len(relationNames)
        for i in range(csvFilesRead):
            relation = Relation(relationNames[i], self)
#            NTmessage("Reading relation : " + relation.name)
            csvFileDir = os.path.abspath(csvFileDir)
            csv_fileName = os.path.join(csvFileDir, relation.name + ".csv")
            if relation.readCsvFile(csv_fileName, containsHeaderRow):
                NTerror("Failed to read csv file: " + csv_fileName)
                return True

