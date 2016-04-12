
from dimensioning import *
import selectionOverlay, previewDimension
from dimensionSvgConstructor import *

d = DimensioningProcessTracker()

def tableSVG( top_left_x, top_left_y, column_widths, contents, row_heights,
                   border_width=0.5, border_color='black', padding_x=1.0, padding_y=1.0, extra_rows=0,
                   textRenderer_table=defaultTextRenderer):
    no_columns = len(column_widths)
    no_rows = int( numpy.ceil( len(contents) / float(no_columns) ) + extra_rows )
    XML_body = [ ]
    def addLine(x1,y1,x2,y2):
        'relative to top_left corner of table'
        XML_body.append('<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:%s;stroke-width:%1.2f" />' % (x1, y1, x2, y2, border_color, border_width) )
        #building table body
    width = sum( column_widths )
    addLine( 0, 0, width, 0 )
    y_offset = 0
    row_y = []
    for i in range(no_rows):
        y_offset += row_heights[ i % len(row_heights) ]
        row_y.append( y_offset )
        addLine( 0, y_offset, width, y_offset )
    #debugPrint(1, 'row y : ' + str(row_y))
    x_offset = 0
    column_x = []
    addLine( 0, 0, 0, y_offset )
    for j in range(no_columns):
        column_x.append( x_offset )
        x_offset += column_widths[j]
        addLine( x_offset, 0, x_offset, y_offset )
    for i, text in enumerate( contents ):
        row = int(i / no_columns)
        col = i % no_columns
        XML_body.append( textRenderer_table( 
                column_x[col] + padding_x, 
                row_y[row] - padding_y, 
                text ) )
    return  '''<g transform="translate(%f,%f)" > %s </g>''' % ( top_left_x, top_left_y, '\n'.join(XML_body) )

d.registerPreference( 'column_widths', [20.0, 30.0], kind='float_list')
d.registerPreference( 'contents', 'number of rows adjusted to fit table contents'.split(' '), kind='string_list')
d.registerPreference( 'row_heights', [7.0], kind='float_list')
d.registerPreference( 'border_width', 0.3, increment=0.05  )
d.registerPreference( 'border_color',  RGBtoUnsigned(0, 0, 0), kind='color')
d.registerPreference( 'padding_x', 1.0 )
d.registerPreference( 'padding_y', 1.0 )
d.registerPreference( 'extra_rows', 0, decimals=0 )
d.registerPreference( 'textRenderer_table', ['inherit','5', 0], 'text properties (table)', kind='font' )

d.max_selections = 1
def table_preview(mouseX, mouseY):
    selections = d.selections + [ PlacementClick( mouseX, mouseY) ] if len(d.selections) < d.max_selections else d.selections
    return tableSVG( *selections_to_svg_fun_args(selections), **d.dimensionConstructorKWs )

def table_clickHandler( x, y ):
    d.selections.append( PlacementClick( x, y) )
    if len(d.selections) == d.max_selections:
        return 'createDimension:%s' % findUnusedObjectName('table')

def selectFun( event, referer, elementXML, elementParms, elementViewObject ):
    viewInfo = selectionOverlay.DrawingsViews_info[elementViewObject.Name]
    d.selections = [ PointSelection( elementParms, elementXML, viewInfo ) ]
    selectionOverlay.hideSelectionGraphicsItems()
    previewDimension.initializePreview( d, noteCircle_preview, noteCircle_clickHandler)


class Proxy_table( Proxy_DimensionObject_prototype ):
     def dimensionProcess( self ):
         return d
d.ProxyClass = Proxy_table
d.proxy_svgFun = tableSVG


class AddTable:
    def Activated(self):
        V = getDrawingPageGUIVars() 
        d.activate( V,  dialogTitle='Add Table', dialogIconPath= ':/dd/icons/table_dd.svg', endFunction=self.Activated )
        previewDimension.initializePreview( d, table_preview, table_clickHandler)
        
    def GetResources(self): 
        return {
            'Pixmap' : ':/dd/icons/table_dd.svg' , 
            'MenuText': 'Add table to drawing', 
            'ToolTip': 'Add table to drawing'
            } 
FreeCADGui.addCommand('dd_addTable', AddTable())

