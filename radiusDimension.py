
from dimensioning import *
from dimensioning import iconPath # not imported with * directive
import selectionOverlay, previewDimension
from dimensionSvgConstructor import radiusDimensionSVG

dimensioning = DimensioningProcessTracker()

def selectFun(  event, referer, elementXML, elementParms, elementViewObject ):
    x,y = elementParms['x'], elementParms['y']
    dimensioning.point1 = x, y
    debugPrint(2, 'center selected at x=%3.1f y=%3.1f' % (x,y))
    dimensioning.radius = elementParms['r']
    dimensioning.dimScale = 1/elementXML.rootNode().scaling() / UnitConversionFactor()
    dimensioning.stage = 1
    selectionOverlay.hideSelectionGraphicsItems()
    previewDimension.initializePreview( dimensioning.drawingVars, clickFunPreview, hoverFunPreview )

def clickFunPreview( x, y ):
    if dimensioning.stage == 1:
        dimensioning.point2 = x,y
        debugPrint(2, 'dimension radial direction point set to x=%3.1f y=%3.1f' % (x,y))
        dimensioning.stage = 2
        return None, None
    elif dimensioning.stage == 2:
        dimensioning.point3 = x, y
        debugPrint(2, 'radius dimension tail defining point set to x=%3.1f y=%3.1f' % (x,y))
        dimensioning.stage = 3
        return None, None
    else:
        XML = radiusDimensionSVG( dimensioning.point1[0], dimensioning.point1[1], dimensioning.radius,
                                  dimensioning.point2[0], dimensioning.point2[1],
                                  dimensioning.point3[0], dimensioning.point3[1],
                                  x, y, dimScale=dimensioning.dimScale,
                                  **dimensioning.dimensionConstructorKWs)
        return findUnusedObjectName('dim'), XML

def hoverFunPreview( x, y):
    if dimensioning.stage == 1:
        return radiusDimensionSVG( dimensioning.point1[0], dimensioning.point1[1], dimensioning.radius, x, y, dimScale=dimensioning.dimScale, **dimensioning.svg_preview_KWs )
    elif dimensioning.stage == 2:
        return radiusDimensionSVG( dimensioning.point1[0], dimensioning.point1[1], dimensioning.radius,
                                     dimensioning.point2[0], dimensioning.point2[1], x, y, dimScale=dimensioning.dimScale, **dimensioning.svg_preview_KWs )
    else:
        return radiusDimensionSVG( dimensioning.point1[0], dimensioning.point1[1], dimensioning.radius,
                                     dimensioning.point2[0], dimensioning.point2[1],
                                     dimensioning.point3[0], dimensioning.point3[1],
                                     x, y,
                                     dimScale=dimensioning.dimScale, **dimensioning.svg_preview_KWs )


maskPen =      QtGui.QPen( QtGui.QColor(0,255,0,100) )
maskPen.setWidth(2.0)
maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) )
maskHoverPen.setWidth(2.0)

class radiusDimension:
    def Activated(self):
        V = getDrawingPageGUIVars()
        dimensioning.activate(V, ['strokeWidth','arrowL1','arrowL2','arrowW','centerPointDia'], ['lineColor'], ['textRenderer'])
        selectionOverlay.generateSelectionGraphicsItems(
            [obj for obj in V.page.Group  if not obj.Name.startswith('dim')],
            selectFun ,
            transform = V.transform,
            sceneToAddTo = V.graphicsScene,
            doCircles=True, doFittedCircles=True,
            maskPen=maskPen,
            maskHoverPen=maskHoverPen,
            maskBrush = QtGui.QBrush() #clear
            )
        selectionOverlay.addProxyRectToRescaleGraphicsSelectionItems( V.graphicsScene, V.graphicsView, V.width, V.height)

    def GetResources(self):
        return {
            'Pixmap' : os.path.join( iconPath , 'radiusDimension.svg' ) ,
            'MenuText': 'Radius Dimension',
            'ToolTip': 'Creates a radius dimension'
            }

FreeCADGui.addCommand('radiusDimension', radiusDimension())
