
from dimensioning import *
from dimensioning import __dir__ # not imported with * directive


class PreviewVars:
    def __init__(self):
        self.createQtItems = True # cleanUp is perhaps the wrong word
    def setTransform(self,drawingVars):
        self.x_offset = drawingVars.VRT_ox
        self.y_offset = drawingVars.VRT_oy
        self.scale =  drawingVars.VRT_scale
    def applyTransform(self, pos ):
        x_new = ( pos.x() - self.x_offset )/ self.scale
        y_new = ( pos.y() - self.y_offset )/ self.scale
        return x_new, y_new        

preview = PreviewVars() 


def initializePreview( drawingVars, clickFunPreview, hoverFunPreview ):
    preview.drawingVars = drawingVars
    preview.setTransform(drawingVars)
    if preview.createQtItems: 
        # then initialize graphicsScene Objects, otherwise dont recreate objects. 
        # initializing dimPreview is particularly troublesome, as in FreeCAD 0.15 this is unstable and occasionally causes FreeCAD to crash.
        debugPrint(4, 'creating dimPreview QtGraphicsItems')
        preview.rect = DimensionPreviewRect()
        preview.SVG =  QtSvg.QGraphicsSvgItem() 
        preview.SVGRenderer = QtSvg.QSvgRenderer()
        preview.SVGRenderer.load( QtCore.QByteArray( '''<svg width="%i" height="%i"> </svg>''' % (drawingVars.width, drawingVars.height) ) ) #without this something goes wrong...
        preview.SVG.setSharedRenderer( preview.SVGRenderer )
    debugPrint(4, 'adding SVG')
    preview.SVGRenderer.load( QtCore.QByteArray( '''<svg width="%i" height="%i"> </svg>''' % (drawingVars.width, drawingVars.height) ) )
    preview.SVG.update()
    drawingVars.graphicsScene.addItem( preview.SVG )

    debugPrint(4, 'adding Rect')
    preview.rect.setRect(0, 0, drawingVars.width, drawingVars.height)
    preview.rect.hoverFunPreview = hoverFunPreview
    preview.rect.clickFunPreview = clickFunPreview
    preview.rect.setAcceptHoverEvents(True)
    preview.rect.setFlag( QtGui.QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True )
    preview.rect.setCursor( QtCore.Qt.ArrowCursor ) # http://qt-project.org/doc/qt-5/qt.html#CursorShape-enum
    drawingVars.graphicsScene.addItem( preview.rect )
    debugPrint(4, 'DimensionPreviewSvgGraphicsItem added to graphics Scene')


class DimensionPreviewRect(QtGui.QGraphicsRectItem):

    def cleanUp( self ):
        preview.drawingVars.graphicsScene.removeItem( preview.SVG )
        preview.drawingVars.graphicsScene.removeItem( self )
        preview.createQtItems = False
        debugPrint(4,'cleanUP: preview.Svg removed from scene, now recomputing')
        preview.drawingVars.page.touch()
        App.ActiveDocument.recompute()

    def keyPressEvent(self, event):
        #if len(event.text()) == 1:
        #   debugPrint(2, 'key pressed: event.text %s (ord %i)' % (event.text(), ord(event.text())))
        if event.text() == chr(27): #escape key
            self.cleanUp()

    def mousePressEvent( self, event ):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            x, y =  preview.applyTransform( event.scenePos() )
            debugPrint(3, 'mousePressEvent: x %f, y %f' % (x, y) )
            viewName, XML = self.clickFunPreview(x,y)
            if XML <> None:
                debugPrint(3, XML)
                debugPrint(2, 'creating dimension %s' % viewName)
                obj = App.ActiveDocument.addObject('Drawing::FeatureView',viewName)
                obj.ViewResult = XML                    
                preview.drawingVars.page.addObject( obj ) #App.ActiveDocument.getObject(viewName) )
                self.cleanUp()
        else:
            event.ignore()

    def hoverMoveEvent(self, event):
        x, y =  preview.applyTransform( event.scenePos() )
        debugPrint(4, 'hoverMoveEvent: x %f, y %f' % (x, y) )
        XML = self.hoverFunPreview( x, y)
        #debugPrint(4, XML)
        preview.SVGRenderer.load( QtCore.QByteArray( XML ) )
        preview.SVG.update()
