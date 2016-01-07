# -*- coding: utf-8 -*-
'''
The biggest problem drawing dimensioning in FreeCAD 0.15 is that drawing objects have no selection support.
This library provides a crude hack to get around this problem.
Specifically, DrawingObject.ViewResults are parsed as to create QGraphicsItems to handle selection.
'''
from XMLlib import SvgXMLTreeNode
from svgLib_dd import SvgPath
import sys, numpy, traceback, pickle
from PySide import QtGui, QtCore, QtSvg
from recomputeDimensions import DrawingViewInfo

defaultMaskBrush = QtGui.QBrush( QtGui.QColor(0,255,0,100) )
defaultMaskPen =      QtGui.QPen( QtGui.QColor(0,255,0,100) )
defaultMaskPen.setWidthF(0.5)
defaultMaskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) )
defaultMaskHoverPen.setWidthF(1.0)

class CircleSelectionGraphicsItem(QtGui.QGraphicsEllipseItem):
    def mousePressEvent( self, event ):
        if self.acceptHoverEvents():
            try:
                self._onClickFun( event, self, self.elementXML, self.elementParms, self.elementViewObject )
            except:
                import FreeCAD as App
                App.Console.PrintError(traceback.format_exc())
        else:
            event.ignore()
    def hoverMoveEvent( self, event):
        self.setPen( self.selectionMaskHoverPen)
    def hoverLeaveEvent( self, event):
        self.setPen( self.selectionMaskPen )
    def lockSelection( self ) :
        self.setAcceptHoverEvents(False)
        #self.setAcceptedMouseButtons(0) #guessing some kind of bit mask stored as an integer
        self.setPen( self.selectionMaskHoverPen )
    def unlockSelection( self ) :
        self.setAcceptHoverEvents(True)
        self.setPen( self.selectionMaskPen )
    def adjustScale( self, newScale ):
        'used to adjust SelectionGraphicsItems'
        if not hasattr(self, '_orgPenWidth'):
            self._orgPenWidth = self.selectionMaskPen.widthF()
            self._orgPenWidthHover = self.selectionMaskHoverPen.widthF()
        pen = self.pen()
        s = newScale ** 0.7
        pen.setWidthF( self._orgPenWidth* s )
        self.setPen(pen)
        self.selectionMaskHoverPen.setWidthF( self._orgPenWidthHover * s ) #selectionMaskHoverPen instance shared amongth all graphic items(?)
        self.selectionMaskPen.setWidthF(  self._orgPenWidth * s )
        self.adjustScaleShape(newScale)
    def adjustScaleShape(self, newScale):
        pass
        
class PointSelectionGraphicsItem(CircleSelectionGraphicsItem ):
    def adjustScaleShape(self, newScale): #change points size on adjust scale
        if not hasattr(self, '_orgCenter_x'):
            rect = self.rect()
            self._orgCenter_x = rect.center().x()
            self._orgCenter_y = rect.center().y()
            self._orgWidth = rect.width()
        r = self._orgWidth *newScale
        self.setRect( self._orgCenter_x - r , self._orgCenter_y - r , 2*r, 2*r )
        
        
class LineSelectionGraphicsItem( QtGui.QGraphicsLineItem, CircleSelectionGraphicsItem ):
    def setBrush(self, Brush):
        pass #this function should not been inherrited from CircleSelectionGraphicsItem

class PathSelectionGraphicsItem( QtGui.QGraphicsPathItem, CircleSelectionGraphicsItem ):
    pass


graphicItems = [] #storing selection graphics items here as to protect against the garbage collector
DrawingsViews_info = {}


def generateSelectionGraphicsItems( viewObjects, onClickFun, transform=None, sceneToAddTo=None, clearPreviousSelectionItems=True, 
                                    doPoints=False, doTextItems=False, doLines=False, doCircles=False, doFittedCircles=False, doPathEndPoints=False, doMidPoints=False, doSelectViewObjectPoints=False, doEllipses=False, doArcCenters=True,
                                    pointWid=1.0 , maskPen=defaultMaskPen , maskBrush=defaultMaskBrush, maskHoverPen=defaultMaskHoverPen ):
    if clearPreviousSelectionItems:         
        if sceneToAddTo <> None:
            for gi in sceneToAddTo.items():
                if isinstance(gi, CircleSelectionGraphicsItem):
                    sceneToAddTo.removeItem(gi)
        del graphicItems[:]
    def postProcessGraphicsItem(gi, elementParms, zValue=0.99):
        gi.setBrush( maskBrush  )
        gi.setPen(maskPen)
        gi.selectionMaskPen = QtGui.QPen(maskPen)
        gi.selectionMaskHoverPen = QtGui.QPen(maskHoverPen)
        gi._onClickFun = onClickFun
        gi.elementParms = elementParms
        gi.elementXML = element #should be able to get from functions name space
        gi.elementViewObject = viewObject
        gi.setAcceptHoverEvents(True)
        gi.setCursor( QtCore.Qt.CrossCursor ) # http://qt-project.org/doc/qt-5/qt.html#CursorShape-enum ; may not work for lines ...
        gi.setZValue(zValue)
        if transform <> None:
            gi.setTransform( transform )
        if sceneToAddTo <> None:
            sceneToAddTo.addItem(gi)
        graphicItems.append(gi)
    pointsAlreadyAdded = []
    def addSelectionPoint( x, y, zValue=1.0 ): #common code
        if [x,y] in pointsAlreadyAdded:
            return
        pointsAlreadyAdded.append( [x,y] )
        graphicsItem = PointSelectionGraphicsItem( x-pointWid, y-pointWid, 2*pointWid, 2*pointWid )
        postProcessGraphicsItem(graphicsItem, {'x':x, 'y':y}, zValue)
    def addCircle( x, y, r, **extraKWs):
        graphicsItem = CircleSelectionGraphicsItem( x-r, y-r, 2*r, 2*r )
        KWs = {'x':x,'y':y,'r':r}
        KWs.update(extraKWs)
        postProcessGraphicsItem(graphicsItem, KWs, zValue=1.01**-r ) #smaller circles on top
    def circlePoints( x, y, rx, ry ):
        addSelectionPoint ( x, y, 2 ) #Circle/ellipse center point
        addSelectionPoint ( x + rx, y, 2 ) #Circle/ellipse right quadrant point
        addSelectionPoint ( x - rx, y, 2 ) #Circle/ellipse left quadrant point
        addSelectionPoint ( x , y + ry, 2 ) #Circle/ellipse top quadrant point
        addSelectionPoint ( x , y - ry, 2 ) #Circle/ellipse bottom quadrant point

    for viewObject in viewObjects:
        if not hasattr(viewObject, 'ViewResult'):
            continue
        if viewObject.ViewResult.strip() == '':
            continue
        DrawingsViews_info[viewObject.Name] = DrawingViewInfo( viewObject )
        viewInfo = DrawingsViews_info[viewObject.Name] #shorthand
        XML_tree =  SvgXMLTreeNode(viewObject.ViewResult,0)
        scaling = XML_tree.scaling()
        viewInfo.scale = scaling
        SelectViewObjectPoint_loc = None
        for element in XML_tree.getAllElements():
            if element.tag == 'circle':
                x, y = element.applyTransforms( float( element.parms['cx'] ), float( element.parms['cy'] ) )
                r =  float( element.parms['r'] )* scaling
                if doCircles: 
                    addCircle( x, y, r)
                if doPoints: 
                    circlePoints( x, y, r, r)
                viewInfo.updateBounds_ellipse( x, y, r, r )
            if element.tag == 'ellipse':
                cx, cy = element.applyTransforms( float( element.parms['cx'] ), float( element.parms['cy'] ) )
                rx, ry = float( element.parms['rx'] )* scaling, float( element.parms['ry'] )* scaling
                if doCircles: 
                    if rx == ry:
                        addCircle( cx, cy, rx)
                if doEllipses:
                    raise NotImplemented
                if doPoints: 
                    circlePoints( cx, cy, rx, ry)
                viewInfo.updateBounds_ellipse( cx, cy, rx, ry )
                
            if element.tag == 'text' and element.parms.has_key('x'):
                if doTextItems:
                    addSelectionPoint( *element.applyTransforms( float( element.parms['x'] ), float( element.parms['y'] ) ) )
                elif doSelectViewObjectPoints:
                    addSelectionPoint( *element.applyTransforms( float( element.parms['x'] ), float( element.parms['y'] ) ) )

            if element.tag == 'path': 
                path = SvgPath( element )
                for p in path.points:
                    if doPoints:
                        addSelectionPoint( p.x, p.y )
                    viewInfo.updateBounds( p.x, p.y )

                if doLines:
                    for line in path.lines:
                        x1, y1, x2, y2 = line.x1, line.y1, line.x2, line.y2
                        graphicsItem = LineSelectionGraphicsItem( x1, y1, x2, y2 )
                        postProcessGraphicsItem(graphicsItem, {'x1':x1,'y1':y1,'x2':x2,'y2':y2} )
                if doMidPoints:
                    for line in path.lines:
                        addSelectionPoint( *line.midPoint() )
                for arc in path.arcs:
                    if doCircles or doEllipses:
                        if arc.circular:
                            gi = PathSelectionGraphicsItem()
                            gi.setPath( arc.QPainterPath() )
                            postProcessGraphicsItem( gi, {'x': arc.center[0],'y': arc.center[1],'r': arc.r*scaling, 'arcPickle': pickle.dumps(arc)} )
                        elif doEllipses:
                            gi = PathSelectionGraphicsItem()
                            gi.setPath( arc.QPainterPath() )
                            postProcessGraphicsItem( gi, {'x': arc.center[0],'y': arc.center[1], 'arcPickle': pickle.dumps(arc)} )
                    if doPoints and doArcCenters:
                        addSelectionPoint( arc.center[0], arc.center[1], 2 )
                if doFittedCircles:
                    for bezierCurve in path.bezierCurves:
                        x, y, r, r_error = bezierCurve.fitCircle()
                        if r_error < 10**-4:
                            gi = PathSelectionGraphicsItem()
                            gi.setPath( bezierCurve.QPainterPath() )
                            postProcessGraphicsItem( gi, {'x':x,'y':y,'r':r} )
                if doPathEndPoints and len(path.points) > 0:
                    addSelectionPoint ( path.points[-1].x,  path.points[-1].y )
                if doSelectViewObjectPoints and SelectViewObjectPoint_loc == None and len(path.points) > 0:
                    SelectViewObjectPoint_loc = path.points[-1].x,  path.points[-1].y

            if element.tag == 'line':
                x1, y1 = element.applyTransforms( float( element.parms['x1'] ), float( element.parms['y1'] ) )
                x2, y2 = element.applyTransforms( float( element.parms['x2'] ), float( element.parms['y2'] ) )
                if doPoints:
                    addSelectionPoint ( x1, y1 )
                    addSelectionPoint ( x2, y2 )
                viewInfo.updateBounds( x1, y1 )
                viewInfo.updateBounds( x1, y2 )

                if doLines:
                    graphicsItem = LineSelectionGraphicsItem( x1, y1, x2, y2 )
                    postProcessGraphicsItem(graphicsItem, {'x1':x1,'y1':y1,'x2':x2,'y2':y2})
                if doMidPoints:
                    addSelectionPoint( (x1+x2)/2, (y1+y2)/2 )
                if doSelectViewObjectPoints and SelectViewObjectPoint_loc == None: #second check to textElementes preference
                    SelectViewObjectPoint_loc = x2, y2

        if doSelectViewObjectPoints and SelectViewObjectPoint_loc <> None:
            addSelectionPoint( *SelectViewObjectPoint_loc )
                #if len(fitData) > 0: 
                #    x, y, r, r_error = fitCircle_to_path(fitData)
                #    #print('fittedCircle: x, y, r, r_error', x, y, r, r_error)
                #    if r_error < 10**-4:
                #        if doFittedCircles:
                #            addCircle( x, y, r , r_error=r_error )
                #        if doPoints:
                #            circlePoints( x, y, r, r)

    return graphicItems
    
def hideSelectionGraphicsItems( hideFunction=None, deleteFromGraphicItemsList = True ):
    delList = []
    for ind, gi in enumerate(graphicItems):
        if hideFunction == None or hideFunction(gi):
            try:
                gi.hide()
            except RuntimeError, msg:
                import FreeCAD
                FreeCAD.Console.PrintError('hideSelectionGraphicsItems unable to hide graphicItem, RuntimeError msg %s\n' % str(msg))
            if deleteFromGraphicItemsList:
                delList.append( ind )
    for delInd in reversed(delList):
        del graphicItems[delInd]


#import FreeCAD
class ResizeGraphicItemsRect(QtGui.QGraphicsRectItem):
    '''
    from src/Mod/Drawing/Gui/DrawingView.cpp 

    void SvgView::wheelEvent(QWheelEvent *event)
    {
    qreal factor = std::pow(1.2, -event->delta() / 240.0);
    scale(factor, factor);
    event->accept();
    }
    so cant really do anything here, but attempting something on mouse move ...
    '''
    def hoverMoveEvent(self, event):
        #FreeCAD.Console.PrintMessage('1\n')
        currentScale = self._graphicsView.transform().m11() #since no rotation...
        if currentScale <> self._previousScale :
            #FreeCAD.Console.PrintMessage('adjusting Scale of graphics items\n')
            for gi in graphicItems:
                gi.adjustScale( 1 / currentScale  )
            self._previousScale = currentScale
            #FreeCAD.Console.PrintMessage('finished adjusting Scale of graphics items\n')

garbageCollectionProtector = []

def addProxyRectToRescaleGraphicsSelectionItems( graphicsScene, graphicsView, width, height):
    if any([ isinstance(c,ResizeGraphicItemsRect) for c in graphicsScene.items() ]):
        return #ResizeGraphicItemsRect already in screne, dimensioning must have been interupted.
    rect = ResizeGraphicItemsRect()
    rect.setRect(0, 0, width, height)
    rect._graphicsView = graphicsView
    rect._previousScale = 1.0 #adjustment, will happen on hoverMoveEvent
    rect.setAcceptHoverEvents(True)
    rect.setCursor( QtCore.Qt.ArrowCursor )
    graphicsScene.addItem( rect )
    rect.hoverMoveEvent( QtGui.QGraphicsSceneWheelEvent() ) # adjust scale
    garbageCollectionProtector.append( rect )


if __name__ == "__main__":
    if len(sys.argv) == 2:
        print('Testing selectionOverlay.py')
        XML = open(sys.argv[1]).read()
    else:
        print('usage\n\tpython selectionOverlay.py svg_file')
        exit(2)
        #XML = testCase9
    
    app = QtGui.QApplication([])
    width = 1200
    height = 1200 / 16.0 * 9

    graphicsScene = QtGui.QGraphicsScene()#0,0,width,height)
    #graphicsScene.addText("Svg_Tools.py test")
    orthoViews = []
    def addOrthoView( XML ):
        o1 = QtSvg.QGraphicsSvgItem()
        o1Renderer = QtSvg.QSvgRenderer()
        o1Renderer.load( QtCore.QByteArray( XML ))
        o1.setSharedRenderer( o1Renderer )
        graphicsScene.addItem( o1 )
        orthoViews.append([o1, o1Renderer, XML]) #protect o1 and o1Renderer against garbage collector
    addOrthoView(XML)


    class dummyViewObject:
        def __init__(self, XML):
            self.ViewResult = XML
    viewObject = dummyViewObject( XML )

    def onClickFun( event, referer, elementXML, elementParms, elementViewObject ):
        print( elementXML  )
        print( elementParms )
        referer.adjustScale( 2 )


    maskBrush = QtGui.QBrush( QtGui.QColor(0,255,0,100) )
    maskPen =      QtGui.QPen( QtGui.QColor(0,255,0,100) )
    maskPen.setWidth(4)
    maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) )
    maskHoverPen.setWidthF(5)
    generateSelectionGraphicsItems( 
        [viewObject], onClickFun, sceneToAddTo=graphicsScene, doPoints=True, doCircles=True, doTextItems=True, doLines=True, doFittedCircles=True, doEllipses=True,
        maskPen=maskPen , maskBrush=maskBrush, maskHoverPen=maskHoverPen, pointWid=4.0
    )

    view = QtGui.QGraphicsView(graphicsScene)
    view.setGeometry(0, 0, height-30, height-30)
    #view.show()
    class ViewHoldingWidget(QtGui.QWidget):
        def __init__(self):
            super(ViewHoldingWidget, self).__init__()
            self.initUI()
        
        def initUI(self):
            vbox = QtGui.QVBoxLayout()
            vbox.addWidget( view )
            self.setLayout(vbox)   
            self.setGeometry(0, 0, width+30, height+30)
        
    ex = ViewHoldingWidget()
    #view.fitInView( graphicsScene.itemsBoundingRect(), QtCore.Qt.KeepAspectRatio)
    #noTransform = QtGui.QTransform(1, 0, 0, 1, 0.0, 0.0)
    #view.setTransform( noTransform )

    ex.show()
    sys.exit(app.exec_())



