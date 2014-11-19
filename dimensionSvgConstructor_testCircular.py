'''
library for constructing dimension SVGs
'''

from dimensionSvgConstructor import *

print('Testing dimensionSvgConstructor.py')
import sys
from PySide import QtGui, QtCore, QtSvg

app = QtGui.QApplication(sys.argv)
width = 640
height = 480
radius = 12

graphicsScene = QtGui.QGraphicsScene(0,0,width,height)
graphicsScene.addText("Circular dimensioning testing app.\nEsc to Exit")

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
        graphicsScene.addItem( self.dimPreview )
        self.dim_svg_KWs = dict(
            svgTag='svg', svgParms='width="%i" height="%i"' % (args[2],args[3]),
            fontSize= 16, strokeWidth=1.0, arrowL1=10, arrowL2=4, arrowW=6,
            centerPointDia = 4
            )
        self.radius = 6

    def mousePressEvent( self, event ):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            #print( 'current action: %s' % self.actions[self.action_ind] )
            pos = event.scenePos()
            x, y = pos.x(), pos.y()
            if self.action_ind == 0:
                self.point1 = x, y
                print('point1 set to x=%3.1f y=%3.1f' % (x,y))
                self.action_ind = self.action_ind + 1
            elif self.action_ind == 1:
                self.point2 = x, y
                print('point2 set to x=%3.1f y=%3.1f' % (x,y))
                self.action_ind = self.action_ind + 1
            elif self.action_ind == 2:
                self.point3 = x, y
                print('point3 set to x=%3.1f y=%3.1f' % (x,y))
                self.action_ind = self.action_ind + 1
            else: #'placeDimensionText'
                self.point4 = x, y                
                XML = circularDimensionSVG( self.point1[0], self.point1[1], self.radius,
                                            self.point2[0], self.point2[1], 
                                            self.point3[0], self.point3[1], 
                                            x, y, **self.dim_svg_KWs )
                self.action_ind = 0
                self.radius = self.radius * 2
                if XML <> None:
                    print(XML)
                    newSvg = QtSvg.QGraphicsSvgItem(  )
                    svgRenderer = QtSvg.QSvgRenderer()
                    svgRenderer.load( QtCore.QByteArray( XML ))
                    newSvg.setSharedRenderer( svgRenderer )
                    dimensions.append([ newSvg, svgRenderer]) #as to prevent the garbage collector from freeing these resources (which causes a crash)
                    self.scene().addItem( newSvg )
        elif event.button() == QtCore.Qt.MouseButton.RightButton:
            self.action_ind = self.action_ind - 1

    def hoverMoveEvent(self, event):
        pos = event.scenePos()
        x, y = pos.x(), pos.y()
        XML = None
        if self.action_ind == 0:
            XML = circularDimensionSVG( x, y, self.radius, **self.dim_svg_KWs )
        elif self.action_ind == 1:
            XML = circularDimensionSVG( self.point1[0], self.point1[1], self.radius, x, y, **self.dim_svg_KWs )
        elif  self.action_ind == 2:
            XML = circularDimensionSVG( self.point1[0], self.point1[1], self.radius,
                                        self.point2[0], self.point2[1], 
                                        x, y, **self.dim_svg_KWs )
        elif  self.action_ind == 3:
            XML = circularDimensionSVG( self.point1[0], self.point1[1], self.radius,
                                        self.point2[0], self.point2[1], 
                                        self.point3[0], self.point3[1], 
                                        x, y, **self.dim_svg_KWs )
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
