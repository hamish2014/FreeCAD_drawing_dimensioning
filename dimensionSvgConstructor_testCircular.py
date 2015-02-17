'''
library for constructing dimension SVGs
'''

from dimensionSvgConstructor import *
from selectionOverlay import  generateSelectionGraphicsItems

print('Testing dimensionSvgConstructor.py')
import sys
from PySide import QtGui, QtCore, QtSvg

app = QtGui.QApplication(sys.argv)
width = 640
height = 480
textRenderer = SvgTextRenderer(font_family='Verdana', font_size='16pt', fill="red")

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
            strokeWidth=1.0, arrowL1=10, arrowL2=4, arrowW=6, textRenderer=textRenderer,
            centerPointDia = 4
            )

    def selectCircle( self, event, referer, elementXML, elementParms, elementViewObject ):
        if self.action_ind <> 0:
            return
        self.point1 = elementParms['x'], elementParms['y']
        print('point1 set to x=%3.1f y=%3.1f' % self.point1)
        self.radius = elementParms['r']
        self.action_ind = 1

    def mousePressEvent( self, event ):
        if self.action_ind == 0:
            return
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            #print( 'current action: %s' % self.actions[self.action_ind] )
            pos = event.scenePos()
            x, y = pos.x(), pos.y()
            if self.action_ind == 1:
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
        if self.action_ind == 1:
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

#creating points to dimension.
circlesXML = []
rand = numpy.random.rand
for i in range(24):
    circlesXML.append( '<circle id="circ%03i" cx ="%f" cy ="%f" r ="%s" />' % (i, (0.1+0.8*rand())*width , (0.1+0.8*rand())*height, 6 + 64*rand()  ))
XML = '''<svg id="Ortho_0_1" width="%i" height="%i">  <g stroke-width="0.2" >
%s
</g> </svg>''' % (width, height, '\n'.join(circlesXML) )
class dummyViewObject:
    def __init__(self, XML):
        self.ViewResult = XML
viewObject = dummyViewObject( XML )
    

maskPen = QtGui.QPen( QtGui.QColor(255,0,0, 125) )
maskPen.setWidth(3.0)
hoverPen = QtGui.QPen( QtGui.QColor(255,0,0) )
hoverPen.setWidth(3.0)

selectGraphicsItems = generateSelectionGraphicsItems( [viewObject], dimensioningRect.selectCircle , doCircles=True,
                                                      maskPen=maskPen  , 
                                                      maskBrush=QtGui.QBrush(), 
                                                      maskHoverPen= hoverPen )

graphicsScene.addItem(dimensioningRect)    
for g in selectGraphicsItems:
    graphicsScene.addItem(g)



view = QtGui.QGraphicsView(graphicsScene)
#view.scale(2, 2)
view.show()

sys.exit(app.exec_())
