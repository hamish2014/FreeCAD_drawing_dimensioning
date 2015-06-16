
from dimensioning import *
import selectionOverlay, previewDimension
from dimensionSvgConstructor import *
from linearDimension import linearDimension_parallels_hide_non_parallel

d = DimensioningProcessTracker()

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

def _centerLinesSVG( center, topLeft, bottomRight, dimScale, centerLine_len_dot, centerLine_len_dash, centerLine_len_gap, strokeWidth, lineColor, doVertical, doHorizontal ):
    XML_body = []
    center = numpy.array( center ) / dimScale
    topLeft = numpy.array( topLeft ) / dimScale
    if bottomRight <> None: bottomRight =  numpy.array( bottomRight ) / dimScale
    commonArgs =  centerLine_len_dot / dimScale,  centerLine_len_dash / dimScale,  centerLine_len_gap / dimScale
    if doVertical: XML_body.append( _centerLineSVG(center[0], center[1], center[0], topLeft[1], *commonArgs ) )
    if doHorizontal: XML_body.append( _centerLineSVG(center[0], center[1], topLeft[0], center[1], *commonArgs ) )
    if bottomRight <> None:
        if doVertical: XML_body.append( _centerLineSVG(center[0], center[1], center[0], bottomRight[1], *commonArgs ) )
        if doHorizontal: XML_body.append( _centerLineSVG(center[0], center[1], bottomRight[0], center[1], *commonArgs ) )
    return '<g transform="scale(%f,%f)" stroke="%s"  stroke-width="%f" > %s </g> ''' % ( dimScale, dimScale, lineColor, strokeWidth/ dimScale, "\n".join(XML_body) )


def centerLinesSVG( center, topLeft, bottomRight=None, dimScale=1.0, centerLine_len_dot=2.0, centerLine_len_dash=6.0, centerLine_len_gap=2.0, centerLine_width=0.5, centerLine_color='blue'):
    return _centerLinesSVG( center, topLeft, bottomRight, dimScale, centerLine_len_dot, centerLine_len_dash, centerLine_len_gap, centerLine_width, centerLine_color, True, True )

def centerLineSVG( center, topLeft, bottomRight=None,  dimScale=1.0, centerLine_len_dot=2.0, centerLine_len_dash=6.0, centerLine_len_gap=2.0, centerLine_width=0.5, centerLine_color='blue'):
    v = abs(center[0] - topLeft[0]) < abs(center[1] - topLeft[1]) #vertical
    return _centerLinesSVG( center, topLeft, bottomRight, dimScale, centerLine_len_dot, centerLine_len_dash, centerLine_len_gap, centerLine_width, centerLine_color, v, not v )


d.registerPreference( 'centerLine_len_dot', 3 , label='dot length', increment=0.5)
d.registerPreference( 'centerLine_len_dash', 6 , label='dash length', increment=0.5)
d.registerPreference( 'centerLine_len_gap', 2 , label='gap length', increment=0.5)
d.registerPreference( 'centerLine_width', 0.32 , label='line width', increment=0.05)
d.registerPreference( 'centerLine_color', 255 << 8, kind='color' )

def centerLine_preview(mouseX, mouseY):
    args = d.args + [[ mouseX, mouseY ]] if len(d.args) < 3 else d.args
    return d.SVGFun( *args, dimScale = d.dimScale, **d.dimensionConstructorKWs )

def centerLine_clickHandler( x, y ):
    d.args = d.args + [[ x, y ]]
    d.stage = d.stage + 1
    if d.stage == 3:
        return 'createDimension:%s' % findUnusedObjectName('centerLines')

def selectFun(  event, referer, elementXML, elementParms, elementViewObject ):
    if not isinstance(referer,selectionOverlay.LineSelectionGraphicsItem):
        x,y = elementParms['x'], elementParms['y']
        d.args = [[x, y]]
        d.stage = 1
        d.dimScale = elementXML.rootNode().scaling()
        debugPrint(3, 'center selected at x=%3.1f y=%3.1f scale %3.1f' % (x,y, d.dimScale))
        selectionOverlay.hideSelectionGraphicsItems()
        previewDimension.initializePreview( d, centerLine_preview , centerLine_clickHandler)
    else:
        if d.stage == 0:
            d.line1 = [ elementParms[k] for k in [ 'x1', 'y1', 'x2', 'y2' ] ]
            d.stage = 1
            linearDimension_parallels_hide_non_parallel( elementParms, elementViewObject)
        else:
            x1, y1, x2, y2 = d.line1
            x3, y3, x4, y4 = [ elementParms[k] for k in [ 'x1', 'y1', 'x2', 'y2' ] ]
            d.args = [[0.25*(x1 + x2 + x3 + x4), 0.25*(y1 + y2 + y3 + y4)]]
            d.stage = 1
            d.dimScale = elementXML.rootNode().scaling()
            selectionOverlay.hideSelectionGraphicsItems()
            previewDimension.initializePreview( d, centerLine_preview , centerLine_clickHandler)


class CenterLines:
    def Activated(self):
        V = getDrawingPageGUIVars()
        d.activate(V, dialogTitle='Add Center Lines', dialogIconPath=os.path.join( iconPath , 'centerLines.svg' ), endFunction=self.Activated )
        d.SVGFun = centerLinesSVG
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
    def GetResources(self): 
        return {
            'Pixmap' : os.path.join( iconPath , 'centerLines.svg' ) , 
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
        d.activate(V, dialogTitle='Add Center Lines', dialogIconPath=os.path.join( iconPath , 'centerLine.svg' ), endFunction=self.Activated )
        d.SVGFun = centerLineSVG
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
        selectionOverlay.generateSelectionGraphicsItems( 
            [obj for obj in V.page.Group  if not obj.Name.startswith('dim') and not obj.Name.startswith('center')],
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
            'Pixmap' : os.path.join( iconPath , 'centerLine.svg' ) , 
            'MenuText': 'Center Line', 
            'ToolTip': 'Center Line',
            } 
FreeCADGui.addCommand('dd_centerLine', CenterLine())
