
from dimensioning import *
from dimensioning import iconPath # not imported with * directive
import selectionOverlay, previewDimension
import XMLlib

dimensioning = DimensioningProcessTracker()

def moveTextSvg( x, y, svgTag='g', svgParms=''):
    e = dimensioning.elementXML
    xml = e.XML[e.pStart:e.pEnd]
    xml = XMLlib.replaceParm(xml, 'x', '%f' % x )
    xml = XMLlib.replaceParm(xml, 'y', '%f' % y )
    if e.parms.has_key('transform'):
        xml = XMLlib.replaceParm(xml, 'transform', "rotate(%s %f,%f)" % (dimensioning.textRotation,x,y) )
    if svgTag == 'g': #then for viewResult
        newXML = e.XML[:e.pStart] + xml + e.XML[e.pEnd:]
    else:
        newXML = u'''<%s %s > %s </%s> ''' % ( svgTag, svgParms, xml, svgTag )
    return newXML

def previewTextSvg( x, y):
    return moveTextSvg( x, y, **dimensioning.svg_preview_KWs )

def placeText( x, y):
    dimensioning.dimToEdit.ViewResult = moveTextSvg(x, y )
    return None, dimensioning.dimToEdit.ViewResult

def MoveDimensionText( event, referer, elementXML, elementParms, elementViewObject ):
    dimensioning.dimToEdit = elementViewObject    
    dimensioning.elementXML = elementXML
    debugPrint(2, 'moving %s' % elementViewObject.Name)
    if elementXML.parms.has_key('transform'):
        transform = elementXML.parms['transform']
        t = transform[ XMLlib.findOffset(transform,'rotate(',0): ]
        dimensioning.textRotation =  XMLlib.splitMultiSep(t, ', ')[0]
        debugPrint(3, 'dimensioning.textRotation %s' % dimensioning.textRotation)
    else:
        dimensioning.textRotation = None
    selectionOverlay.hideSelectionGraphicsItems()
    previewDimension.initializePreview(
            dimensioning.drawingVars,
            placeText, 
            previewTextSvg )

maskBrush  =   QtGui.QBrush( QtGui.QColor(0,160,0,100) )
maskPen =      QtGui.QPen( QtGui.QColor(0,160,0,100) )
maskPen.setWidth(0.0)
maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) )
maskHoverPen.setWidth(0.0)

class MoveText:
    def Activated(self):
        V = getDrawingPageGUIVars() #needs to be done before dialog show, else Qt active is dialog and not freecads
        dimensioning.activate( V )
        selectGraphicsItems = selectionOverlay.generateSelectionGraphicsItems( 
            [obj for obj in V.page.Group  if obj.Name.startswith('dim')], 
            MoveDimensionText , 
            sceneToAddTo = V.graphicsScene, 
            transform = V.transform,
            doTextItems = True, 
            pointWid=2.0,
            maskPen=maskPen, 
            maskHoverPen=maskHoverPen, 
            maskBrush = maskBrush
            )
        
    def GetResources(self): 
        msg = "Move a dimension's text"
        return {
            'Pixmap' : os.path.join( iconPath , 'textMove.svg' ) , 
            'MenuText': msg, 
            'ToolTip': msg
            } 
FreeCADGui.addCommand('textMoveDimensioning', MoveText())


