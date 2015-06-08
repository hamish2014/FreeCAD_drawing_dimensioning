
from dimensioning import *
import selectionOverlay, previewDimension
from dimensionSvgConstructor import *

d = DimensioningProcessTracker()

def halfLinearDimensionSVG( x1, y1, x2, y2, x3, y3, x4=None, y4=None, 
                            scale=1.0, textFormat='%3.3f',  gap_datum_points = 2, dimension_line_overshoot=1, arrowL1=3, arrowL2=1, arrowW=2, strokeWidth=0.5, lineColor='blue', 
                            textRenderer=defaultTextRenderer):
    lines = []
    p1 = numpy.array([ x1, y1 ]) #first point
    p2 = numpy.array([ x2, y2 ]) #second point
    p3 = numpy.array([ x3, y3 ]) #line position
    if min(x1,x2) <= x3 and x3 <= max(x1,x2): #horizontal line
        d = numpy.array([ 0, 1])
        textRotation = 0
    elif  min(y1,y2) <= y3 and y3 <= max(y1,y2): # vertical line
        d = numpy.array([ 1, 0])
        textRotation = -90
    elif numpy.linalg.norm(p2 - p1) > 0: # other angle
        d = numpy.dot( [[ 0, -1],[ 1, 0]], directionVector(p1,p2))
        if abs( sum( numpy.sign(d) * numpy.sign( p3- (p1+p2)/2 ))) == 0:
            return None
        textRotation = numpy.arctan( (y2 - y1)/(x2 - x1))  / numpy.pi * 180
    else:
        return None
    A = p1 + numpy.dot(p3-p1,d)*d # projection vector on axis d
    B = p2 + numpy.dot(p3-p2,d)*d
    lines.append( dimensionSVG_trimLine( p2, B, gap_datum_points,-dimension_line_overshoot)) #linePerpendic2
    lines.append( p3.tolist() +  B.tolist() ) #line from pointer to B
    lineXML = '\n'.join( svgLine( x1, y1, x2, y2, lineColor, strokeWidth ) for  x1, y1, x2, y2 in lines )
    if x4 <> None and y4 <> None:
        v = numpy.linalg.norm(A-B)*scale
        textXML = textRenderer( x4, y4, dimensionText(v,textFormat), rotation=textRotation )
    else :
        textXML = ''
    distAB = numpy.linalg.norm(A-B)
    if distAB > 0:
        arrowXML = arrowHeadSVG( B, directionVector(B,A), arrowL1, arrowL2, arrowW, lineColor )
    else:
        arrowXML = ''
    return '<g> \n  %s \n  %s \n  %s </g>' % ( lineXML, arrowXML, textXML )

def linearDimension_half_preview(mouseX, mouseY):
    args = d.args + [ mouseX, mouseY ] if len(d.args) < 8 else d.args
    dimScale = d._dimScale / UnitConversionFactor()
    return halfLinearDimensionSVG( *args, scale=dimScale, **d.dimensionConstructorKWs )

def linearDimension_half_clickHandler( x, y ):
    d.args = d.args + [ x, y ]
    d.stage = d.stage + 1
    if d.stage == 3:
        selectionOverlay.hideSelectionGraphicsItems() # for distance between parallels case
    elif d.stage == 4 :
        return 'createDimension:%s' % findUnusedObjectName('dim')


def selectDimensioningPoint( event, referer, elementXML, elementParms, elementViewObject ):
    if isinstance(referer,selectionOverlay.PointSelectionGraphicsItem):
        x, y = elementParms['x'], elementParms['y']
        referer.lockSelection()
        if d.stage == 0: #then selectPoint1
            d.args = [x,y]
            debugPrint(2, 'point1 set to x=%3.1f y=%3.1f' % (x,y))
            d.stage = 1
            selectionOverlay.hideSelectionGraphicsItems(
                lambda gi: isinstance(gi,  selectionOverlay.LineSelectionGraphicsItem)
                )
        else:
            d.args = d.args + [x,y]
            debugPrint(2, 'point2 set to x=%3.1f y=%3.1f' % (x,y))
            d.stage = 2 
            d._dimScale = 1 / elementXML.rootNode().scaling() / UnitConversionFactor()
            selectionOverlay.hideSelectionGraphicsItems()
            previewDimension.initializePreview( d.drawingVars, linearDimension_half_preview, linearDimension_half_clickHandler, launchControlDialog=True )
    else:#then line
        if d.stage == 0: 
            x1,y1,x2,y2 = [ elementParms[k] for k in [ 'x1', 'y1', 'x2', 'y2' ] ]
            debugPrint(2,'selecting line x1=%3.1f y1=%3.1f, x2=%3.1f y2=%3.1f' % (x1,y1,x2,y2))
            d.args = [x1,y1, x2,y2]
            d.stage = 2 
            d._dimScale = 1 / elementXML.rootNode().scaling() / UnitConversionFactor()
            selectionOverlay.hideSelectionGraphicsItems()
            previewDimension.initializePreview( d.drawingVars, linearDimension_half_preview, linearDimension_half_clickHandler, launchControlDialog=True )


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

class HalfLinearDimension:
    "this class will create a line after the user clicked 2 points on the screen"
    def Activated(self):
        V = getDrawingPageGUIVars()
        d.activate( V, ['strokeWidth','arrowL1','arrowL2','arrowW','gap_datum_points', 'dimension_line_overshoot'], ['lineColor'], ['textRenderer'] )
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

FreeCADGui.addCommand('dd_halfLinearDimension', HalfLinearDimension())


