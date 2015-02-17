'''
Dialog notes
Use Qt Designer to edit the toleranceDialog.ui
Once completed $ pyside-uic toleranceDialog.ui > toleranceDialog.py
'''

from dimensioning import *
from dimensioning import iconPath # not imported with * directive
import previewDimension, selectionOverlay 
import toleranceDialog
from textEdit import maskBrush, maskPen, maskHoverPen
from dimensionSvgConstructor import rotate2D

dimensioning = DimensioningProcessTracker()
dimensioning.assignedPrefenceValues = False

def AddToleranceToText( event, referer, elementXML, elementParms, elementViewObject ):
    try :
        dimensioning.dimToEdit = elementViewObject  
        dimensioning.elementXML = elementXML
        selectionOverlay.hideSelectionGraphicsItems()
        svgText = SvgTextParser( elementXML.XML[elementXML.pStart:elementXML.pEnd] )
        dimensioning.svgText = svgText
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
            dimensioning.upper = widgets['upperLineEdit'].text()
            dimensioning.lower = widgets['lowerLineEdit'].text()
            svgText =  dimensioning.svgText
            fontSize =  widgets['scaleDoubleSpinBox'].value() * svgText.height()
            dimensioning.textRenderer = SvgTextRenderer(
                font_family = svgText.font_family,
                fill = svgText.fill,
                font_size = fontSize
                )
            previewDimension.initializePreview(
                dimensioning.drawingVars,
                clickEvent, 
                hoverEvent )
        except:
            errorMessagebox_with_traceback()

def _textSVG_sub(x_offset, y_offset, text):
    svgText = dimensioning.svgText
    offset = rotate2D([x_offset, y_offset], svgText.rotation*numpy.pi/180)
    x = svgText.x + offset[0]
    y = svgText.y + offset[1]
    return dimensioning.textRenderer(x, y, text, text_anchor='end', rotation=svgText.rotation )

def textSVG( x, y, svgTag='g', svgParms=''):
    fontSize = dimensioning.textRenderer.font_size
    svgText = dimensioning.svgText
    w = rotate2D([x - svgText.x, y - svgText.y], -svgText.rotation*numpy.pi/180)[0]
    textXML_lower = _textSVG_sub(  w, 0.0*fontSize, dimensioning.lower )
    textXML_upper = _textSVG_sub(  w,    -fontSize, dimensioning.upper )
    XML = '''<%s  %s >
  %s
  %s
</%s> ''' % ( svgTag, svgParms,
              textXML_lower,
              textXML_upper, 
              svgTag )
    return XML

def clickEvent( x, y):
    viewName = findUnusedObjectName('dimText')
    XML = textSVG(x,y)
    return viewName, XML

def hoverEvent( x, y):
    return textSVG( x, y, svgTag=dimensioning.svg_preview_KWs['svgTag'], svgParms=dimensioning.svg_preview_KWs['svgParms'] )



dialog = ToleranceDialogWidget()
dialogUi = toleranceDialog.Ui_Dialog()
dialogUi.setupUi(dialog)

class AddTolerance:
    def Activated(self):
        V = getDrawingPageGUIVars() #needs to be done before dialog show, else active window is dialog and not freecad
        dimensioning.activate( V )
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
            'MenuText': 'Add tolerance super and subscript to text', 
            } 
FreeCADGui.addCommand('toleranceAdd', AddTolerance())


