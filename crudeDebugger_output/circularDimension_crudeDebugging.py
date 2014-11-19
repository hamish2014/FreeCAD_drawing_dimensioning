from crudeDebugger import crudeDebuggerPrint
crudeDebuggerPrint('''circularDimension.py:0  	import numpy ''')
import numpy
crudeDebuggerPrint('''circularDimension.py:1  	from PySide import QtGui, QtCore, QtSvg ''')
from PySide import QtGui, QtCore, QtSvg
crudeDebuggerPrint('''circularDimension.py:2  	import FreeCAD as App ''')
import FreeCAD as App
crudeDebuggerPrint('''circularDimension.py:3  	import FreeCADGui, Part, os ''')
import FreeCADGui, Part, os
crudeDebuggerPrint('''circularDimension.py:4  	from dimensioning import debugPrint, __dir__, get_FreeCAD_drawing_variables, DimensioningRectPrototype ''')
from dimensioning import debugPrint, __dir__, get_FreeCAD_drawing_variables, DimensioningRectPrototype
crudeDebuggerPrint('''circularDimension.py:5  	from XMLlib import SvgXMLTreeNode ''')
from XMLlib import SvgXMLTreeNode
crudeDebuggerPrint('''circularDimension.py:6  	from dimensionSvgConstructor import circularDimensionSVG ''')
from dimensionSvgConstructor import circularDimensionSVG


class CircularDimensioningRect( DimensioningRectPrototype ):

    def activate(self, graphicsScene, graphicsView, page, width, height, 
                 VRT_scale, VRT_ox, VRT_oy, 
                 snapHint, dimPreview, dimSVGRenderer, **otherKWs):
        ' called each time before dimensioning '
        crudeDebuggerPrint('''circularDimension.py:15  	        self.graphicsScene = graphicsScene ''')
        self.graphicsScene = graphicsScene
        crudeDebuggerPrint('''circularDimension.py:16  	        self.graphicsView = graphicsView ''')
        self.graphicsView = graphicsView
        crudeDebuggerPrint('''circularDimension.py:17  	        self.drawingPage = page ''')
        self.drawingPage = page
        crudeDebuggerPrint('''circularDimension.py:18  	        self.drawingPageWidth = width ''')
        self.drawingPageWidth = width
        crudeDebuggerPrint('''circularDimension.py:19  	        self.drawingPageHeight = height ''')
        self.drawingPageHeight = height
        crudeDebuggerPrint('''circularDimension.py:20  	        self.VRT_ox = VRT_ox ''')
        self.VRT_ox = VRT_ox
        crudeDebuggerPrint('''circularDimension.py:21  	        self.VRT_oy = VRT_oy ''')
        self.VRT_oy = VRT_oy
        crudeDebuggerPrint('''circularDimension.py:22  	        self.VRT_scale = VRT_scale ''')
        self.VRT_scale = VRT_scale
        crudeDebuggerPrint('''circularDimension.py:23  	        self.snapHint = snapHint ''')
        self.snapHint = snapHint
        crudeDebuggerPrint('''circularDimension.py:24  	        self.dimPreview = dimPreview ''')
        self.dimPreview = dimPreview
        crudeDebuggerPrint('''circularDimension.py:25  	        self.dimSVGRenderer = dimSVGRenderer ''')
        self.dimSVGRenderer = dimSVGRenderer

        crudeDebuggerPrint('''circularDimension.py:27  	        self.action_ind = 0 ''')
        self.action_ind = 0
        crudeDebuggerPrint('''circularDimension.py:28  	        self.dim_svg_KWs = dict( ''')
        self.dim_svg_KWs = dict(
            svgParms='width="%(width)i" height="%(height)i" transform="translate( %(VRT_ox)f, %(VRT_oy)f) scale( %(VRT_scale)f, %(VRT_scale)f)"' % locals(),
            svgTag='svg'
            )
        
        crudeDebuggerPrint('''circularDimension.py:33  	        debugPrint(3, 'adding graphicsScene Objects for aiding to dimensioning to scene') ''')
        debugPrint(3, 'adding graphicsScene Objects for aiding to dimensioning to scene')
        crudeDebuggerPrint('''circularDimension.py:34  	        graphicsScene.addItem( snapHint ) ''')
        graphicsScene.addItem( snapHint )
        crudeDebuggerPrint('''circularDimension.py:35  	        snapHint.hide() ''')
        snapHint.hide()
        crudeDebuggerPrint('''circularDimension.py:36  	        graphicsScene.addItem( dimPreview ) ''')
        graphicsScene.addItem( dimPreview )
        crudeDebuggerPrint('''circularDimension.py:37  	        dimPreview.hide() ''')
        dimPreview.hide()
        crudeDebuggerPrint('''circularDimension.py:38  	        self.cleanUpList = [ snapHint, dimPreview ] ''')
        self.cleanUpList = [ snapHint, dimPreview ]
        crudeDebuggerPrint('''circularDimension.py:39  	        self.cleanedUp = False ''')
        self.cleanedUp = False

        crudeDebuggerPrint('''circularDimension.py:41  	        self.setRect(0, 0, width, height) ''')
        self.setRect(0, 0, width, height)
        crudeDebuggerPrint('''circularDimension.py:42  	        graphicsScene.addItem( self ) ''')
        graphicsScene.addItem( self )
        crudeDebuggerPrint('''circularDimension.py:43  	        self.generateSnapPoints() ''')
        self.generateSnapPoints()
        crudeDebuggerPrint('''circularDimension.py:44  	        self.setAcceptHoverEvents(True) ''')
        self.setAcceptHoverEvents(True)
        crudeDebuggerPrint('''circularDimension.py:45  	        self.setFlag( QtGui.QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True ) ''')
        self.setFlag( QtGui.QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True )
        crudeDebuggerPrint('''circularDimension.py:46  	        debugPrint(3, 'CircularDimensioningRect.Activated') ''')
        debugPrint(3, 'CircularDimensioningRect.Activated')

    def generateSnapPoints(self):
        crudeDebuggerPrint('''circularDimension.py:49  	        points = [] ''')
        points = []
        crudeDebuggerPrint('''circularDimension.py:50  	        for obj in self.drawingPage.Group : ''')
        for obj in self.drawingPage.Group :
            crudeDebuggerPrint('''circularDimension.py:51  	            if not obj.Name.startswith('dim') and len(obj.ViewResult.strip()) > 0: ''')
            if not obj.Name.startswith('dim') and len(obj.ViewResult.strip()) > 0:
                crudeDebuggerPrint('''circularDimension.py:52  	                svg = SvgXMLTreeNode(obj.ViewResult, 0) ''')
                svg = SvgXMLTreeNode(obj.ViewResult, 0)
                crudeDebuggerPrint('''circularDimension.py:53  	                points = points + svg.circularDimensioningSnapPoints() ''')
                points = points + svg.circularDimensioningSnapPoints()
        crudeDebuggerPrint('''circularDimension.py:54  	        self.dimScale = 1.0/ svg.scaling() ''')
        self.dimScale = 1.0/ svg.scaling()
        crudeDebuggerPrint('''circularDimension.py:55  	        self.snapX = numpy.array( [p[0] for p in points] ) ''')
        self.snapX = numpy.array( [p[0] for p in points] )
        crudeDebuggerPrint('''circularDimension.py:56  	        self.snapY = numpy.array( [p[1] for p in points] ) ''')
        self.snapY = numpy.array( [p[1] for p in points] )
        crudeDebuggerPrint('''circularDimension.py:57  	        for x,y in zip(self.snapX, self.snapY): ''')
        for x,y in zip(self.snapX, self.snapY):
            crudeDebuggerPrint('''circularDimension.py:58  	            self.graphicsScene.addEllipse( x*self.VRT_scale + self.VRT_ox-4, y*self.VRT_scale + self.VRT_oy-4, 8, 8, ''')
            self.graphicsScene.addEllipse( x*self.VRT_scale + self.VRT_ox-4, y*self.VRT_scale + self.VRT_oy-4, 8, 8, 
                                           QtGui.QPen(QtGui.QColor(0,255,0)), QtGui.QBrush(QtGui.QColor(0,155,0)))

    def mousePressEvent( self, event ):
        crudeDebuggerPrint('''circularDimension.py:62  	        if event.button() == QtCore.Qt.MouseButton.LeftButton: ''')
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            crudeDebuggerPrint('''circularDimension.py:63  	            pos = event.scenePos() ''')
            pos = event.scenePos()
            crudeDebuggerPrint('''circularDimension.py:64  	            x = ( pos.x() - self.VRT_ox )/ self.VRT_scale ''')
            x = ( pos.x() - self.VRT_ox )/ self.VRT_scale
            crudeDebuggerPrint('''circularDimension.py:65  	            y = ( pos.y() - self.VRT_oy )/ self.VRT_scale ''')
            y = ( pos.y() - self.VRT_oy )/ self.VRT_scale
            crudeDebuggerPrint('''circularDimension.py:66  	            debugPrint(3, 'mousePressEvent: x %f, y %f' % (x, y)) ''')
            debugPrint(3, 'mousePressEvent: x %f, y %f' % (x, y))
            crudeDebuggerPrint('''circularDimension.py:67  	            if self.action_ind == 0: ''')
            if self.action_ind == 0:
                crudeDebuggerPrint('''circularDimension.py:68  	                if self.findSnapPoint(x, y) <> None : ''')
                if self.findSnapPoint(x, y) <> None :
                    crudeDebuggerPrint('''circularDimension.py:69  	                    self.point1 = self.findSnapPoint(x, y) ''')
                    self.point1 = self.findSnapPoint(x, y)
                    crudeDebuggerPrint('''circularDimension.py:70  	                    debugPrint(2, 'center selected at x=%3.1f y=%3.1f' % (x,y)) ''')
                    debugPrint(2, 'center selected at x=%3.1f y=%3.1f' % (x,y))
                    crudeDebuggerPrint('''circularDimension.py:71  	                    for obj in self.drawingPage.Group : ''')
                    for obj in self.drawingPage.Group :
                        crudeDebuggerPrint('''circularDimension.py:72  	                        if not obj.Name.startswith('dim') and len(obj.ViewResult.strip()) > 0: ''')
                        if not obj.Name.startswith('dim') and len(obj.ViewResult.strip()) > 0:
                            crudeDebuggerPrint('''circularDimension.py:73  	                            svg = SvgXMLTreeNode(obj.ViewResult, 0) ''')
                            svg = SvgXMLTreeNode(obj.ViewResult, 0)
                            crudeDebuggerPrint('''circularDimension.py:74  	                            for element in svg.getAllElements(): ''')
                            for element in svg.getAllElements():
                                crudeDebuggerPrint('''circularDimension.py:75  	                                element.calculate_local_snap_points() ''')
                                element.calculate_local_snap_points()
                                crudeDebuggerPrint('''circularDimension.py:76  	                                if self.point1 in element.LSP_circularDimensioning : ''')
                                if self.point1 in element.LSP_circularDimensioning :
                                    crudeDebuggerPrint('''circularDimension.py:77  	                                    if element.tag == 'path': ''')
                                    if element.tag == 'path':
                                        crudeDebuggerPrint('''circularDimension.py:78  	                                        self.radius = float(element.parms['r']) ''')
                                        self.radius = float(element.parms['r'])
                                    else:
                                        crudeDebuggerPrint('''circularDimension.py:80  	                                        self.radius = float(element.parms['r']) / self.dimScale ''')
                                        self.radius = float(element.parms['r']) / self.dimScale
                                    crudeDebuggerPrint('''circularDimension.py:81  	                                    debugPrint(2, 'radius=%3.1f' % (self.radius)) ''')
                                    debugPrint(2, 'radius=%3.1f' % (self.radius))
                                    crudeDebuggerPrint('''circularDimension.py:82  	                                    break ''')
                                    break
                            crudeDebuggerPrint('''circularDimension.py:83  	                            debugPrint(4,'done') ''')
                            debugPrint(4,'done')
                    crudeDebuggerPrint('''circularDimension.py:84  	                    if not hasattr(self,'radius'): ''')
                    if not hasattr(self,'radius'):
                        crudeDebuggerPrint('''circularDimension.py:85  	                        raise RuntimeError, "could not find cicle with center at %s" % self.point1 ''')
                        raise RuntimeError, "could not find cicle with center at %s" % self.point1 
                    crudeDebuggerPrint('''circularDimension.py:86  	                    self.action_ind = self.action_ind + 1 ''')
                    self.action_ind = self.action_ind + 1
                    crudeDebuggerPrint('''circularDimension.py:87  	                    self.snapHint.hide() ''')
                    self.snapHint.hide()
            elif self.action_ind == 1:
                crudeDebuggerPrint('''circularDimension.py:89  	                self.point2 = x,y ''')
                self.point2 = x,y
                crudeDebuggerPrint('''circularDimension.py:90  	                debugPrint(2, 'dimension radial direction point set to x=%3.1f y=%3.1f' % (x,y)) ''')
                debugPrint(2, 'dimension radial direction point set to x=%3.1f y=%3.1f' % (x,y))
                crudeDebuggerPrint('''circularDimension.py:91  	                self.action_ind = self.action_ind + 1 ''')
                self.action_ind = self.action_ind + 1
            elif self.action_ind == 2:
                crudeDebuggerPrint('''circularDimension.py:93  	                self.point3 = x, y ''')
                self.point3 = x, y
                crudeDebuggerPrint('''circularDimension.py:94  	                debugPrint(2, 'radius dimension tail defining point set to x=%3.1f y=%3.1f' % (x,y)) ''')
                debugPrint(2, 'radius dimension tail defining point set to x=%3.1f y=%3.1f' % (x,y))
                crudeDebuggerPrint('''circularDimension.py:95  	                self.action_ind = self.action_ind + 1 ''')
                self.action_ind = self.action_ind + 1
            else: #'placeDimensionText'
                crudeDebuggerPrint('''circularDimension.py:97  	                XML = circularDimensionSVG( self.point1[0], self.point1[1], self.radius, ''')
                XML = circularDimensionSVG( self.point1[0], self.point1[1], self.radius,
                                          self.point2[0], self.point2[1], 
                                          self.point3[0], self.point3[1], 
                                          x, y, dimScale=self.dimScale)
                crudeDebuggerPrint('''circularDimension.py:101  	                if XML <> None: ''')
                if XML <> None:
                    crudeDebuggerPrint('''circularDimension.py:102  	                    debugPrint(3, XML) ''')
                    debugPrint(3, XML)
                    crudeDebuggerPrint('''circularDimension.py:103  	                    viewName = 'dim001' ''')
                    viewName = 'dim001'
                    crudeDebuggerPrint('''circularDimension.py:104  	                    while hasattr(App.ActiveDocument, viewName): ''')
                    while hasattr(App.ActiveDocument, viewName):
                        crudeDebuggerPrint('''circularDimension.py:105  	                        viewName = 'dim%03i' % (int(viewName[3:])+1) ''')
                        viewName = 'dim%03i' % (int(viewName[3:])+1)
                    crudeDebuggerPrint('''circularDimension.py:106  	                    debugPrint(2, 'creating dimension %s' % viewName) ''')
                    debugPrint(2, 'creating dimension %s' % viewName)
                    crudeDebuggerPrint('''circularDimension.py:107  	                    App.ActiveDocument.addObject('Drawing::FeatureView',viewName) ''')
                    App.ActiveDocument.addObject('Drawing::FeatureView',viewName)
                    crudeDebuggerPrint('''circularDimension.py:108  	                    App.ActiveDocument.getObject(viewName).ViewResult = XML ''')
                    App.ActiveDocument.getObject(viewName).ViewResult = XML                    
                    crudeDebuggerPrint('''circularDimension.py:109  	                    self.drawingPage.addObject(App.ActiveDocument.getObject(viewName)) ''')
                    self.drawingPage.addObject(App.ActiveDocument.getObject(viewName))
                crudeDebuggerPrint('''circularDimension.py:110  	                self.cleanUp() ''')
                self.cleanUp()

        elif event.button() == QtCore.Qt.MouseButton.RightButton:
            crudeDebuggerPrint('''circularDimension.py:113  	            if self.action_ind > 0: ''')
            if self.action_ind > 0:
                crudeDebuggerPrint('''circularDimension.py:114  	                self.action_ind = self.action_ind - 1 ''')
                self.action_ind = self.action_ind - 1
            else:
                crudeDebuggerPrint('''circularDimension.py:116  	                self.cleanUp() ''')
                self.cleanUp()

    def hoverMoveEvent(self, event):
        crudeDebuggerPrint('''circularDimension.py:119  	        pos = event.scenePos() ''')
        pos = event.scenePos()
        crudeDebuggerPrint('''circularDimension.py:120  	        x = ( pos.x() - self.VRT_ox )/ self.VRT_scale ''')
        x = ( pos.x() - self.VRT_ox )/ self.VRT_scale
        crudeDebuggerPrint('''circularDimension.py:121  	        y = ( pos.y() - self.VRT_oy )/ self.VRT_scale ''')
        y = ( pos.y() - self.VRT_oy )/ self.VRT_scale
        crudeDebuggerPrint('''circularDimension.py:122  	        debugPrint(4, 'hoverMoveEvent: x %f, y %f'%(x,y)) ''')
        debugPrint(4, 'hoverMoveEvent: x %f, y %f'%(x,y))
        crudeDebuggerPrint('''circularDimension.py:123  	        XML = None ''')
        XML = None
        crudeDebuggerPrint('''circularDimension.py:124  	        if self.action_ind == 0 : ''')
        if self.action_ind == 0 :
            crudeDebuggerPrint('''circularDimension.py:125  	            snapPoint = self.findSnapPoint(x, y) ''')
            snapPoint = self.findSnapPoint(x, y)
            crudeDebuggerPrint('''circularDimension.py:126  	            if snapPoint <> None: ''')
            if snapPoint <> None:
                crudeDebuggerPrint('''circularDimension.py:127  	                debugPrint(4, 'updating snap point position') ''')
                debugPrint(4, 'updating snap point position')
                crudeDebuggerPrint('''circularDimension.py:128  	                self.snapHint.setPos( snapPoint[0]*self.VRT_scale + self.VRT_ox-8, snapPoint[1]*self.VRT_scale + self.VRT_oy-8 ) ''')
                self.snapHint.setPos( snapPoint[0]*self.VRT_scale + self.VRT_ox-8, snapPoint[1]*self.VRT_scale + self.VRT_oy-8 )
                crudeDebuggerPrint('''circularDimension.py:129  	                self.snapHint.show() ''')
                self.snapHint.show()
            else:
                crudeDebuggerPrint('''circularDimension.py:131  	                self.snapHint.hide() ''')
                self.snapHint.hide()
        elif self.action_ind == 1 :
            crudeDebuggerPrint('''circularDimension.py:133  	            XML = circularDimensionSVG( self.point1[0], self.point1[1], self.radius, x, y, dimScale=self.dimScale, **self.dim_svg_KWs ) ''')
            XML = circularDimensionSVG( self.point1[0], self.point1[1], self.radius, x, y, dimScale=self.dimScale, **self.dim_svg_KWs )
        elif self.action_ind == 2:
            crudeDebuggerPrint('''circularDimension.py:135  	            XML = circularDimensionSVG( self.point1[0], self.point1[1], self.radius, ''')
            XML = circularDimensionSVG( self.point1[0], self.point1[1], self.radius, 
                                self.point2[0], self.point2[1], x, y, dimScale=self.dimScale, **self.dim_svg_KWs )
        else: #self.actions[self.action_ind] == 'placeDimensionText'
            crudeDebuggerPrint('''circularDimension.py:138  	            XML = circularDimensionSVG( self.point1[0], self.point1[1], self.radius, ''')
            XML = circularDimensionSVG( self.point1[0], self.point1[1], self.radius, 
                                self.point2[0], self.point2[1], 
                                self.point3[0], self.point3[1], 
                                x, y, dimScale=self.dimScale,**self.dim_svg_KWs )
        crudeDebuggerPrint('''circularDimension.py:142  	        if XML <> None: ''')
        if XML <> None:
            crudeDebuggerPrint('''circularDimension.py:143  	            self.dimSVGRenderer.load( QtCore.QByteArray( XML ) ) ''')
            self.dimSVGRenderer.load( QtCore.QByteArray( XML ) )
            crudeDebuggerPrint('''circularDimension.py:144  	            self.dimPreview.update() ''')
            self.dimPreview.update()
            crudeDebuggerPrint('''circularDimension.py:145  	            self.dimPreview.show() ''')
            self.dimPreview.show()
        else:
            crudeDebuggerPrint('''circularDimension.py:147  	            self.dimPreview.hide() ''')
            self.dimPreview.hide()
    


crudeDebuggerPrint('''circularDimension.py:151  	moduleGlobals = {} ''')
moduleGlobals = {}
class circularDimension:
    "this class will create a line after the user clicked 2 points on the screen"
    def Activated(self):
        crudeDebuggerPrint('''circularDimension.py:155  	        moduleGlobals.update(get_FreeCAD_drawing_variables()) ''')
        moduleGlobals.update(get_FreeCAD_drawing_variables())        
        crudeDebuggerPrint('''circularDimension.py:156  	        if not moduleGlobals.has_key('dimensioningRect') or not moduleGlobals['dimensioningRect'].cleanedUp: ''')
        if not moduleGlobals.has_key('dimensioningRect') or not moduleGlobals['dimensioningRect'].cleanedUp: 
            crudeDebuggerPrint('''circularDimension.py:157  	            # then initialize graphicsScene Objects, otherwise dont recreate objects. ''')
            # then initialize graphicsScene Objects, otherwise dont recreate objects. 
            crudeDebuggerPrint('''circularDimension.py:158  	            # initializing dimPreview is particularly troublesome, as in FreeCAD 0.15 this is unstable and occasionally causes FreeCAD to crash. ''')
            # initializing dimPreview is particularly troublesome, as in FreeCAD 0.15 this is unstable and occasionally causes FreeCAD to crash.
            crudeDebuggerPrint('''circularDimension.py:159  	            debugPrint(4, 'creating snapHint ellipse') ''')
            debugPrint(4, 'creating snapHint ellipse')
            crudeDebuggerPrint('''circularDimension.py:160  	            snapHint = QtGui.QGraphicsEllipseItem(0, 0, 16, 16) ''')
            snapHint = QtGui.QGraphicsEllipseItem(0, 0, 16, 16)
            crudeDebuggerPrint('''circularDimension.py:161  	            snapHint.setPen( QtGui.QPen(QtGui.QColor(150,0,0)) ) ''')
            snapHint.setPen( QtGui.QPen(QtGui.QColor(150,0,0)) )

            crudeDebuggerPrint('''circularDimension.py:163  	            debugPrint(4, 'creating dimPreview') ''')
            debugPrint(4, 'creating dimPreview')
            crudeDebuggerPrint('''circularDimension.py:164  	            dimPreview = QtSvg.QGraphicsSvgItem() ''')
            dimPreview = QtSvg.QGraphicsSvgItem()
            crudeDebuggerPrint('''circularDimension.py:165  	            dimSVGRenderer = QtSvg.QSvgRenderer() ''')
            dimSVGRenderer = QtSvg.QSvgRenderer()
            crudeDebuggerPrint('''circularDimension.py:166  	            dimSVGRenderer.load( QtCore.QByteArray( ''' +"'''" +'''<svg width="%i" height="%i"> </svg>''' +"'''" +''' % (moduleGlobals['width'], moduleGlobals['height']) ) ) ''')
            dimSVGRenderer.load( QtCore.QByteArray( '''<svg width="%i" height="%i"> </svg>''' % (moduleGlobals['width'], moduleGlobals['height']) ) )
            crudeDebuggerPrint('''circularDimension.py:167  	            dimPreview.setSharedRenderer( dimSVGRenderer ) ''')
            dimPreview.setSharedRenderer( dimSVGRenderer )

            crudeDebuggerPrint('''circularDimension.py:169  	            debugPrint(4, 'Adding CircularDimensioningRect to graphicsScene') ''')
            debugPrint(4, 'Adding CircularDimensioningRect to graphicsScene')
            crudeDebuggerPrint('''circularDimension.py:170  	            dimensioningRect = CircularDimensioningRect() ''')
            dimensioningRect = CircularDimensioningRect()

            crudeDebuggerPrint('''circularDimension.py:172  	            moduleGlobals.update(locals()) ''')
            moduleGlobals.update(locals())
            crudeDebuggerPrint('''circularDimension.py:173  	            del moduleGlobals['self'] ''')
            del moduleGlobals['self']
            crudeDebuggerPrint('''circularDimension.py:174  	            assert not moduleGlobals.has_key('moduleGlobals') ''')
            assert not moduleGlobals.has_key('moduleGlobals')
        crudeDebuggerPrint('''circularDimension.py:175  	        moduleGlobals['dimensioningRect'].activate(**moduleGlobals) ''')
        moduleGlobals['dimensioningRect'].activate(**moduleGlobals)
        
    def GetResources(self): 
        crudeDebuggerPrint('''circularDimension.py:178  	        return { ''')
        return {
            'Pixmap' : os.path.join( __dir__ , 'circularDimension.svg' ) , 
            'MenuText': 'Circular Dimension', 
            'ToolTip': 'Creates a circular dimension'
            } 

crudeDebuggerPrint('''circularDimension.py:184  	FreeCADGui.addCommand('circularDimension', circularDimension()) ''')
FreeCADGui.addCommand('circularDimension', circularDimension())