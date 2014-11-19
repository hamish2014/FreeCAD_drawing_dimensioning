from crudeDebugger import crudeDebuggerPrint
crudeDebuggerPrint('''deleteDimension.py:0  	import FreeCAD as App ''')
import FreeCAD as App
crudeDebuggerPrint('''deleteDimension.py:1  	import FreeCADGui, Part, os ''')
import FreeCADGui, Part, os
crudeDebuggerPrint('''deleteDimension.py:2  	from PySide import QtGui, QtCore, QtSvg ''')
from PySide import QtGui, QtCore, QtSvg
crudeDebuggerPrint('''deleteDimension.py:3  	import numpy ''')
import numpy
crudeDebuggerPrint('''deleteDimension.py:4  	from XMLlib import SvgXMLTreeNode ''')
from XMLlib import SvgXMLTreeNode
crudeDebuggerPrint('''deleteDimension.py:5  	from dimensioning import debugPrint, __dir__, get_FreeCAD_drawing_variables, DimensioningRectPrototype ''')
from dimensioning import debugPrint, __dir__, get_FreeCAD_drawing_variables, DimensioningRectPrototype


class DeletionRect(DimensioningRectPrototype):

    def activate(self, graphicsScene, graphicsView, page, width, height, 
                 VRT_scale, VRT_ox, VRT_oy, snapHint, **otherKWs):
        ' called each time before dimensioning '
        crudeDebuggerPrint('''deleteDimension.py:13  	        self.graphicsScene = graphicsScene ''')
        self.graphicsScene = graphicsScene
        crudeDebuggerPrint('''deleteDimension.py:14  	        self.graphicsView = graphicsView ''')
        self.graphicsView = graphicsView
        crudeDebuggerPrint('''deleteDimension.py:15  	        self.drawingPage = page ''')
        self.drawingPage = page
        crudeDebuggerPrint('''deleteDimension.py:16  	        self.drawingPageWidth = width ''')
        self.drawingPageWidth = width
        crudeDebuggerPrint('''deleteDimension.py:17  	        self.drawingPageHeight = height ''')
        self.drawingPageHeight = height
        crudeDebuggerPrint('''deleteDimension.py:18  	        self.VRT_ox = VRT_ox ''')
        self.VRT_ox = VRT_ox
        crudeDebuggerPrint('''deleteDimension.py:19  	        self.VRT_oy = VRT_oy ''')
        self.VRT_oy = VRT_oy
        crudeDebuggerPrint('''deleteDimension.py:20  	        self.VRT_scale = VRT_scale ''')
        self.VRT_scale = VRT_scale
        crudeDebuggerPrint('''deleteDimension.py:21  	        self.snapHint = snapHint ''')
        self.snapHint = snapHint
        
        crudeDebuggerPrint('''deleteDimension.py:23  	        debugPrint(3, 'adding graphics objects to scene') ''')
        debugPrint(3, 'adding graphics objects to scene')
        crudeDebuggerPrint('''deleteDimension.py:24  	        graphicsScene.addItem( snapHint ) ''')
        graphicsScene.addItem( snapHint )
        crudeDebuggerPrint('''deleteDimension.py:25  	        self.cleanUpList = [snapHint] ''')
        self.cleanUpList = [snapHint]
        crudeDebuggerPrint('''deleteDimension.py:26  	        snapHint.hide() ''')
        snapHint.hide()
        crudeDebuggerPrint('''deleteDimension.py:27  	        graphicsScene.addItem( self ) ''')
        graphicsScene.addItem( self )
        crudeDebuggerPrint('''deleteDimension.py:28  	        self.setRect(0, 0, width, height) ''')
        self.setRect(0, 0, width, height)
        crudeDebuggerPrint('''deleteDimension.py:29  	        self.generateSnapPoints() ''')
        self.generateSnapPoints()
        crudeDebuggerPrint('''deleteDimension.py:30  	        self.setAcceptHoverEvents(True) ''')
        self.setAcceptHoverEvents(True)
        crudeDebuggerPrint('''deleteDimension.py:31  	        self.setFlag( QtGui.QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True ) ''')
        self.setFlag( QtGui.QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True )
        crudeDebuggerPrint('''deleteDimension.py:32  	        self.cleanedUp = False ''')
        self.cleanedUp = False

    def generateSnapPoints(self):
        crudeDebuggerPrint('''deleteDimension.py:35  	        points = [] ''')
        points = []
        crudeDebuggerPrint('''deleteDimension.py:36  	        for obj in self.drawingPage.Group: ''')
        for obj in self.drawingPage.Group:
            crudeDebuggerPrint('''deleteDimension.py:37  	            if obj.Name.startswith('dim'): ''')
            if obj.Name.startswith('dim'):
                crudeDebuggerPrint('''deleteDimension.py:38  	                svg = SvgXMLTreeNode(obj.ViewResult, 0) ''')
                svg = SvgXMLTreeNode(obj.ViewResult, 0)
                crudeDebuggerPrint('''deleteDimension.py:39  	                points = points + svg.textAnchorSnapPoints() ''')
                points = points + svg.textAnchorSnapPoints()
        crudeDebuggerPrint('''deleteDimension.py:40  	        self.snapX = numpy.array( [p[0] for p in points] ) ''')
        self.snapX = numpy.array( [p[0] for p in points] )
        crudeDebuggerPrint('''deleteDimension.py:41  	        self.snapY = numpy.array( [p[1] for p in points] ) ''')
        self.snapY = numpy.array( [p[1] for p in points] )
        crudeDebuggerPrint('''deleteDimension.py:42  	        for x,y in zip(self.snapX, self.snapY): ''')
        for x,y in zip(self.snapX, self.snapY):
            crudeDebuggerPrint('''deleteDimension.py:43  	            self.graphicsScene.addEllipse( x*self.VRT_scale + self.VRT_ox-4, y*self.VRT_scale + self.VRT_oy-4, 8, 8, QtGui.QPen(QtGui.QColor(255,0,0)), QtGui.QBrush(QtGui.QColor(127,0,0))) ''')
            self.graphicsScene.addEllipse( x*self.VRT_scale + self.VRT_ox-4, y*self.VRT_scale + self.VRT_oy-4, 8, 8, QtGui.QPen(QtGui.QColor(255,0,0)), QtGui.QBrush(QtGui.QColor(127,0,0)))
                
    def mousePressEvent( self, event ):
        crudeDebuggerPrint('''deleteDimension.py:46  	        if event.button() == QtCore.Qt.MouseButton.LeftButton: ''')
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            crudeDebuggerPrint('''deleteDimension.py:47  	            pos = event.scenePos() ''')
            pos = event.scenePos()
            crudeDebuggerPrint('''deleteDimension.py:48  	            x = ( pos.x() - self.VRT_ox ) / self.VRT_scale ''')
            x = ( pos.x() - self.VRT_ox ) / self.VRT_scale
            crudeDebuggerPrint('''deleteDimension.py:49  	            y = ( pos.y() - self.VRT_oy ) / self.VRT_scale ''')
            y = ( pos.y() - self.VRT_oy ) / self.VRT_scale
            crudeDebuggerPrint('''deleteDimension.py:50  	            if self.findSnapPoint(x, y) <> None : ''')
            if self.findSnapPoint(x, y) <> None :
                crudeDebuggerPrint('''deleteDimension.py:51  	                x, y = self.findSnapPoint(x, y) ''')
                x, y = self.findSnapPoint(x, y)
                crudeDebuggerPrint('''deleteDimension.py:52  	                for obj in self.drawingPage.Group: ''')
                for obj in self.drawingPage.Group:
                    crudeDebuggerPrint('''deleteDimension.py:53  	                    if obj.Name.startswith('dim'): ''')
                    if obj.Name.startswith('dim'):
                        crudeDebuggerPrint('''deleteDimension.py:54  	                        svg = SvgXMLTreeNode(obj.ViewResult, 0) ''')
                        svg = SvgXMLTreeNode(obj.ViewResult, 0)
                        crudeDebuggerPrint('''deleteDimension.py:55  	                        if (x,y) in svg.textAnchorSnapPoints(): ''')
                        if (x,y) in svg.textAnchorSnapPoints():
                            crudeDebuggerPrint('''deleteDimension.py:56  	                            debugPrint(2, 'deleting dimension %s' % obj.Name) ''')
                            debugPrint(2, 'deleting dimension %s' % obj.Name)
                            crudeDebuggerPrint('''deleteDimension.py:57  	                            App.ActiveDocument.removeObject(obj.Name) ''')
                            App.ActiveDocument.removeObject(obj.Name)
                            crudeDebuggerPrint('''deleteDimension.py:58  	                            self.cleanUp() ''')
                            self.cleanUp()
                            crudeDebuggerPrint('''deleteDimension.py:59  	                            break ''')
                            break
        elif event.button() == QtCore.Qt.MouseButton.RightButton:
            crudeDebuggerPrint('''deleteDimension.py:61  	            self.cleanUp() ''')
            self.cleanUp()

    def hoverMoveEvent(self, event):
        crudeDebuggerPrint('''deleteDimension.py:64  	        pos = event.scenePos() ''')
        pos = event.scenePos()
        crudeDebuggerPrint('''deleteDimension.py:65  	        x = ( pos.x() - self.VRT_ox )/ self.VRT_scale ''')
        x = ( pos.x() - self.VRT_ox )/ self.VRT_scale
        crudeDebuggerPrint('''deleteDimension.py:66  	        y = ( pos.y() - self.VRT_oy )/ self.VRT_scale ''')
        y = ( pos.y() - self.VRT_oy )/ self.VRT_scale
        crudeDebuggerPrint('''deleteDimension.py:67  	        snapPoint = self.findSnapPoint(x, y) ''')
        snapPoint = self.findSnapPoint(x, y)
        crudeDebuggerPrint('''deleteDimension.py:68  	        if snapPoint <> None: ''')
        if snapPoint <> None:
            crudeDebuggerPrint('''deleteDimension.py:69  	            debugPrint(4, 'updating snap point position') ''')
            debugPrint(4, 'updating snap point position')
            crudeDebuggerPrint('''deleteDimension.py:70  	            self.snapHint.setPos( snapPoint[0]* self.VRT_scale + self.VRT_ox-8, ''')
            self.snapHint.setPos( snapPoint[0]* self.VRT_scale + self.VRT_ox-8, 
                                  snapPoint[1]* self.VRT_scale + self.VRT_oy-8 )
            crudeDebuggerPrint('''deleteDimension.py:72  	            self.snapHint.show() ''')
            self.snapHint.show()
        else:
            crudeDebuggerPrint('''deleteDimension.py:74  	            self.snapHint.hide() ''')
            self.snapHint.hide()
    

crudeDebuggerPrint('''deleteDimension.py:77  	moduleGlobals = {} ''')
moduleGlobals = {}
class DeleteDimension:
    def Activated(self):
        crudeDebuggerPrint('''deleteDimension.py:80  	        moduleGlobals.update(get_FreeCAD_drawing_variables()) ''')
        moduleGlobals.update(get_FreeCAD_drawing_variables())
        crudeDebuggerPrint('''deleteDimension.py:81  	        if not moduleGlobals.has_key('deletionRect') or not moduleGlobals['deletionRect'].cleanedUp : ''')
        if not moduleGlobals.has_key('deletionRect') or not moduleGlobals['deletionRect'].cleanedUp :
            crudeDebuggerPrint('''deleteDimension.py:82  	            debugPrint(4, 'creating snapHint ellipse') ''')
            debugPrint(4, 'creating snapHint ellipse')
            crudeDebuggerPrint('''deleteDimension.py:83  	            snapHint = QtGui.QGraphicsEllipseItem(0, 0, 16, 16) ''')
            snapHint = QtGui.QGraphicsEllipseItem(0, 0, 16, 16)
            crudeDebuggerPrint('''deleteDimension.py:84  	            snapHint.setPen( QtGui.QPen(QtGui.QColor(150,0,0)) ) ''')
            snapHint.setPen( QtGui.QPen(QtGui.QColor(150,0,0)) )
            crudeDebuggerPrint('''deleteDimension.py:85  	            debugPrint(3, 'Initializing DeleteRect') ''')
            debugPrint(3, 'Initializing DeleteRect')
            crudeDebuggerPrint('''deleteDimension.py:86  	            deletionRect = DeletionRect() ''')
            deletionRect = DeletionRect()
            crudeDebuggerPrint('''deleteDimension.py:87  	            moduleGlobals.update(locals()) ''')
            moduleGlobals.update(locals())
            crudeDebuggerPrint('''deleteDimension.py:88  	            del moduleGlobals['self'] ''')
            del moduleGlobals['self']
        
        crudeDebuggerPrint('''deleteDimension.py:90  	        moduleGlobals['deletionRect'].activate(**moduleGlobals) ''')
        moduleGlobals['deletionRect'].activate(**moduleGlobals)
        
    def GetResources(self): 
        crudeDebuggerPrint('''deleteDimension.py:93  	        return { ''')
        return {
            'Pixmap' : os.path.join( __dir__ , 'deleteDimension.svg' ) , 
            'MenuText': 'Delete Dimension', 
            'ToolTip': 'Delete a dimension'
            } 

crudeDebuggerPrint('''deleteDimension.py:99  	FreeCADGui.addCommand('deleteDimension', DeleteDimension()) ''')
FreeCADGui.addCommand('deleteDimension', DeleteDimension())