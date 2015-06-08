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
from dimensionSvgConstructor import rotate2D

d = DimensioningProcessTracker()
d.assignedPrefenceValues = False

def AddToleranceToText( event, referer, elementXML, elementParms, elementViewObject ):
    try :
        d.dimToEdit = elementViewObject  
        d.elementXML = elementXML
        selectionOverlay.hideSelectionGraphicsItems()
        svgText = SvgTextParser( elementXML.XML[elementXML.pStart:elementXML.pEnd] )
        d.svgText = svgText
        debugPrint(3,'svgText.width() %s' % svgText.width())
        debugPrint(3,'adding tolerance %s' % repr(elementViewObject.Name))
        dialog.show()
    except:
        errorMessagebox_with_traceback()

class ToleranceDialogWidget( QtGui.QWidget ):
    def accept( self ):
        try :
            widgets = dict( [c.objectName(), c] for c in self.children() )
            self.hide()
            d.upper = widgets['upperLineEdit'].text()
            d.lower = widgets['lowerLineEdit'].text()
            svgText =  d.svgText
            fontSize =  widgets['scaleDoubleSpinBox'].value() * svgText.height()
            d.textRenderer = SvgTextRenderer(
                font_family = svgText.font_family,
                fill = svgText.fill,
                font_size = fontSize
                )
            previewDimension.initializePreview(
                d.drawingVars,
                textSVG, 
                clickHandler )
        except:
            errorMessagebox_with_traceback()

def _textSVG_sub(x_offset, y_offset, text):
    svgText = d.svgText
    offset = rotate2D([x_offset, y_offset], svgText.rotation*numpy.pi/180)
    x = svgText.x + offset[0]
    y = svgText.y + offset[1]
    return d.textRenderer(x, y, text, text_anchor='end', rotation=svgText.rotation )

def textSVG( x, y ):
    fontSize = d.textRenderer.font_size
    svgText = d.svgText
    w = rotate2D([x - svgText.x, y - svgText.y], -svgText.rotation*numpy.pi/180)[0]
    textXML_lower = _textSVG_sub(  w, 0.0*fontSize, d.lower )
    textXML_upper = _textSVG_sub(  w,    -fontSize, d.upper )
    return '<g > %s \n %s </g> ' % ( textXML_lower, textXML_upper )

def clickHandler(x, y):
    return 'createDimension:%s' % findUnusedObjectName('dimText')


dialog = ToleranceDialogWidget()
dialogUi = toleranceDialog.Ui_Dialog()
dialogUi.setupUi(dialog)

class AddTolerance:
    def Activated(self):
        V = getDrawingPageGUIVars()
        d.activate( V )
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


