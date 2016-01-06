
from dimensioning import *
import previewDimension, selectionOverlay 
from dimensionSvgConstructor import arrowHeadSVG, numpy, directionVector

d = DimensioningProcessTracker()
d.registerPreference( 'arrowL1')
d.registerPreference( 'arrowL2')
d.registerPreference( 'arrowW')
d.registerPreference( 'strokeWidth' )
d.registerPreference( 'lineColor' )
d.registerPreference( 'textRenderer' )

class Proxy_weldingSymbol( Proxy_DimensionObject_prototype ):
     def dimensionProcess( self ):
         return d
d.ProxyClass =  Proxy_weldingSymbol
class Command_svg_fun_wrapper: #to make instance method pickalble!
    def __init__(self, command ):
        self.command = command
    def __call__(self, *args, **KWS):
        return self.command.generateSvg( *args, **KWS)

maskBrush  =   QtGui.QBrush( QtGui.QColor(0,160,0,100) )
maskPen =      QtGui.QPen( QtGui.QColor(0,160,0,100) )
maskPen.setWidth(0.0)
maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) )
maskHoverPen.setWidth(0.0)
weldingCmds = []

class WeldingSymbol_prototype:
    def Activated(self):
        V = getDrawingPageGUIVars()
        d.activate(V, dialogTitle='Add Welding Note', dialogIconPath=self.generateIcon(), endFunction=self.Activated )
        d.proxy_svgFun = Command_svg_fun_wrapper(self)
        from grabPointAdd import  Proxy_grabPoint
        selectionOverlay.generateSelectionGraphicsItems( 
            dimensionableObjects( V.page ) + [obj for obj in V.page.Group if hasattr(obj,'Proxy') and isinstance( obj.Proxy, Proxy_grabPoint) ],
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
        viewInfo = selectionOverlay.DrawingsViews_info[elementViewObject.Name]
        d.selections = [ PointSelection( elementParms, elementXML, viewInfo) ]
        selectionOverlay.hideSelectionGraphicsItems()
        previewDimension.initializePreview( 
            d, 
            self.preview_svgRenderer, 
            self.preview_clickHandler )

    noSelections = 4
    def preview_clickHandler( self, x, y ):
        d.selections.append( PlacementClick( x, y) )
        if len(d.selections) == self.noSelections:
            return 'createDimension:%s' % findUnusedObjectName('weld')

    def preview_svgRenderer(self,  x, y):
        s =  d.selections + [ PlacementClick( x, y) ] if len(d.selections) < self.noSelections else d.selections
        return self.generateSvg( 
            *selections_to_svg_fun_args(s),  
             **d.dimensionConstructorKWs 
             )

    def getScaleFactor( self, textRenderer):
        xml = textRenderer(0,0,"Q")
        svgText = SvgTextParser( xml )
        return svgText.width()*2

    def svgLine(self, x1, y1, x2, y2):
        return '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:%s;stroke-width:%1.2f" />' % (x1, y1, x2, y2, self.svg_lineColor, self.svg_strokeWidth ) 

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

    def generateSvg(self,  c_x, c_y, radialLine_x=None, radialLine_y=None, tail_x=None, tail_y=None, weldingMarker_x=None, weldingMarker_y=None, 
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
                if weldingMarker_x <> None:
                    self.radialLine_x = radialLine_x #storing values incase self.weldingMarkerSvg needs them
                    self.radialLine_y = radialLine_y 
                    self.tail_x = tail_x 
                    self.tail_y = tail_y
                    XML_body.append( self.weldingMarkerSvg( weldingMarker_x, radialLine_y, lineColor, strokeWidth, textRenderer) )
        return '''<%s  %s >
%s
</%s> ''' % ( svgTag, svgParms, "\n".join(XML_body), svgTag )

    def generateIcon(self):
        fn = os.path.join( iconPath, 'welding', self.label.replace(' ','_')) + '.svg'
        if not os.path.exists(fn):
            svgParameters = ' xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:cc="http://creativecommons.org/ns#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg" xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" width="48px" height="48px" version="1.1" '
            xml =  self.generateSvg(
                c_x=-10, c_y=58, radialLine_x=0, radialLine_y=36, tail_x=48, tail_y=36, weldingMarker_x=24, weldingMarker_y=36, 
                arrowL1=12,arrowL2=6,arrowW=8, svgTag='svg', svgParms=svgParameters, strokeWidth=2,  lineColor='blue', 
                textRenderer=SvgTextRenderer( font_size='24px' )
            )
            f = open(fn,'w')
            f.write(xml)
            f.close()
        return ':/dd/icons/welding/' + self.label.replace(' ','_') + '.svg'
        
    def GetResources(self): 
        return {
            'Pixmap' : self.generateIcon(),
            'MenuText': 'symbol - %s' % self.label, 
            } 

def addWeldingCommand( WeldingClass ):
    name ='DrawingDimensioning_weldingSymbol%02i' % (len(weldingCmds))
    FreeCADGui.addCommand(name, WeldingClass())
    weldingCmds.append(name)

class WeldingGroupCommand: #for FreeCAD version 0.16 onwards
    def GetCommands(self):
        return tuple(weldingCmds) # a tuple of command names that you want to group
    #def GetDefaultCommand(self): # return the index of the tuple of the default command. This method is optional and when not implemented '0' is used 
    #    return 2
    def GetResources(self):
        return { 'MenuText': 'Welding/Grove Symbols command', 'ToolTip': 'Welding/Grove Symbols commands'}
FreeCADGui.addCommand('dd_weldingGroupCommand', WeldingGroupCommand())
    

class WeldingSymbol0(WeldingSymbol_prototype):
    label='no grove symbol'
    noSelections = 3
    def generateIcon(self):
        return ':/dd/icons/welding/plain.svg'
addWeldingCommand( WeldingSymbol0 )

class WeldingSymbol1(WeldingSymbol_prototype):
    label='square groove'
    def weldingMarkerSvg(self, x, y, lineColor, strokeWidth, textRenderer):
        XML = []
        f = self.getScaleFactor(textRenderer)
        XML.append( self.svgLine( x - 0.15*f, y, x - 0.15*f, y - f) )
        XML.append( self.svgLine( x + 0.15*f, y, x + 0.15*f, y - f) )
        return '\n'.join(XML)
addWeldingCommand( WeldingSymbol1 )


class WeldingSymbol2(WeldingSymbol_prototype):
    label='flange edge'
    def weldingMarkerSvg(self, x, y, lineColor, strokeWidth, textRenderer):
        XML = []
        f = self.getScaleFactor(textRenderer)
        r = f*0.7
        XML.append( self.svgCircularArc( x - r - 0.15*f, y - r, r, 0, 90) )
        XML.append( self.svgCircularArc( x + r + 0.15*f, y - r, r, 90, 180) )
        return '\n'.join(XML)
addWeldingCommand( WeldingSymbol2 )

class WeldingSymbol3(WeldingSymbol_prototype):
    label='double square groove'
    def weldingMarkerSvg(self, x, y, lineColor, strokeWidth, textRenderer):
        XML = []
        f = self.getScaleFactor(textRenderer)
        XML.append( self.svgLine( x - 0.15*f, y + f, x - 0.15*f, y - f) )
        XML.append( self.svgLine( x + 0.15*f, y + f, x + 0.15*f, y - f) )
        return '\n'.join(XML)
addWeldingCommand( WeldingSymbol3 )

class WeldingSymbol4(WeldingSymbol_prototype):
    label='V groove'
    def weldingMarkerSvg(self, x, y, lineColor, strokeWidth, textRenderer):
        XML = []
        f = self.getScaleFactor(textRenderer)
        XML.append( self.svgLine( x , y , x - 0.5*f, y - f) )
        XML.append( self.svgLine( x , y , x + 0.5*f, y - f) )
        return '\n'.join(XML)
addWeldingCommand( WeldingSymbol4 )

class WeldingSymbol5(WeldingSymbol_prototype):
    label='VU groove'
    def weldingMarkerSvg(self, x, y, lineColor, strokeWidth, textRenderer):
        XML = []
        f = self.getScaleFactor(textRenderer)
        XML.append( self.svgLine( x , y , x - 0.5*f, y - f) )
        XML.append( self.svgLine( x , y , x + 0.5*f, y - f) )
        XML.append( self.svgLine( x , y + 0.1*f , x , y + 0.4*f) )
        r = 0.5*f
        XML.append( self.svgCircularArc( x , y + 0.9*f, r, 180, 360) )
        return '\n'.join(XML)
addWeldingCommand( WeldingSymbol5 )

class WeldingSymbol6(WeldingSymbol_prototype):
    label='Double V groove'
    def weldingMarkerSvg(self, x, y, lineColor, strokeWidth, textRenderer):
        XML = []
        f = self.getScaleFactor(textRenderer)
        XML.append( self.svgLine( x + 0.5*f , y +f , x - 0.5*f, y - f) )
        XML.append( self.svgLine( x - 0.5*f, y +f , x + 0.5*f, y - f) )
        return '\n'.join(XML)
addWeldingCommand( WeldingSymbol6 )

class WeldingSymbol7(WeldingSymbol_prototype):
    label='Bevel groove'
    def weldingMarkerSvg(self, x, y, lineColor, strokeWidth, textRenderer):
        XML = []
        f = self.getScaleFactor(textRenderer)
        XML.append( self.svgLine( x , y , x    , y - f) )
        XML.append( self.svgLine( x , y , x + f, y - f) )
        return '\n'.join(XML)
addWeldingCommand( WeldingSymbol7 )

class WeldingSymbol8(WeldingSymbol_prototype):
    label='Double bevel groove'
    def weldingMarkerSvg(self, x, y, lineColor, strokeWidth, textRenderer):
        XML = []
        f = self.getScaleFactor(textRenderer)
        XML.append( self.svgLine( x , y +f , x    , y - f) )
        XML.append( self.svgLine( x , y , x + f, y - f) )
        XML.append( self.svgLine( x , y , x + f, y + f) )
        return '\n'.join(XML)
addWeldingCommand( WeldingSymbol8 )

class WeldingSymbol9(WeldingSymbol_prototype):
    label='Y groove'
    def weldingMarkerSvg(self, x, y, lineColor, strokeWidth, textRenderer):
        XML = []
        f = self.getScaleFactor(textRenderer)
        XML.append( self.svgLine( x , y , x    , y - 0.5*f) )
        XML.append( self.svgLine( x , y  - 0.5*f,  x + 0.25*f, y - f) )
        XML.append( self.svgLine( x , y  - 0.5*f , x - 0.25*f, y - f) )
        return '\n'.join(XML)
addWeldingCommand( WeldingSymbol9 )
class WeldingSymbol10(WeldingSymbol_prototype):
    label='Double Y groove'
    def weldingMarkerSvg(self, x, y, lineColor, strokeWidth, textRenderer):
        XML = []
        f = self.getScaleFactor(textRenderer)
        XML.append( self.svgLine( x , y  + 0.5*f , x    , y - 0.5*f) )
        XML.append( self.svgLine( x , y  - 0.5*f,  x + 0.25*f, y - f) )
        XML.append( self.svgLine( x , y  - 0.5*f , x - 0.25*f, y - f) )
        XML.append( self.svgLine( x , y  + 0.5*f,  x + 0.25*f, y + f) )
        XML.append( self.svgLine( x , y  + 0.5*f , x - 0.25*f, y + f) )
        return '\n'.join(XML)
addWeldingCommand( WeldingSymbol10 )

class WeldingSymbol11(WeldingSymbol_prototype):
    label='J groove'
    def weldingMarkerSvg(self, x, y, lineColor, strokeWidth, textRenderer):
        XML = []
        f = self.getScaleFactor(textRenderer)
        XML.append( self.svgLine( x , y , x    , y - f) )
        XML.append( self.svgLine( x , y  - 0.5*f,  x + 0.5*f, y - f) )
        return '\n'.join(XML)
addWeldingCommand( WeldingSymbol11 )
class WeldingSymbol12(WeldingSymbol_prototype):
    label='Double J groove'
    def weldingMarkerSvg(self, x, y, lineColor, strokeWidth, textRenderer):
        XML = []
        f = self.getScaleFactor(textRenderer)
        XML.append( self.svgLine( x , y + f , x    , y - f) )
        XML.append( self.svgLine( x , y  - 0.5*f,  x + 0.5*f, y - f) )
        XML.append( self.svgLine( x , y  + 0.5*f,  x + 0.5*f, y + f) )
        return '\n'.join(XML)
addWeldingCommand( WeldingSymbol12 )

class WeldingSymbol13(WeldingSymbol_prototype):
    label='U groove'
    def weldingMarkerSvg(self, x, y, lineColor, strokeWidth, textRenderer):
        XML = []
        f = self.getScaleFactor(textRenderer)
        XML.append( self.svgLine( x , y , x    , y - 0.5*f) )
        r = 0.5*f
        XML.append( self.svgCircularArc( x , y  - f,  r, 0, 180) )
        return '\n'.join(XML)
addWeldingCommand( WeldingSymbol13 )
class WeldingSymbol16(WeldingSymbol_prototype):
    label='Double U groove'
    def weldingMarkerSvg(self, x, y, lineColor, strokeWidth, textRenderer):
        XML = []
        f = self.getScaleFactor(textRenderer)
        XML.append( self.svgLine( x , y+0.5*f , x, y-0.5*f) )
        r = 0.5*f
        XML.append( self.svgCircularArc( x , y - f,  r, 0, 180) )
        XML.append( self.svgCircularArc( x , y + f,  r, 180, 360) )
        return '\n'.join(XML)
addWeldingCommand( WeldingSymbol16 )

class WeldingSymbol15(WeldingSymbol_prototype):
    label='J groove (alt)'
    def weldingMarkerSvg(self, x, y, lineColor, strokeWidth, textRenderer):
        XML = []
        f = self.getScaleFactor(textRenderer)
        XML.append( self.svgLine( x , y , x    , y - f) )
        r = 0.5*f
        XML.append( self.svgCircularArc( x , y  - f,  r, 0, 90) )
        return '\n'.join(XML)
addWeldingCommand( WeldingSymbol15 )
class WeldingSymbol16(WeldingSymbol_prototype):
    label='Double J groove (alt)'
    def weldingMarkerSvg(self, x, y, lineColor, strokeWidth, textRenderer):
        XML = []
        f = self.getScaleFactor(textRenderer)
        XML.append( self.svgLine( x , y+f , x    , y - f) )
        r = 0.5*f
        XML.append( self.svgCircularArc( x , y  - f,  r, 0, 90) )
        XML.append( self.svgCircularArc( x , y  + f,  r, 270, 360) )
        return '\n'.join(XML)
addWeldingCommand( WeldingSymbol16 )

class WeldingSymbol17(WeldingSymbol_prototype):
    label='fillet'
    def weldingMarkerSvg(self, x, y, lineColor, strokeWidth, textRenderer):
        XML = []
        f = self.getScaleFactor(textRenderer)
        XML.append( self.svgLine( x , y , x , y - 0.8*f) )
        XML.append( self.svgLine( x, y - 0.8*f , x+0.8*f , y) )
        return '\n'.join(XML)
addWeldingCommand( WeldingSymbol17 )

class WeldingSymbol18(WeldingSymbol_prototype):
    label='double fillet'
    def weldingMarkerSvg(self, x, y, lineColor, strokeWidth, textRenderer):
        XML = []
        f = self.getScaleFactor(textRenderer)
        XML.append( self.svgLine( x , y + 0.8*f , x , y - 0.8*f) )
        XML.append( self.svgLine( x, y - 0.8*f , x+0.8*f , y) )
        XML.append( self.svgLine( x+0.8*f , y,  x , y + 0.8*f) )
        return '\n'.join(XML)
addWeldingCommand( WeldingSymbol18 )

class WeldingSymbol19(WeldingSymbol_prototype):
    label='Plug or slot'
    def weldingMarkerSvg(self, x, y, lineColor, strokeWidth, textRenderer):
        XML = []
        f = self.getScaleFactor(textRenderer)
        XML.append( self.svgLine( x -0.5*f ,         y , x -0.5*f , y- 0.5*f) )
        XML.append( self.svgLine( x -0.5*f,  y - 0.5*f , x +0.5*f , y- 0.5*f) )
        XML.append( self.svgLine( x +0.5*f , y - 0.5*f , x +0.5*f , y))
        return '\n'.join(XML)
addWeldingCommand( WeldingSymbol19 )

class WeldingSymbol20(WeldingSymbol_prototype):
    label='Spot or projection'
    def weldingMarkerSvg(self, x, y, lineColor, strokeWidth, textRenderer):
        XML = []
        f = self.getScaleFactor(textRenderer)
        XML.append( self.svgCircularArc( x , y ,  0.5*f, 0, 180) )
        XML.append( self.svgCircularArc( x , y ,  0.5*f, 180, 360) )
        return '\n'.join(XML)
addWeldingCommand( WeldingSymbol20 )

class WeldingSymbol21(WeldingSymbol_prototype):
    label='Seam'
    def weldingMarkerSvg(self, x, y, lineColor, strokeWidth, textRenderer):
        XML = []
        f = self.getScaleFactor(textRenderer)
        r = 0.5*f
        XML.append( self.svgCircularArc( x, y,  r,   0, 180) )
        XML.append( self.svgCircularArc( x, y,  r, 180, 360) )
        z = 0.14*f
        XML.append( self.svgLine( x - 1.2*r , y - z , x + 1.2*r , y - z ))
        XML.append( self.svgLine( x - 1.2*r , y + z , x + 1.2*r , y + z ))
        return '\n'.join(XML)
addWeldingCommand( WeldingSymbol21 )

class WeldingSymbol22(WeldingSymbol_prototype):
    label='Steilflankennaht'
    def weldingMarkerSvg(self, x, y, lineColor, strokeWidth, textRenderer):
        XML = []
        f = self.getScaleFactor(textRenderer)
        z = 0.1*f
        XML.append( self.svgLine( x - 0.2*f, y , x - 0.2*f -z, y - f) )
        XML.append( self.svgLine( x + 0.2*f, y , x + 0.2*f +z, y - f) )
        return '\n'.join(XML)
addWeldingCommand( WeldingSymbol22 )

class WeldingSymbol23(WeldingSymbol_prototype):
    label='Stirnflachnaht'
    def weldingMarkerSvg(self, x, y, lineColor, strokeWidth, textRenderer):
        XML = []
        f = self.getScaleFactor(textRenderer)
        z = 0.1*f
        XML.append( self.svgLine( x - 0.15*f, y, x - 0.15*f, y - f) )
        XML.append( self.svgLine( x + 0.15*f, y, x + 0.15*f, y - f) )
        XML.append( self.svgLine(          x, y,          x, y - f) )
        return '\n'.join(XML)
addWeldingCommand( WeldingSymbol23 )

class WeldingSymbol24(WeldingSymbol_prototype):
    label='Flachennaht'
    def weldingMarkerSvg(self, x, y, lineColor, strokeWidth, textRenderer):
        XML = []
        f = self.getScaleFactor(textRenderer)
        w = 0.45*f
        z1 = 0.2*f
        z2 = 0.5*f
        XML.append( self.svgLine( x - w, y - z1, x + w, y - z1) )
        XML.append( self.svgLine( x - w, y - z2, x + w, y - z2) )
        return '\n'.join(XML)
addWeldingCommand( WeldingSymbol24 )

class WeldingSymbol25(WeldingSymbol_prototype):
    label='Schragnaht'
    def weldingMarkerSvg(self, x, y, lineColor, strokeWidth, textRenderer):
        XML = []
        f = self.getScaleFactor(textRenderer)
        w = 0.45*f
        z1 = 0.25*f
        z2 = 0.50*f
        XML.append( self.svgLine( x - w, y , x + w, y - z1) )
        XML.append( self.svgLine( x - w, y - z1, x + w, y - z2) )
        return '\n'.join(XML)
addWeldingCommand( WeldingSymbol25 )


class WeldingSymbol26(WeldingSymbol_prototype):
    label='Falznnaht'
    def weldingMarkerSvg(self, x, y, lineColor, strokeWidth, textRenderer):
        XML = []
        f = self.getScaleFactor(textRenderer)
        z = 0.3*f
        w = 0.3*f
        XML.append( self.svgCircularArc( x , y-z ,  z, 90, 270) )
        XML.append( self.svgLine( x , y - 2*z, x + w, y - 2*z) )
        XML.append( self.svgCircularArc( x+w , y-2*z ,  z, 270, 360) )
        XML.append( self.svgCircularArc( x+w , y-2*z ,  z,   0, 90) )
        XML.append( self.svgLine( x , y - 1*z, x + w, y - 1*z) )
        XML.append( self.svgLine( x , y - 3*z, x + w, y - 3*z) )
        return '\n'.join(XML)
addWeldingCommand( WeldingSymbol26 )

class WeldingSymbol27(WeldingSymbol_prototype):
    label='Surfacing'
    def weldingMarkerSvg(self, x, y, lineColor, strokeWidth, textRenderer):
        XML = []
        f = self.getScaleFactor(textRenderer)
        r = 0.3*f
        XML.append( self.svgCircularArc( x - r , y ,  r, 180, 360) )
        XML.append( self.svgCircularArc( x + r , y ,  r, 180, 360) )
        return '\n'.join(XML)
addWeldingCommand( WeldingSymbol27 )

class WeldingSymbol28(WeldingSymbol_prototype):
    label='fillet with circle'
    def weldingMarkerSvg(self, x, y, lineColor, strokeWidth, textRenderer):
        XML = []
        f = self.getScaleFactor(textRenderer)
        XML.append( self.svgLine( x , y , x , y - 0.8*f) )
        XML.append( self.svgLine( x, y - 0.8*f , x+0.8*f , y) )
        r = 0.18*f
        XML.append( self.svgCircularArc( self.radialLine_x, self.radialLine_y, r,   0, 180 ) )
        XML.append( self.svgCircularArc( self.radialLine_x, self.radialLine_y, r, 180, 360 ) )
        return '\n'.join(XML)
addWeldingCommand( WeldingSymbol28 )

class WeldingSymbol29(WeldingSymbol_prototype):
    label='fillet with dashed line'
    def weldingMarkerSvg(self, x, y, lineColor, strokeWidth, textRenderer):
        XML = []
        f = self.getScaleFactor(textRenderer)
        XML.append( self.svgLine( x , y , x , y - 0.8*f) )
        XML.append( self.svgLine( x, y - 0.8*f , x+0.8*f , y) )
        gap_length = 0.2*f
        dash_length = 0.6*f
        x_start = min(self.tail_x, self.radialLine_x)
        x_end   = max(self.tail_x, self.radialLine_x)
        pen_x = x_start + gap_length
        pen_y = y - 0.18*f
        while pen_x + dash_length < x_end:
            XML.append( self.svgLine( pen_x , pen_y , pen_x + dash_length ,  pen_y ) )
            pen_x = pen_x +  dash_length + gap_length
        return '\n'.join(XML)
addWeldingCommand( WeldingSymbol29 )


