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

def _textSVG_sub(x_offset, y_offset, text, comma_decimal_place ):
    svgText = d.svgText
    offset = rotate2D([x_offset, y_offset], svgText.rotation*numpy.pi/180)
    x = svgText.x + offset[0]
    y = svgText.y + offset[1]
    return d.textRenderer(x, y, text if not comma_decimal_place else text.replace('.',','),
                          text_anchor='end', rotation=svgText.rotation )

def textSVG( x, y, toleranceText_sizeRatio=0.8, comma_decimal_place=False ):
    fontSize = float(d.svgText.font_size)*toleranceText_sizeRatio
    d.textRenderer.font_size = fontSize
    svgText = d.svgText
    w = rotate2D([x - svgText.x, y - svgText.y], -svgText.rotation*numpy.pi/180)[0]
    textXML_lower = _textSVG_sub(  w, 0.0*fontSize, d.lower, comma_decimal_place )
    textXML_upper = _textSVG_sub(  w,    -fontSize, d.upper, comma_decimal_place )
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
d.dialogWidgets.append( boundText_widget('upper','+0.0') )
d.dialogWidgets.append( boundText_widget('lower','-0.0') )


def toleranceAdd_preview( mouseX, mouseY ):
    return textSVG( mouseX, mouseY, **d.dimensionConstructorKWs )

def toleranceAdd_clickHandler(x, y):
    return 'createDimension:%s' % findUnusedObjectName('dimText')

def AddToleranceToText( event, referer, elementXML, elementParms, elementViewObject ):
    try :
        d.dimToEdit = elementViewObject  
        d.elementXML = elementXML
        selectionOverlay.hideSelectionGraphicsItems()
        svgText = SvgTextParser( elementXML.XML[elementXML.pStart:elementXML.pEnd] )
        d.svgText = svgText
        debugPrint(3,'svgText.width() %s' % svgText.width())
        debugPrint(3,'adding tolerance %s' % repr(elementViewObject.Name))
        d.textRenderer = SvgTextRenderer(
            font_family = svgText.font_family,
            fill = svgText.fill,
            font_size = svgText.font_size
            )
        previewDimension.initializePreview(d, toleranceAdd_preview, toleranceAdd_clickHandler)
    except:
        errorMessagebox_with_traceback()


class AddTolerance:
    def Activated(self):
        V = getDrawingPageGUIVars()
        d.activate( V,  dialogTitle='Add Tolerance', dialogIconPath=os.path.join( iconPath , 'toleranceAdd.svg' ), endFunction=self.Activated  )
        selectGraphicsItems = selectionOverlay.generateSelectionGraphicsItems( 
            [obj for obj in V.page.Group  if obj.Name.startswith('dim')], 
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
            'Pixmap' : os.path.join( iconPath , 'toleranceAdd.svg' ) , 
            'MenuText': 'Add tolerance super and subscript to dimension', 
            } 
FreeCADGui.addCommand('dd_addTolerance', AddTolerance())


