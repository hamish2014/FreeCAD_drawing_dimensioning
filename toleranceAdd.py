'''
Dialog notes
------------
Use Qt Designer to edit the toleranceDialog.ui
Once completed 
    $ pyside-uic toleranceDialog.ui > toleranceDialog.py
'''

from dimensioning import *
import previewDimension, selectionOverlay 
import toleranceDialog
from textEdit import maskBrush, maskPen, maskHoverPen
from dimensionSvgConstructor import *

d = DimensioningProcessTracker()

def _textSVG_sub(x_offset, y_offset, text, comma_decimal_place, rotation, text_x, text_y ):
    offset = rotate2D([x_offset, y_offset], rotation*numpy.pi/180)
    x = text_x + offset[0]
    y = svgText.y + offset[1]
    return d.textRenderer(x, y, text if not comma_decimal_place else text.replace('.',','),
                          text_anchor='end', rotation=svgText.rotation )

def textSVG( text_x, text_y, text, font_size, rotation, font_family, font_fill, x, y, text_upper, text_lower, toleranceText_sizeRatio=0.8, comma_decimal_place=False ):
    fS = float(font_size) * toleranceText_sizeRatio
    textRenderer = SvgTextRenderer(
            font_family = font_family, 
            fill = font_fill,
            font_size = fS
            )
    w = rotate2D([x - text_x, y - text_y], -rotation*numpy.pi/180)[0]
    def _textSVG_sub(x_offset, y_offset, text ):
        offset = rotate2D([x_offset, y_offset], rotation*numpy.pi/180)
        x = text_x + offset[0]
        y = text_y + offset[1]
        return textRenderer(x, y, text if not comma_decimal_place else text.replace('.',','),
                            text_anchor='end', rotation=rotation )
    textXML_lower = _textSVG_sub(  w, 0.0*fS, text_lower )
    textXML_upper = _textSVG_sub(  w,    -fS, text_upper )
    return '<g > %s \n %s </g> ' % ( textXML_lower, textXML_upper )
d.registerPreference( 'toleranceText_sizeRatio', 0.8, increment=0.1, label='size ratio')
d.registerPreference( 'comma_decimal_place')

class boundText_widget:
    def __init__(self, name, default):
        self.name = name
        self.default = default
    def valueChanged( self, arg1):
        setattr(d, self.name, arg1)
    def generateWidget( self, dimensioningProcess ):
        self.lineEdit = QtGui.QLineEdit()
        self.lineEdit.setText(self.default)
        setattr(d, self.name, self.default)
        self.lineEdit.textChanged.connect(self.valueChanged)
        return DimensioningTaskDialog_generate_row_hbox(self.name, self.lineEdit)
    def add_properties_to_dimension_object( self, obj ):
        obj.addProperty("App::PropertyString",  self.name+'_text', 'Parameters')
        setattr( obj, self.name+'_text', getattr( d, self.name ).encode('utf8') )
    def get_values_from_dimension_object( self, obj, KWs ):
        KWs['text_'+self.name] =  getattr( obj, self.name+'_text')  #should be unicode

d.dialogWidgets.append( boundText_widget('upper','+0.0') )
d.dialogWidgets.append( boundText_widget('lower','-0.0') )


def toleranceAdd_preview( mouse_x, mouse_y ):
    s = d.selections + [PlacementClick( mouse_x, mouse_y)] if len(d.selections) == 1 else d.selections
    return textSVG( *selections_to_svg_fun_args(s), text_upper=d.upper, text_lower=d.lower, **d.dimensionConstructorKWs )

def toleranceAdd_clickHandler(x, y):
    d.selections.append( PlacementClick( x, y) )
    return 'createDimension:%s' % findUnusedObjectName('tolerance')

def AddToleranceToText( event, referer, elementXML, elementParms, elementViewObject ):
    viewInfo = selectionOverlay.DrawingsViews_info[elementViewObject.Name]
    d.selections = [ TextSelection( elementParms, elementXML, viewInfo ) ]
    selectionOverlay.hideSelectionGraphicsItems()
    previewDimension.initializePreview(d, toleranceAdd_preview, toleranceAdd_clickHandler)

class Proxy_toleranceAdd( Proxy_DimensionObject_prototype ):
     def dimensionProcess( self ):
         return d
d.ProxyClass = Proxy_toleranceAdd
d.proxy_svgFun = textSVG

class AddTolerance:
    def Activated(self):
        V = getDrawingPageGUIVars()
        d.activate( V,  dialogTitle='Add Tolerance', dialogIconPath=':/dd/icons/toleranceAdd.svg', endFunction=self.Activated  )
        selectGraphicsItems = selectionOverlay.generateSelectionGraphicsItems( 
            [obj for obj in V.page.Group if hasattr(obj,'Proxy') and isinstance(obj.Proxy, Proxy_DimensionObject_prototype)], 
            AddToleranceToText , 
            sceneToAddTo = V.graphicsScene, 
            transform = V.transform,
            doTextItems = True, 
            pointWid=2.0,
            maskPen=maskPen, 
            maskHoverPen=maskHoverPen, 
            maskBrush = maskBrush
            )
        
    def GetResources(self): 
        return {
            'Pixmap' : ':/dd/icons/toleranceAdd.svg' , 
            'MenuText': 'Add tolerance super and subscript to dimension', 
            } 
FreeCADGui.addCommand('dd_addTolerance', AddTolerance())


