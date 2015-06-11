# This Python file uses the following encoding: utf-8

from dimensioning import *
import selectionOverlay, previewDimension
from dimensionSvgConstructor import *

d = DimensioningProcessTracker()

def circularDimensionSVG( center_x, center_y, radius, radialLine_x=None, radialLine_y=None, tail_x=None, tail_y=None, text_x=None, text_y=None, 
                          scale=1.0, textFormat_circular='Ø%3.3f', centerPointDia = 1, arrowL1=3, arrowL2=1, arrowW=2, strokeWidth=0.5, lineColor='blue', 
                          textRenderer=defaultTextRenderer):
    XML_body = [ ' <circle cx ="%f" cy ="%f" r="%f" stroke="none" fill="%s" /> ' % (center_x, center_y, centerPointDia*0.5, lineColor) ]
    #XML_body.append( '<circle cx="%f" cy="%f" r="%f" stroke="rgb(0,0,255)" stroke-width="%1.2f" fill="none" />' % (center_x, center_y, radius, strokeWidth) )
    if radialLine_x <> None and radialLine_y <> None:
        theta = numpy.arctan2( radialLine_y - center_y, radialLine_x - center_x )
        A = numpy.array([ center_x + radius*numpy.cos(theta) , center_y + radius*numpy.sin(theta) ])
        B = numpy.array([ center_x - radius*numpy.cos(theta) , center_y - radius*numpy.sin(theta) ])
        XML_body.append( svgLine(radialLine_x, radialLine_y, B[0], B[1], lineColor, strokeWidth) )
        if radius > 0:
            s = 1 if radius > arrowL1 + arrowL2 + 0.5*centerPointDia else -1
            XML_body.append( arrowHeadSVG( A, s*directionVector(A,B), arrowL1, arrowL2, arrowW, lineColor ) )
            XML_body.append( arrowHeadSVG( B, s*directionVector(B,A), arrowL1, arrowL2, arrowW, lineColor ) )
        if tail_x <> None and tail_y <> None:
            XML_body.append( svgLine( radialLine_x, radialLine_y, tail_x, radialLine_y, lineColor, strokeWidth ) )
    if text_x <> None and text_y <> None:
        XML_body.append( textRenderer( text_x, text_y, dimensionText(2*radius*scale,textFormat_circular) ))
    return '<g> %s </g>' % "\n".join(XML_body)

d.dialogWidgets.append( unitSelectionWidget )
d.registerPreference( 'textFormat_circular', 'Ø%3.3f', 'format mask')
d.registerPreference( 'centerPointDia', 0.5, increment=0.5)
d.registerPreference( 'arrowL1')
d.registerPreference( 'arrowL2')
d.registerPreference( 'arrowW')
d.registerPreference( 'strokeWidth')
d.registerPreference( 'lineColor')
d.registerPreference( 'textRenderer' )

def circularDimensionSVG_preview(mouseX, mouseY):
    args = d.args + [ mouseX, mouseY ] if len(d.args) < 9 else d.args
    return circularDimensionSVG( *args, scale=d.viewScale*d.unitConversionFactor, **d.dimensionConstructorKWs )

def circularDimensionSVG_clickHandler( x, y ):
    d.args = d.args + [ x, y ]
    d.stage = d.stage + 1
    if d.stage == 4 :
        return 'createDimension:%s' % findUnusedObjectName('dim')


def selectFun(  event, referer, elementXML, elementParms, elementViewObject ):
    x,y = elementParms['x'], elementParms['y']
    debugPrint(2, 'center selected at x=%3.1f y=%3.1f' % (x,y))
    d.args = [x, y, elementParms['r']]
    d.viewScale = 1/elementXML.rootNode().scaling()
    d.stage = 1
    selectionOverlay.hideSelectionGraphicsItems()
    previewDimension.initializePreview( d, circularDimensionSVG_preview, circularDimensionSVG_clickHandler )

maskPen =      QtGui.QPen( QtGui.QColor(0,255,0,100) )
maskPen.setWidth(2.0)
maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) )
maskHoverPen.setWidth(2.0)

class CircularDimension:
    def Activated(self):
        V = getDrawingPageGUIVars()
        d.activate(V, dialogTitle='Add Circular Dimension', dialogIconPath=os.path.join( iconPath , 'circularDimension.svg' ), endFunction=self.Activated  )
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
            'Pixmap' : os.path.join( iconPath , 'circularDimension.svg' ) , 
            'MenuText': 'Circular Dimension', 
            'ToolTip': 'Creates a circular dimension'
            } 

FreeCADGui.addCommand('dd_circularDimension', CircularDimension())
