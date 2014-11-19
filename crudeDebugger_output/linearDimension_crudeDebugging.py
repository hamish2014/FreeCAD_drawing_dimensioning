from crudeDebugger import crudeDebuggerPrint
crudeDebuggerPrint('''linearDimension.py:0  	import numpy ''')
import numpy
crudeDebuggerPrint('''linearDimension.py:1  	from PySide import QtGui, QtCore, QtSvg ''')
from PySide import QtGui, QtCore, QtSvg
crudeDebuggerPrint('''linearDimension.py:2  	import FreeCAD as App ''')
import FreeCAD as App
crudeDebuggerPrint('''linearDimension.py:3  	import FreeCADGui, Part, os ''')
import FreeCADGui, Part, os
crudeDebuggerPrint('''linearDimension.py:4  	from dimensioning import debugPrint, __dir__, get_FreeCAD_drawing_variables, DimensioningRectPrototype ''')
from dimensioning import debugPrint, __dir__, get_FreeCAD_drawing_variables, DimensioningRectPrototype
crudeDebuggerPrint('''linearDimension.py:5  	from XMLlib import SvgXMLTreeNode ''')
from XMLlib import SvgXMLTreeNode
crudeDebuggerPrint('''linearDimension.py:6  	from dimensionSvgConstructor import linearDimensionSVG ''')
from dimensionSvgConstructor import linearDimensionSVG


class DimensioningRect( DimensioningRectPrototype ):

    def activate(self, graphicsScene, graphicsView, page, width, height, 
                 VRT_scale, VRT_ox, VRT_oy, 
                 snapHint, dimPreview, dimSVGRenderer, **otherKWs):
        ' called each time before dimensioning '
        crudeDebuggerPrint('''linearDimension.py:15  	        self.graphicsScene = graphicsScene ''')
        self.graphicsScene = graphicsScene
        crudeDebuggerPrint('''linearDimension.py:16  	        self.graphicsView = graphicsView ''')
        self.graphicsView = graphicsView
        crudeDebuggerPrint('''linearDimension.py:17  	        self.drawingPage = page ''')
        self.drawingPage = page
        crudeDebuggerPrint('''linearDimension.py:18  	        self.drawingPageWidth = width ''')
        self.drawingPageWidth = width
        crudeDebuggerPrint('''linearDimension.py:19  	        self.drawingPageHeight = height ''')
        self.drawingPageHeight = height
        crudeDebuggerPrint('''linearDimension.py:20  	        self.VRT_ox = VRT_ox ''')
        self.VRT_ox = VRT_ox
        crudeDebuggerPrint('''linearDimension.py:21  	        self.VRT_oy = VRT_oy ''')
        self.VRT_oy = VRT_oy
        crudeDebuggerPrint('''linearDimension.py:22  	        self.VRT_scale = VRT_scale ''')
        self.VRT_scale = VRT_scale
        crudeDebuggerPrint('''linearDimension.py:23  	        self.snapHint = snapHint ''')
        self.snapHint = snapHint
        crudeDebuggerPrint('''linearDimension.py:24  	        self.dimPreview = dimPreview ''')
        self.dimPreview = dimPreview
        crudeDebuggerPrint('''linearDimension.py:25  	        self.dimSVGRenderer = dimSVGRenderer ''')
        self.dimSVGRenderer = dimSVGRenderer

        crudeDebuggerPrint('''linearDimension.py:27  	        self.action_ind = 0 ''')
        self.action_ind = 0
        crudeDebuggerPrint('''linearDimension.py:28  	        self.actions = ['selectPoint1','selectPoint2','placeDimensionBaseLine','placeDimensionText'] ''')
        self.actions = ['selectPoint1','selectPoint2','placeDimensionBaseLine','placeDimensionText']
        crudeDebuggerPrint('''linearDimension.py:29  	        self.dimPreview_SvgParms = 'width="%(width)i" height="%(height)i" transform="translate( %(VRT_ox)f, %(VRT_oy)f) scale( %(VRT_scale)f, %(VRT_scale)f)"' % locals() ''')
        self.dimPreview_SvgParms = 'width="%(width)i" height="%(height)i" transform="translate( %(VRT_ox)f, %(VRT_oy)f) scale( %(VRT_scale)f, %(VRT_scale)f)"' % locals()

        crudeDebuggerPrint('''linearDimension.py:31  	        debugPrint(3, 'adding graphicsScene Objects for aiding to dimensioning to scene') ''')
        debugPrint(3, 'adding graphicsScene Objects for aiding to dimensioning to scene')
        crudeDebuggerPrint('''linearDimension.py:32  	        graphicsScene.addItem( snapHint ) ''')
        graphicsScene.addItem( snapHint )
        crudeDebuggerPrint('''linearDimension.py:33  	        snapHint.hide() ''')
        snapHint.hide()
        crudeDebuggerPrint('''linearDimension.py:34  	        graphicsScene.addItem( dimPreview ) ''')
        graphicsScene.addItem( dimPreview )
        crudeDebuggerPrint('''linearDimension.py:35  	        dimPreview.hide() ''')
        dimPreview.hide()
        crudeDebuggerPrint('''linearDimension.py:36  	        self.cleanUpList = [ snapHint, dimPreview ] ''')
        self.cleanUpList = [ snapHint, dimPreview ]
        crudeDebuggerPrint('''linearDimension.py:37  	        self.cleanedUp = False ''')
        self.cleanedUp = False

        crudeDebuggerPrint('''linearDimension.py:39  	        self.setRect(0, 0, width, height) ''')
        self.setRect(0, 0, width, height)
        crudeDebuggerPrint('''linearDimension.py:40  	        graphicsScene.addItem( self ) ''')
        graphicsScene.addItem( self )
        crudeDebuggerPrint('''linearDimension.py:41  	        self.generateSnapPoints() ''')
        self.generateSnapPoints()
        crudeDebuggerPrint('''linearDimension.py:42  	        self.setAcceptHoverEvents(True) ''')
        self.setAcceptHoverEvents(True)
        crudeDebuggerPrint('''linearDimension.py:43  	        self.setFlag( QtGui.QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True ) ''')
        self.setFlag( QtGui.QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True )
        crudeDebuggerPrint('''linearDimension.py:44  	        debugPrint(3, 'DimensioningRect.Activated completed') ''')
        debugPrint(3, 'DimensioningRect.Activated completed')

    def generateSnapPoints(self):
        crudeDebuggerPrint('''linearDimension.py:47  	        points = [] ''')
        points = []
        crudeDebuggerPrint('''linearDimension.py:48  	        for obj in self.drawingPage.Group : ''')
        for obj in self.drawingPage.Group :
            crudeDebuggerPrint('''linearDimension.py:49  	            if not obj.Name.startswith('dim') and len(obj.ViewResult.strip()) > 0: ''')
            if not obj.Name.startswith('dim') and len(obj.ViewResult.strip()) > 0:
                crudeDebuggerPrint('''linearDimension.py:50  	                svg = SvgXMLTreeNode(obj.ViewResult, 0) ''')
                svg = SvgXMLTreeNode(obj.ViewResult, 0)
                crudeDebuggerPrint('''linearDimension.py:51  	                points = points + svg.linearDimensioningSnapPoints() ''')
                points = points + svg.linearDimensioningSnapPoints()
        crudeDebuggerPrint('''linearDimension.py:52  	        self.dimScale = 1.0/ svg.scaling() ''')
        self.dimScale = 1.0/ svg.scaling()
        crudeDebuggerPrint('''linearDimension.py:53  	        self.snapX = numpy.array( [p[0] for p in points] ) ''')
        self.snapX = numpy.array( [p[0] for p in points] )
        crudeDebuggerPrint('''linearDimension.py:54  	        self.snapY = numpy.array( [p[1] for p in points] ) ''')
        self.snapY = numpy.array( [p[1] for p in points] )
        crudeDebuggerPrint('''linearDimension.py:55  	        for x,y in zip(self.snapX, self.snapY): ''')
        for x,y in zip(self.snapX, self.snapY):
            crudeDebuggerPrint('''linearDimension.py:56  	            self.graphicsScene.addEllipse( x*self.VRT_scale + self.VRT_ox-4, y*self.VRT_scale + self.VRT_oy-4, 8, 8, ''')
            self.graphicsScene.addEllipse( x*self.VRT_scale + self.VRT_ox-4, y*self.VRT_scale + self.VRT_oy-4, 8, 8, 
                                           QtGui.QPen(QtGui.QColor(0,255,0)), QtGui.QBrush(QtGui.QColor(0,155,0)))

    def mousePressEvent( self, event ):
        crudeDebuggerPrint('''linearDimension.py:60  	        if event.button() == QtCore.Qt.MouseButton.LeftButton: ''')
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            crudeDebuggerPrint('''linearDimension.py:61  	            pos = event.scenePos() ''')
            pos = event.scenePos()
            crudeDebuggerPrint('''linearDimension.py:62  	            x = ( pos.x() - self.VRT_ox )/ self.VRT_scale ''')
            x = ( pos.x() - self.VRT_ox )/ self.VRT_scale
            crudeDebuggerPrint('''linearDimension.py:63  	            y = ( pos.y() - self.VRT_oy )/ self.VRT_scale ''')
            y = ( pos.y() - self.VRT_oy )/ self.VRT_scale
            crudeDebuggerPrint('''linearDimension.py:64  	            debugPrint(3, 'mousePressEvent: x %f, y %f, %s' % (x, y, self.actions[self.action_ind])) ''')
            debugPrint(3, 'mousePressEvent: x %f, y %f, %s' % (x, y, self.actions[self.action_ind]))
            crudeDebuggerPrint('''linearDimension.py:65  	            if self.actions[self.action_ind] == 'selectPoint1': ''')
            if self.actions[self.action_ind] == 'selectPoint1':
                crudeDebuggerPrint('''linearDimension.py:66  	                if self.findSnapPoint(x, y) <> None : ''')
                if self.findSnapPoint(x, y) <> None :
                    crudeDebuggerPrint('''linearDimension.py:67  	                    self.point1 = self.findSnapPoint(x, y) ''')
                    self.point1 = self.findSnapPoint(x, y)
                    crudeDebuggerPrint('''linearDimension.py:68  	                    debugPrint(2, 'point1 set to x=%3.1f y=%3.1f' % (x,y)) ''')
                    debugPrint(2, 'point1 set to x=%3.1f y=%3.1f' % (x,y))
                    crudeDebuggerPrint('''linearDimension.py:69  	                    self.action_ind = self.action_ind + 1 ''')
                    self.action_ind = self.action_ind + 1
            elif self.actions[self.action_ind] == 'selectPoint2':
                crudeDebuggerPrint('''linearDimension.py:71  	                if self.findSnapPoint(x, y) <> None : ''')
                if self.findSnapPoint(x, y) <> None :
                    crudeDebuggerPrint('''linearDimension.py:72  	                    self.point2 = self.findSnapPoint(x, y) ''')
                    self.point2 = self.findSnapPoint(x, y)
                    crudeDebuggerPrint('''linearDimension.py:73  	                    debugPrint(2, 'point2 set to x=%3.1f y=%3.1f' % (x,y)) ''')
                    debugPrint(2, 'point2 set to x=%3.1f y=%3.1f' % (x,y))
                    crudeDebuggerPrint('''linearDimension.py:74  	                    self.action_ind = self.action_ind + 1 ''')
                    self.action_ind = self.action_ind + 1
                    crudeDebuggerPrint('''linearDimension.py:75  	                    self.snapHint.hide() ''')
                    self.snapHint.hide()
            elif self.actions[self.action_ind] == 'placeDimensionBaseLine':
                crudeDebuggerPrint('''linearDimension.py:77  	                self.point3 = x, y ''')
                self.point3 = x, y
                crudeDebuggerPrint('''linearDimension.py:78  	                debugPrint(2, 'point3 set to x=%3.1f y=%3.1f' % (x,y)) ''')
                debugPrint(2, 'point3 set to x=%3.1f y=%3.1f' % (x,y))
                crudeDebuggerPrint('''linearDimension.py:79  	                self.action_ind = self.action_ind + 1 ''')
                self.action_ind = self.action_ind + 1
            else: #'placeDimensionText'
                crudeDebuggerPrint('''linearDimension.py:81  	                self.point4 = x, y ''')
                self.point4 = x, y
                crudeDebuggerPrint('''linearDimension.py:82  	                XML = linearDimensionSVG( self.point1[0], self.point1[1], ''')
                XML = linearDimensionSVG( self.point1[0], self.point1[1],
                                          self.point2[0], self.point2[1], 
                                          self.point3[0], self.point3[1], 
                                          x, y, scale=self.dimScale)
                crudeDebuggerPrint('''linearDimension.py:86  	                if XML <> None: ''')
                if XML <> None:
                    crudeDebuggerPrint('''linearDimension.py:87  	                    debugPrint(3, XML) ''')
                    debugPrint(3, XML)
                    crudeDebuggerPrint('''linearDimension.py:88  	                    viewName = 'dim001' ''')
                    viewName = 'dim001'
                    crudeDebuggerPrint('''linearDimension.py:89  	                    while hasattr(App.ActiveDocument, viewName): ''')
                    while hasattr(App.ActiveDocument, viewName):
                        crudeDebuggerPrint('''linearDimension.py:90  	                        viewName = 'dim%03i' % (int(viewName[3:])+1) ''')
                        viewName = 'dim%03i' % (int(viewName[3:])+1)
                    crudeDebuggerPrint('''linearDimension.py:91  	                    debugPrint(2, 'creating dimension %s' % viewName) ''')
                    debugPrint(2, 'creating dimension %s' % viewName)
                    crudeDebuggerPrint('''linearDimension.py:92  	                    App.ActiveDocument.addObject('Drawing::FeatureView',viewName) ''')
                    App.ActiveDocument.addObject('Drawing::FeatureView',viewName)
                    crudeDebuggerPrint('''linearDimension.py:93  	                    App.ActiveDocument.getObject(viewName).ViewResult = XML ''')
                    App.ActiveDocument.getObject(viewName).ViewResult = XML                    
                    crudeDebuggerPrint('''linearDimension.py:94  	                    self.drawingPage.addObject(App.ActiveDocument.getObject(viewName)) ''')
                    self.drawingPage.addObject(App.ActiveDocument.getObject(viewName))
                crudeDebuggerPrint('''linearDimension.py:95  	                self.cleanUp() ''')
                self.cleanUp()

        elif event.button() == QtCore.Qt.MouseButton.RightButton:
            crudeDebuggerPrint('''linearDimension.py:98  	            if self.action_ind > 0: ''')
            if self.action_ind > 0:
                crudeDebuggerPrint('''linearDimension.py:99  	                self.action_ind = self.action_ind - 1 ''')
                self.action_ind = self.action_ind - 1
            crudeDebuggerPrint('''linearDimension.py:100  	            #else: ''')
            #else:
            crudeDebuggerPrint('''linearDimension.py:101  	            #    self.cleanUp() ''')
            #    self.cleanUp()

    def hoverMoveEvent(self, event):
        crudeDebuggerPrint('''linearDimension.py:104  	        pos = event.scenePos() ''')
        pos = event.scenePos()
        crudeDebuggerPrint('''linearDimension.py:105  	        x = ( pos.x() - self.VRT_ox )/ self.VRT_scale ''')
        x = ( pos.x() - self.VRT_ox )/ self.VRT_scale
        crudeDebuggerPrint('''linearDimension.py:106  	        y = ( pos.y() - self.VRT_oy )/ self.VRT_scale ''')
        y = ( pos.y() - self.VRT_oy )/ self.VRT_scale
        crudeDebuggerPrint('''linearDimension.py:107  	        debugPrint(4, 'hoverMoveEvent: x %f, y %f, %s'%(x,y,self.actions[self.action_ind])) ''')
        debugPrint(4, 'hoverMoveEvent: x %f, y %f, %s'%(x,y,self.actions[self.action_ind]))
        crudeDebuggerPrint('''linearDimension.py:108  	        XML = None ''')
        XML = None
        crudeDebuggerPrint('''linearDimension.py:109  	        if self.actions[self.action_ind] in ['selectPoint1', 'selectPoint2'] : ''')
        if self.actions[self.action_ind] in ['selectPoint1', 'selectPoint2'] :
            crudeDebuggerPrint('''linearDimension.py:110  	            snapPoint = self.findSnapPoint(x, y) ''')
            snapPoint = self.findSnapPoint(x, y)
            crudeDebuggerPrint('''linearDimension.py:111  	            if snapPoint <> None: ''')
            if snapPoint <> None:
                crudeDebuggerPrint('''linearDimension.py:112  	                debugPrint(4, 'updating snap point position') ''')
                debugPrint(4, 'updating snap point position')
                crudeDebuggerPrint('''linearDimension.py:113  	                self.snapHint.setPos( snapPoint[0]*self.VRT_scale + self.VRT_ox-8, snapPoint[1]*self.VRT_scale + self.VRT_oy-8 ) ''')
                self.snapHint.setPos( snapPoint[0]*self.VRT_scale + self.VRT_ox-8, snapPoint[1]*self.VRT_scale + self.VRT_oy-8 )
                crudeDebuggerPrint('''linearDimension.py:114  	                self.snapHint.show() ''')
                self.snapHint.show()
            else:
                crudeDebuggerPrint('''linearDimension.py:116  	                self.snapHint.hide() ''')
                self.snapHint.hide()
        elif self.actions[self.action_ind] == 'placeDimensionBaseLine':
            crudeDebuggerPrint('''linearDimension.py:118  	            XML = linearDimensionSVG( self.point1[0], self.point1[1], ''')
            XML = linearDimensionSVG( self.point1[0], self.point1[1],
                                self.point2[0], self.point2[1], x, y, svgTag='svg', 
                                svgParms = self.dimPreview_SvgParms )
        else: #self.actions[self.action_ind] == 'placeDimensionText'
            crudeDebuggerPrint('''linearDimension.py:122  	            XML = linearDimensionSVG( self.point1[0], self.point1[1], ''')
            XML = linearDimensionSVG( self.point1[0], self.point1[1],
                                self.point2[0], self.point2[1], 
                                self.point3[0], self.point3[1], 
                                x, y, svgTag='svg', scale=self.dimScale, 
                                svgParms = self.dimPreview_SvgParms )
        crudeDebuggerPrint('''linearDimension.py:127  	        if XML <> None: ''')
        if XML <> None:
            crudeDebuggerPrint('''linearDimension.py:128  	            self.dimSVGRenderer.load( QtCore.QByteArray( XML ) ) ''')
            self.dimSVGRenderer.load( QtCore.QByteArray( XML ) )
            crudeDebuggerPrint('''linearDimension.py:129  	            self.dimPreview.update() ''')
            self.dimPreview.update()
            crudeDebuggerPrint('''linearDimension.py:130  	            self.dimPreview.show() ''')
            self.dimPreview.show()
        else:
            crudeDebuggerPrint('''linearDimension.py:132  	            self.dimPreview.hide() ''')
            self.dimPreview.hide()
    


crudeDebuggerPrint('''linearDimension.py:136  	moduleGlobals = {} ''')
moduleGlobals = {}
class linearDimension:
    "this class will create a line after the user clicked 2 points on the screen"
    def Activated(self):
        crudeDebuggerPrint('''linearDimension.py:140  	        moduleGlobals.update(get_FreeCAD_drawing_variables()) ''')
        moduleGlobals.update(get_FreeCAD_drawing_variables())        
        crudeDebuggerPrint('''linearDimension.py:141  	        if not moduleGlobals.has_key('dimensioningRect') or not moduleGlobals['dimensioningRect'].cleanedUp: ''')
        if not moduleGlobals.has_key('dimensioningRect') or not moduleGlobals['dimensioningRect'].cleanedUp: 
            crudeDebuggerPrint('''linearDimension.py:142  	            # then initialize graphicsScene Objects, otherwise dont recreate objects. ''')
            # then initialize graphicsScene Objects, otherwise dont recreate objects. 
            crudeDebuggerPrint('''linearDimension.py:143  	            # initializing dimPreview is particularly troublesome, as in FreeCAD 0.15 this is unstable and occasionally causes FreeCAD to crash. ''')
            # initializing dimPreview is particularly troublesome, as in FreeCAD 0.15 this is unstable and occasionally causes FreeCAD to crash.
            crudeDebuggerPrint('''linearDimension.py:144  	            debugPrint(4, 'creating snapHint ellipse') ''')
            debugPrint(4, 'creating snapHint ellipse')
            crudeDebuggerPrint('''linearDimension.py:145  	            snapHint = QtGui.QGraphicsEllipseItem(0, 0, 16, 16) ''')
            snapHint = QtGui.QGraphicsEllipseItem(0, 0, 16, 16)
            crudeDebuggerPrint('''linearDimension.py:146  	            snapHint.setPen( QtGui.QPen(QtGui.QColor(150,0,0)) ) ''')
            snapHint.setPen( QtGui.QPen(QtGui.QColor(150,0,0)) )

            crudeDebuggerPrint('''linearDimension.py:148  	            debugPrint(4, 'creating dimPreview') ''')
            debugPrint(4, 'creating dimPreview')
            crudeDebuggerPrint('''linearDimension.py:149  	            dimPreview = QtSvg.QGraphicsSvgItem() ''')
            dimPreview = QtSvg.QGraphicsSvgItem()
            crudeDebuggerPrint('''linearDimension.py:150  	            dimSVGRenderer = QtSvg.QSvgRenderer() ''')
            dimSVGRenderer = QtSvg.QSvgRenderer()
            crudeDebuggerPrint('''linearDimension.py:151  	            dimSVGRenderer.load( QtCore.QByteArray( ''' +"'''" +'''<svg width="%i" height="%i"> </svg>''' +"'''" +''' % (moduleGlobals['width'], moduleGlobals['height']) ) ) ''')
            dimSVGRenderer.load( QtCore.QByteArray( '''<svg width="%i" height="%i"> </svg>''' % (moduleGlobals['width'], moduleGlobals['height']) ) )
            crudeDebuggerPrint('''linearDimension.py:152  	            dimPreview.setSharedRenderer( dimSVGRenderer ) ''')
            dimPreview.setSharedRenderer( dimSVGRenderer )

            crudeDebuggerPrint('''linearDimension.py:154  	            debugPrint(4, 'Adding DimensioningRect to graphicsScene') ''')
            debugPrint(4, 'Adding DimensioningRect to graphicsScene')
            crudeDebuggerPrint('''linearDimension.py:155  	            dimensioningRect = DimensioningRect() ''')
            dimensioningRect = DimensioningRect()

            crudeDebuggerPrint('''linearDimension.py:157  	            moduleGlobals.update(locals()) ''')
            moduleGlobals.update(locals())
            crudeDebuggerPrint('''linearDimension.py:158  	            del moduleGlobals['self'] ''')
            del moduleGlobals['self']
            crudeDebuggerPrint('''linearDimension.py:159  	            assert not moduleGlobals.has_key('moduleGlobals') ''')
            assert not moduleGlobals.has_key('moduleGlobals')
        crudeDebuggerPrint('''linearDimension.py:160  	        moduleGlobals['dimensioningRect'].activate(**moduleGlobals) ''')
        moduleGlobals['dimensioningRect'].activate(**moduleGlobals)
        
    def GetResources(self): 
        crudeDebuggerPrint('''linearDimension.py:163  	        return { ''')
        return {
            'Pixmap' : os.path.join( __dir__ , 'linearDimension.svg' ) , 
            'MenuText': 'Linear Dimension', 
            'ToolTip': 'Creates a linear dimension'
            } 

crudeDebuggerPrint('''linearDimension.py:169  	FreeCADGui.addCommand('linearDimension', linearDimension()) ''')
FreeCADGui.addCommand('linearDimension', linearDimension())