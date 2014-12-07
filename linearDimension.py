
from dimensioning import *
from dimensioning import __dir__ # not imported with * directive
import selectionOverlay, previewDimension
from dimensionSvgConstructor import linearDimensionSVG

dimensioning = DimensioningProcessTracker()

def selectDimensioningPoint( event, referer, elementXML, elementParms, elementViewObject ):
    x, y = elementParms['x'], elementParms['y']
    referer.lockSelection()
    if dimensioning.stage == 0: #then selectPoint1
        dimensioning.point1 =  x,y
        debugPrint(2, 'point1 set to x=%3.1f y=%3.1f' % (x,y))
        dimensioning.stage = 1
    else:
        dimensioning.point2 =  x,y
        debugPrint(2, 'point2 set to x=%3.1f y=%3.1f' % (x,y))
        dimensioning.stage = 2 
        dimensioning.dimScale = 1/elementXML.rootNode().scaling()
        selectionOverlay.hideSelectionGraphicsItems()
        previewDimension.initializePreview( dimensioning.drawingVars, clickFunPreview, hoverFunPreview )

def clickFunPreview( x, y ):
    if dimensioning.stage == 2 :
        dimensioning.point3 = x, y
        debugPrint(2, 'point3 set to x=%3.1f y=%3.1f' % (x,y))
        dimensioning.stage = 3
        return None, None
    else:
        p1,p2,p3 = dimensioning.point1,  dimensioning.point2,  dimensioning.point3
        XML = linearDimensionSVG( p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], 
                                  x, y, scale=dimensioning.dimScale)
        return findUnusedObjectName('dim'), XML

def hoverFunPreview( x, y ):
    p1, p2 = dimensioning.point1, dimensioning.point2 
    if dimensioning.stage == 2 :
        return linearDimensionSVG( p1[0], p1[1], p2[0], p2[1], x, y, **dimensioning.svg_preview_KWs )
    else:
        return  linearDimensionSVG( p1[0], p1[1], p2[0], p2[1],
                                    dimensioning.point3[0], dimensioning.point3[1], 
                                    x, y, scale=dimensioning.dimScale,  **dimensioning.svg_preview_KWs )

maskBrush  =   QtGui.QBrush( QtGui.QColor(0,160,0,100) )
maskPen =      QtGui.QPen( QtGui.QColor(0,160,0,100) )
maskPen.setWidth(0.0)
maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) )
maskHoverPen.setWidth(0.0)

class linearDimension:
    "this class will create a line after the user clicked 2 points on the screen"
    def Activated(self):
        V = getDrawingPageGUIVars()
        dimensioning.activate(V)
        selectionOverlay.generateSelectionGraphicsItems( 
            [obj for obj in V.page.Group  if not obj.Name.startswith('dim')], 
            selectDimensioningPoint ,
            transform = V.transform,
            sceneToAddTo = V.graphicsScene, 
            doPoints=True, 
            pointWid=1.0,
            maskPen=maskPen, 
            maskHoverPen=maskHoverPen, 
            maskBrush = maskBrush
            )
        selectionOverlay.addProxyRectToRescaleGraphicsSelectionItems( V.graphicsScene, V.graphicsView, V.width, V.height)
        
    def GetResources(self): 
        return {
            'Pixmap' : os.path.join( __dir__ , 'linearDimension.svg' ) , 
            'MenuText': 'Linear Dimension', 
            'ToolTip': 'Creates a linear dimension'
            } 

FreeCADGui.addCommand('linearDimension', linearDimension())
