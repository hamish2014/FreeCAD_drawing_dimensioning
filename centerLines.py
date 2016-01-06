
from dimensioning import *
import selectionOverlay, previewDimension
from dimensionSvgConstructor import *
from linearDimension import linearDimension_parallels_hide_non_parallel

d = DimensioningProcessTracker( add_viewScale_KW = True )

def _centerLineSVG( x1, y1, x2, y2, len_dot, len_dash, len_gap, start_with_half_dot=False):
    start = numpy.array( [x1, y1] )
    end = numpy.array( [x2, y2] )
    d = directionVector(start, end)
    dCode = ''
    pos = start
    step = len_dot*0.5 if start_with_half_dot else len_dot
    while norm(pos - start) + 10**-6 < norm(end - start):
        dCode = dCode + 'M %f,%f' %  (pos[0], pos[1])
        pos = pos + d*step
        if norm(pos - start) > norm(end - start):
            pos = end
        dCode = dCode + ' L %f,%f ' % (pos[0], pos[1])
        pos = pos + d*len_gap
        step = len_dash if step < len_dash else len_dot
    if dCode <> '':
        return '<path d="%s"/>' % dCode
    else:
        return ''

def _centerLinesSVG( center, topLeft, bottomRight, viewScale, centerLine_len_dot, centerLine_len_dash, centerLine_len_gap, strokeWidth, lineColor, doVertical, doHorizontal ):
    XML_body = []
    center = numpy.array( center ) / viewScale
    topLeft = numpy.array( topLeft ) / viewScale
    if bottomRight <> None: bottomRight =  numpy.array( bottomRight ) / viewScale
    commonArgs =  centerLine_len_dot / viewScale,  centerLine_len_dash / viewScale,  centerLine_len_gap / viewScale
    if doVertical: XML_body.append( _centerLineSVG(center[0], center[1], center[0], topLeft[1], *commonArgs ) )
    if doHorizontal: XML_body.append( _centerLineSVG(center[0], center[1], topLeft[0], center[1], *commonArgs ) )
    if bottomRight <> None:
        if doVertical: XML_body.append( _centerLineSVG(center[0], center[1], center[0], bottomRight[1], *commonArgs ) )
        if doHorizontal: XML_body.append( _centerLineSVG(center[0], center[1], bottomRight[0], center[1], *commonArgs ) )
    return '<g transform="scale(%f,%f)" stroke="%s"  stroke-width="%f" > %s </g> ''' % ( viewScale, viewScale, lineColor, strokeWidth/ viewScale, "\n".join(XML_body) )


def centerLinesSVG( center, topLeft, bottomRight=None, viewScale=1.0, centerLine_len_dot=2.0, centerLine_len_dash=6.0, centerLine_len_gap=2.0, centerLine_width=0.5, centerLine_color='blue'):
    return _centerLinesSVG( center, topLeft, bottomRight, viewScale, centerLine_len_dot, centerLine_len_dash, centerLine_len_gap, centerLine_width, centerLine_color, True, True )

def centerLineSVG( center, topLeft, bottomRight=None,  viewScale=1.0, centerLine_len_dot=2.0, centerLine_len_dash=6.0, centerLine_len_gap=2.0, centerLine_width=0.5, centerLine_color='blue'):
    v = abs(center[0] - topLeft[0]) < abs(center[1] - topLeft[1]) #vertical
    return _centerLinesSVG( center, topLeft, bottomRight, viewScale, centerLine_len_dot, centerLine_len_dash, centerLine_len_gap, centerLine_width, centerLine_color, v, not v )


d.registerPreference( 'centerLine_len_dot', 3 , label='dot length', increment=0.5)
d.registerPreference( 'centerLine_len_dash', 6 , label='dash length', increment=0.5)
d.registerPreference( 'centerLine_len_gap', 2 , label='gap length', increment=0.5)
d.registerPreference( 'centerLine_width', 0.32 , label='line width', increment=0.05)
d.registerPreference( 'centerLine_color', 255 << 8, kind='color' )
d.max_selections = 3

def centerLine_preview(mouseX, mouseY):
    selections = d.selections + [ PlacementClick( mouseX, mouseY, condensed_args=True) ] if len(d.selections) < d.max_selections else d.selections
    return d.SVGFun( *selections_to_svg_fun_args(selections), viewScale = d.viewScale, **d.dimensionConstructorKWs )

def centerLine_clickHandler( x, y ):
    d.selections.append( PlacementClick( x, y, condensed_args=True) )
    if len(d.selections) == d.max_selections:
        return 'createDimension:%s' % findUnusedObjectName('centerLines')

def selectFun(  event, referer, elementXML, elementParms, elementViewObject ):
    viewInfo = selectionOverlay.DrawingsViews_info[elementViewObject.Name]
    d.viewScale = elementXML.rootNode().scaling()
    # center line
    if isinstance(referer,selectionOverlay.PointSelectionGraphicsItem):
        d.selections = [ PointSelection( elementParms, elementXML, viewInfo, condensed_args=True ) ]
        selectionOverlay.hideSelectionGraphicsItems()
        previewDimension.initializePreview( d, centerLine_preview , centerLine_clickHandler)
    elif isinstance(referer,selectionOverlay.LineSelectionGraphicsItem):
        if len(d.selections) == 0:
            d.selections = [ TwoLineSelection() ]
            linearDimension_parallels_hide_non_parallel( elementParms, elementViewObject)
            for gi in selectionOverlay.graphicItems:
                if isinstance(gi,  selectionOverlay.PointSelectionGraphicsItem):
                    gi.hide()
        d.selections[0].addLine(  elementParms, elementXML, viewInfo )
        if len(d.selections[0].lines) == 2:
            selectionOverlay.hideSelectionGraphicsItems()
            previewDimension.initializePreview( d, centerLine_preview , centerLine_clickHandler)
    else: #centerlines selection overlay
        d.selections = [ CircularArcSelection( elementParms, elementXML, viewInfo, output_mode = 'xy' ) ]
        selectionOverlay.hideSelectionGraphicsItems()
        previewDimension.initializePreview( d, centerLine_preview , centerLine_clickHandler)

class Proxy_CenterLines( Proxy_DimensionObject_prototype ):
     def dimensionProcess( self ):
         return d
d.ProxyClass = Proxy_CenterLines


class CenterLines:
    def Activated(self):
        V = getDrawingPageGUIVars()
        d.activate(V, dialogTitle='Add Center Lines', dialogIconPath=':/dd/icons/centerLines.svg', endFunction=self.Activated )
        d.SVGFun = centerLinesSVG
        d.ProxyClass = Proxy_CenterLines
        d.proxy_svgFun = centerLinesSVG
        maskPen =      QtGui.QPen( QtGui.QColor(0,255,0,100) )
        maskPen.setWidth(2.0)
        maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) )
        maskHoverPen.setWidth(2.0)
        selectionOverlay.generateSelectionGraphicsItems( 
            dimensionableObjects( V.page ),
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
            'Pixmap' : ':/dd/icons/centerLines.svg', 
            'MenuText': 'Center Lines', 
            'ToolTip': 'Center Lines',
            } 
FreeCADGui.addCommand('dd_centerLines', CenterLines())

line_maskPen =      QtGui.QPen( QtGui.QColor(0,255,0,100) )
line_maskPen.setWidth(2.0)
line_maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) )
line_maskHoverPen.setWidth(2.0)
line_maskBrush = QtGui.QBrush() #clear

class CenterLine(CenterLines):
    def Activated(self):
        V = getDrawingPageGUIVars()
        d.activate(V, dialogTitle='Add Center Lines', dialogIconPath=':/dd/icons/centerLine.svg', endFunction=self.Activated )
        d.SVGFun = centerLineSVG
        d.ProxyClass = Proxy_CenterLines
        d.proxy_svgFun = centerLineSVG
        maskBrush  =   QtGui.QBrush( QtGui.QColor(0,160,0,100) )
        maskPen =      QtGui.QPen( QtGui.QColor(0,160,0,100) )
        maskPen.setWidth(0.0)
        maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) )
        maskHoverPen.setWidth(0.0)
        selectionOverlay.generateSelectionGraphicsItems( 
            dimensionableObjects( V.page ), 
            selectFun,
            transform = V.transform,
            sceneToAddTo = V.graphicsScene, 
            doPoints=True, doMidPoints=True,
            pointWid=1.0,
            maskPen=maskPen, 
            maskHoverPen=maskHoverPen, 
            maskBrush = maskBrush
            )
        selectionOverlay.generateSelectionGraphicsItems( 
            dimensionableObjects( V.page ),
            clearPreviousSelectionItems = False,
            doLines=True, 
            onClickFun=selectFun,
            transform = V.transform,
            sceneToAddTo = V.graphicsScene, 
            maskPen= line_maskPen, 
            maskHoverPen= line_maskHoverPen, 
            maskBrush = line_maskBrush
            )
        selectionOverlay.addProxyRectToRescaleGraphicsSelectionItems( V.graphicsScene, V.graphicsView, V.width, V.height)

    def GetResources(self): 
        return {
            'Pixmap' : ':/dd/icons/centerLine.svg', 
            'MenuText': 'Center Line', 
            'ToolTip': 'Center Line',
            } 
FreeCADGui.addCommand('dd_centerLine', CenterLine())
