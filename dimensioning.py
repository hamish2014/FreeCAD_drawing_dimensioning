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
def get_FreeCAD_drawing_variables( moduleGlobals ):
    '''
    Get the FreeCAD window, graphicsScene, drawing page object (...) and returns a dictionary of them
    '''
    mw = QtGui.qApp.activeWindow()
    MdiArea = [c for c in mw.children() if isinstance(c,QtGui.QMdiArea)][0]
    
    try:
        subWinMW = MdiArea.activeSubWindow().children()[3]
    except AttributeError:
        QtGui.QMessageBox.information( QtGui.qApp.activeWindow(), notDrawingPage_title, notDrawingPage_msg  )
        return False
    page = App.ActiveDocument.getObject( subWinMW.objectName() )
    try:
        graphicsView = [ c for c in subWinMW.children() if isinstance(c,QtGui.QGraphicsView)][0]
    except IndexError:
        QtGui.QMessageBox.information( QtGui.qApp.activeWindow(), notDrawingPage_title, notDrawingPage_msg  )
        return False
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

    # updating moduleGlobals
    data = locals()
    del data['moduleGlobals']
    moduleGlobals.update(data)

    transform = QtGui.QTransform()
    transform.translate(VRT_ox, VRT_oy)
    transform.scale(VRT_scale, VRT_scale)
    drawingSelectionLib.Transform_selectionGraphicsItems = transform
    return True

class DimensioningRectPrototype(QtGui.QGraphicsRectItem):

    def activate(self, graphicsScene, graphicsView, page, VRT_scale, VRT_ox, VRT_oy, **otherKWs):
        self.graphicsScene = graphicsScene
        self.graphicsView = graphicsView
        self.drawingPage = page
        self.VRT_ox = VRT_ox
        self.VRT_oy = VRT_oy
        self.VRT_scale = VRT_scale
        graphicsScene.addItem( self )
        self.cleanUpList = []
        self.cleanedUp = False
        #cleanedUp flag required as to monitor for external App.ActiveDocument.recompute() call, which would result in the items in cleanUpList and self being deleted.

    def cleanUp(self):
        for item in self.cleanUpList:
            self.graphicsScene.removeItem(item)
        self.graphicsScene.removeItem(self)
        self.cleanedUp = True 
        #to do add code to keep graphicsView from reseting
        debugPrint(4,'cleanUP: items removed from scene, now recomputing')
        self.drawingPage.touch()
        App.ActiveDocument.recompute()
                
    def keyPressEvent(self, event):
        #if len(event.text()) == 1:
        #   debugPrint(2, 'key pressed: event.text %s (ord %i)' % (event.text(), ord(event.text())))
        if event.text() == chr(27): #escape key
            self.cleanUp()
