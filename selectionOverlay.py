# -*- coding: utf-8 -*-
'''
The biggest problem drawing dimensioning in FreeCAD 0.15 is that drawing objects have no selection support.
This library provides a crude hack to get around this problem.
Specifically, DrawingObject.ViewResults are parsed as to create QGraphicsItems to handle selection.
'''
from XMLlib import SvgXMLTreeNode
from circleLib import fitCircle_to_path, findCircularArcCentrePoint, pointsAlongCircularArc
import sys, numpy, traceback
from PySide import QtGui, QtCore, QtSvg

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

def generateSelectionGraphicsItems( viewObjects, onClickFun, transform=None, sceneToAddTo=None, clearPreviousSelectionItems=True, 
                                    doPoints=False, doTextItems=False, doLines=False, doCircles=False, doFittedCircles=False, doPathEndPoints=False, doMidPoints=False, doSelectViewObjectPoints=True,
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
    def circlePoints( x, y, r ):
        addSelectionPoint ( x, y, 2 ) #Circle center point
        addSelectionPoint ( x + r, y, 2 ) #Circle right quadrant point
        addSelectionPoint ( x - r, y, 2 ) #Circle left quadrant point
        addSelectionPoint ( x , y + r, 2 ) #Circle top quadrant point
        addSelectionPoint ( x , y - r, 2 ) #Circle bottom quadrant point

    for viewObject in viewObjects:
        if viewObject.ViewResult.strip() == '':
            continue
        XML_tree =  SvgXMLTreeNode(viewObject.ViewResult,0)
        scaling = XML_tree.scaling()
        SelectViewObjectPoint_loc = None
        for element in XML_tree.getAllElements():
            if element.tag == 'circle':
                x, y = element.applyTransforms( float( element.parms['cx'] ), float( element.parms['cy'] ) )
                r =  float( element.parms['r'] )* scaling
                if doCircles: 
                    addCircle( x, y, r)
                if doPoints: 
                    circlePoints( x, y, r)
                
            if element.tag == 'text' and element.parms.has_key('x'):
                if doTextItems:
                    addSelectionPoint( *element.applyTransforms( float( element.parms['x'] ), float( element.parms['y'] ) ) )
                elif doSelectViewObjectPoints:
                    addSelectionPoint( *element.applyTransforms( float( element.parms['x'] ), float( element.parms['y'] ) ) )

            if element.tag == 'path': #https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/d
                #print(element.XML)
                fitData = []
                dParmsXML = element.parms['d']
                #<spacing corrections>
                i = 0
                while i < len(dParmsXML)-1:
                    if dParmsXML[i] in 'MmLlACcQZz,' and dParmsXML[i+1] in '-.0123456789':
                        dParmsXML = dParmsXML[:i+1] + ' ' + dParmsXML[i+1:]
                    i = i + 1
                #</spacing corrections>
                parms = dParmsXML.replace(',',' ').strip().split()
                _pen_x = 0
                _pen_y = 0
                j = 0
                pathDescriptor = None
                while j < len(parms):
                    #print(parms[j:])
                    if parms[j] in list('MmLlACcQZz,'):
                        pathDescriptor = parms[j]
                    else: #using previous pathDescriptor
                        if pathDescriptor == None:
                            raise RuntimeError, 'pathDescriptor == None! unable to parse path "%s" with d parms %s' % (element.XML[element.pStart: element.pEnd], parms)
                        parms.insert(j, pathDescriptor.replace('m','l').replace('M','L'))

                    if parms[j] == 'M' or parms[j] == 'm':
                        if parms[j] == 'M':
                            _pen_x, _pen_y = float(parms[j+1]), float(parms[j+2])
                        else:
                            _pen_x = _pen_x + float(parms[j+1])
                            _pen_y = _pen_y + float(parms[j+2])
                        pen_x, pen_y = element.applyTransforms( _pen_x, _pen_y )
                        _path_start_x , _path_start_y = _pen_x, _pen_y
                        path_start_x , path_start_y = pen_x, pen_y
                        j = j + 3                        
                    elif parms[j] in ['L','l','Z','z']:
                        if  parms[j] == 'L' or parms[j] == 'l':
                            if parms[j] == 'L':
                                _end_x, _end_y = float(parms[j+1]), float(parms[j+2])
                            else:
                                _end_x = _pen_x + float(parms[j+1])
                                _end_y = _pen_y + float(parms[j+2])
                            end_x, end_y = element.applyTransforms( _end_x, _end_y )
                            j = j + 3
                        else: #parms[j] == 'Z':
                            _end_x, _end_y = _path_start_x , _path_start_y
                            end_x, end_y = path_start_x , path_start_y
                            j = j + 1
                        if doPoints:
                            addSelectionPoint ( pen_x, pen_y )
                            addSelectionPoint ( end_x, end_y )
                        if doLines:
                            graphicsItem = LineSelectionGraphicsItem( pen_x, pen_y, end_x, end_y )
                            postProcessGraphicsItem(graphicsItem, {'x1':pen_x,'y1':pen_y,'x2':end_x,'y2':end_y})
                        if doMidPoints:
                            addSelectionPoint( (pen_x+end_x)/2, (pen_y+end_y)/2 )
                        _pen_x, _pen_y = _end_x, _end_y
                        pen_x, pen_y = end_x, end_y
                    elif parms[j] == 'A':
                        # The arc command begins with the x and y radius and ends with the ending point of the arc. 
                        # Between these are three other values: x axis rotation, large arc flag and sweep flag.
                        rX, rY, xRotation, largeArc, sweep, _end_x, _end_y = map( float, parms[j+1:j+1 + 7] )
                        end_x, end_y = element.applyTransforms( _end_x, _end_y )
                        if doPoints:
                            addSelectionPoint ( pen_x, pen_y )
                            addSelectionPoint ( end_x, end_y )
                        if rX==rY :
                            _c_x, _c_y = findCircularArcCentrePoint( rX, _pen_x, _pen_y, _end_x, _end_y, largeArc==1, sweep==1 ) #do in untranformed co-ordinates as to preserve sweep flag
                            if not numpy.isnan(_c_x): #if all went well findCircularArcCentrePoint
                                c_x, c_y = element.applyTransforms( _c_x, _c_y )
                                r = rX * scaling
                                if doCircles: 
                                    #addCircle( c_x, c_y, r , largeArc=largeArc, sweep=sweep)
                                    gi = PathSelectionGraphicsItem()
                                    path = QtGui.QPainterPath(QtCore.QPointF(pen_x, pen_y))
                                    #path.arcTo(c_x - r, c_y -r , 2*r, 2*r, angle_1, angle_CCW) #dont know what is up with this function so trying something else.
                                    for _p in pointsAlongCircularArc(rX, _pen_x, _pen_y, _end_x, _end_y, largeArc==1, sweep==1, noPoints=12):
                                        path.lineTo(* element.applyTransforms(*_p) )
                                    gi.setPath(path)
                                    postProcessGraphicsItem( gi, {'x':c_x,'y':c_y,'r':r, 'largeArc':largeArc, 'sweep':sweep,  } )
                                #if doPoints:
                                #    circlePoints( c_x, c_y, r)
                        _pen_x, _pen_y = _end_x, _end_y
                        pen_x, pen_y = end_x, end_y
                        j = j + 8
                    elif parms[j] == 'C' or parms[j] == 'c' or parms[j] =='Q': #Bézier curve 
                        if parms[j] == 'C' or parms[j] == 'c':
                            #cubic Bézier curve from the current point to (x,y) using 
                            # (x1,y1) as the control point at the beginning of the curve and (x2,y2) as the control point at the end of the curve.
                            if parms[j] == 'C':
                                _x1, _y1, _x2, _y2, _end_x, _end_y = map( float, parms[j+1:j+1 + 6] ) 
                            else: #parms[j] == 'c':
                                _x1, _y1, _x2, _y2, _end_x, _end_y = numpy.array(map( float, parms[j+1:j+1 + 6] )) + numpy.array([_pen_x,_pen_y]*3)
                            P = [ [pen_x, pen_y], element.applyTransforms(_x1, _y1), element.applyTransforms(_x2, _y2), element.applyTransforms(_end_x, _end_y) ]
                            j = j + 7
                        elif parms[j] == 'Q': # quadratic Bézier curve from the current point to (x,y) using (x1,y1) as the control point. 
                            # Q (uppercase) indicates that absolute coordinates will follow; 
                            # q (lowercase) indicates that relative coordinates will follow. 
                            # Multiple sets of coordinates may be specified to draw a polybézier. 
                            # At the end of the command, the new current point becomes the final (x,y) coordinate pair used in the polybézier.
                            _x1, _y1, _end_x, _end_y = map( float, parms[j+1:j+1 + 4] ) 
                            j = j + 5
                            P = [ [pen_x, pen_y], element.applyTransforms(_x1, _y1), element.applyTransforms(_end_x, _end_y) ]
                        if doFittedCircles or True:
                            x, y, r, r_error = fitCircle_to_path([P])
                            #print('fittedCircle: x, y, r, r_error', x, y, r, r_error)
                            if r_error < 10**-4:
                                gi = PathSelectionGraphicsItem()
                                path = QtGui.QPainterPath(QtCore.QPointF(pen_x, pen_y))
                                if len(P) == 4:
                                    path.cubicTo( QtCore.QPointF(*P[1]), QtCore.QPointF(*P[2]), QtCore.QPointF(*P[3]) )
                                else:
                                    path.quadTo( QtCore.QPointF(*P[1]), QtCore.QPointF(*P[2]) )
                                gi.setPath(path)
                                postProcessGraphicsItem( gi, {'x':x,'y':y,'r':r} )

                        end_x, end_y = P[-1]
                        if doPoints:
                            addSelectionPoint ( pen_x, pen_y )
                            addSelectionPoint ( end_x, end_y )
                        #fitData.append( P )
                        _pen_x, _pen_y = _end_x, _end_y
                        pen_x, pen_y = end_x, end_y
                    else:
                        raise RuntimeError, 'unable to parse path "%s" with d parms %s' % (element.XML[element.pStart: element.pEnd], parms)
                if j > 0 and doPathEndPoints:
                    addSelectionPoint ( pen_x, pen_y )
                if j > 0 and doSelectViewObjectPoints and SelectViewObjectPoint_loc == None:
                    SelectViewObjectPoint_loc = pen_x, pen_y

            if element.tag == 'line':
                x1, y1 = element.applyTransforms( float( element.parms['x1'] ), float( element.parms['y1'] ) )
                x2, y2 = element.applyTransforms( float( element.parms['x2'] ), float( element.parms['y2'] ) )
                if doPoints:
                    addSelectionPoint ( x1, y1 )
                    addSelectionPoint ( x2, y2 )
                if doLines:
                    graphicsItem = LineSelectionGraphicsItem( x1, y1, x2, y2 )
                    postProcessGraphicsItem(graphicsItem, {'x1':x1,'y1':y1,'x2':x2,'y2':y2})
                if doMidPoints:
                    addSelectionPoint( (x1+x2)/2, (y1+y2)/2 )
                if doSelectViewObjectPoints and SelectViewObjectPoint_loc == None: #second check to textElementes preference
                    SelectViewObjectPoint_loc = x2,y2

        if doSelectViewObjectPoints and SelectViewObjectPoint_loc <> None:
            addSelectionPoint( *SelectViewObjectPoint_loc )
                #if len(fitData) > 0: 
                #    x, y, r, r_error = fitCircle_to_path(fitData)
                #    #print('fittedCircle: x, y, r, r_error', x, y, r, r_error)
                #    if r_error < 10**-4:
                #        if doFittedCircles:
                #            addCircle( x, y, r , r_error=r_error )
                #        if doPoints:
                #            circlePoints( x, y, r)

    return graphicItems
    
def hideSelectionGraphicsItems( hideFunction=None  ):
    for gi in graphicItems:
        if hideFunction == None:
            gi.hide()
        elif hideFunction(gi):
            gi.hide()


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
    print('Testing selectionOverlay.py')
    testCase1 = '''<svg id="Ortho_0_1" width="640" height="480"
   transform="rotate(90,122.43,123.757) translate(250,0) scale(3.0,3.0)"
  >
<g   stroke="rgb(0, 0, 0)"
   stroke-width="0.233333"
   stroke-linecap="butt"
   stroke-linejoin="miter"
   fill="none"
   transform="scale(1,-1)"
  >
<path id= "1" d=" M 65.9612 -59.6792 L -56.2041 -59.6792 " />
<path d="M-56.2041 -59.6792 A4.2 4.2 0 0 0 -60.4041 -55.4792" /><path id= "3" d=" M 65.9612 49.7729 L 65.9612 -59.6792 " />
<path id= "4" d=" M -60.4041 -55.4792 L -60.4041 49.7729 " />
<path id= "5" d=" M -60.4041 49.7729 L 65.9612 49.7729 " />
<circle cx ="22.2287" cy ="-15.2218" r ="13.8651" /><!--Comment-->
<path id= "7" d="M18,0 L17.9499,-4.32955e-16  L17.8019,-4.00111e-16  L17.5637,-3.47203e-16  L17.247,-2.76885e-16  L16.8678,-1.92683e-16  L16.445,-9.88191e-17  L16,-5.43852e-32  L15.555,9.88191e-17  L15.1322,1.92683e-16  L14.753,2.76885e-16  L14.4363,3.47203e-16  L14.1981,4.00111e-16  L14.0501,4.32955e-16  L14,4.44089e-16 " />
<path d="M12.7,-53.35 C13.0276,-53.3497 13.3353,-53.4484 13.5837,-53.6066  C13.8332,-53.7643 14.0231,-53.9807 14.1457,-54.2047  C14.4256,-54.721 14.41,-55.3038 14.1502,-55.787  C14.0319,-56.0053 13.8546,-56.213 13.6163,-56.3722  C13.3789,-56.5307 13.0795,-56.6413 12.7378,-56.6496  C12.3961,-56.6571 12.0892,-56.5598 11.8429,-56.4099  C11.5956,-56.2597 11.4083,-56.0565 11.282,-55.8436  C11.0014,-55.3672 10.9667,-54.7868 11.2231,-54.2642  C11.3401,-54.0279 11.5293,-53.7969 11.7844,-53.6273  C12.0382,-53.4574 12.3575,-53.3497 12.7,-53.35 " />
</g>
<text x="50" y="-60" fill="blue" style="font-size:8" transform="rotate(0.000000 50,-60)">256.426</text>
</svg>'''
    testCase2 = '''<g id="Ortho_0_0"
   transform="rotate(180,44,35.6) translate(44,35.6) scale(4.0,4.0)"
  >
<g   stroke="rgb(0, 0, 0)"
   stroke-width="0.583333"
   stroke-linecap="butt"
   stroke-linejoin="miter"
   fill="none"
   transform="scale(1,-1)"
  >
<path id= "1" d=" M 0 0 L -120 0 " />
<path id= "2" d=" M 0 35 L 0 0 " />
<path id= "3" d=" M -120 0 L -120 35 " />
<path id= "4" d=" M -120 35 L -106 35 " />
<path d="M-105.916 36 A6 6 0 1 0 -106 35" />
<path id= "6" d=" M -105.916 36 L -120 36 " />
<path id= "7" d=" M -120 36 L -120 48 " />
<path id= "8" d=" M -120 48 L 0 48 " />
<path id= "9" d=" M 0 48 L 0 36 " />
<path id= "10" d=" M -14.0839 36 L 0 36 " />
<path d="M-26 35 A6 6 0 0 0 -14.0839 36" />
<path d="M-14 35 A6 6 0 1 0 -26 35" />
<path id= "13" d=" M 0 35 L -14 35 " />
<circle cx ="-60" cy ="35" r ="3" /></g>
</g>'''
    testCase3 = '<g id="Ortho_0_0"\n   transform="rotate(0,98.5,131.5) translate(200,400) scale(30,30)"\n  >\n<g   stroke="rgb(0, 0, 0)"\n   stroke-width="0.035"\n   stroke-linecap="butt"\n   stroke-linejoin="miter"\n   fill="none"\n   transform="scale(1,-1)"\n  >\n<path id= "1" d=" M 0 1 L 0 9 " />\n<path d="M-2.22045e-16 1 A1 1 0 0 1 1 -2.22045e-16" /><path d="M-2.22045e-16 9 A1 1 0 0 0 1 10" /><path id= "4" d=" M 1 0 L 9 0 " />\n<path id= "5" d=" M 1 10 L 9 10 " />\n<path d="M10 1 A1 1 0 0 0 9 -2.22045e-16" /><path d="M10 9 A1 1 0 0 1 9 10" /><path id= "8" d=" M 10 1 L 10 9 " />\n</g>\n</g>\n'

    testCase4 = '<g id="Ortho_0_0"\n   transform="rotate(-90,75.6667,71) translate(-300,100) scale(30,30)"\n  >\n<g   stroke="rgb(0, 0, 0)"\n   stroke-width="0.0875"\n   stroke-linecap="butt"\n   stroke-linejoin="miter"\n   fill="none"\n   transform="scale(1,-1)"\n  >\n<path id= "1" d=" M 1 2.22045e-16 L 9 2.22045e-16 " />\n<path id= "2" d=" M -2.22045e-16 -1 L -2.22045e-16 -9 " />\n<path id= "3" d=" M 10 -1 L 10 -9 " />\n<path id= "4" d=" M 1 -10 L 9 -10 " />\n<path d="M0 -1 A1 1 0 0 0 1 2.22045e-16" /><path d="M10 -1 A1 1 0 0 1 9 2.22045e-16" /><path d="M0 -9 A1 1 0 0 1 1 -10" /><path d="M9 -10 A1 1 0 0 1 10 -9" /></g>\n</g>\n'

    testCase5 = '<g id="Ortho_0_-1"\n   transform="rotate(90,75.6667,132) translate(300,100) scale(30,30)"\n  >\n<g   stroke="rgb(0, 0, 0)"\n   stroke-width="0.0875"\n   stroke-linecap="butt"\n   stroke-linejoin="miter"\n   fill="none"\n   transform="scale(1,-1)"\n  >\n<path id= "1" d=" M 1.11022e-16 1 L 1.11022e-16 9 " />\n<path d="M1.11022e-16 1 A1 1 0 0 0 -1 -2.22045e-16" /><path id= "3" d=" M -1 -2.22045e-16 L -9 -2.22045e-16 " />\n<path d="M1.11022e-16 9 A1 1 0 0 1 -1 10" /><path id= "5" d=" M -1 10 L -9 10 " />\n<path id= "6" d=" M -1 10 L -9 10 " />\n<path id= "7" d=" M -10 1 L -10 9 " />\n<path id= "8" d=" M -10 1 L -10 9 " />\n<path d="M-10 1 A1 1 0 0 1 -9 -2.22045e-16" /><path d="M-10 1 A1 1 0 0 1 -9 -2.22045e-16" /><path d="M-10 9 A1 1 0 0 0 -9 10" /><path d="M-9 10 A1 1 0 0 1 -10 9" /></g>\n</g>\n'

    testCase6 = '''<g
     inkscape:label="Layer 1"
     inkscape:groupmode="layer"
     id="layer1">
    <g
       id="g542"
       transform="matrix(1.25,0,0,-1.25,-348.3393,383.537)">
      <path
         d="m 418.1,165.6 -35.4,0 0,67.5 70.8,0 0,-67.5 -35.4,0 z"
         style="fill:none;stroke:#000000;stroke-width:1.41499996;stroke-linecap:butt;stroke-linejoin:round;stroke-miterlimit:10;stroke-dasharray:none;stroke-opacity:1"
         id="path544"
         inkscape:connector-curvature="0" />
    </g>
    <g
       id="g546"
       transform="matrix(1.25,0,0,-1.25,-348.3393,383.537)">
      <path
         d="m 388.3,230.3 c 1.6,0 2.9,-1.2 2.9,-2.8 0,-1.6 -1.3,-2.8 -2.9,-2.8 -1.6,0 -2.8,1.2 -2.8,2.8 0,1.6 1.2,2.8 2.8,2.8 z"
         style="fill:none;stroke:#000000;stroke-width:0.56598997;stroke-linecap:butt;stroke-linejoin:round;stroke-miterlimit:10;stroke-dasharray:none;stroke-opacity:1"
         id="path548"
         inkscape:connector-curvature="0" />
    </g>
    <g
       id="g550"
       transform="matrix(1.25,0,0,-1.25,-348.3393,383.537)">
      <path
         d="m 385.5,230.3 0,0 z"
         style="fill:none;stroke:#000000;stroke-width:0.56598997;stroke-linecap:butt;stroke-linejoin:round;stroke-miterlimit:10;stroke-dasharray:none;stroke-opacity:1"
         id="path552"
         inkscape:connector-curvature="0" />
    </g>
    <g
       id="g554"
       transform="matrix(1.25,0,0,-1.25,-348.3393,383.537)">
      <path
         d="m 391.2,224.7 0,0 z"
         style="fill:none;stroke:#000000;stroke-width:0.56598997;stroke-linecap:butt;stroke-linejoin:round;stroke-miterlimit:10;stroke-dasharray:none;stroke-opacity:1"
         id="path556"
         inkscape:connector-curvature="0" />
    </g>
    <g
       id="g558"
       transform="matrix(1.25,0,0,-1.25,-348.3393,383.537)">
      <path
         d="m 447.8,230.3 c 1.6,0 2.9,-1.2 2.9,-2.8 0,-1.6 -1.3,-2.8 -2.9,-2.8 -1.5,0 -2.8,1.2 -2.8,2.8 0,1.6 1.3,2.8 2.8,2.8 z"
         style="fill:none;stroke:#000000;stroke-width:0.56598997;stroke-linecap:butt;stroke-linejoin:round;stroke-miterlimit:10;stroke-dasharray:none;stroke-opacity:1"
         id="path560"
         inkscape:connector-curvature="0" />
    </g>
    <g
       id="g562"
       transform="matrix(1.25,0,0,-1.25,-348.3393,383.537)">
      <path
         d="m 445,230.3 0,0 z"
         style="fill:none;stroke:#000000;stroke-width:0.56598997;stroke-linecap:butt;stroke-linejoin:round;stroke-miterlimit:10;stroke-dasharray:none;stroke-opacity:1"
         id="path564"
         inkscape:connector-curvature="0" />
    </g>
    <g
       id="g566"
       transform="matrix(1.25,0,0,-1.25,-348.3393,383.537)">
      <path
         d="m 450.7,224.7 0,0 z"
         style="fill:none;stroke:#000000;stroke-width:0.56598997;stroke-linecap:butt;stroke-linejoin:round;stroke-miterlimit:10;stroke-dasharray:none;stroke-opacity:1"
         id="path568"
         inkscape:connector-curvature="0" />
    </g>
    <g
       id="g570"
       transform="matrix(1.25,0,0,-1.25,-348.3393,383.537)">
      <path
         d="m 388.3,195.2 c 1.6,0 2.9,-1.3 2.9,-2.8 0,-1.6 -1.3,-2.9 -2.9,-2.9 -1.6,0 -2.8,1.3 -2.8,2.9 0,1.5 1.2,2.8 2.8,2.8 z"
         style="fill:none;stroke:#000000;stroke-width:0.56598997;stroke-linecap:butt;stroke-linejoin:round;stroke-miterlimit:10;stroke-dasharray:none;stroke-opacity:1"
         id="path572"
         inkscape:connector-curvature="0" />
    </g>
    <g
       id="g574"
       transform="matrix(1.25,0,0,-1.25,-348.3393,383.537)">
      <path
         d="m 385.5,195.2 0,0 z"
         style="fill:none;stroke:#000000;stroke-width:0.56598997;stroke-linecap:butt;stroke-linejoin:round;stroke-miterlimit:10;stroke-dasharray:none;stroke-opacity:1"
         id="path576"
         inkscape:connector-curvature="0" />
    </g>
    <g
       id="g578"
       transform="matrix(1.25,0,0,-1.25,-348.3393,383.537)">
      <path
         d="m 391.2,189.5 0,0 z"
         style="fill:none;stroke:#000000;stroke-width:0.56598997;stroke-linecap:butt;stroke-linejoin:round;stroke-miterlimit:10;stroke-dasharray:none;stroke-opacity:1"
         id="path580"
         inkscape:connector-curvature="0" />
    </g>
    <g
       id="g582"
       transform="matrix(1.25,0,0,-1.25,-348.3393,383.537)">
      <path
         d="m 447.8,195.2 c 1.6,0 2.9,-1.3 2.9,-2.8 0,-1.6 -1.3,-2.9 -2.9,-2.9 -1.5,0 -2.8,1.3 -2.8,2.9 0,1.5 1.3,2.8 2.8,2.8 z"
         style="fill:none;stroke:#000000;stroke-width:0.56598997;stroke-linecap:butt;stroke-linejoin:round;stroke-miterlimit:10;stroke-dasharray:none;stroke-opacity:1"
         id="path584"
         inkscape:connector-curvature="0" />
    </g>
    <g
       id="g586"
       transform="matrix(1.25,0,0,-1.25,-348.3393,383.537)">
      <path
         d="m 445,195.2 0,0 z"
         style="fill:none;stroke:#000000;stroke-width:0.56598997;stroke-linecap:butt;stroke-linejoin:round;stroke-miterlimit:10;stroke-dasharray:none;stroke-opacity:1"
         id="path588"
         inkscape:connector-curvature="0" />
    </g>
    <g
       id="g590"
       transform="matrix(1.25,0,0,-1.25,-348.3393,383.537)">
      <path
         d="m 450.7,189.5 0,0 z"
         style="fill:none;stroke:#000000;stroke-width:0.56598997;stroke-linecap:butt;stroke-linejoin:round;stroke-miterlimit:10;stroke-dasharray:none;stroke-opacity:1"
         id="path592"
         inkscape:connector-curvature="0" />
    </g>
    <path
       d="m 174.28572,157.16197 -14.125,0 0,-28.125 28.25,0 0,28.125 -14.125,0 z"
       style="fill:#e6e6e6;fill-opacity:1;fill-rule:evenodd;stroke:none"
       id="path594"
       inkscape:connector-curvature="0" />
    <path
       inkscape:connector-curvature="0"
       id="path598"
       style="fill:none;stroke:#333333;stroke-width:1.76874995;stroke-linecap:butt;stroke-linejoin:round;stroke-miterlimit:10;stroke-dasharray:none;stroke-opacity:1"
       d="m 174.28572,157.16196 -14.125,0 0,-28.125 28.25,0 0,28.125 -14.125,0 z" />
    <path
       d="m 174.28572,129.91197 c 7.5,0 13.25,5.75 13.25,13.125 0,7.5 -5.75,13.25 -13.25,13.25 -7.5,0 -13.25,-5.75 -13.25,-13.25 0,-7.375 5.75,-13.125 13.25,-13.125 z m -13.25,0 0,0 z m 26.625,26.375 0,0 z"
       style="fill:#333333;fill-opacity:1;fill-rule:evenodd;stroke:none"
       id="path600"
       inkscape:connector-curvature="0" />
    <path
       d="m 174.28572,132.53697 c 6,0 10.625,4.625 10.625,10.5 0,6 -4.625,10.625 -10.625,10.625 -6,0 -10.625,-4.625 -10.625,-10.625 0,-5.875 4.625,-10.5 10.625,-10.5 z m -10.625,0 0,0 z m 21.25,21.125 0,0 z"
       style="fill:#e6e6e6;fill-opacity:1;fill-rule:evenodd;stroke:none"
       id="path602"
       inkscape:connector-curvature="0" />
    <path
       d="m 174.28572,139.53697 c 2,0 3.5,1.625 3.5,3.5 0,2 -1.5,3.625 -3.5,3.625 -2,0 -3.5,-1.625 -3.5,-3.625 0,-1.875 1.5,-3.5 3.5,-3.5 z m -3.5,0 0,0 z m 7.125,7.125 0,0 z"
       style="fill:#000000;fill-opacity:1;fill-rule:evenodd;stroke:none"
       id="path604"
       inkscape:connector-curvature="0" />
    <g
       id="g606"
       transform="matrix(1.25,0,0,-1.25,-348.3393,383.537)">
      <path
         d="m 418.1,195.2 c 1.6,0 2.8,-1.3 2.8,-2.8 0,-1.6 -1.2,-2.9 -2.8,-2.9 -1.6,0 -2.8,1.3 -2.8,2.9 0,1.5 1.2,2.8 2.8,2.8 z"
         style="fill:none;stroke:#808080;stroke-width:0.80000001;stroke-linecap:butt;stroke-linejoin:round;stroke-miterlimit:10;stroke-dasharray:none;stroke-opacity:1"
         id="path608"
         inkscape:connector-curvature="0" />
    </g>
    <g
       id="g610"
       transform="matrix(1.25,0,0,-1.25,-348.3393,383.537)">
      <path
         d="m 415.3,195.2 0,0 z"
         style="fill:none;stroke:#808080;stroke-width:0.80000001;stroke-linecap:butt;stroke-linejoin:round;stroke-miterlimit:10;stroke-dasharray:none;stroke-opacity:1"
         id="path612"
         inkscape:connector-curvature="0" />
    </g>
    <g
       id="g614"
       transform="matrix(1.25,0,0,-1.25,-348.3393,383.537)">
      <path
         d="m 421,189.5 0,0 z"
         style="fill:none;stroke:#808080;stroke-width:0.80000001;stroke-linecap:butt;stroke-linejoin:round;stroke-miterlimit:10;stroke-dasharray:none;stroke-opacity:1"
         id="path616"
         inkscape:connector-curvature="0" />
    </g>
    <g
       id="g618"
       transform="matrix(1.25,0,0,-1.25,-348.3393,383.537)">
      <path
         d="m 447.9,227.5 5.6,0"
         style="fill:none;stroke:#cccccc;stroke-width:0.80000001;stroke-linecap:butt;stroke-linejoin:round;stroke-miterlimit:10;stroke-dasharray:1.4433, 1.4433, 1.4433, 1.4433;stroke-dashoffset:0;stroke-opacity:1"
         id="path620"
         inkscape:connector-curvature="0" />
    </g>
    <g
       id="g622"
       transform="matrix(1.25,0,0,-1.25,-348.3393,383.537)">
      <path
         d="m 382.7,227.5 5.6,0"
         style="fill:none;stroke:#cccccc;stroke-width:0.80000001;stroke-linecap:butt;stroke-linejoin:round;stroke-miterlimit:10;stroke-dasharray:1.4433, 1.4433, 1.4433, 1.4433;stroke-dashoffset:0;stroke-opacity:1"
         id="path624"
         inkscape:connector-curvature="0" />
    </g>
    <g
       id="g626"
       transform="matrix(1.25,0,0,-1.25,-348.3393,383.537)">
      <path
         d="m 382.7,192.3 5.6,0"
         style="fill:none;stroke:#cccccc;stroke-width:0.80000001;stroke-linecap:butt;stroke-linejoin:round;stroke-miterlimit:10;stroke-dasharray:1.4433, 1.4433, 1.4433, 1.4433;stroke-dashoffset:0;stroke-opacity:1"
         id="path628"
         inkscape:connector-curvature="0" />
    </g>
    <g
       id="g630"
       transform="matrix(1.25,0,0,-1.25,-348.3393,383.537)">
      <path
         d="m 388.3,233.1 0,-5.6"
         style="fill:none;stroke:#cccccc;stroke-width:0.80000001;stroke-linecap:butt;stroke-linejoin:round;stroke-miterlimit:10;stroke-dasharray:1.4433, 1.4433, 1.4433, 1.4433;stroke-dashoffset:0;stroke-opacity:1"
         id="path632"
         inkscape:connector-curvature="0" />
    </g>
    <g
       id="g634"
       transform="matrix(1.25,0,0,-1.25,-348.3393,383.537)">
      <path
         d="m 447.9,233.1 0,-5.6"
         style="fill:none;stroke:#cccccc;stroke-width:0.80000001;stroke-linecap:butt;stroke-linejoin:round;stroke-miterlimit:10;stroke-dasharray:1.4433, 1.4433, 1.4433, 1.4433;stroke-dashoffset:0;stroke-opacity:1"
         id="path636"
         inkscape:connector-curvature="0" />
    </g>
    <g
       id="g638"
       transform="matrix(1.25,0,0,-1.25,-348.3393,383.537)">
      <text
         transform="matrix(1,0,0,-1,389.8,152.2)"
         style="font-variant:normal;font-weight:normal;font-size:6px;font-family:ArialMT;-inkscape-font-specification:ArialMT;writing-mode:lr-tb;fill:#808080;fill-opacity:1;fill-rule:nonzero;stroke:none"
         id="text640">
        <tspan
           x="0 3.9000001 8.2019997 12.198 13.89 17.886 19.278 22.278 25.577999 27.27 28.962 30.653999 33.953999 37.349998 40.248001 43.548 46.944 51.743999"
           y="0"
           sodipodi:role="line"
           id="tspan642">PCB Size : 25x24mm</tspan>
      </text>
    </g>
    <g
       id="g644"
       transform="matrix(1.25,0,0,-1.25,-348.3393,383.537)">
      <text
         transform="matrix(1,0,0,-1,389.8,145.3)"
         style="font-variant:normal;font-weight:normal;font-size:6px;font-family:ArialMT;-inkscape-font-specification:ArialMT;writing-mode:lr-tb;fill:#808080;fill-opacity:1;fill-rule:nonzero;stroke:none"
         id="text646">
        <tspan
           x="0 4.302 7.6020002 9.0959997 12.396 15.396 17.087999 20.483999 22.482 25.878 27.57 30.870001 35.669998"
           y="0"
           sodipodi:role="line"
           id="tspan648">Holes are 2mm</tspan>
      </text>
    </g>
  </g>'''


    XML = testCase6

    app = QtGui.QApplication(sys.argv)
    width = 640
    height = 480

    graphicsScene = QtGui.QGraphicsScene(0,0,width,height)
    graphicsScene.addText("Svg_Tools.py test")
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
    maskPen.setWidth(3)
    maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) )
    maskHoverPen.setWidthF(5)
    generateSelectionGraphicsItems( 
        [viewObject], onClickFun, sceneToAddTo=graphicsScene, doPoints=True, doCircles=True, doTextItems=True, doLines=True, doFittedCircles=True,
        maskPen=maskPen , maskBrush=maskBrush, maskHoverPen=maskHoverPen, pointWid=4.0
    )

    view = QtGui.QGraphicsView(graphicsScene)
    view.show()

    sys.exit(app.exec_())



