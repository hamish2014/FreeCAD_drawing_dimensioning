
from dimensioning import *
from dimensioning import iconPath # not imported with * directive
import selectionOverlay, previewDimension
from dimensionSvgConstructor import linearDimensionSVG, halfLinearDimensionSVG, rotate2D, distanceBetweenParallelsSVG

dimensioning = DimensioningProcessTracker()

def selectDimensioningPoint( event, referer, elementXML, elementParms, elementViewObject ):
    if isinstance(referer,selectionOverlay.PointSelectionGraphicsItem):
        x, y = elementParms['x'], elementParms['y']
        referer.lockSelection()
        if dimensioning.stage == 0: #then selectPoint1
            dimensioning.point1 =  x,y
            debugPrint(2, 'point1 set to x=%3.1f y=%3.1f' % (x,y))
            dimensioning.stage = 1
            selectionOverlay.hideSelectionGraphicsItems(
                lambda gi: isinstance(gi,  selectionOverlay.LineSelectionGraphicsItem)
                )
        else:
            dimensioning.point2 =  x,y
            debugPrint(2, 'point2 set to x=%3.1f y=%3.1f' % (x,y))
            dimensioning.stage = 2 
            dimensioning.dimScale = 1 / elementXML.rootNode().scaling() / UnitConversionFactor()
            selectionOverlay.hideSelectionGraphicsItems()
            previewDimension.initializePreview( dimensioning.drawingVars, clickFunPreview, hoverFunPreview )
    else:#then line
        if dimensioning.stage == 0: 
            x1,y1,x2,y2 = [ elementParms[k] for k in [ 'x1', 'y1', 'x2', 'y2' ] ]
            debugPrint(2,'selecting line x1=%3.1f y1=%3.1f, x2=%3.1f y2=%3.1f' % (x1,y1,x2,y2))
            dimensioning.point1 =  x1,y1
            dimensioning.point2 =  x2,y2
            dimensioning.stage = 2 
            dimensioning.dimScale = 1 / elementXML.rootNode().scaling() / UnitConversionFactor()
            lineSelected_hideSelectionGraphicsItems(elementParms, elementViewObject)
            previewDimension.initializePreview( dimensioning.drawingVars, clickFunPreview, hoverFunPreview )
        else: #then distance between parallels
            x1,y1,x2,y2 = [ elementParms[k] for k in [ 'x1', 'y1', 'x2', 'y2' ] ]
            debugPrint(2,'distance between parallels, line2 x1=%3.1f y1=%3.1f, x2=%3.1f y2=%3.1f' % (x1,y1,x2,y2))
            dimensioning.line1 =  list(dimensioning.point1) + list(dimensioning.point2)
            dimensioning.line2 =  [ x1,y1,x2,y2 ]
            debugPrint(3,'dim scale %f' % dimensioning.dimScale)
            selectionOverlay.hideSelectionGraphicsItems()
            previewDimension.removePreviewGraphicItems( False )
            previewDimension.initializePreview( dimensioning.drawingVars, distanceParallels_clickFunPreview, distanceParallels_hoverFunPreview )


def clickFunPreview( x, y ):
    if dimensioning.stage == 2 :
        dimensioning.point3 = x, y
        debugPrint(2, 'point3 set to x=%3.1f y=%3.1f' % (x,y))
        dimensioning.stage = 3
        selectionOverlay.hideSelectionGraphicsItems() # for distance between parallels case
        return None, None
    else:
        p1,p2,p3 = dimensioning.point1,  dimensioning.point2,  dimensioning.point3
        XML = halfLinearDimensionSVG( p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], 
                                  x, y, scale=dimensioning.dimScale, 
                                  **dimensioning.dimensionConstructorKWs)
        return findUnusedObjectName('dim'), XML

def hoverFunPreview( x, y ):
    p1, p2 = dimensioning.point1, dimensioning.point2 
    if dimensioning.stage == 2 :
        return halfLinearDimensionSVG( p1[0], p1[1], p2[0], p2[1], x, y, **dimensioning.svg_preview_KWs )
    else:
        return halfLinearDimensionSVG( p1[0], p1[1], p2[0], p2[1],
                                    dimensioning.point3[0], dimensioning.point3[1], 
                                    x, y, scale=dimensioning.dimScale,  **dimensioning.svg_preview_KWs )

maskBrush  =   QtGui.QBrush( QtGui.QColor(0,160,0,100) )
maskPen =      QtGui.QPen( QtGui.QColor(0,160,0,100) )
maskPen.setWidth(0.0)
maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) )
maskHoverPen.setWidth(0.0)
line_maskPen =      QtGui.QPen( QtGui.QColor(0,255,0,100) )
line_maskPen.setWidth(2.0)
line_maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) )
line_maskHoverPen.setWidth(2.0)
line_maskBrush = QtGui.QBrush() #clear

class halfLinearDimension:
    "this class will create a line after the user clicked 2 points on the screen"
    def Activated(self):
        V = getDrawingPageGUIVars()
        dimensioning.activate( V, ['strokeWidth','arrowL1','arrowL2','arrowW','gap_datum_points', 'dimension_line_overshoot'], ['lineColor'], ['textRenderer'] )
        commonArgs = dict( 
            onClickFun=selectDimensioningPoint,
            transform = V.transform,
            sceneToAddTo = V.graphicsScene, 
            pointWid=1.0,
            maskPen=maskPen, 
            maskHoverPen=maskHoverPen, 
            maskBrush = maskBrush
            )
        selectionOverlay.generateSelectionGraphicsItems( 
            [obj for obj in V.page.Group  if not obj.Name.startswith('dim') and not obj.Name.startswith('center')],
            doPoints=True, 
            **commonArgs
            )
        selectionOverlay.generateSelectionGraphicsItems( 
            [obj for obj in V.page.Group if obj.Name.startswith('center')], 
            clearPreviousSelectionItems = False,
            doPathEndPoints=True, 
            **commonArgs
            )
        selectionOverlay.generateSelectionGraphicsItems( 
            [obj for obj in V.page.Group  if not obj.Name.startswith('dim') and not obj.Name.startswith('center')],
            clearPreviousSelectionItems = False,
            doLines=True, 
            onClickFun=selectDimensioningPoint,
            transform = V.transform,
            sceneToAddTo = V.graphicsScene, 
            maskPen= line_maskPen, 
            maskHoverPen= line_maskHoverPen, 
            maskBrush = line_maskBrush
            )
        selectionOverlay.addProxyRectToRescaleGraphicsSelectionItems( V.graphicsScene, V.graphicsView, V.width, V.height)
        
    def GetResources(self): 
        return {
            'Pixmap' : os.path.join( iconPath , 'halfLinearDimension.svg' ) , 
            'MenuText': 'Half Linear Dimension', 
            'ToolTip': 'Creates a half linear dimension'
            } 

FreeCADGui.addCommand('halfLinearDimension', halfLinearDimension())


#distance between parallels code
def lineSelected_hideSelectionGraphicsItems(elementParms, elementViewObject):
    x1,y1,x2,y2 = [ elementParms[k] for k in [ 'x1', 'y1', 'x2', 'y2' ] ]
    d = numpy.array([ x2 - x1, y2 - y1] )
    d_ref = d / numpy.linalg.norm(d)
    p = numpy.array([ x1, y1] )
    def hideFun( gi ):
        if isinstance(gi,selectionOverlay.LineSelectionGraphicsItem):
            if gi.elementParms <> elementParms:
                x1,y1,x2,y2 = [ gi.elementParms[k] for k in [ 'x1', 'y1', 'x2', 'y2' ] ]
                d = numpy.array([ x2 - x1, y2 - y1] )
                d = d / numpy.linalg.norm(d)
                if abs(numpy.dot(d_ref,d)) > 1.0 - 10**-9: #then parallel
                    d_rotated = rotate2D(d, numpy.pi/2)
                    offset =  numpy.array([ x1, y1] ) - p
                    if abs(numpy.dot(d_rotated, offset)) > 10**-6: #then not colinear
                        return False
        return True
    selectionOverlay.hideSelectionGraphicsItems(hideFun)


def distanceParallels_clickFunPreview( x, y ):
    if dimensioning.stage == 2 :
        dimensioning.point3 = x, y
        debugPrint(2, 'base-line point set to x=%3.1f y=%3.1f' % (x,y))
        dimensioning.stage = 3
        return None, None
    else:
        XML = distanceBetweenParallelsSVG( 
            dimensioning.line1, dimensioning.line2,
            dimensioning.point3[0], dimensioning.point3[1], 
            x, y, scale=dimensioning.dimScale,  
            **dimensioning.dimensionConstructorKWs)
        return findUnusedObjectName('dim'), XML

def distanceParallels_hoverFunPreview( x, y ):
    if dimensioning.stage == 2 :
        return distanceBetweenParallelsSVG( 
            dimensioning.line1, dimensioning.line2, x, y, 
            scale=dimensioning.dimScale,  
            **dimensioning.svg_preview_KWs )
    else:
        return distanceBetweenParallelsSVG( 
            dimensioning.line1, dimensioning.line2,
            dimensioning.point3[0], dimensioning.point3[1], 
            x, y, scale=dimensioning.dimScale,  
            **dimensioning.svg_preview_KWs )
