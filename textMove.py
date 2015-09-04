
from dimensioning import *
import selectionOverlay, previewDimension
import XMLlib

d = DimensioningProcessTracker()

def moveTextSvg( x, y):
    e = d.elementXML
    xml = e.XML[e.pStart:e.pEnd]
    xml = XMLlib.replaceParm(xml, 'x', '%f' % x )
    xml = XMLlib.replaceParm(xml, 'y', '%f' % y )
    if e.parms.has_key('transform'):
        xml = XMLlib.replaceParm(xml, 'transform', "rotate(%s %f,%f)" % (d.textRotation,x,y) )
    return e.XML[:e.pStart] + xml + e.XML[e.pEnd:]

def placeText( x, y):
    FreeCAD.ActiveDocument.openTransaction("move text")
    d.dimToEdit.ViewResult = moveTextSvg(x, y )
    FreeCAD.ActiveDocument.commitTransaction()
    return 'stopPreview'

def MoveDimensionText( event, referer, elementXML, elementParms, elementViewObject ):
    d.dimToEdit = elementViewObject    
    d.elementXML = elementXML
    debugPrint(2, 'moving %s' % elementViewObject.Name)
    if elementXML.parms.has_key('transform'):
        transform = elementXML.parms['transform']
        t = transform[ XMLlib.findOffset(transform,'rotate(',0): ]
        d.textRotation =  XMLlib.splitMultiSep(t, ', ')[0]
        debugPrint(3, 'd.textRotation %s' % d.textRotation)
    else:
        d.textRotation = None
    selectionOverlay.hideSelectionGraphicsItems()
    previewDimension.initializePreview( d, moveTextSvg, placeText )

maskBrush  =   QtGui.QBrush( QtGui.QColor(0,160,0,100) )
maskPen =      QtGui.QPen( QtGui.QColor(0,160,0,100) )
maskPen.setWidth(0.0)
maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) )
maskHoverPen.setWidth(0.0)

class MoveText:
    def Activated(self):
        V = getDrawingPageGUIVars() #needs to be done before dialog show, else Qt active is dialog and not freecads
        d.activate( V,  dialogTitle='Move Text', dialogIconPath=':/dd/icons/textMove.svg', endFunction=self.Activated  )
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
            'Pixmap' : ':/dd/icons/textMove.svg' , 
            'MenuText': msg, 
            'ToolTip': msg
            } 
FreeCADGui.addCommand('dd_moveText', MoveText())


