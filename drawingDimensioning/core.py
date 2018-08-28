import numpy
import FreeCAD as App
import FreeCAD, FreeCADGui, Part, os
from PySide import QtGui, QtCore, QtSvg
from svgLib import SvgTextRenderer, SvgTextParser
import traceback


__dir__ = os.path.dirname(os.path.dirname(__file__))
iconPath = os.path.join( __dir__, 'Gui','Resources', 'icons' )
path_dd_resources =  os.path.join( __dir__, 'Gui', 'Resources', 'dd_resources.rcc')
resourcesLoaded = QtCore.QResource.registerResource(path_dd_resources)
assert resourcesLoaded

def debugPrint( level, msg ):
    if level <= debugPrint.level:
        App.Console.PrintMessage(msg + '\n')
debugPrint.level = 3 if hasattr(os,'uname') and os.uname()[1].startswith('antoine') else 2

def findUnusedObjectName(base, counterStart=1, fmt='%03i'):
    i = counterStart
    objName = '%s%s' % (base, fmt%i)
    while hasattr(App.ActiveDocument, objName):
        i = i + 1
        objName = '%s%s' % (base, fmt%i)
    return objName

def errorMessagebox_with_traceback(title='Error'):
    'for also those PySide linked codes where the Python debugger does not work...'
    App.Console.PrintError(traceback.format_exc())
    QtGui.QMessageBox.critical( 
        QtGui.qApp.activeWindow(), 
        title,
        traceback.format_exc(),
        )

notDrawingPage_title = "Current Window not showing a Drawing Page"
notDrawingPage_msg =  "Drawing Dimensioning tools are for page objects generated using the Drawing workbench. Aborting operation."

def getDrawingPageGUIVars():
    '''
    Get the FreeCAD window, graphicsScene, drawing page object, ...
    '''
    # get the active window
    mw = QtGui.qApp.activeWindow()
    MdiArea = [c for c in mw.children() if isinstance(c,QtGui.QMdiArea)][0]

    try:
        subWinMW = MdiArea.activeSubWindow().children()[3]
    except AttributeError:
        QtGui.QMessageBox.information( QtGui.qApp.activeWindow(), notDrawingPage_title, notDrawingPage_msg  )
        raise ValueError, notDrawingPage_title

    # The drawing 'page' is really a group in the model tree
    # The objectName for the group object is not the same as the name shown in
    # the model view, this is the 'Label' property, it *should* be unique.
    # To find the page we are on, we get all the pages which have the same label as
    # the current object. In theory there should therefore only be one page in the list
    # returned by getObjectsByLabel, so we'll just take the first in the list
    pages = App.ActiveDocument.getObjectsByLabel( subWinMW.objectName().encode('utf8') )

    # raise an error explaining that the page wasn't found if the list is empty
    if len(pages) <> 1:
        QtGui.QMessageBox.information( QtGui.qApp.activeWindow(), notDrawingPage_title, notDrawingPage_msg  )
        raise ValueError, notDrawingPage_title

    # get the page from the list
    page = pages[0]

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
    import selectionOverlay
    selectionOverlay.hideSelectionGraphicsItems()    
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


class helpCommand:
    def Activated(self):
        QtGui.QMessageBox.information( 
            QtGui.qApp.activeWindow(), 
            'Drawing Dimensioning Help', 
            '''For help getting started, please refer to the following YouTube video tutorials:

- https://www.youtube.com/watch?v=CTEPu50bG4U
- https://www.youtube.com/watch?v=ztMTLp4wZx4 '''  )
    def GetResources(self): 
        return {
            'Pixmap' : ':/dd/icons/help.svg', 
            'MenuText': 'Help', 
            'ToolTip': 'Help'
            } 

FreeCADGui.addCommand('dd_help', helpCommand())


def dimensionableObjects ( page ):
    'commonly used code in Activate, exclude centerlines'
    from unfold import Proxy_unfold
    drawingViews = []
    for obj in page.Group:
        if hasattr(obj, 'ViewResult'):
            if hasattr(obj, 'Proxy'):
                if isinstance( obj.Proxy, Proxy_unfold ):
                        drawingViews.append( obj )
            else: #assuming some kind of drawing view ...
                drawingViews.append( obj )
    return drawingViews
