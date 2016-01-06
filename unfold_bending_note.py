# This Python file uses the following encoding: utf-8

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
class angleText_widget:
    default = unicode('90°','utf8')
    def valueChanged( self, arg1):
        d.angleText = arg1
    def generateWidget( self, dimensioningProcess ):
        self.lineEdit = QtGui.QLineEdit()
        self.lineEdit.setText(self.default)
        d.angleText = self.default
        self.lineEdit.textChanged.connect(self.valueChanged)
        return DimensioningTaskDialog_generate_row_hbox('angle text:', self.lineEdit)
    def add_properties_to_dimension_object( self, obj ):
        obj.addProperty("App::PropertyString", 'angleText', 'Parameters')
        obj.angleText = d.angleText.encode('utf8') 
    def get_values_from_dimension_object( self, obj, KWs ):
        KWs['angleText'] = obj.angleText #should be unicode
d.dialogWidgets.append( angleText_widget() )


maskBrush  =   QtGui.QBrush( QtGui.QColor(0,160,0,100) )
maskPen =      QtGui.QPen( QtGui.QColor(0,160,0,100) )
maskPen.setWidth(0.0)
maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) )
maskHoverPen.setWidth(0.0)

class BendingNoteCommand:
    def Activated(self):
        V = getDrawingPageGUIVars()
        d.activate(V, dialogTitle='Add Bend Note', dialogIconPath=':/dd/icons/bendingNote.svg', endFunction=self.Activated )
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

    def preview_clickHandler( self, x, y ):
        d.selections.append( PlacementClick( x, y) )
        if len(d.selections) == 3:
            return 'createDimension:%s' % findUnusedObjectName('bendNote')

    def preview_svgRenderer(self,  x, y):
        s =  d.selections + [ PlacementClick( x, y) ] if len(d.selections) < 3 else d.selections
        return self.generateSvg( 
            *selections_to_svg_fun_args(s),  
             angleText = d.angleText,    
             **d.dimensionConstructorKWs 
             )

    def svgLine(self, x1, y1, x2, y2, clr=None):
        return '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:%s;stroke-width:%1.2f" />' % (x1, y1, x2, y2, self.svg_lineColor if clr==None else clr, self.svg_strokeWidth ) 

    def generateSvg(self,  c_x, c_y, radialLine_x=None, radialLine_y=None, tail_x=None, tail_y=None, angleText='90°',
                    arrowL1=3,arrowL2=1,arrowW=2, strokeWidth=0.5,  lineColor='blue', textRenderer=None):
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
                XML_body.append( textRenderer(x + box_w*1.2, y+box_w*0.8, angleText) )


        return '<g> %s </g> ''' % "\n".join(XML_body)

    def GetResources(self): 
        return {
            'Pixmap' : ':/dd/icons/bendingNote.svg',
            'MenuText': 'bending note', 
            } 
bendingNoteCommand = BendingNoteCommand()
FreeCADGui.addCommand('dd_bendingNote', bendingNoteCommand)

class Proxy_bendNote( Proxy_DimensionObject_prototype ):
     def dimensionProcess( self ):
         return d
d.ProxyClass = Proxy_bendNote

class Command_svg_fun_wrapper: #to make instance method pickalble!
    def __init__(self, command ):
        self.command = command
    def __call__(self, *args, **KWS):
        return self.command.generateSvg( *args, **KWS)
d.proxy_svgFun = Command_svg_fun_wrapper(bendingNoteCommand)
