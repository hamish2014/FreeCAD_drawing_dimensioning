# This Python file uses the following encoding: utf-8

from dimensioning import *
from dimensioning import iconPath # not imported with * directive
import previewDimension, selectionOverlay 
from dimensionSvgConstructor import arrowHeadSVG, numpy, directionVector

dimensioning = DimensioningProcessTracker()
maskBrush  =   QtGui.QBrush( QtGui.QColor(0,160,0,100) )
maskPen =      QtGui.QPen( QtGui.QColor(0,160,0,100) )
maskPen.setWidth(0.0)
maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) )
maskHoverPen.setWidth(0.0)

class BendingNoteCommand:
    def Activated(self):
        V = getDrawingPageGUIVars()
        dimensioning.activate(V, ['strokeWidth','arrowL1','arrowL2','arrowW'], ['lineColor'], ['textRenderer'] )
        selectionOverlay.generateSelectionGraphicsItems( 
            [obj for obj in V.page.Group  if not obj.Name.startswith('dim') and not obj.Name.startswith('center')], 
            self.selectFun ,
            transform = V.transform,
            sceneToAddTo = V.graphicsScene, 
            doPoints=True, doMidPoints=True,
            pointWid=1.0,
            maskPen=maskPen, 
            maskHoverPen=maskHoverPen, 
            maskBrush = maskBrush #clear
            )
        selectionOverlay.addProxyRectToRescaleGraphicsSelectionItems( V.graphicsScene, V.graphicsView, V.width, V.height)

    def selectFun(self, event, referer, elementXML, elementParms, elementViewObject ):
        x,y = elementParms['x'], elementParms['y']
        dimensioning.dArgs = [x,y]
        dimensioning.stage = 1
        debugPrint(2, 'welding symbol to point at x=%3.1f y=%3.1f' % (x,y))
        selectionOverlay.hideSelectionGraphicsItems()
        previewDimension.initializePreview( 
            dimensioning.drawingVars, 
            self.clickFunPreview, 
            self.hoverFunPreview )

    noOfStages = 3
    def clickFunPreview( self, x, y ):
        dimensioning.dArgs = dimensioning.dArgs + [x,y]
        dimensioning.stage = dimensioning.stage + 1
        if dimensioning.stage == self.noOfStages:
            viewName = findUnusedObjectName('dimLine')
            XML =  self.generateSvg( 
                *dimensioning.dArgs,
                 **dimensioning.dimensionConstructorKWs ) 
            return viewName, XML
        else:
            return None,None

    def hoverFunPreview(self,  x, y):
        return self.generateSvg( 
            *(dimensioning.dArgs + [x, y]), 
             **dimensioning.svg_preview_KWs 
             )

    def svgLine(self, x1, y1, x2, y2, clr=None):
        return '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:%s;stroke-width:%1.2f" />' % (x1, y1, x2, y2, self.svg_lineColor if clr==None else clr, self.svg_strokeWidth ) 

    def svgCircularArc(self, cx, cy, r, dStart, dEnd): #with d denoting degrees
        largeArc = abs(dEnd - dStart) >= 180
        sweep = dEnd > dStart
        theta1 = dStart * numpy.pi/180
        theta2 = dEnd   * numpy.pi/180
        x1 = cx + r * numpy.cos(theta1)
        y1 = cy + r * numpy.sin(theta1)
        x2 = cx + r * numpy.cos(theta2)
        y2 = cy + r * numpy.sin(theta2)
        return '<path d = "M %f %f A %f %f 0 %i %i %f %f" style="stroke:%s;stroke-width:%1.2f;fill:none" />' % (x1,y1,r,r,largeArc,sweep, x2,y2, self.svg_lineColor, self.svg_strokeWidth ) 

    def generateSvg(self,  c_x, c_y, radialLine_x=None, radialLine_y=None, tail_x=None, tail_y=None, 
                    arrowL1=3,arrowL2=1,arrowW=2, svgTag='g', svgParms='', strokeWidth=0.5,  lineColor='blue', textRenderer=None):
        self.svg_lineColor = lineColor
        self.svg_strokeWidth = strokeWidth
        XML_body = []
        if radialLine_x <> None and radialLine_y <> None:
            XML_body.append( self.svgLine(radialLine_x, radialLine_y, c_x, c_y) )
            d = directionVector(
                numpy.array([      c_x, c_y]),
                numpy.array([radialLine_x, radialLine_y]),
                )
            XML_body.append( arrowHeadSVG( numpy.array([c_x, c_y]), d, arrowL1, arrowL2, arrowW, lineColor ) )
            if tail_x <> None and tail_y <> None:
                XML_body.append(  self.svgLine( radialLine_x, radialLine_y, tail_x, radialLine_y) )
                #getting scale factor
                svgText = SvgTextParser( textRenderer(0,0,"0") )
                f = svgText.width()
                box_w = f * 1.6
                rect_w = f * 3
                x, y = tail_x, radialLine_y-box_w/2
                #rects
                XML_body.append(  self.svgLine( x,         y, x        , y+box_w)  )
                XML_body.append(  self.svgLine( x + box_w, y, x + box_w, y+box_w)  )
                xe = x + box_w + rect_w
                XML_body.append(  self.svgLine( x,         y, xe, y)  )
                XML_body.append(  self.svgLine( x,         y+box_w, xe, y+box_w)  )
                XML_body.append(  self.svgLine( xe,        y, xe, y+box_w)  )
                #bend symbol
                XML_body.append(  self.svgLine( x + 0.2*box_w, y + 0.8*box_w, x + 0.8*box_w , y + 0.8*box_w,  textRenderer.fill)  )
                XML_body.append(  self.svgLine( x + 0.2*box_w, y + 0.8*box_w, x + 0.8*box_w , y + 0.2*box_w,  textRenderer.fill)  )
                #text
                XML_body.append( textRenderer(x + box_w*1.2, y+box_w*0.8, "90°") )


        return '''<%s  %s >
%s
</%s> ''' % ( svgTag, svgParms, "\n".join(XML_body), svgTag )

    def GetResources(self): 
        return {
            #'Pixmap' : os.path.join( iconPath , 'drawLineWithArrow.svg' ) , 
            'Pixmap' : os.path.join( iconPath, 'bendingNote.svg'),
            'MenuText': 'bending note', 
            } 


FreeCADGui.addCommand('drawingDimensioning_bendingNote', BendingNoteCommand())
