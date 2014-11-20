import FreeCAD as App
import FreeCADGui, Part, os
from PySide import QtGui, QtCore, QtSvg
import numpy
from XMLlib import SvgXMLTreeNode
from dimensioning import debugPrint, __dir__, get_FreeCAD_drawing_variables, DimensioningRectPrototype


class DeletionRect(DimensioningRectPrototype):

    def activate(self, graphicsScene, graphicsView, page, width, height, 
                 VRT_scale, VRT_ox, VRT_oy, snapHint, **otherKWs):
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
        
        debugPrint(3, 'adding graphics objects to scene')
        graphicsScene.addItem( snapHint )
        self.cleanUpList = [snapHint]
        snapHint.hide()
        graphicsScene.addItem( self )
        self.setRect(0, 0, width, height)
        self.generateSnapPoints()
        self.setAcceptHoverEvents(True)
        self.setFlag( QtGui.QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True )
        self.cleanedUp = False

    def generateSnapPoints(self):
        points = []
        for obj in self.drawingPage.Group:
            if obj.Name.startswith('dim'):
                svg = SvgXMLTreeNode(obj.ViewResult, 0)
                points = points + svg.textAnchorSnapPoints()
        self.snapX = numpy.array( [p[0] for p in points] )
        self.snapY = numpy.array( [p[1] for p in points] )
        for x,y in zip(self.snapX, self.snapY):
            self.graphicsScene.addEllipse( x*self.VRT_scale + self.VRT_ox-4, y*self.VRT_scale + self.VRT_oy-4, 8, 8, QtGui.QPen(QtGui.QColor(255,0,0)), QtGui.QBrush(QtGui.QColor(127,0,0)))
                
    def mousePressEvent( self, event ):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            pos = event.scenePos()
            x = ( pos.x() - self.VRT_ox ) / self.VRT_scale
            y = ( pos.y() - self.VRT_oy ) / self.VRT_scale
            if self.findSnapPoint(x, y) <> None :
                x, y = self.findSnapPoint(x, y)
                for obj in self.drawingPage.Group:
                    if obj.Name.startswith('dim'):
                        svg = SvgXMLTreeNode(obj.ViewResult, 0)
                        if (x,y) in svg.textAnchorSnapPoints():
                            debugPrint(2, 'deleting dimension %s' % obj.Name)
                            App.ActiveDocument.removeObject(obj.Name)
                            self.cleanUp()
                            break
        elif event.button() == QtCore.Qt.MouseButton.RightButton:
            self.cleanUp()

    def hoverMoveEvent(self, event):
        pos = event.scenePos()
        x = ( pos.x() - self.VRT_ox )/ self.VRT_scale
        y = ( pos.y() - self.VRT_oy )/ self.VRT_scale
        snapPoint = self.findSnapPoint(x, y)
        if snapPoint <> None:
            debugPrint(4, 'updating snap point position')
            self.snapHint.setPos( snapPoint[0]* self.VRT_scale + self.VRT_ox-8, 
                                  snapPoint[1]* self.VRT_scale + self.VRT_oy-8 )
            self.snapHint.show()
        else:
            self.snapHint.hide()
    

moduleGlobals = {}
class DeleteDimension:
    def Activated(self):
        if not get_FreeCAD_drawing_variables(moduleGlobals):
            return
        if not moduleGlobals.has_key('deletionRect') or not moduleGlobals['deletionRect'].cleanedUp :
            debugPrint(4, 'creating snapHint ellipse')
            snapHint = QtGui.QGraphicsEllipseItem(0, 0, 16, 16)
            snapHint.setPen( QtGui.QPen(QtGui.QColor(150,0,0)) )
            debugPrint(3, 'Initializing DeleteRect')
            deletionRect = DeletionRect()
            moduleGlobals.update(locals())
            del moduleGlobals['self']
        
        moduleGlobals['deletionRect'].activate(**moduleGlobals)
        
    def GetResources(self): 
        return {
            'Pixmap' : os.path.join( __dir__ , 'deleteDimension.svg' ) , 
            'MenuText': 'Delete Dimension', 
            'ToolTip': 'Delete a dimension'
            } 

FreeCADGui.addCommand('deleteDimension', DeleteDimension())
