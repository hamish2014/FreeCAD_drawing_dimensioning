
from dimensioning import *
from dimensioning import __dir__ # not imported with * directive
import dimensioning
from grid_dd import *

class PreviewVars:
    def __init__(self):
        self.SVG_initialization_width = -1
        self.SVG_initialization_height = -1
    def setTransform(self,drawingVars):
        self.x_offset = drawingVars.VRT_ox
        self.y_offset = drawingVars.VRT_oy
        self.scale =  drawingVars.VRT_scale
    def applyTransform(self, pos ):
        x_new = ( pos.x() - self.x_offset )/ self.scale
        y_new = ( pos.y() - self.y_offset )/ self.scale
        return x_new, y_new        

preview = PreviewVars() 


def initializePreview( dimensioningProcessTracker, dimensionSvgFun, dimensionClickHandler ):
    drawingVars  = dimensioningProcessTracker.drawingVars #shorthand
    preview.dimensioningProcessTracker = dimensioningProcessTracker
    preview.drawingVars = drawingVars
    preview.setTransform(drawingVars)
    if not hasattr(preview, 'SVG'):
        createQtItems = True
    elif not preview.removedQtItems:
        debugPrint(3, 'initializePreview: flag indicating preview QtItems not removed from scene,')
        #there are two possible options here
        case_msgs = [
            'FreeCAD.ActivieDocument.recompute() has been called without clean up, therefore Qt items would have been deleted',
            'dimensioningPreview interrupted by user selecting another dimensioning tool'
        ]
        case = 0 
        for c in drawingVars.graphicsScene.children():
            if isinstance(c,DimensionPreviewRect):
                case = 1
        debugPrint(3, 'initializePreview: case %s' % case_msgs[case])
        if case == 0:
            createQtItems = True
        else:
            removePreviewGraphicItems( recomputeActiveDocument=False)
            createQtItems = False
    else:
        createQtItems = False
    if preview.SVG_initialization_width <> drawingVars.width or preview.SVG_initialization_height <> drawingVars.height:
        debugPrint(3, 'initializePreview: change in page rect size dected, recreating SVG graphics item')
        createQtItems = True
    if createQtItems:
        # then initialize graphicsScene Objects, otherwise dont recreate objects. 
        # initializing dimPreview is particularly troublesome, rather unstable and occasionally causes FreeCAD to crash.
        debugPrint(3, 'creating dimPreview QtGraphicsItems')
        preview.rect = DimensionPreviewRect()
        preview.SVG =  QtSvg.QGraphicsSvgItem() 
        debugPrint(3, 'creating dimPreview SVG renderer')
        preview.SVGRenderer = QtSvg.QSvgRenderer()
        preview.SVGRenderer.load( QtCore.QByteArray( '''<svg width="%i" height="%i"> </svg>''' % (drawingVars.width, drawingVars.height) ) ) #without this something goes wrong...
        preview.SVG_initialization_width = drawingVars.width
        preview.SVG_initialization_height = drawingVars.height
        preview.SVG.setSharedRenderer( preview.SVGRenderer )
        preview.SVG.setTransform( drawingVars.transform )
        preview.SVG.setZValue( 0.09 )
    preview.removedQtItems = False
    debugPrint(4, 'adding SVG')
    preview.SVGRenderer.load( QtCore.QByteArray( '''<svg width="%i" height="%i"> </svg>''' % (drawingVars.width, drawingVars.height) ) )
    preview.SVG.update()
    #preview.SVG.
    drawingVars.graphicsScene.addItem( preview.SVG )

    debugPrint(4, 'adding Rect')
    preview.rect.setRect(0, 0, drawingVars.width, drawingVars.height)
    preview.rect.dimensionSvgFun = dimensionSvgFun
    preview.rect.dimensionClickHandler = dimensionClickHandler
    preview.rect.setAcceptHoverEvents(True)
    preview.rect.setFlag( QtGui.QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True )
    preview.rect.setCursor( QtCore.Qt.ArrowCursor ) # http://qt-project.org/doc/qt-5/qt.html#CursorShape-enum
    preview.rect.setZValue( 0.1 )
    drawingVars.graphicsScene.addItem( preview.rect )
    debugPrint(4, 'DimensionPreviewSvgGraphicsItem added to graphics Scene')


def removePreviewGraphicItems( recomputeActiveDocument = True, launchEndFunction=False, closeDialog=True ):
    debugPrint(4,'removePreviewGraphicItems called, recomputeActiveDocument %s' % recomputeActiveDocument)
    preview.drawingVars.graphicsScene.removeItem( preview.SVG )
    preview.drawingVars.graphicsScene.removeItem( preview.rect )
    preview.removedQtItems = True
    if recomputeActiveDocument:
        debugPrint(3,'removePreviewGraphicItems: recomputing')
        recomputeWithOutViewReset( preview.drawingVars )
    if closeDialog and preview.dimensioningProcessTracker.taskDialog <> None:
        FreeCADGui.Control.closeDialog()
    del preview.drawingVars
    if launchEndFunction and preview.dimensioningProcessTracker.endFunction <> None:
        timer.start( 1 ) # 1 ms (in theory)


def executeEndFunction():
    'if problems try increasing time tick...'
    timer.stop()
    preview.dimensioningProcessTracker.endFunction()
timer = QtCore.QTimer()
timer.timeout.connect(executeEndFunction)


class DimensionPreviewRect(QtGui.QGraphicsRectItem):

    def keyPressEvent(self, event):
        #if len(event.text()) == 1:
        #   debugPrint(2, 'key pressed: event.text %s (ord %i)' % (event.text(), ord(event.text())))
        if event.text() == chr(27): #escape key
            removePreviewGraphicItems( recomputeActiveDocument = True )

    def mousePressEvent( self, event ):
        try:
            if event.button() == QtCore.Qt.MouseButton.LeftButton:
                x, y =  preview.applyTransform( event.scenePos() )
                debugPrint(3, 'mousePressEvent: x %f, y %f' % (x, y) )
                x, y= applyGridRounding( x, y)
                instruction = self.dimensionClickHandler( x, y )
                if instruction == None:
                    pass
                elif instruction.startswith('createDimension:'):
                    viewName = instruction.split(':')[1]
                    FreeCAD.ActiveDocument.openTransaction(viewName)
                    XML = self.dimensionSvgFun( x, y )
                    debugPrint(3, XML)
                    debugPrint(2, 'creating dimension %s' % viewName)
                    obj = App.ActiveDocument.addObject('Drawing::FeatureViewPython',viewName)
                    obj.ViewResult = XML
                    d = preview.dimensioningProcessTracker
                    d.ProxyClass( obj, d.selections, d.proxy_svgFun )
                    if hasattr( obj.ViewObject, 'Proxy'):
                        d.ViewObjectProxyClass( obj.ViewObject, d.dialogIconPath )
                    preview.drawingVars.page.addObject( obj ) #App.ActiveDocument.getObject(viewName) )
                    removePreviewGraphicItems( recomputeActiveDocument=True, launchEndFunction=True )
                    FreeCAD.ActiveDocument.commitTransaction()
                elif instruction == 'stopPreview':
                    removePreviewGraphicItems( recomputeActiveDocument=True, launchEndFunction=True )
            else:
                event.ignore()
        except:
            App.Console.PrintError(traceback.format_exc())

    def hoverMoveEvent(self, event):
        try:
            x, y = preview.applyTransform( event.scenePos() )
            debugPrint(4, 'hoverMoveEvent: x %f, y %f' % (x, y) )
            x, y= applyGridRounding( x, y)
            XML = '<svg width="%i" height="%i"> %s </svg>' % (preview.drawingVars.width, preview.drawingVars.height, self.dimensionSvgFun( x, y ))
            if isinstance(XML, unicode): 
                XML = XML.encode('utf8')
            debugPrint(5, XML)
            preview.SVGRenderer.load( QtCore.QByteArray( XML ) )
            preview.SVG.update()
        except:
            App.Console.PrintError(traceback.format_exc())

