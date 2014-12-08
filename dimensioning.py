import numpy
import FreeCAD as App
import FreeCADGui, Part, os
from PySide import QtGui, QtCore, QtSvg

__dir__ = os.path.dirname(__file__)

def debugPrint( level, msg ):
    if level <= debugPrint.level:
        App.Console.PrintMessage(msg + '\n')
debugPrint.level = 2

def findUnusedObjectName(base, counterStart=1, fmt='%03i'):
    i = counterStart
    objName = '%s%s' % (base, fmt%i)
    while hasattr(App.ActiveDocument, objName):
        i = i + 1
        objName = '%s%s' % (base, fmt%i)
    return objName

notDrawingPage_title = "Current Window not showing a Drawing Page"
notDrawingPage_msg =  "Drawing Dimensioning tools are for page objects generated using the Drawing workbench. Aborting operation."

def getDrawingPageGUIVars():
    '''
    Get the FreeCAD window, graphicsScene, drawing page object, ...
    '''
    mw = QtGui.qApp.activeWindow()
    MdiArea = [c for c in mw.children() if isinstance(c,QtGui.QMdiArea)][0]
    
    try:
        subWinMW = MdiArea.activeSubWindow().children()[3]
    except AttributeError:
        QtGui.QMessageBox.information( QtGui.qApp.activeWindow(), notDrawingPage_title, notDrawingPage_msg  )
        raise ValueError, notDrawingPage_title 
    page = App.ActiveDocument.getObject( subWinMW.objectName() )
    try:
        graphicsView = [ c for c in subWinMW.children() if isinstance(c,QtGui.QGraphicsView)][0]
    except IndexError:
        QtGui.QMessageBox.information( QtGui.qApp.activeWindow(), notDrawingPage_title, notDrawingPage_msg  )
        raise ValueError, notDrawingPage_title 
    graphicsScene = graphicsView.scene()
    pageRect = graphicsScene.items()[0] #hope this index does not change!
    width = pageRect.boundingRect().width()
    height = pageRect.boundingRect().height()
    #ViewResult has an additional tranform on it [VRT].
    if 'A3' in os.path.basename( page.Template ):
        VRT_scale = width / 420.0 #VRT = view result transform, where 420mm is the width of an A3 page.
    else: #assuming A4
        VRT_scale = width / 297.0
    VRT_ox = -1 / VRT_scale
    VRT_oy = -1 / VRT_scale

    transform = QtGui.QTransform()
    transform.translate(VRT_ox, VRT_oy)
    transform.scale(VRT_scale, VRT_scale)

    return DrawingPageGUIVars(locals())

class DrawingPageGUIVars:
    "for codding convience, wrt v.transform instead of v['transform']"
    def __init__(self, data):
        self.__dict__.update(data)

class DimensioningProcessTracker:
    def activate( self, drawingVars):
        V = drawingVars #short hand
        self.drawingVars = V
        self.stage = 0
        self.svg_preview_KWs = {
            'svgTag' : 'svg',
            'svgParms' : 'width="%(width)i" height="%(height)i" transform="translate( %(VRT_ox)f, %(VRT_oy)f) scale( %(VRT_scale)f, %(VRT_scale)f)"' % V.__dict__
            }


def recomputeWithOutViewReset( drawingVars ):
    '''
    By default app.recompute() resets the drawing view, which can be rather frustrating...
    '''
    printGraphicsViewInfo( drawingVars )
    gV =  drawingVars.graphicsView
    T = gV.transform() 
    scale = T.m11()
    ##attempting to find centre of view
    #dx = gV.mapToScene( 0,0).x()
    #dy = gV.mapToScene( 0,0).y()
    ## now scene_x = view_x/scale + dx; so
    #centerView = [
    #    0.5*gV.width(),
    #    0.5*gV.height(), 
    #    ]
    #centerScene = gV.mapToScene( *centerView )
    #centerOn approach did not work rather using scroll bars.
    h_scrollValue = gV.horizontalScrollBar().value()
    v_scrollValue = gV.verticalScrollBar().value()
    drawingVars.page.touch()
    App.ActiveDocument.recompute()
    gV.scale( scale , scale ) # 1.38 is a correction factor derived from printGraphicsViewInfo
    #scale correction
    for i in range(3):
        scale_actual = gV.transform().m11()
        debugPrint(4, 'scale_desired %1.3f scale_actual %1.3f' % (scale, scale_actual))
        s_correction = scale / scale_actual
        gV.scale( s_correction, s_correction )

    gV.horizontalScrollBar().setValue( h_scrollValue )
    gV.verticalScrollBar().setValue( v_scrollValue )    
    printGraphicsViewInfo( drawingVars )


def printGraphicsViewInfo( drawingVars ):
        '''
        A PySide.QtGui.QTransform object contains a 3 x 3 matrix. The m31 (dx ) and m32 (dy ) elements specify horizontal and vertical translation. 
        The m11 and m22 elements specify horizontal and vertical scaling. 
        The m21 and m12 elements specify horizontal and vertical shearing . 
        And finally, the m13 and m23 elements specify horizontal and vertical projection, with m33 as an additional projection factor.

        This function was written help restore the view transform after App.ActiveDocument.recompute(); 
        example of how to get T, T= preview.drawingVars.graphicsView.transform()

        DrawingView.cpp: line134: s->setSceneRect(m_outlineItem->boundingRect().adjusted(-10, -10, 10, 10)); # s is QGraphicsScene  used for scroll bars!
        '''
        T = drawingVars.graphicsView.transform()
        sx, sy, dx, dy = T.m11(), T.m22(), T.m31(), T.m32()
        debugPrint(4,'graphicsView transform info: sx %1.2f, sy %1.2f, dx %1.2f, dy %1.2f' % (sx, sy, dx, dy) )
        debugPrint(4,'    [ %1.2f  %1.2f  %1.2f ]' % (T.m11(), T.m12(), T.m13() ))
        debugPrint(4,'M = [ %1.2f  %1.2f  %1.2f ]' % (T.m21(), T.m22(), T.m23() ))
        debugPrint(4,'    [ %1.2f  %1.2f  %1.2f ]' % (T.m31(), T.m32(), T.m33() ))

        #r = preview.drawingVars.graphicsView.sceneRect() #seems to be used for scroll bars, not for anything else
        #debugPrint(2,'graphicsView.sceneRect info: topLeft.x %3.2f, topLeft.y %3.2f, bottomRight.x %3.2f, bottomRight.y %3.2f' \
        #               % (r.topLeft().x(), r.topLeft().y(), r.bottomRight().x(), r.bottomRight().y() ) )

        #T = drawingVars.graphicsView.viewportTransform()
        #sx, sy, dx, dy = T.m11(), T.m22(), T.m31(), T.m32()
        #debugPrint(2,'viewPort transform info: sx %1.2f, sy %1.2f, dx %1.2f, dy %1.2f' % (sx, sy, dx, dy) )
        #debugPrint(4,'    [ %1.2f  %1.2f  %1.2f ]' % (T.m11(), T.m12(), T.m13() ))
        #debugPrint(4,'M = [ %1.2f  %1.2f  %1.2f ]' % (T.m21(), T.m22(), T.m23() ))
        #debugPrint(4,'    [ %1.2f  %1.2f  %1.2f ]' % (T.m31(), T.m32(), T.m33() ))
