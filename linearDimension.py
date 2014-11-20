import numpy
from PySide import QtGui, QtCore, QtSvg
import FreeCAD as App
import FreeCADGui, Part, os
from dimensioning import debugPrint, __dir__, get_FreeCAD_drawing_variables, DimensioningRectPrototype
from XMLlib import SvgXMLTreeNode
from dimensionSvgConstructor import linearDimensionSVG


class DimensioningRect( DimensioningRectPrototype ):

    def activate(self, graphicsScene, graphicsView, page, width, height, 
                 VRT_scale, VRT_ox, VRT_oy, 
                 snapHint, dimPreview, dimSVGRenderer, **otherKWs):
        ' called each time before dimensioning '
        self.graphicsScene = graphicsScene
        self.graphicsView = graphicsView
        self.drawingPage = page
        self.drawingPageWidth = width
        self.drawingPageHeight = height
        self.VRT_ox = VRT_ox
        self.VRT_oy = VRT_oy
        self.VRT_scale = VRT_scale
        self.snapHint = snapHint
        self.dimPreview = dimPreview
        self.dimSVGRenderer = dimSVGRenderer

        self.action_ind = 0
        self.actions = ['selectPoint1','selectPoint2','placeDimensionBaseLine','placeDimensionText']
        self.dimPreview_SvgParms = 'width="%(width)i" height="%(height)i" transform="translate( %(VRT_ox)f, %(VRT_oy)f) scale( %(VRT_scale)f, %(VRT_scale)f)"' % locals()

        debugPrint(3, 'adding graphicsScene Objects for aiding to dimensioning to scene')
        graphicsScene.addItem( snapHint )
        snapHint.hide()
        graphicsScene.addItem( dimPreview )
        dimPreview.hide()
        self.cleanUpList = [ snapHint, dimPreview ]
        self.cleanedUp = False

        self.setRect(0, 0, width, height)
        graphicsScene.addItem( self )
        self.generateSnapPoints()
        self.setAcceptHoverEvents(True)
        self.setFlag( QtGui.QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True )
        debugPrint(3, 'DimensioningRect.Activated completed')

    def generateSnapPoints(self):
        points = []
        for obj in self.drawingPage.Group :
            if not obj.Name.startswith('dim') and len(obj.ViewResult.strip()) > 0:
                svg = SvgXMLTreeNode(obj.ViewResult, 0)
                points = points + svg.linearDimensioningSnapPoints()
        self.dimScale = 1.0/ svg.scaling()
        self.snapX = numpy.array( [p[0] for p in points] )
        self.snapY = numpy.array( [p[1] for p in points] )
        for x,y in zip(self.snapX, self.snapY):
            self.graphicsScene.addEllipse( x*self.VRT_scale + self.VRT_ox-4, y*self.VRT_scale + self.VRT_oy-4, 8, 8, 
                                           QtGui.QPen(QtGui.QColor(0,255,0)), QtGui.QBrush(QtGui.QColor(0,155,0)))

    def mousePressEvent( self, event ):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            pos = event.scenePos()
            x = ( pos.x() - self.VRT_ox )/ self.VRT_scale
            y = ( pos.y() - self.VRT_oy )/ self.VRT_scale
            debugPrint(3, 'mousePressEvent: x %f, y %f, %s' % (x, y, self.actions[self.action_ind]))
            if self.actions[self.action_ind] == 'selectPoint1':
                if self.findSnapPoint(x, y) <> None :
                    self.point1 = self.findSnapPoint(x, y)
                    debugPrint(2, 'point1 set to x=%3.1f y=%3.1f' % (x,y))
                    self.action_ind = self.action_ind + 1
            elif self.actions[self.action_ind] == 'selectPoint2':
                if self.findSnapPoint(x, y) <> None :
                    self.point2 = self.findSnapPoint(x, y)
                    debugPrint(2, 'point2 set to x=%3.1f y=%3.1f' % (x,y))
                    self.action_ind = self.action_ind + 1
                    self.snapHint.hide()
            elif self.actions[self.action_ind] == 'placeDimensionBaseLine':
                self.point3 = x, y
                debugPrint(2, 'point3 set to x=%3.1f y=%3.1f' % (x,y))
                self.action_ind = self.action_ind + 1
            else: #'placeDimensionText'
                self.point4 = x, y
                XML = linearDimensionSVG( self.point1[0], self.point1[1],
                                          self.point2[0], self.point2[1], 
                                          self.point3[0], self.point3[1], 
                                          x, y, scale=self.dimScale)
                if XML <> None:
                    debugPrint(3, XML)
                    viewName = 'dim001'
                    while hasattr(App.ActiveDocument, viewName):
                        viewName = 'dim%03i' % (int(viewName[3:])+1)
                    debugPrint(2, 'creating dimension %s' % viewName)
                    App.ActiveDocument.addObject('Drawing::FeatureView',viewName)
                    App.ActiveDocument.getObject(viewName).ViewResult = XML                    
                    self.drawingPage.addObject(App.ActiveDocument.getObject(viewName))
                self.cleanUp()

        elif event.button() == QtCore.Qt.MouseButton.RightButton:
            if self.action_ind > 0:
                self.action_ind = self.action_ind - 1
            #else:
            #    self.cleanUp()

    def hoverMoveEvent(self, event):
        pos = event.scenePos()
        x = ( pos.x() - self.VRT_ox )/ self.VRT_scale
        y = ( pos.y() - self.VRT_oy )/ self.VRT_scale
        debugPrint(4, 'hoverMoveEvent: x %f, y %f, %s'%(x,y,self.actions[self.action_ind]))
        XML = None
        if self.actions[self.action_ind] in ['selectPoint1', 'selectPoint2'] :
            snapPoint = self.findSnapPoint(x, y)
            if snapPoint <> None:
                debugPrint(4, 'updating snap point position')
                self.snapHint.setPos( snapPoint[0]*self.VRT_scale + self.VRT_ox-8, snapPoint[1]*self.VRT_scale + self.VRT_oy-8 )
                self.snapHint.show()
            else:
                self.snapHint.hide()
        elif self.actions[self.action_ind] == 'placeDimensionBaseLine':
            XML = linearDimensionSVG( self.point1[0], self.point1[1],
                                self.point2[0], self.point2[1], x, y, svgTag='svg', 
                                svgParms = self.dimPreview_SvgParms )
        else: #self.actions[self.action_ind] == 'placeDimensionText'
            XML = linearDimensionSVG( self.point1[0], self.point1[1],
                                self.point2[0], self.point2[1], 
                                self.point3[0], self.point3[1], 
                                x, y, svgTag='svg', scale=self.dimScale, 
                                svgParms = self.dimPreview_SvgParms )
        if XML <> None:
            self.dimSVGRenderer.load( QtCore.QByteArray( XML ) )
            self.dimPreview.update()
            self.dimPreview.show()
        else:
            self.dimPreview.hide()
    


moduleGlobals = {}
class linearDimension:
    "this class will create a line after the user clicked 2 points on the screen"
    def Activated(self):
        if not get_FreeCAD_drawing_variables(moduleGlobals):
            return #an error has occurred ...
        if not moduleGlobals.has_key('dimensioningRect') or not moduleGlobals['dimensioningRect'].cleanedUp: 
            # then initialize graphicsScene Objects, otherwise dont recreate objects. 
            # initializing dimPreview is particularly troublesome, as in FreeCAD 0.15 this is unstable and occasionally causes FreeCAD to crash.
            debugPrint(4, 'creating snapHint ellipse')
            snapHint = QtGui.QGraphicsEllipseItem(0, 0, 16, 16)
            snapHint.setPen( QtGui.QPen(QtGui.QColor(150,0,0)) )

            debugPrint(4, 'creating dimPreview')
            dimPreview = QtSvg.QGraphicsSvgItem()
            dimSVGRenderer = QtSvg.QSvgRenderer()
            dimSVGRenderer.load( QtCore.QByteArray( '''<svg width="%i" height="%i"> </svg>''' % (moduleGlobals['width'], moduleGlobals['height']) ) )
            dimPreview.setSharedRenderer( dimSVGRenderer )

            debugPrint(4, 'Adding DimensioningRect to graphicsScene')
            dimensioningRect = DimensioningRect()

            moduleGlobals.update(locals())
            del moduleGlobals['self']
            assert not moduleGlobals.has_key('moduleGlobals')
        moduleGlobals['dimensioningRect'].activate(**moduleGlobals)
        
    def GetResources(self): 
        return {
            'Pixmap' : os.path.join( __dir__ , 'linearDimension.svg' ) , 
            'MenuText': 'Linear Dimension', 
            'ToolTip': 'Creates a linear dimension'
            } 

FreeCADGui.addCommand('linearDimension', linearDimension())
