
from dimensioning import *
from dimensioning import __dir__ # not imported with * directive
import selectionOverlay, previewDimension
from dimensionSvgConstructor import angularDimensionSVG

dimensioning = DimensioningProcessTracker()
        
def selectFun( event, referer, elementXML, elementParms, elementViewObject ):
    x1,y1,x2,y2 = [ elementParms[k] for k in [ 'x1', 'y1', 'x2', 'y2' ] ]
    debugPrint(2, 'selecting line %i with x1=%3.1f y1=%3.1f, x2=%3.1f y2=%3.1f' % (dimensioning.stage, x1,y1,x2,y2) )
    referer.lockSelection()
    if dimensioning.stage == 0: #then select line1
        dimensioning.line1 = x1,y1,x2,y2
        dimensioning.stage = 1
    else: 
        dimensioning.line2 = x1,y1,x2,y2
        dimensioning.stage = 2
        selectionOverlay.hideSelectionGraphicsItems()
        previewDimension.initializePreview( dimensioning.drawingVars, clickFunPreview, hoverFunPreview )

def clickFunPreview( x, y ):
    if dimensioning.stage == 2 :
        dimensioning.point3 = x, y
        debugPrint(2, 'base-line point set to x=%3.1f y=%3.1f' % (x,y))
        dimensioning.stage = 3
        return None, None
    else:
        XML = angularDimensionSVG( dimensioning.line1, dimensioning.line2,
                                   dimensioning.point3[0], dimensioning.point3[1], 
                                   x, y, **dimensioning.dimensionConstructorKWs)
        return findUnusedObjectName('dim'), XML

def hoverFunPreview( x, y ):
    if dimensioning.stage == 2 :
        return angularDimensionSVG( dimensioning.line1, dimensioning.line2, x, y, **dimensioning.svg_preview_KWs)
    else:
        return angularDimensionSVG( dimensioning.line1, dimensioning.line2,
                                    dimensioning.point3[0], dimensioning.point3[1], 
                                    x, y, **dimensioning.svg_preview_KWs )

#selection variables for angular dimensioning
maskPen =      QtGui.QPen( QtGui.QColor(0,255,0,100) )
maskPen.setWidth(2.0)
maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) )
maskHoverPen.setWidth(2.0)

class angularDimension:
    def Activated(self):
        V = getDrawingPageGUIVars()
        dimensioning.activate(V, [['gap_datum_points', 2.0 ], ['dimension_line_overshoot',1.0]] )
        selectionOverlay.generateSelectionGraphicsItems( 
            [obj for obj in V.page.Group  if not obj.Name.startswith('dim')], 
            selectFun ,
            transform = V.transform,
            sceneToAddTo = V.graphicsScene, 
            doLines=True,
            maskPen=maskPen, 
            maskHoverPen=maskHoverPen, 
            maskBrush = QtGui.QBrush() #clear
            )
        selectionOverlay.addProxyRectToRescaleGraphicsSelectionItems( V.graphicsScene, V.graphicsView, V.width, V.height)
        
    def GetResources(self): 
        return {
            'Pixmap' : os.path.join( __dir__ , 'angularDimension.svg' ) , 
            'MenuText': 'Angular Dimension', 
            'ToolTip': 'Creates a angular dimension'
            } 

FreeCADGui.addCommand('angularDimension', angularDimension())
