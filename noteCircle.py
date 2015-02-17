
from dimensioning import *
from dimensioning import iconPath # not imported with * directive
import selectionOverlay, previewDimension
from dimensionSvgConstructor import noteCircleSVG

dimensioning = DimensioningProcessTracker()

def selectFun( event, referer, elementXML, elementParms, elementViewObject ):
    x,y = elementParms['x'], elementParms['y']
    dimensioning.point1 = x, y
    debugPrint(2, 'note start point selected at x=%3.1f y=%3.1f' % (x,y))
    dimensioning.dimScale = 1/elementXML.rootNode().scaling() / UnitConversionFactor()
    dimensioning.stage = 1
    selectionOverlay.hideSelectionGraphicsItems()
    previewDimension.initializePreview( dimensioning.drawingVars, clickFunPreview, hoverFunPreview )

def clickFunPreview( x, y ):
    """
    this method is called in response to a mouse click during a
    dimensioning operation
    """
    if dimensioning.stage == 1:
        dimensioning.point2 = x,y
        debugPrint(2, 'dimension radial direction point set to x=%3.1f y=%3.1f' % (x,y))
        dimensioning.stage = 2
        return None, None
    else:
        XML = noteCircleSVG( dimensioning.point1[0], dimensioning.point1[1],
                             dimensioning.point2[0], dimensioning.point2[1],
                             x, y,
                             dimScale=dimensioning.dimScale, **dimensioning.dimensionConstructorKWs)
        return findUnusedObjectName('dim'), XML

def hoverFunPreview( x, y ):
    """
    this method is called in when updating the screen while hovering during a
    dimensioning operation
    """
    if dimensioning.stage == 1:
        return noteCircleSVG( dimensioning.point1[0], dimensioning.point1[1],
                              x, y,
                              dimScale=dimensioning.dimScale, **dimensioning.svg_preview_KWs )
    else:
        return noteCircleSVG( dimensioning.point1[0], dimensioning.point1[1],
                              dimensioning.point2[0], dimensioning.point2[1],
                              x, y,
                              dimScale=dimensioning.dimScale,**dimensioning.svg_preview_KWs )


maskBrush  =   QtGui.QBrush( QtGui.QColor(0,160,0,100) )
maskPen =      QtGui.QPen( QtGui.QColor(0,160,0,100) )
maskPen.setWidth(0.0)
maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) )
maskHoverPen.setWidth(0.0)

class noteCircle:
    def Activated(self):
        V = getDrawingPageGUIVars()
        dimensioning.activate(V, ['strokeWidth','centerPointDia'], ['lineColor'], ['textRenderer'])
        #dimensioning.SVGFun = noteCircleSVG
        selectionOverlay.generateSelectionGraphicsItems(
            [obj for obj in V.page.Group  if not obj.Name.startswith('dim') and not obj.Name.startswith('center')],
            selectFun,
            transform = V.transform,
            sceneToAddTo = V.graphicsScene,
            doPoints=True, doMidPoints=True,
            pointWid=1.0,
            maskPen=maskPen,
            maskHoverPen=maskHoverPen,
            maskBrush = maskBrush
            )
        selectionOverlay.addProxyRectToRescaleGraphicsSelectionItems( V.graphicsScene, V.graphicsView, V.width, V.height)

    def GetResources(self):
        return {
            'Pixmap' : os.path.join( iconPath , 'noteCircle.svg' ) ,
            'MenuText': 'Notation',
            'ToolTip': 'Creates a notation indicator'
            }

FreeCADGui.addCommand('noteCircle', noteCircle())
