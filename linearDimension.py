
from dimensioning import *
import selectionOverlay, previewDimension
from dimensionSvgConstructor import *


d = DimensioningProcessTracker() #shorthand

#
# linear distance between 2 points
#
def linearDimensionSVG_points( x1, y1, x2, y2, x3, y3, x4=None, y4=None, autoPlaceText=False, autoPlaceOffset=2.0,
                               scale=1.0, textFormat_linear='%(value)3.3f', comma_decimal_place=False,
                               gap_datum_points = 2, dimension_line_overshoot=1, arrowL1=3, arrowL2=1, arrowW=2, strokeWidth=0.5, lineColor='blue', arrow_scheme='auto',
                               halfDimension_linear=False, textRenderer= defaultTextRenderer):
    lines = []
    p1 = numpy.array([ x1, y1 ])
    p2 = numpy.array([ x2, y2 ])
    p3 = numpy.array([ x3, y3 ])
    if min(x1,x2) <= x3 and x3 <= max(x1,x2):
        d = numpy.array([ 0, 1])
        textRotation = 0
    elif  min(y1,y2) <= y3 and y3 <= max(y1,y2):
        d = numpy.array([ 1, 0])
        textRotation = -90
    elif numpy.linalg.norm(p2 - p1) > 0:
        d = numpy.dot( [[ 0, -1],[ 1, 0]], directionVector(p1,p2))
        if abs( sum( numpy.sign(d) * numpy.sign( p3- (p1+p2)/2 ))) == 0:
            return None
        textRotation = numpy.arctan( (y2 - y1)/(x2 - x1))  / numpy.pi * 180
        #if textRotation <
    else:
        return None
    A = p1 + numpy.dot(p3-p1,d)*d
    B = p2 + numpy.dot(p3-p2,d)*d
    if not halfDimension_linear:
        lines.append( dimensionSVG_trimLine( p1, A, gap_datum_points,-dimension_line_overshoot))
        lines.append( dimensionSVG_trimLine( p2, B, gap_datum_points,-dimension_line_overshoot))
        lines.append( A.tolist() +  B.tolist() )
    else:
        lines.append( dimensionSVG_trimLine( p2, B, gap_datum_points,-dimension_line_overshoot)) #linePerpendic2
        lines.append( p3.tolist() +  B.tolist() ) #line from pointer to B
    lineXML = '\n'.join( svgLine( x1, y1, x2, y2, lineColor, strokeWidth ) for  x1, y1, x2, y2 in lines )
    v = numpy.linalg.norm(A-B)*scale
    text = dimensionText( v, textFormat_linear, comma=comma_decimal_place)
    textXML = textPlacement_common_procedure(A, B, text, x4, y4, textRotation, textRenderer, autoPlaceText, autoPlaceOffset)
    distAB = numpy.linalg.norm(A-B)
    if distAB > 0 and arrow_scheme <> 'off': #then draw arrows
        if arrow_scheme == 'auto':
            s = 1 if distAB > 2.5*(arrowL1 + arrowL2) else -1
        elif arrow_scheme == 'in':
            s = 1
        elif arrow_scheme == 'out':
            s = -1
        arrowXML = arrowHeadSVG( B, s*directionVector(B,A), arrowL1, arrowL2, arrowW, lineColor )
        if not halfDimension_linear:
            arrowXML = arrowXML +  arrowHeadSVG( A, s*directionVector(A,B), arrowL1, arrowL2, arrowW, lineColor )
    else:
        arrowXML = ''
    return '<g> \n  %s \n  %s \n  %s </g>' % ( lineXML, arrowXML, textXML )

d.dialogWidgets.append( unitSelectionWidget )
d.registerPreference( 'halfDimension_linear', False, 'compact')
d.registerPreference( 'textFormat_linear', '%(value)3.3f', 'format mask')
d.registerPreference( 'arrow_scheme', ['auto','in','out','off'], 'arrows', kind='choice')
d.registerPreference( 'autoPlaceText', True, 'auto place text')
d.registerPreference( 'comma_decimal_place', False, 'comma')
d.registerPreference( 'gap_datum_points', 2, 'gap') 
d.registerPreference( 'dimension_line_overshoot', 1, 'overshoot')
d.registerPreference( 'arrowL1', 3 , increment=0.5)
d.registerPreference( 'arrowL2', 1 , min=-100, increment=0.5)
d.registerPreference( 'arrowW', 2 , increment=0.5)
d.registerPreference( 'strokeWidth', 0.5, increment=0.05 )
d.registerPreference( 'lineColor', 255 << 8, kind='color' )
d.registerPreference( 'textRenderer', ['inherit','3.6',255 << 8], 'text properties', kind='font' )
d.registerPreference( 'autoPlaceOffset', 2, 'auto place offset')

    

def linearDimension_points_preview(mouseX, mouseY):
    selections = d.selections + [ PlacementClick( mouseX, mouseY ) ] if len(d.selections) < d.max_selections else d.selections
    return linearDimensionSVG_points( *selections_to_svg_fun_args(selections), scale= d.viewScale*d.unitConversionFactor, **d.dimensionConstructorKWs )

def linearDimension_points_clickHandler( x, y ):
    d.selections.append( PlacementClick( x, y ) )
    if isinstance( d.selections[0], LineSelection ):
        selectionOverlay.hideSelectionGraphicsItems()
    if len(d.selections) == d.max_selections - 1 and d.dimensionConstructorKWs['autoPlaceText']:
        d.selections.append( PlacementClick( x, y ) ) #to avoid crash when autoPlaceText switched off
        return 'createDimension:%s' % findUnusedObjectName('dim')
    elif len(d.selections) == d.max_selections :
        return 'createDimension:%s' % findUnusedObjectName('dim')


#
# linear distance between parallels
#
def linearDimensionSVG_parallels( line1, line2, x_baseline, y_baseline, x_text=None, y_text=None, autoPlaceText=False, autoPlaceOffset=2.0,
                                  scale=1.0, textFormat_linear='%(value)3.3f', comma_decimal_place=False,
                                  gap_datum_points = 2, dimension_line_overshoot=1,
                                  arrowL1=3, arrowL2=1, arrowW=2, svgTag='g', svgParms='', strokeWidth=0.5, lineColor='blue', arrow_scheme='auto',
                                  halfDimension_linear=False, #notUsed, added for compatibility with d.preferences
                                  textRenderer=defaultTextRenderer):
    XML = []
    p1 = numpy.array( [line1[0], line1[1]] )
    p2 = numpy.array( [line1[2], line1[3]] )
    p3 = numpy.array( [line2[0], line2[1]] )
    p4 = numpy.array( [line2[2], line2[3]] )
    p5 = numpy.array([ x_baseline, y_baseline ])
    d = directionVector(p1,p2)
    # arrow positions
    p_arrow1 = p1 + d*dot(d, p5-p1)
    p_arrow2 = p3 + d*dot(d, p5-p3)
    p_center = (p_arrow1 + p_arrow2)/2
    def line_to_arrow_point( a, b, c): # where a=p1,b=p2 or a=p3,b=p4 and c=p_arrow1 or c=p_arrow2
        if abs( norm(a -b) - (norm(a-c) + norm(b-c))) < norm(a -b)/1000:
            return
        if norm(a-c) < norm(b-c): #then closer to a
            d_a =  directionVector(a, c)
            v = a + gap_datum_points*d_a
            w = c + dimension_line_overshoot*d_a
        else:
            d_b =  directionVector(b, c)
            v = b + gap_datum_points*d_b
            w = c + dimension_line_overshoot*d_b
        XML.append( svgLine(v[0],v[1],w[0],w[1], lineColor, strokeWidth) )
    line_to_arrow_point( p1, p2, p_arrow1)
    line_to_arrow_point( p3, p4, p_arrow2)
    XML.append( svgLine( p_arrow1[0], p_arrow1[1], p_arrow2[0], p_arrow2[1], lineColor, strokeWidth) )
    dist = norm(p_arrow1 - p_arrow2)
    if dist > 0 and arrow_scheme <> 'off': #then draw arrows
        if arrow_scheme == 'auto':
            s = -1 if dist > 2.5*(arrowL1 + arrowL2) else 1
        elif arrow_scheme == 'in':
            s = -1
        elif arrow_scheme == 'out':
            s =  1
        XML.append( arrowHeadSVG( p_arrow1,  directionVector(p_center, p_arrow1)*s, arrowL1, arrowL2, arrowW, lineColor ) )
        XML.append( arrowHeadSVG( p_arrow2,  directionVector(p_center, p_arrow2)*s, arrowL1, arrowL2, arrowW, lineColor ) )
    textRotation = numpy.arctan2( d[1], d[0]) / numpy.pi * 180 + 90
    text = dimensionText(dist*scale,textFormat_linear,comma=comma_decimal_place)
    XML.append( textPlacement_common_procedure( p_arrow1, p_arrow2, text, x_text, y_text, textRotation, textRenderer, autoPlaceText, autoPlaceOffset) )
    return '<g> %s </g> ''' % '\n'.join(XML)

def linearDimension_parallels_preview(mouseX, mouseY):
    selections = d.selections + [ PlacementClick( mouseX, mouseY ) ] if  len(d.selections) < d.max_selections else d.selections
    return linearDimensionSVG_parallels( *selections_to_svg_fun_args(selections), scale= d.viewScale*d.unitConversionFactor, **d.dimensionConstructorKWs )

def linearDimension_parallels_clickHandler( x, y ):
    d.selections.append( PlacementClick( x, y ) )
    if len(d.selections) == d.max_selections - 1 and d.dimensionConstructorKWs['autoPlaceText']:
        d.selections.append( PlacementClick( x, y ) ) #avoid crash when auto place turned off
        return 'createDimension:%s' % findUnusedObjectName('dim')
    elif len(d.selections) == d.max_selections :
        return 'createDimension:%s' % findUnusedObjectName('dim')


class Proxy_linearDimension( Proxy_DimensionObject_prototype ):
     def dimensionProcess( self ):
         return d
d.ProxyClass = Proxy_linearDimension


def linearDimension_parallels_hide_non_parallel(elementParms, elementViewObject):
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
        elif isinstance(gi,selectionOverlay.PointSelectionGraphicsItem):
            return False
        return True 
    selectionOverlay.hideSelectionGraphicsItems(hideFun)



def selectDimensioningPoint( event, referer, elementXML, elementParms, elementViewObject ):
    referer.lockSelection()
    d.viewScale = 1 / elementXML.rootNode().scaling()
    viewInfo = selectionOverlay.DrawingsViews_info[elementViewObject.Name]
    if isinstance(referer,selectionOverlay.PointSelectionGraphicsItem) :
        if len( d.selections) == 0:
            d.selections.append( PointSelection( elementParms, elementXML, viewInfo ) )
            selectionOverlay.hideSelectionGraphicsItems(
                lambda gi: isinstance(gi,  selectionOverlay.LineSelectionGraphicsItem)
                )
        elif isinstance( d.selections[0], PointSelection ):
            d.selections.append( PointSelection( elementParms, elementXML, viewInfo ) )
            d.max_selections = 4
            selectionOverlay.hideSelectionGraphicsItems()
            d.proxy_svgFun = linearDimensionSVG_points
            previewDimension.initializePreview( d, linearDimension_points_preview, linearDimension_points_clickHandler )
        else : #first selection was a line
            d.selections[0].condensed_args = True
            d.selections.append( PointLinePertubationSelection( elementParms, elementXML, viewInfo, d.selections[0] ) )
            d.max_selections = 4
            selectionOverlay.hideSelectionGraphicsItems()
            d.proxy_svgFun = linearDimensionSVG_parallels
            previewDimension.removePreviewGraphicItems( False, closeDialog=False ) #required since previewDimension.initializePreview called when line selected
            previewDimension.initializePreview( d, linearDimension_parallels_preview, linearDimension_parallels_clickHandler )
    else: #then line slected
        if len( d.selections ) == 0: 
            d.selections.append( LineSelection( elementParms, elementXML, viewInfo) )
            d.selections[0].condensed_args = False
            d.max_selections = 3
            linearDimension_parallels_hide_non_parallel( elementParms, elementViewObject)
            d.proxy_svgFun = linearDimensionSVG_points
            previewDimension.initializePreview( d, linearDimension_points_preview, linearDimension_points_clickHandler )
        else:
            d.selections[0].condensed_args = True
            d.selections.append( LineSelection( elementParms, elementXML, viewInfo) )
            d.max_selections = 4
            selectionOverlay.hideSelectionGraphicsItems()
            d.proxy_svgFun = linearDimensionSVG_parallels
            previewDimension.removePreviewGraphicItems( False, closeDialog=False )
            previewDimension.initializePreview( d, linearDimension_parallels_preview, linearDimension_parallels_clickHandler )

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



class LinearDimensionCommand:
    def __init__(self):
        self.iconPath = ':/dd/icons/linearDimension.svg'
        self.toolTip = 'Add Linear Dimension'
        self.onClickFun = selectDimensioningPoint
        self.d = d

    def Activated(self):
        V = getDrawingPageGUIVars()
        self.d.activate( V, dialogTitle = self.toolTip, dialogIconPath = self.iconPath, endFunction = self.Activated )
        commonArgs = dict( 
            onClickFun= self.onClickFun,
            transform = V.transform,
            sceneToAddTo = V.graphicsScene, 
            pointWid=1.0,
            maskPen=maskPen, 
            maskHoverPen=maskHoverPen, 
            maskBrush = maskBrush
            )
        selectionOverlay.generateSelectionGraphicsItems( 
            dimensionableObjects( V.page ), 
            doPoints=True, 
            **commonArgs
            )
        from centerLines import Proxy_CenterLines
        selectionOverlay.generateSelectionGraphicsItems( 
            [ obj for obj in V.page.Group if hasattr(obj, 'Proxy') and isinstance( obj.Proxy, Proxy_CenterLines )], 
            clearPreviousSelectionItems = False,
            doPathEndPoints=True, 
            **commonArgs
            )
        selectionOverlay.generateSelectionGraphicsItems( 
            dimensionableObjects( V.page ), 
            clearPreviousSelectionItems = False,
            doLines=True, 
            onClickFun= self.onClickFun,
            transform = V.transform,
            sceneToAddTo = V.graphicsScene, 
            maskPen= line_maskPen, 
            maskHoverPen= line_maskHoverPen, 
            maskBrush = line_maskBrush
            )
        selectionOverlay.addProxyRectToRescaleGraphicsSelectionItems( V.graphicsScene, V.graphicsView, V.width, V.height)
        
    def GetResources(self): 
        return {
            'Pixmap' : self.iconPath, 
            'MenuText': self.toolTip, 
            'ToolTip':  self.toolTip
            } 

FreeCADGui.addCommand('dd_linearDimension', LinearDimensionCommand())


