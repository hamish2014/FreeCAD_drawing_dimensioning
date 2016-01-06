# This Python file uses the following encoding: utf-8

from dimensioning import *
import selectionOverlay, previewDimension
from dimensionSvgConstructor import *

d = DimensioningProcessTracker()

def circularDimensionSVG( center_x, center_y, radius, radialLine_x=None, radialLine_y=None, tail_x=None, tail_y=None, text_x=None, text_y=None, autoPlaceText=False, autoPlaceOffset=2.0,
                          scale=1.0, textFormat_circular='Ø%3.3f', comma_decimal_place=False,
                          centerPointDia = 1, arrowL1=3, arrowL2=1, arrowW=2, strokeWidth=0.5, lineColor='blue', arrow_scheme='auto',
                          textRenderer=defaultTextRenderer):
    XML_body = [ ' <circle cx ="%f" cy ="%f" r="%f" stroke="none" fill="%s" /> ' % (center_x, center_y, centerPointDia*0.5, lineColor) ]
    #XML_body.append( '<circle cx="%f" cy="%f" r="%f" stroke="rgb(0,0,255)" stroke-width="%1.2f" fill="none" />' % (center_x, center_y, radius, strokeWidth) )
    if radialLine_x <> None and radialLine_y <> None:
        theta = numpy.arctan2( radialLine_y - center_y, radialLine_x - center_x )
        A = numpy.array([ center_x + radius*numpy.cos(theta) , center_y + radius*numpy.sin(theta) ])
        B = numpy.array([ center_x - radius*numpy.cos(theta) , center_y - radius*numpy.sin(theta) ])
        XML_body.append( svgLine(radialLine_x, radialLine_y, B[0], B[1], lineColor, strokeWidth) )
        if radius > 0:
            if arrow_scheme <> 'off':
                if arrow_scheme == 'auto':
                    s = 1 if radius > arrowL1 + arrowL2 + 0.5*centerPointDia else -1
                elif arrow_scheme == 'in':
                    s = 1
                elif arrow_scheme == 'out':
                    s = -1
                XML_body.append( arrowHeadSVG( A, s*directionVector(A,B), arrowL1, arrowL2, arrowW, lineColor ) )
                XML_body.append( arrowHeadSVG( B, s*directionVector(B,A), arrowL1, arrowL2, arrowW, lineColor ) )
        if tail_x <> None and tail_y <> None:
            XML_body.append( svgLine( radialLine_x, radialLine_y, tail_x, radialLine_y, lineColor, strokeWidth ) )
            text = dimensionText(2*radius*scale,textFormat_circular, comma=comma_decimal_place)
            XML_body.append( textPlacement_common_procedure(numpy.array([radialLine_x, radialLine_y]), numpy.array([tail_x, radialLine_y]), text, text_x, text_y, 0, textRenderer, autoPlaceText, autoPlaceOffset) )
    return '<g> %s </g>' % "\n".join(XML_body)

d.dialogWidgets.append( unitSelectionWidget )
d.registerPreference( 'textFormat_circular', 'Ø%(value)3.3f', 'format mask')
d.registerPreference( 'arrow_scheme')
d.registerPreference( 'autoPlaceText')
d.registerPreference( 'comma_decimal_place')
d.registerPreference( 'centerPointDia', 0.5, increment=0.5)
d.registerPreference( 'arrowL1')
d.registerPreference( 'arrowL2')
d.registerPreference( 'arrowW')
d.registerPreference( 'strokeWidth')
d.registerPreference( 'lineColor')
d.registerPreference( 'textRenderer' )
d.registerPreference( 'autoPlaceOffset')
d.max_selections = 4


def circularDimensionSVG_preview(mouseX, mouseY):
    selections = d.selections + [ PlacementClick( mouseX, mouseY ) ] if len(d.selections) < d.max_selections else d.selections
    return circularDimensionSVG( *selections_to_svg_fun_args(selections), scale=d.viewScale*d.unitConversionFactor, **d.dimensionConstructorKWs )

def circularDimensionSVG_clickHandler( x, y ):
    d.selections.append( PlacementClick( x, y ) )
    if len(d.selections) == d.max_selections - 1 and d.dimensionConstructorKWs['autoPlaceText']:
        d.selections.append( PlacementClick( x, y ) ) # to avoid crash when auto place turned off
        return 'createDimension:%s' % findUnusedObjectName('dia')
    elif len(d.selections) == d.max_selections :
        return 'createDimension:%s' % findUnusedObjectName('dia')

def selectFun(  event, referer, elementXML, elementParms, elementViewObject ):
    viewInfo = selectionOverlay.DrawingsViews_info[elementViewObject.Name]
    d.viewScale = 1/elementXML.rootNode().scaling()
    d.selections.append( CircularArcSelection( elementParms, elementXML, viewInfo ) )
    selectionOverlay.hideSelectionGraphicsItems()
    previewDimension.initializePreview( d, circularDimensionSVG_preview, circularDimensionSVG_clickHandler )

class Proxy_CircularDimension( Proxy_DimensionObject_prototype ):
     def dimensionProcess( self ):
         return d
d.ProxyClass = Proxy_CircularDimension
d.proxy_svgFun = circularDimensionSVG



maskPen =      QtGui.QPen( QtGui.QColor(0,255,0,100) )
maskPen.setWidth(2.0)
maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) )
maskHoverPen.setWidth(2.0)


class CircularDimension:
    def Activated(self):
        V = getDrawingPageGUIVars()
        d.activate(V, dialogTitle='Add Circular Dimension', dialogIconPath=':/dd/icons/circularDimension.svg', endFunction=self.Activated  )
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
            'Pixmap' : ':/dd/icons/circularDimension.svg' , 
            'MenuText': 'Circular Dimension', 
            'ToolTip': 'Creates a circular dimension'
            } 

FreeCADGui.addCommand('dd_circularDimension', CircularDimension())
