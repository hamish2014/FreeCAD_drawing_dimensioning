
from dimensioning import *
import selectionOverlay, previewDimension
from dimensionSvgConstructor import *

d = DimensioningProcessTracker() #shorthand

#
# linear distance between 2 points
#
def linearDimensionSVG_points( x1, y1, x2, y2, x3, y3, x4=None, y4=None, autoPlaceText=False, autoPlaceOffset=2.0,
                               scale=1.0, textFormat_linear='%3.3f', comma_decimal_place=False,
                               gap_datum_points = 2, dimension_line_overshoot=1, arrowL1=3, arrowL2=1, arrowW=2, strokeWidth=0.5, lineColor='blue', 
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
    if distAB > 0:
        s = 1 if distAB > 2.5*(arrowL1 + arrowL2) else -1
        arrowXML = arrowHeadSVG( B, s*directionVector(B,A), arrowL1, arrowL2, arrowW, lineColor )
        if not halfDimension_linear:
            arrowXML = arrowXML +  arrowHeadSVG( A, s*directionVector(A,B), arrowL1, arrowL2, arrowW, lineColor )
    else:
        arrowXML = ''
    return '<g> \n  %s \n  %s \n  %s </g>' % ( lineXML, arrowXML, textXML )

d.dialogWidgets.append( unitSelectionWidget )
d.registerPreference( 'halfDimension_linear', False, 'compact')
d.registerPreference( 'textFormat_linear', '%3.3f', 'format mask')
d.registerPreference( 'autoPlaceText', True, 'auto place text')
d.registerPreference( 'comma_decimal_place', False, 'comma')
d.registerPreference( 'autoPlaceOffset', 2, 'auto place offset')
d.registerPreference( 'gap_datum_points', 2, 'gap') 
d.registerPreference( 'dimension_line_overshoot', 1, 'overshoot')
d.registerPreference( 'arrowL1', 3 , increment=0.5)
d.registerPreference( 'arrowL2', 1 , min=-100, increment=0.5)
d.registerPreference( 'arrowW', 1 , increment=0.5)
d.registerPreference( 'strokeWidth', 0.5, increment=0.05 )
d.registerPreference( 'lineColor', 255 << 8, kind='color' )
d.registerPreference( 'textRenderer', ['inherit','3.6',255 << 8], 'text properties', kind='font' )
    

def linearDimension_points_preview(mouseX, mouseY):
    args = d.args + [ mouseX, mouseY ] if len(d.args) < 8 else d.args
    return linearDimensionSVG_points( *args, scale= d.viewScale*d.unitConversionFactor, **d.dimensionConstructorKWs )

def linearDimension_points_clickHandler( x, y ):
    d.args = d.args + [ x, y ]
    d.stage = d.stage + 1
    if d.stage == 3:
        if d.dimensionConstructorKWs['autoPlaceText']:
            return 'createDimension:%s' % findUnusedObjectName('dim')
        else:
            selectionOverlay.hideSelectionGraphicsItems() # for distance between parallels case
    elif d.stage == 4 :
        return 'createDimension:%s' % findUnusedObjectName('dim')


#
# linear distance between parallels
#
def linearDimensionSVG_parallels( line1, line2, x_baseline, y_baseline, x_text=None, y_text=None, autoPlaceText=False, autoPlaceOffset=2.0,
                                  scale=1.0, textFormat_linear='%3.3f', comma_decimal_place=False,
                                  gap_datum_points = 2, dimension_line_overshoot=1,
                                  arrowL1=3, arrowL2=1, arrowW=2, svgTag='g', svgParms='', strokeWidth=0.5, lineColor='blue',
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
    if dist > 0:
        s = -1 if dist > 2.5*(arrowL1 + arrowL2) else 1
    XML.append( arrowHeadSVG( p_arrow1,  directionVector(p_center, p_arrow1)*s, arrowL1, arrowL2, arrowW, lineColor ) )
    XML.append( arrowHeadSVG( p_arrow2,  directionVector(p_center, p_arrow2)*s, arrowL1, arrowL2, arrowW, lineColor ) )
    textRotation = numpy.arctan2( d[1], d[0]) / numpy.pi * 180 + 90
    text = dimensionText(dist*scale,textFormat_linear,comma=comma_decimal_place)
    XML.append( textPlacement_common_procedure( p_arrow1, p_arrow2, text, x_text, y_text, textRotation, textRenderer, autoPlaceText, autoPlaceOffset) )
    return '<g> %s </g> ''' % '\n'.join(XML)

def linearDimension_parallels_preview(mouseX, mouseY):
    args = d.args + [ mouseX, mouseY ] if len(d.args) < 6 else d.args
    return linearDimensionSVG_parallels( *args, scale= d.viewScale*d.unitConversionFactor, **d.dimensionConstructorKWs )

def linearDimension_parallels_clickHandler( x, y ):
    d.args = d.args + [ x, y ]
    d.stage = d.stage + 1
    if d.stage == 3 and d.dimensionConstructorKWs['autoPlaceText']:
        return 'createDimension:%s' % findUnusedObjectName('dim')
    elif d.stage == 4 :
        return 'createDimension:%s' % findUnusedObjectName('dim')

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
    if isinstance(referer,selectionOverlay.PointSelectionGraphicsItem) and d.stage < 2:
        x, y = elementParms['x'], elementParms['y']
        referer.lockSelection()
        if d.stage == 0: #then selectPoint1
            d.args =  [x,y]
            debugPrint(2, 'point1 set to x=%3.1f y=%3.1f' % (x,y))
            d.stage = 1
            selectionOverlay.hideSelectionGraphicsItems(
                lambda gi: isinstance(gi,  selectionOverlay.LineSelectionGraphicsItem)
                )
        else:
            d.args = d.args + [x,y]
            debugPrint(2, 'point2 set to x=%3.1f y=%3.1f' % (x,y))
            d.stage = 2 
            d.viewScale = 1 / elementXML.rootNode().scaling()
            selectionOverlay.hideSelectionGraphicsItems()
            previewDimension.initializePreview( d, linearDimension_points_preview, linearDimension_points_clickHandler )
    else:#then line
        if d.stage == 0: 
            x1,y1,x2,y2 = [ elementParms[k] for k in [ 'x1', 'y1', 'x2', 'y2' ] ]
            debugPrint(2,'selecting line x1=%3.1f y1=%3.1f, x2=%3.1f y2=%3.1f' % (x1,y1,x2,y2))
            d.args = [ x1,y1,x2,y2 ]
            d.stage = 2 
            d.viewScale = 1 / elementXML.rootNode().scaling()
            linearDimension_parallels_hide_non_parallel( elementParms, elementViewObject)
            previewDimension.initializePreview( d, linearDimension_points_preview, linearDimension_points_clickHandler )
        else:
            if isinstance(referer, selectionOverlay.LineSelectionGraphicsItem): #then distance between parallels
                x1,y1,x2,y2 = [ elementParms[k] for k in [ 'x1', 'y1', 'x2', 'y2' ] ]
                debugPrint(2,'distance between parallels, line2 x1=%3.1f y1=%3.1f, x2=%3.1f y2=%3.1f' % (x1,y1,x2,y2))
                line1 = d.args
                d.args = [ line1, [ x1,y1,x2,y2 ] ]
            else: #distance between line and point
                line1 = d.args
                x1,y1,x2,y2 = line1
                dx = (x2-x1)*10**-6
                dy = (y2-y1)*10**-6
                debugPrint(3,'distance between line and point, dx %e dy %e' % (dx,dy))
                x, y =  elementParms['x'], elementParms['y']
                d.args = [ line1, [ x-dx,y-dy,x+dx,y+dy ] ]
            d.stage = 2 
            selectionOverlay.hideSelectionGraphicsItems()
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
    def Activated(self):
        V = getDrawingPageGUIVars()
        d.activate( V, dialogTitle='Add Linear Dimension', dialogIconPath=os.path.join( iconPath , 'linearDimension.svg' ), endFunction=self.Activated )

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
            'Pixmap' : os.path.join( iconPath , 'linearDimension.svg' ) , 
            'MenuText': 'Linear Dimension', 
            'ToolTip': 'Creates a linear dimension'
            } 

FreeCADGui.addCommand('dd_linearDimension', LinearDimensionCommand())
