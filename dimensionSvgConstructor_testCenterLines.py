print('Testing dimensionSvgConstructor.py centerLines')

from dimensionSvgConstructor import *
import sys
from PySide import QtGui, QtCore, QtSvg

app = QtGui.QApplication(sys.argv)
width = 640
height = 480

graphicsScene = QtGui.QGraphicsScene(0,0,width,height)
graphicsScene.addText("Center Lines testing app.\nEsc to Exit")

dimensions = []

class DimensioningRect(QtGui.QGraphicsRectItem):
    def __init__(self,*args):
        super(DimensioningRect, self).__init__(*args)
        svgRenderer = QtSvg.QSvgRenderer()
        self.action_ind = 0
        self.dimPreview = QtSvg.QGraphicsSvgItem()
        self.dimSVGRenderer = QtSvg.QSvgRenderer()
        self.dimSVGRenderer.load( QtCore.QByteArray( '''<svg width="%i" height="%i"></svg>''' % (args[2],args[3])))
        self.dimPreview.setSharedRenderer( self.dimSVGRenderer )
        self.dimPreview.setZValue(100)
        graphicsScene.addItem( self.dimPreview )
        self.dim_svg_KWs = dict(
            svgTag='svg', svgParms='width="%i" height="%i"' % (args[2],args[3]),
            centerLine_width=2.0, centerLine_len_dot=5, centerLine_len_dash=15, centerLine_len_gap=5
            )
        assert not hasattr(self, 'topLeft')
        assert not hasattr(self, 'bottomRight')
        assert not hasattr(self, 'center')

    def mousePressEvent( self, event ):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            pos = event.scenePos()
            x, y = pos.x(), pos.y()
            if self.action_ind == 0:
                self.center = x, y
                print('center set to x=%3.1f y=%3.1f' % (x,y))
                self.action_ind = self.action_ind + 1
            elif self.action_ind == 1:
                self.topLeft  = x, y
                print('topLeft set to x=%3.1f y=%3.1f' % (x,y))
                self.action_ind = self.action_ind + 1
            elif self.action_ind == 2: # then place
                self.bottomRight = x, y
                self.action_ind = 0
                XML = centerLinesSVG( self.center, self.topLeft, self.bottomRight,
                                   **self.dim_svg_KWs )
                if XML <> None:
                    print(XML)
                    newSvg = QtSvg.QGraphicsSvgItem(  )
                    svgRenderer = QtSvg.QSvgRenderer()
                    svgRenderer.load( QtCore.QByteArray( XML ))
                    newSvg.setSharedRenderer( svgRenderer )
                    dimensions.append([ newSvg, svgRenderer]) #as to prevent the garbage collector from freeing these resources (which causes a crash)
                    self.scene().addItem( newSvg )

    def hoverMoveEvent(self, event):
        if self.action_ind == 0:
            return
        pos = event.scenePos()
        x, y = pos.x(), pos.y()
        XML = None
        if self.action_ind == 1: # then placeDimensionBaseLine action
            XML = centerLinesSVG( self.center, [x, y],
                                      **self.dim_svg_KWs )
        elif self.action_ind == 2: # then placeDimensionText
            XML = centerLinesSVG( self.center, self.topLeft, [ x, y ], **self.dim_svg_KWs )
        if XML <> None:
            self.dimSVGRenderer.load( QtCore.QByteArray( XML ) )
            self.dimPreview.update()
            self.dimPreview.show()
        else:
            self.dimPreview.hide()
            
    def wheelEvent( self, event):
        if event.delta() > 0:
            view.scale(1.1, 1.1)
        else:
            view.scale(0.9, 0.9)
    
    def keyPressEvent(self, event):
        if len(event.text()) == 1:
            print('key pressed: event.text %s (ord %i)' % (event.text(), ord(event.text())))
        if event.text() == chr(27): #escape key
            sys.exit(2)

dimensioningRect = DimensioningRect(0,0,width,height)
dimensioningRect.setAcceptHoverEvents(True)
dimensioningRect.setFlag( QtGui.QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True )
graphicsScene.addItem(dimensioningRect)    

view = QtGui.QGraphicsView(graphicsScene)
#view.scale(2, 2)
view.show()

sys.exit(app.exec_())
