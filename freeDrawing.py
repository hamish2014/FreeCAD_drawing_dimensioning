from dimensioning import *
import previewDimension
import textAddDialog

dimensioning = DimensioningProcessTracker()

def lineSVG( x1, y1, x2, y2, svgTag='g', svgParms='', strokeWidth=0.5, lineColor='blue'):
    XML = '''<%s  %s >
  <line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:%s;stroke-width:%1.2f" />
</%s> ''' % ( svgTag, svgParms, x1, y1, x2, y2, lineColor, strokeWidth, svgTag )
    return XML

def line_ClickEvent( x, y):
    if dimensioning.stage == 0:
        dimensioning.x1 = x
        dimensioning.y1 = y
        dimensioning.stage = 1
        return None, None
    else: #dimensioning.stage == 1 :
        viewName = findUnusedObjectName('dimLine')
        XML =  lineSVG( dimensioning.x1, dimensioning.y1, 
                        x, y, **dimensioning.dimensionConstructorKWs ) 
        return viewName, XML

def line_hoverEvent( x, y):
    if dimensioning.stage == 1 :
        return lineSVG( dimensioning.x1, dimensioning.y1, 
                        x, y, **dimensioning.svg_preview_KWs ) 

class lineFreeDrawing:
    def Activated(self):
        V = getDrawingPageGUIVars()
        dimensioning.activate( V, ['strokeWidth'],['lineColor'] )
        previewDimension.initializePreview( 
            dimensioning.drawingVars, 
            line_ClickEvent, 
            line_hoverEvent,
            )
        
    def GetResources(self): 
        return {
            'Pixmap' : ':/dd/icons/drawLine.svg', 
            'MenuText': 'Draw a line' 
            } 
FreeCADGui.addCommand('DrawingDimensioning_drawLine', lineFreeDrawing())


from dimensionSvgConstructor import arrowHeadSVG, numpy, directionVector

def ArrowWithTail_SVG( c_x, c_y, radialLine_x=None, radialLine_y=None, tail_x=None, tail_y=None, arrowL1=3,arrowL2=1,arrowW=2, svgTag='g', svgParms='', strokeWidth=0.5,  lineColor='blue'):
    XML_body = []
    if radialLine_x <> None and radialLine_y <> None:
        XML_body.append( '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:%s;stroke-width:%1.2f" />' % (radialLine_x, radialLine_y, c_x, c_y, lineColor, strokeWidth) )
        d = directionVector(
            numpy.array([      c_x, c_y]),
            numpy.array([radialLine_x, radialLine_y]),
            )
        XML_body.append( arrowHeadSVG( numpy.array([c_x, c_y]), d, arrowL1, arrowL2, arrowW, lineColor ) )
    if tail_x <> None and tail_y <> None:
        XML_body.append( '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:%s;stroke-width:%1.2f" />' % (radialLine_x, radialLine_y, tail_x, radialLine_y, lineColor, strokeWidth) )
    return '''<%s  %s >
%s
</%s> ''' % ( svgTag, svgParms, "\n".join(XML_body), svgTag )

def ArrowWithTail_ClickEvent( x, y):
    dimensioning.dArgs = dimensioning.dArgs + [x,y]
    dimensioning.stage = dimensioning.stage + 1
    if dimensioning.stage == 3:
        viewName = findUnusedObjectName('dimLine')
        XML =  ArrowWithTail_SVG( 
            *dimensioning.dArgs,
             **dimensioning.dimensionConstructorKWs ) 
        return viewName, XML
    else:
        return None,None

def ArrowWithTail_hoverEvent( x, y):
    if dimensioning.stage > 0 :
        return ArrowWithTail_SVG( 
            *(dimensioning.dArgs + [x, y]), 
             **dimensioning.svg_preview_KWs 
             ) 

class ArrowWithTail_Drawing:
    def Activated(self):
        V = getDrawingPageGUIVars()
        dimensioning.activate( V, ['strokeWidth','arrowL1','arrowL2','arrowW'],['lineColor'] )
        dimensioning.dArgs = []
        previewDimension.initializePreview( 
            dimensioning.drawingVars, 
            ArrowWithTail_ClickEvent, 
            ArrowWithTail_hoverEvent,
            )
        
    def GetResources(self): 
        return {
            'Pixmap' : ':/dd/icons/drawLineWithArrow.svg', 
            'MenuText': 'Draw an arrow with a tail', 
            } 
FreeCADGui.addCommand('DrawingDimensioning_drawArrowWithTail', ArrowWithTail_Drawing())



