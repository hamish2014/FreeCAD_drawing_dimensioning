import numpy
import FreeCAD as App
import FreeCADGui, Part, os
from PySide import QtGui, QtCore, QtSvg

__dir__ = os.path.dirname(__file__)
iconPath = os.path.join( __dir__, 'Resources', 'icons' )

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
    width = pageRect.rect().width()
    height = pageRect.rect().height()
    #ViewResult has an additional tranform on it [VRT].
    #if width > 1400: #then A3 # or == 1488 in FreeCAD v 0.15 
    #    VRT_scale = width / 420.0 #VRT = view result transform, where 420mm is the width of an A3 page.
    #else: #assuming A4
    #    VRT_scale = width / 297.0
    VRT_scale = 3.542 #i wonder where this number comes from

    VRT_ox = pageRect.rect().left() / VRT_scale
    VRT_oy = pageRect.rect().top() / VRT_scale

    transform = QtGui.QTransform()
    transform.translate(VRT_ox, VRT_oy)
    transform.scale(VRT_scale, VRT_scale)

    return DrawingPageGUIVars(locals())

class DrawingPageGUIVars:
    "for coding convience, wrt v.transform instead of v['transform']"
    def __init__(self, data):
        self.__dict__.update(data)

class DimensioningProcessTracker:
    def activate( self, drawingVars, extraRealParms = []):
        V = drawingVars #short hand
        self.drawingVars = V
        self.stage = 0
        self.svg_preview_KWs = {
            'svgTag' : 'svg',
            'svgParms' : 'width="%(width)i" height="%(height)i"' % V.__dict__ }
        # get FreeCAD preferences
        self.dimensionConstructorKWs = {}
        parms = App.ParamGet("User parameter:BaseApp/Preferences/Mod/Drawing_Dimensioning")
        parmNames =    ['strokeWidth', 'fontSize', 'arrowL1', 'arrowL2', 'arrowW']
        parmDefaults = [ 0.3, 4.0, 3.0, 1.0, 2.0 ]
        assert len(parmNames) == len(parmDefaults)
        for name, default in zip(parmNames, parmDefaults) + extraRealParms:
            self.dimensionConstructorKWs[name] = parms.GetFloat(name, default)
        def getColor(parmName, default):
            v = parms.GetUnsigned(parmName, default)
            r = v >> 24
            g = (v >> 16) - (v >> 24 << 8 )
            b = (v >>  8) - (v >> 16 << 8 )
            return 'rgb(%i,%i,%i)' % (r, g, b)
        self.dimensionConstructorKWs['lineColor'] = getColor('lineColor',255 << 8)
        self.dimensionConstructorKWs['fontColor'] = getColor('fontColor',255 << 24)
        debugPrint(3, 'dimensionConstructorKWs %s' % self.dimensionConstructorKWs )
        self.svg_preview_KWs.update( self.dimensionConstructorKWs )
        
            
        


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
    gV.scale( scale , scale )
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
