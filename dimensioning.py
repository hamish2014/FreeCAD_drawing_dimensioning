import numpy
import FreeCAD as App
import FreeCAD, FreeCADGui, Part, os
from PySide import QtGui, QtCore, QtSvg
from textSvg import SvgTextRenderer, SvgTextParser
import traceback

__dir__ = os.path.dirname(__file__)
iconPath = os.path.join( __dir__, 'Resources', 'icons' )

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
    pages = App.ActiveDocument.getObjectsByLabel( subWinMW.objectName() )

    # raise an error explaining that the page wasn't found if the list is empty
    if len(pages) <> 1:
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


defaultRealParameters = {
    'strokeWidth': 0.3,
    'arrowL1': 3.0,
    'arrowL2': 1.0,
    'arrowW': 2.0,
    'gap_datum_points': 2.0,
    'dimension_line_overshoot': 1.0,
    'centerPointDia': 1.0,
    'centerLine_len_gap': 2.0,
    'centerLine_len_dash': 6.0,
    'centerLine_len_dot': 2.0,
    'centerLine_width': 0.3,
}

def unsignedToRGBText(v):
    r = v >> 24
    g = (v >> 16) - (v >> 24 << 8 )
    b = (v >>  8) - (v >> 16 << 8 )
    return 'rgb(%i,%i,%i)' % (r, g, b)

def RGBtoUnsigned(r,g,b):
    return (r << 24) + (g << 16) + (b << 8) 

defaultColorParameters = {
    'lineColor' : RGBtoUnsigned(0, 0, 255),
    'centerLine_color' : RGBtoUnsigned(0, 0, 255),
}

defaultTextParameters = {
    'textRenderer_family':'Verdana',
    'textRenderer_size':'3.6',
    'textRenderer_color': RGBtoUnsigned(255, 0, 0),
}

class DimensioningProcessTracker:
    def activate( self, drawingVars, realParms=[], colorParms=[], textParms=[]):
        V = drawingVars #short hand
        self.drawingVars = V
        self.stage = 0
        # get FreeCAD preferences
        parms = App.ParamGet("User parameter:BaseApp/Preferences/Mod/Drawing_Dimensioning")
        KWs = {}
        for name in realParms:
            KWs[name] = parms.GetFloat( name, defaultRealParameters[name] )
        for cName in colorParms:
            KWs[cName] = unsignedToRGBText( parms.GetUnsigned(cName, defaultColorParameters[cName]) )
        for prefix in textParms:
            family = parms.GetString( prefix+'_family', defaultTextParameters[ prefix+'_family' ])
            size = parms.GetString( prefix+'_size', defaultTextParameters[ prefix+'_size' ])
            color = unsignedToRGBText(  parms.GetUnsigned(prefix+'_color', defaultTextParameters[ prefix+'_color' ] ) )
            KWs[prefix] = SvgTextRenderer(family, size, color)
        self.dimensionConstructorKWs = KWs
        debugPrint(3, 'dimensionConstructorKWs %s' % self.dimensionConstructorKWs )
        self.svg_preview_KWs = {
            'svgTag' : 'svg',
            'svgParms' : 'width="%(width)i" height="%(height)i"' % V.__dict__ 
        }
        self.svg_preview_KWs.update( KWs )

def UnitConversionFactor():
    #found using App.ParamGet("User parameter:BaseApp/Preferences").Export('/tmp/p3')
    p = App.ParamGet("User parameter:BaseApp/Preferences/Units")
    UserSchema = p.GetInt("UserSchema")
    if UserSchema == 0: #standard (mm/kg/s/degree
        return 1.0
    elif UserSchema == 1: #standard (m/kg/s/degree)
        return 1000.0
    else: #either US customary, or Imperial decimal
        return 25.4

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

