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

graphicsScene = QtGui.QGraphicsScene(0,0,width,height)
graphicsScene.addText("Linear dimensioning testing app.\nEsc to Exit")

#creating some points to snap to.
noPoints = 12
X = [ numpy.random.rand()*width*0.8 for i in range(noPoints) ]
Y = [ numpy.random.rand()*height*0.8 for i in range(noPoints) ]
for i in range(noPoints):
    graphicsScene.addEllipse( X[i]-5, Y[i]-5, 10, 10, QtGui.QPen(QtGui.QColor(0,255,0)), QtGui.QBrush(QtGui.QColor(0,155,0))) 

dimensions = []

class DimensioningRect(QtGui.QGraphicsRectItem):
    def __init__(self,*args):
        super(DimensioningRect, self).__init__(*args)
        svgRenderer = QtSvg.QSvgRenderer()
        self.action_ind = 0
        self.snapHint = graphicsScene.addEllipse(0, 0, 16, 16, QtGui.QPen(QtGui.QColor(150,0,0)))
        self.snapHint.hide()
        self.actions = ['selectPoint1','selectPoint2','placeDimensionBaseLine','placeDimensionText']
        self.dimPreview = QtSvg.QGraphicsSvgItem()
        self.dimSVGRenderer = QtSvg.QSvgRenderer()
        self.dimSVGRenderer.load( QtCore.QByteArray( '''<svg width="%i" height="%i"></svg>''' % (args[2],args[3])))
        self.dimPreview.setSharedRenderer( self.dimSVGRenderer )
        graphicsScene.addItem( self.dimPreview )
        self.snapX = numpy.array(X)
        self.snapY = numpy.array(Y)
        self.dim_svg_KWs = dict(
            svgTag='svg', svgParms='width="%i" height="%i"' % (args[2],args[3]),
            fontSize= 16, strokeWidth=1.0, arrowL1=10, arrowL2=4, arrowW=6,
            scale= 1.0, gap_datum_points = 8, dimension_line_overshoot=4,
            )

    def findSnapPoint(self, x, y, tol= 10 ):
        D = (x - self.snapX)**2 + (y - self.snapY)**2
        #print(D.min())
        if D.min() <= tol**2:
            ind = numpy.argmin(D)
            return self.snapX[ind], self.snapY[ind]
        else:
            return None
        
    def mousePressEvent( self, event ):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            #print( 'current action: %s' % self.actions[self.action_ind] )
            pos = event.scenePos()
            x, y = pos.x(), pos.y()
            if self.actions[self.action_ind] == 'selectPoint1':
                if self.findSnapPoint(x, y) <> None :
                    self.point1 = self.findSnapPoint(x, y)
                    print('point1 set to x=%3.1f y=%3.1f' % (x,y))
                    self.action_ind = self.action_ind + 1
            elif self.actions[self.action_ind] == 'selectPoint2':
                if self.findSnapPoint(x, y) <> None :
                    self.point2 = self.findSnapPoint(x, y)
                    print('point2 set to x=%3.1f y=%3.1f' % (x,y))
                    self.action_ind = self.action_ind + 1
                    self.snapHint.hide()
            elif self.actions[self.action_ind] == 'placeDimensionBaseLine':
                self.point3 = x, y
                print('point3 set to x=%3.1f y=%3.1f' % (x,y))
                self.action_ind = self.action_ind + 1
            else: #'placeDimensionText'
                self.point4 = x, y
                self.action_ind = 0
                XML = linearDimensionSVG( self.point1[0], self.point1[1],
                                          self.point2[0], self.point2[1], 
                                          self.point3[0], self.point3[1], 
                                          x, y, **self.dim_svg_KWs )
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
        if self.actions[self.action_ind] in ['selectPoint1', 'selectPoint2'] :
            snapPoint = self.findSnapPoint(x, y)
            if snapPoint <> None:
                self.snapHint.setPos( snapPoint[0]-8,  snapPoint[1]-8 )
                self.snapHint.show()
            else:
                self.snapHint.hide()
        elif self.actions[self.action_ind] == 'placeDimensionBaseLine':
            XML = linearDimensionSVG( self.point1[0], self.point1[1],
                                      self.point2[0], self.point2[1], x, y,
                                      **self.dim_svg_KWs )
        else: #self.actions[self.action_ind] == 'placeDimensionText'
            XML = linearDimensionSVG( self.point1[0], self.point1[1],
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
