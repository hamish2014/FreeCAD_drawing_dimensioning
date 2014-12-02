import numpy
import FreeCAD as App
import FreeCADGui, Part, os
from PySide import QtGui, QtCore, QtSvg
import drawingSelectionLib

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
    Get the FreeCAD window, graphicsScene, drawing page object (...) and returns a dictionary of them
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


