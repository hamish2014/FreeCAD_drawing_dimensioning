
from dimensioning import *
from dimensioning import iconPath # not imported with * directive
import selectionOverlay, previewDimension
from dimensionSvgConstructor import centerLinesSVG, centerLineSVG

dimensioning = DimensioningProcessTracker()

def selectFun(  event, referer, elementXML, elementParms, elementViewObject ):
    x,y = elementParms['x'], elementParms['y']
    dimensioning.center = [x, y]
    dimensioning.stage = 1
    dimensioning.dimScale = elementXML.rootNode().scaling()
    debugPrint(3, 'center selected at x=%3.1f y=%3.1f scale %3.1f' % (x,y, dimensioning.dimScale))
    selectionOverlay.hideSelectionGraphicsItems()
    previewDimension.initializePreview( dimensioning.drawingVars, clickFunPreview, hoverFunPreview )

def clickFunPreview( x, y ):
    if dimensioning.stage == 1:
        dimensioning.topLeft = x,y
        debugPrint(3, 'center Lines topLeft set to x=%3.1f y=%3.1f' % (x,y))
        dimensioning.stage = 2
        return None, None
    elif dimensioning.stage == 2:
        dimensioning.bottomRight = x, y
        debugPrint(3, 'center Lines bottomRight set to x=%3.1f y=%3.1f' % (x,y))
        XML = dimensioning.SVGFun( dimensioning.center,
                              dimensioning.topLeft,
                              dimensioning.bottomRight,
                              dimScale = dimensioning.dimScale,
                              **dimensioning.dimensionConstructorKWs)
        return findUnusedObjectName('centerLines'), XML

def hoverFunPreview( x, y):
    if dimensioning.stage == 1:
        return dimensioning.SVGFun( dimensioning.center, [x, y], 
                                    dimScale = dimensioning.dimScale,
                                    **dimensioning.svg_preview_KWs )
    elif dimensioning.stage == 2:
        return dimensioning.SVGFun( dimensioning.center, dimensioning.topLeft, [x, y],
                                    dimScale = dimensioning.dimScale,
                                    **dimensioning.svg_preview_KWs )

class CenterLines:
    def Activated(self):
        V = self.Activated_common()
        dimensioning.SVGFun = centerLinesSVG
        maskPen =      QtGui.QPen( QtGui.QColor(0,255,0,100) )
        maskPen.setWidth(2.0)
        maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) )
        maskHoverPen.setWidth(2.0)
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
    def Activated_common(self):
        V = getDrawingPageGUIVars()
        dimensioning.activate(V, ['centerLine_width','centerLine_len_gap','centerLine_len_dash','centerLine_len_dot'], ['centerLine_color'] )
        return V
    def GetResources(self): 
        return {
            'Pixmap' : os.path.join( iconPath , 'centerLines.svg' ) , 
            'MenuText': 'Center Lines', 
            'ToolTip': 'Center Lines',
            } 
FreeCADGui.addCommand('DrawingDimensioning_centerLines', CenterLines())


class CenterLine(CenterLines):
    def Activated(self):
        V = self.Activated_common()
        dimensioning.SVGFun = centerLineSVG
        maskBrush  =   QtGui.QBrush( QtGui.QColor(0,160,0,100) )
        maskPen =      QtGui.QPen( QtGui.QColor(0,160,0,100) )
        maskPen.setWidth(0.0)
        maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) )
        maskHoverPen.setWidth(0.0)
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
            'Pixmap' : os.path.join( iconPath , 'centerLine.svg' ) , 
            'MenuText': 'Center Line', 
            'ToolTip': 'Center Line',
            } 
FreeCADGui.addCommand('DrawingDimensioning_centerLine', CenterLine())
