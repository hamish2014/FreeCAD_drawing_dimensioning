
from dimensioning import *
from dimensioning import iconPath # not imported with * directive
import selectionOverlay, previewDimension
from dimensionSvgConstructor import angularDimensionSVG

dimensioning = DimensioningProcessTracker()
        
def selectFun( event, referer, elementXML, elementParms, elementViewObject ):
    referer.lockSelection()
    if isinstance(referer, selectionOverlay.LineSelectionGraphicsItem):
        x1,y1,x2,y2 = [ elementParms[k] for k in [ 'x1', 'y1', 'x2', 'y2' ] ]
        debugPrint(2, 'selecting line %i with x1=%3.1f y1=%3.1f, x2=%3.1f y2=%3.1f' % (dimensioning.stage, x1,y1,x2,y2) )
        if dimensioning.stage == 0: #then select line1
            dimensioning.line1 = x1,y1,x2,y2
            dimensioning.stage = 1
            for gi in selectionOverlay.graphicItems:
                if isinstance(gi,  selectionOverlay.PointSelectionGraphicsItem):
                    gi.hide()
        else: 
            dimensioning.line2 = x1,y1,x2,y2
            dimensioning.stage = 2
            selectionOverlay.hideSelectionGraphicsItems()
            previewDimension.initializePreview( dimensioning.drawingVars, clickFunPreview, hoverFunPreview )
    else: #user selecting 3 points
        x, y = elementParms['x'], elementParms['y']
        debugPrint(2, 'point %i selected at x=%3.1f y=%3.1f' %(dimensioning.stage +1,x,y))
        if dimensioning.stage == 0: 
            dimensioning.pointStart = x,y
            dimensioning.stage = 1
            for gi in selectionOverlay.graphicItems:
                if isinstance(gi,  selectionOverlay.LineSelectionGraphicsItem):
                    gi.hide()
        elif dimensioning.stage == 1:
            dimensioning.pointCenter = x,y
            dimensioning.stage = 2
        else: 
            x_c, y_c = dimensioning.pointCenter
            x1, y1 = dimensioning.pointStart
            x2, y2 = x,y
            dimensioning.line1 = x_c, y_c, x1, y1
            dimensioning.line2 = x_c, y_c, x2, y2
            dimensioning.stage = 2 #hack to allow intergation with dim from 2 line code
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
line_maskPen =      QtGui.QPen( QtGui.QColor(0,255,0,100) )
line_maskPen.setWidth(2.0)
line_maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) )
line_maskHoverPen.setWidth(2.0)
line_maskBrush = QtGui.QBrush() #clear
point_maskBrush  =   QtGui.QBrush( QtGui.QColor(0,160,0,100) )
point_maskPen =      QtGui.QPen( QtGui.QColor(0,160,0,100) )
point_maskPen.setWidth(0.0)
point_maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) )
point_maskHoverPen.setWidth(0.0)

class angularDimension:
    def Activated(self):
        V = getDrawingPageGUIVars()
        dimensioning.activate(V, ['strokeWidth','fontSize','arrowL1','arrowL2','arrowW','gap_datum_points', 'dimension_line_overshoot'], ['lineColor','fontColor'] )
        selectionOverlay.generateSelectionGraphicsItems( 
            [obj for obj in V.page.Group  if not obj.Name.startswith('dim')], 
            selectFun ,
            transform = V.transform,
            sceneToAddTo = V.graphicsScene, 
            doLines=True,
            maskPen= line_maskPen, 
            maskHoverPen= line_maskHoverPen, 
            maskBrush = line_maskBrush
            )
        selectionOverlay.generateSelectionGraphicsItems( 
            [obj for obj in V.page.Group  if not obj.Name.startswith('dim')], 
            selectFun ,
            transform = V.transform,
            sceneToAddTo = V.graphicsScene, 
            doPoints=True, 
            maskPen= point_maskPen, 
            maskHoverPen= point_maskHoverPen, 
            maskBrush = point_maskBrush, #clear
            clearPreviousSelectionItems = False,
            )
        selectionOverlay.addProxyRectToRescaleGraphicsSelectionItems( V.graphicsScene, V.graphicsView, V.width, V.height)
        
    def GetResources(self): 
        return {
            'Pixmap' : os.path.join( iconPath , 'angularDimension.svg' ) , 
            'MenuText': 'Angular Dimension', 
            'ToolTip': 'Creates a angular dimension'
            } 

FreeCADGui.addCommand('angularDimension', angularDimension())
