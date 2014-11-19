import numpy
import FreeCAD as App
import FreeCADGui, Part, os
from PySide import QtGui, QtCore, QtSvg

__dir__ = os.path.dirname(__file__)

def debugPrint( level, msg ):
    if level <= debugPrint.level:
        App.Console.PrintMessage(msg + '\n')
debugPrint.level = 2

def get_FreeCAD_drawing_variables():
    '''
    Get the FreeCAD window, graphicsScene, drawing page object (...) and returns a dictionary of them
    '''
    mw = QtGui.qApp.activeWindow()
    MdiArea = [c for c in mw.children() if isinstance(c,QtGui.QMdiArea)][0]
    subWinMW = MdiArea.activeSubWindow().children()[3]
    page = App.ActiveDocument.getObject( subWinMW.objectName() )
    graphicsView = [ c for c in subWinMW.children() if isinstance(c,QtGui.QGraphicsView)][0]
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
    return locals()

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
        

    def findSnapPoint(self, x, y, tol=2 ):
        D = ( x - self.snapX)**2 + (y - self.snapY)**2
        debugPrint(4, 'findSnapPoint minD/VRT_scale**2 : %f' % (D.min()/self.VRT_scale**2))
        if D.min()/self.VRT_scale**2  <= tol**2:
            ind = numpy.argmin(D)
            return self.snapX[ind], self.snapY[ind]
        else:
            return None
        
    def keyPressEvent(self, event):
        #if len(event.text()) == 1:
        #   debugPrint(2, 'key pressed: event.text %s (ord %i)' % (event.text(), ord(event.text())))
        if event.text() == chr(27): #escape key
            self.cleanUp()
            

class DimAndTextSelectRect(DimensioningRectPrototype):
    pass
