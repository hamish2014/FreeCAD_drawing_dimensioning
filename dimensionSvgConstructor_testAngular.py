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
graphicsScene.addText("Angular dimensioning testing app.\nEsc to Exit")

dimensions = []

class DimensioningRect(QtGui.QGraphicsRectItem):
    def __init__(self,*args):
        super(DimensioningRect, self).__init__(*args)
        svgRenderer = QtSvg.QSvgRenderer()
        self.action_ind = 0
        self.actions = ['selectLine1','selectLine2','placeDimensionBaseLine','placeDimensionText']
        self.dimPreview = QtSvg.QGraphicsSvgItem()
        self.dimSVGRenderer = QtSvg.QSvgRenderer()
        self.dimSVGRenderer.load( QtCore.QByteArray( '''<svg width="%i" height="%i"></svg>''' % (args[2],args[3])))
        self.dimPreview.setSharedRenderer( self.dimSVGRenderer )
        self.dimPreview.setZValue(100)
        graphicsScene.addItem( self.dimPreview )
        self.dim_svg_KWs = dict(
            svgTag='svg', svgParms='width="%i" height="%i"' % (args[2],args[3]),
            strokeWidth=1.0, arrowL1=10, arrowL2=4, arrowW=6, textRenderer=textRenderer,
            gap_datum_points = 8, dimension_line_overshoot=4,
            )
    def selectDimensioningLine( self, event, referer, elementXML, elementParms, elementViewObject ):
        print( elementXML )
        if self.action_ind == 0: #then selectPoint1
            self.line1 = elementParms['x1'], elementParms['y1'], elementParms['x2'], elementParms['y2'] 
            self.action_ind = self.action_ind + 1
            referer.lockSelection()
            self.referer1 = referer
        elif self.action_ind == 1: #then selectPoint2
            self.line2 = elementParms['x1'], elementParms['y1'], elementParms['x2'], elementParms['y2'] 
            self.action_ind = self.action_ind + 1
            referer.lockSelection()
            self.referer2 = referer

    def mousePressEvent( self, event ):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            pos = event.scenePos()
            x, y = pos.x(), pos.y()
            if self.action_ind == 2: #then 'placeDimensionBaseLine':
                self.point3 = x, y
                print('point3 set to x=%3.1f y=%3.1f' % (x,y))
                self.action_ind = self.action_ind + 1
            elif self.action_ind == 3: # then placeDimensionText
                self.point4 = x, y
                self.action_ind = 0
                XML = angularDimensionSVG( self.line1, self.line2,
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
                    self.referer1.unlockSelection()
                    self.referer2.unlockSelection()

    def hoverMoveEvent(self, event):
        pos = event.scenePos()
        x, y = pos.x(), pos.y()
        XML = None
        if self.action_ind == 2: # then placeDimensionBaseLine action
            XML = angularDimensionSVG( self.line1, self.line2, x, y,
                                      **self.dim_svg_KWs )
        elif self.action_ind == 3: # then placeDimensionText
            XML = angularDimensionSVG( self.line1, self.line2,
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
dimensioningRect.setZValue(-1000)

#creating points to dimension.
lineXML = []
rand = numpy.random.rand
for i in range(24):
    x1 = numpy.random.rand()*width*0.8
    y1 = numpy.random.rand()*height*0.8 
    x2 = x1 + 200*(rand() - 0.5)
    y2 = y1 + 200*(rand() - 0.5)
    lineXML.append( '<path id= "path%03i" d=" M %f %f L %f %f " />' % (i,x1,y1,x2,y2))
XML = '''<svg id="Ortho_0_1" width="%i" height="%i">  <g stroke-width="0.2" >
%s
</g> </svg>''' % (width, height, '\n'.join(lineXML) )
class dummyViewObject:
    def __init__(self, XML):
        self.ViewResult = XML
viewObject = dummyViewObject( XML )
    

maskPen = QtGui.QPen( QtGui.QColor(0,160,0) )
maskPen.setWidth(5.0)
hoverPen = QtGui.QPen( QtGui.QColor(0,0,255) )
hoverPen.setWidth(5.0)


selectGraphicsItems = generateSelectionGraphicsItems( [viewObject], dimensioningRect.selectDimensioningLine, doLines=True,
                                                      maskPen=maskPen , maskHoverPen= hoverPen )

graphicsScene.addItem(dimensioningRect)    
for g in selectGraphicsItems:
    graphicsScene.addItem(g)


view = QtGui.QGraphicsView(graphicsScene)
#view.scale(2, 2)
view.show()

sys.exit(app.exec_())
