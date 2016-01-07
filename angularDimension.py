# This Python file uses the following encoding: utf-8
from dimensioning import *
import selectionOverlay, previewDimension
from dimensionSvgConstructor import *

d = DimensioningProcessTracker()

def angularDimensionSVG( line1, line2, x_baseline, y_baseline, x_text=None, y_text=None, 
                         textFormat_angular='%(value)3.1f°', comma_decimal_place=False, gap_datum_points = 2, dimension_line_overshoot=1, arrowL1=3, arrowL2=1, arrowW=2, strokeWidth=0.5, lineColor='blue',  arrow_scheme='auto',
                         textRenderer=defaultTextRenderer):
    XML = []
    x_int, y_int = lineIntersection(line1, line2)
    #XML.append( '<circle cx ="%f" cy ="%f" r="4" stroke="none" fill="rgb(0,0,255)" /> ' % (x_int, y_int) ) #for debugging
    p_center = numpy.array([ x_int, y_int ] )
    p1 = numpy.array( [line1[0], line1[1]] )
    p2 = numpy.array( [line1[2], line1[3]] )
    p3 = numpy.array( [line2[0], line2[1]] )
    p4 = numpy.array( [line2[2], line2[3]] )
    p5 = numpy.array([ x_baseline, y_baseline ])
    r_P5 = norm( p5 -p_center )
    # determine arrow position
    def arrowPosition( d ):
        cand1 = p_center + d*r_P5
        cand2 = p_center - d*r_P5
        return cand1 if norm( cand1 - p5) < norm( cand2 - p5) else cand2
    p_arrow1 = arrowPosition(directionVector(p1,p2))
    p_arrow2 = arrowPosition(directionVector(p3,p4))
    def line_to_arrow_point( a, b, c): # where a=p1,b=p2 or a=p3,b=p4 and c=p_arrow1 or c=p_arrow2
        if abs( norm(a -b) - (norm(a-c) + norm(b-c))) < norm(a -b)/1000:
            return
        s = a if norm(a-c) < norm(b-c) else b #start_point
        d = directionVector( s, c)
        v = s + gap_datum_points*d
        w = c + dimension_line_overshoot*d
        XML.append( svgLine(v[0],v[1],w[0],w[1], lineColor, strokeWidth) )
    line_to_arrow_point( p1, p2, p_arrow1)
    line_to_arrow_point( p3, p4, p_arrow2)

    d1 = directionVector(p_center, p_arrow1)
    d2 = directionVector(p_center, p_arrow2)

    largeArc = False # given the selection method for the arrow heads (points and line1 and line2 used for measuring the angle)
    angle_1 = arctan2( d2[1], d2[0] )
    angle_2 = arctan2( d1[1], d1[0] )
    if abs(angle_1 - angle_2) < pi: #modulo correction required, since arctan2 return [-pi, pi]
        if angle_2 < angle_1:
            angle_2 = angle_2 + 2*pi
        else:
            angle_1 = angle_1 + 2*pi
    sweep = angle_2 > angle_1
    #rX, rY, xRotation, largeArc, sweep, _end_x, _end_y =
    XML.append('<path d = "M %f %f A %f %f 0 %i %i %f %f" style="stroke:%s;stroke-width:%1.2f;fill:none" />' % (p_arrow1[0],p_arrow1[1], r_P5, r_P5, largeArc, sweep, p_arrow2[0],p_arrow2[1],lineColor, strokeWidth))

    if arrow_scheme <> 'off': #then draw arrows
        if arrow_scheme == 'auto':
            s = 1 if  angle_2 > angle_1 else -1
        elif arrow_scheme == 'in':
            s = 1
        elif arrow_scheme == 'out':
            s = -1
        XML.append( arrowHeadSVG( p_arrow1, rotate2D(d1, s*pi/2), arrowL1, arrowL2, arrowW, lineColor ) )
        XML.append( arrowHeadSVG( p_arrow2, rotate2D(d2,-s*pi/2), arrowL1, arrowL2, arrowW, lineColor ) )

    if x_text <> None and y_text <> None:
        v = arccos( numpy.dot(d1, d2) )/ pi * 180
        textRotation = numpy.arctan2( y_text - y_int, x_text - x_int)
        textXML = textRenderer( x_text, y_text, dimensionText(v,textFormat_angular, comma=comma_decimal_place), textRotation)
        XML.append( textXML )
    return '<g> %s </g>' % '\n'.join(XML)

d.registerPreference( 'textFormat_angular', '%(value)3.1f°', 'format mask')
d.registerPreference( 'arrow_scheme')
d.registerPreference( 'comma_decimal_place' )
d.registerPreference( 'gap_datum_points') 
d.registerPreference( 'dimension_line_overshoot')
d.registerPreference( 'arrowL1')
d.registerPreference( 'arrowL2')
d.registerPreference( 'arrowW')
d.registerPreference( 'strokeWidth' )
d.registerPreference( 'lineColor' )
d.registerPreference( 'textRenderer' )

def angularDimension_points_preview(mouseX, mouseY):
    selections = d.selections + [ PlacementClick( mouseX, mouseY ) ] if len(d.selections) < d.max_selections else d.selections
    return angularDimensionSVG( *selections_to_svg_fun_args(selections), **d.dimensionConstructorKWs )

def angularDimension_points_clickHandler( x, y ):
    d.selections.append( PlacementClick( x, y ) )
    if len(d.selections) == d.max_selections :
        return 'createDimension:%s' % findUnusedObjectName('dim')

        
def selectFun( event, referer, elementXML, elementParms, elementViewObject ):
    referer.lockSelection()
    viewInfo = selectionOverlay.DrawingsViews_info[elementViewObject.Name]
    if isinstance(referer, selectionOverlay.LineSelectionGraphicsItem):
        d.selections.append( LineSelection( elementParms, elementXML, viewInfo) )
        if len(d.selections) == 1:
            for gi in selectionOverlay.graphicItems:
                if isinstance(gi,  selectionOverlay.PointSelectionGraphicsItem):
                    gi.hide()
        else: 
            d.max_selections = 4
            selectionOverlay.hideSelectionGraphicsItems()
            previewDimension.initializePreview( d, angularDimension_points_preview, angularDimension_points_clickHandler )
    else: #user selecting 3 points
        if len(d.selections) == 0: 
            d.selections = [ThreePointAngleSelection()]
            d.max_selections = 3
            for gi in selectionOverlay.graphicItems:
                if isinstance(gi,  selectionOverlay.LineSelectionGraphicsItem):
                    gi.hide()
        d.selections[0].addPoint( elementParms, elementXML, viewInfo )
        if len(d.selections[0].points) == 3: 
            selectionOverlay.hideSelectionGraphicsItems()
            previewDimension.initializePreview( d,  angularDimension_points_preview, angularDimension_points_clickHandler)

class Proxy_angularDimension( Proxy_DimensionObject_prototype ):
     def dimensionProcess( self ):
         return d
d.ProxyClass = Proxy_angularDimension
d.proxy_svgFun = angularDimensionSVG


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

class AngularDimension:
    def Activated(self):
        V = getDrawingPageGUIVars()
        d.activate(V, dialogTitle='Add Angular Dimension', dialogIconPath=':/dd/icons/angularDimension.svg', endFunction=self.Activated )
        selectionOverlay.generateSelectionGraphicsItems( 
            dimensionableObjects( V.page ), 
            selectFun ,
            transform = V.transform,
            sceneToAddTo = V.graphicsScene, 
            doLines=True,
            maskPen= line_maskPen, 
            maskHoverPen= line_maskHoverPen, 
            maskBrush = line_maskBrush
            )
        selectionOverlay.generateSelectionGraphicsItems( 
            dimensionableObjects( V.page ),
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
            'Pixmap' : ':/dd/icons/angularDimension.svg', 
            'MenuText': 'Angular Dimension', 
            'ToolTip': 'Creates a angular dimension'
            } 

FreeCADGui.addCommand('dd_angularDimension', AngularDimension())
